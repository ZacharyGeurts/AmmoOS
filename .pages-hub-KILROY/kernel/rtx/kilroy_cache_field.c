// SPDX-License-Identifier: GPL-2.0-only
/* CACHE field — shed legacy Linux cache retention; Field coherence is primary */
#include <linux/jiffies.h>
#include <linux/kernel.h>
#include <linux/mm.h>
#include <linux/swap.h>

#include "kilroy_cache_field.h"
#include "kilroy_units.h"
#include "rtx_slots.h"

#define KILROY_CACHE_SHED_MASK	0x1ff
#define KILROY_CACHE_PRESSURE_THRESH_MICRO 650000u

struct kilroy_cache_state {
	u32 shed_count;
	u32 bypass_ops;
	u32 slab_drops;
	u32 lru_drains;
	u32 pressure_micro;
	unsigned long last_shed_jiffies;
};

static struct kilroy_cache_state cache_field;

static bool kilroy_cache_memory_nr(u32 nr)
{
	switch (nr) {
	case 0: case 1: case 2:   /* read write open */
	case 222: case 215: case 214: case 226: /* mmap munmap brk mprotect */
	case 17: case 63:         /* readv pread64 */
		return true;
	default:
		return false;
	}
}

static void kilroy_cache_shed_layers(void)
{
	lru_add_drain();
	cache_field.lru_drains++;
	drop_slab();
	cache_field.slab_drops++;
	cache_field.shed_count++;
	cache_field.last_shed_jiffies = jiffies;
	cache_field.pressure_micro = max_t(u32, 0,
		cache_field.pressure_micro - KILROY_MICRO_FROM_MILLI(120));
}

void kilroy_cache_field_init(void)
{
	memset(&cache_field, 0, sizeof(cache_field));
	cache_field.pressure_micro = KILROY_MICRO_FROM_MILLI(100);
	pr_info("kilroy_field: CACHE field active — field-direct over page-cache retention\n");
}

void kilroy_cache_field_tick(u32 nr)
{
	struct rtx_four_slots *s = rtx_slots();

	if (!kilroy_cache_memory_nr(nr))
		return;

	cache_field.bypass_ops++;

	/* Field RAM pressure feeds CACHE shed decision */
	if (s) {
		u64 alloc = s->memory.allocated_pages;
		u64 usable = max_t(u64, s->memory.usable_pages, 1);

		cache_field.pressure_micro = min_t(u32, KILROY_SCALE_MICRO,
			(u32)div_u64(alloc * KILROY_SCALE_MICRO, usable));
	}

	if ((s->context.syscall_generation & KILROY_CACHE_SHED_MASK) == 0 &&
	    cache_field.pressure_micro >= KILROY_CACHE_PRESSURE_THRESH_MICRO) {
		if (time_after(jiffies, cache_field.last_shed_jiffies + HZ * 5))
			kilroy_cache_shed_layers();
	}
}

void kilroy_cache_field_fill(struct kilroy_field_cache *out)
{
	u32 retention;

	memset(out, 0, sizeof(*out));
	out->shed_count = cache_field.shed_count;
	out->bypass_ops = cache_field.bypass_ops;
	out->slab_drops = cache_field.slab_drops;
	out->lru_drains = cache_field.lru_drains;
	out->pressure_micro = cache_field.pressure_micro;
	retention = KILROY_SCALE_MICRO - min_t(u32, KILROY_SCALE_MICRO,
					       cache_field.pressure_micro);
	out->retention_micro = retention;
}