// SPDX-License-Identifier: GPL-2.0
// KILROY 4-slot security + RAM field (ZMM1024).

#include <linux/errno.h>
#include <linux/kernel.h>
#include <linux/timekeeping.h>
#include <linux/mm.h>
#include <linux/minmax.h>
#include <linux/random.h>
#include <linux/sched.h>
#include <linux/signal.h>

#include "kilroy_units.h"
#include "rtx_slots.h"
#include "rtx_core.h"

static struct rtx_four_slots rtx_slot_state;

struct rtx_four_slots *rtx_slots(void)
{
	return &rtx_slot_state;
}

static u64 rtx_boot_entropy(void)
{
	u64 e;

	get_random_bytes(&e, sizeof(e));
	e ^= ktime_get_boottime_ns();
	e ^= (u64)(current->pid + 1);
	return e;
}

void rtx_slots_init(void)
{
	struct rtx_four_slots *s = &rtx_slot_state;
	u64 entropy = rtx_boot_entropy();

	memset(s, 0, sizeof(*s));
	s->time.genesis_ns = ktime_get_boottime_ns();
	s->time.entropy = entropy;
	s->time.entropy_check = entropy ^ RTX_ENTROPY_XOR_MASK;
	s->memory.total_pages = totalram_pages();
	s->memory.safety_margin_pages =
		(u64)RTX_MEMORY_SAFETY_MB * (1024 * 1024 / PAGE_SIZE);
	s->memory.usable_pages = s->memory.total_pages - s->memory.safety_margin_pages;
	s->thermo.budget_micro = KILROY_THERMO_INIT_MICRO;
	s->thermo.fcc_guard_scale_micro = KILROY_FCC_SCALE_MAX_MICRO;
	s->thermo.acct.phi_micro = KILROY_FIELD_PHI_MICRO;
	s->thermo.acct.entropy_floor_submicro = KILROY_ENTROPY_FLOOR_SUBMICRO;
	s->thermo.acct.boundary_thermo_micro = KILROY_THERMO_INIT_MICRO;
	s->context.magic = KILROY_FIELD_MAGIC;
	s->context.layout_version = KILROY_LAYOUT_VERSION;
	s->context.pid = 0;
	s->context.seal_hash = entropy ^ KILROY_FIELD_MAGIC;
}

void rtx_slots_seal_time(void)
{
	struct rtx_slot_time *t = &rtx_slot_state.time;

	if (t->sealed)
		return;
	t->sealed_ns = ktime_get_boottime_ns() - t->genesis_ns;
	t->sealed = 1;
	pr_info("kilroy_field: slot0 TIME sealed @ %llu ns entropy=0x%016llx\n",
		t->sealed_ns, t->entropy);
}

int rtx_slots_verify(void)
{
	struct rtx_four_slots *s = &rtx_slot_state;

	if (!s->time.sealed)
		return 0;
	if ((s->time.entropy ^ RTX_ENTROPY_XOR_MASK) != s->time.entropy_check)
		return -EFAULT;
	if (s->context.layout_version != KILROY_LAYOUT_VERSION)
		return -EFAULT;
	if (s->context.magic != KILROY_FIELD_MAGIC)
		return -EFAULT;
	return 0;
}

int rtx_slots_tamper_action(void)
{
	pr_alert("kilroy_field: 4-slot tamper detected — aborting task\n");
	return -EFAULT;
}

void rtx_zmm_touch(u32 row, u32 col, u32 delta)
{
	struct rtx_slot_memory *m = &rtx_slot_state.memory;
	u32 r = row % RTX_ZMM_ROWS;
	u32 c = col % RTX_ZMM_COLS;

	m->zmm[r][c] ^= delta ^ ((r * 137u) ^ (c * 73u));
}

static u64 pages_from_len(u64 len)
{
	if (!len)
		return 0;
	return (len + PAGE_SIZE - 1) >> PAGE_SHIFT;
}

void rtx_slots_account_mmap(u64 len)
{
	struct rtx_slot_memory *m = &rtx_slot_state.memory;
	u64 pages = pages_from_len(len);

	m->mmap_ops++;
	m->allocated_pages += pages;
#ifdef CONFIG_RTX_FIELD_ZMM_HOTPATH
	rtx_zmm_touch(m->mmap_ops & 31u, 7u, (u32)pages);
	rtx_zmm_touch((u32)(pages & 31u), (m->mmap_ops >> 3) & 31u, (u32)(len & 0xFFFFFFFFu));
#endif
	if (m->allocated_pages > m->usable_pages)
		m->allocated_pages = m->usable_pages;
}

void rtx_slots_account_munmap(u64 len)
{
	struct rtx_slot_memory *m = &rtx_slot_state.memory;
	u64 pages = pages_from_len(len);

	m->mmap_ops++;
	if (m->allocated_pages >= pages)
		m->allocated_pages -= pages;
	rtx_zmm_touch((m->mmap_ops + 11u) & 31u, (m->mmap_ops + 7u) & 31u, (u32)pages);
}

void rtx_slots_account_brk(u64 new_brk)
{
	rtx_zmm_touch(0u, 2u, (u32)(new_brk >> 12));
}

bool rtx_is_memory_syscall(u32 nr)
{
	switch (nr) {
	case 214:
	case 215:
	case 222:
	case 226:
		return true;
	default:
		return false;
	}
}