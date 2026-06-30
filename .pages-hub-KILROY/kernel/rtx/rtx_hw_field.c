// SPDX-License-Identifier: GPL-2.0
// KILROY CPU + RAM fields — micro/submicro telemetry.

#include <linux/cpumask.h>
#include <linux/kernel.h>
#include <linux/ktime.h>
#include <linux/minmax.h>
#include <linux/percpu.h>
#include <linux/sched.h>

#include <asm/ptrace.h>

#include "kilroy_units.h"
#include "rtx_core.h"
#include "rtx_hw_field.h"
#include "rtx_slots.h"

static struct kilroy_field_cpu kilroy_cpu_state;
static struct kilroy_field_ram kilroy_ram_state;
static u64 kilroy_syscall_window;
static u64 kilroy_window_start_ns;

DEFINE_PER_CPU(u8, rtx_ram_field_hint);
EXPORT_PER_CPU_SYMBOL(rtx_ram_field_hint);

static u32 kilroy_compute_ram_pressure_submicro(void)
{
	u64 alloc, usable, pct;

	alloc = kilroy_ram_state.allocated_pages;
	usable = kilroy_ram_state.usable_pages;
	if (!usable)
		return 0;
	pct = min_t(u64, 1000, (alloc * 1000) / usable);
	return (u32)(pct * KILROY_SUBMICRO_PER_MICRO);
}

void kilroy_hw_fields_init(void)
{
	struct rtx_four_slots *s = rtx_slots();

	kilroy_cpu_state.online_cpus = num_online_cpus();
	kilroy_cpu_state.active_cpu = smp_processor_id();
	kilroy_cpu_state.phi_coupling_micro = KILROY_FIELD_PHI_MICRO;
	kilroy_ram_state.total_pages = s->memory.total_pages;
	kilroy_ram_state.allocated_pages = s->memory.allocated_pages;
	kilroy_ram_state.usable_pages = s->memory.usable_pages;
	kilroy_ram_state.mmap_ops = s->memory.mmap_ops;
	kilroy_ram_state.safety_margin_mb = RTX_MEMORY_SAFETY_MB;
	kilroy_ram_state.zmm_entropy = s->memory.zmm[0][0];
	kilroy_ram_state.pressure_submicro = kilroy_compute_ram_pressure_submicro();
}

void kilroy_cpu_field_tick(u32 nr, bool fabric)
{
	u64 now = ktime_get_ns();

	(void)nr;
	kilroy_cpu_state.syscall_total++;
	kilroy_syscall_window++;

	if (!kilroy_window_start_ns)
		kilroy_window_start_ns = now;

	if (now - kilroy_window_start_ns >= 1000000ULL) {
		kilroy_cpu_state.syscall_rate_submicro =
			(u32)min_t(u64, KILROY_SCALE_SUBMICRO,
				   kilroy_syscall_window * KILROY_SUBMICRO_PER_MICRO);
		kilroy_syscall_window = 0;
		kilroy_window_start_ns = now;
	}

	if (fabric) {
		kilroy_cpu_state.fabric_ops++;
		kilroy_cpu_state.phi_coupling_micro = min_t(u32, KILROY_FCC_SCALE_MAX_MICRO,
			kilroy_cpu_state.phi_coupling_micro + KILROY_MICRO_PER_MILLI);
	} else if (kilroy_cpu_state.phi_coupling_micro > KILROY_FIELD_PHI_MICRO) {
		kilroy_cpu_state.phi_coupling_micro -= KILROY_MICRO_PER_MILLI;
	}

	kilroy_cpu_state.active_cpu = smp_processor_id();
}

void kilroy_ram_field_pre_touch(u32 nr)
{
	if (rtx_is_memory_syscall(nr))
		this_cpu_write(rtx_ram_field_hint, 1);
	else
		this_cpu_write(rtx_ram_field_hint, 0);
}

void kilroy_ram_field_post_touch(u32 nr, long ret, const struct pt_regs *regs)
{
	struct rtx_four_slots *s = rtx_slots();

	if (ret < 0 || !regs)
		return;

	switch (nr) {
	case 214:
		kilroy_ram_state.brk_ops++;
		break;
	case 222:
	case 215:
		kilroy_ram_state.mmap_ops = s->memory.mmap_ops;
		break;
	default:
		break;
	}

	kilroy_ram_state.allocated_pages = s->memory.allocated_pages;
	kilroy_ram_state.zmm_entropy = s->memory.zmm[0][0];
	kilroy_ram_state.pressure_submicro = kilroy_compute_ram_pressure_submicro();
	kilroy_ram_state.bandwidth_micro = min_t(u32, KILROY_FCC_SCALE_MAX_MICRO,
		kilroy_ram_state.bandwidth_micro + KILROY_MICRO_FROM_MILLI(kilroy_ram_state.mmap_ops & 7));
}

void kilroy_cpu_field_sync_power(u8 tier, unsigned int max_khz, bool burst_ready)
{
	kilroy_cpu_state.volt_tier = tier;
	kilroy_cpu_state.max_khz = max_khz;
	kilroy_cpu_state.burst_ready = burst_ready ? 1 : 0;
}

void kilroy_ram_field_fill(struct kilroy_field_ram *out)
{
	if (out)
		*out = kilroy_ram_state;
}

void kilroy_cpu_field_fill(struct kilroy_field_cpu *out)
{
	if (out)
		*out = kilroy_cpu_state;
}

u32 kilroy_ram_pressure_submicro(void)
{
	return kilroy_ram_state.pressure_submicro;
}