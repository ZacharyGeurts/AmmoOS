// SPDX-License-Identifier: GPL-2.0-only
/* DIRECT field — coherence without page-cache layers (beyond legacy caching) */
#include <linux/kernel.h>
#include <linux/mman.h>

#include <asm/ptrace.h>

#include "kilroy_direct_field.h"
#include "kilroy_units.h"

struct kilroy_direct_state {
	u64 direct_maps;
	u64 direct_bytes;
	u64 cached_maps;
	u64 coherence_ops;
};

static struct kilroy_direct_state direct_field;

void kilroy_direct_field_init(void)
{
	memset(&direct_field, 0, sizeof(direct_field));
	pr_info("kilroy_field: DIRECT field active — anonymous/maps bypass cache story\n");
}

void kilroy_direct_field_tick(u32 nr)
{
	switch (nr) {
	case 222: case 215: case 214: case 226:
		direct_field.coherence_ops++;
		break;
	default:
		break;
	}
}

void kilroy_direct_field_post_mmap(const struct pt_regs *regs, long ret)
{
	unsigned long len;
	unsigned long flags;

	if (ret < 0 || !regs)
		return;

	len = regs->si;
	flags = regs->r10;

	if (flags & MAP_ANONYMOUS) {
		direct_field.direct_maps++;
		direct_field.direct_bytes += len;
	} else {
		direct_field.cached_maps++;
	}
}

void kilroy_direct_field_fill(struct kilroy_field_direct *out)
{
	u64 total;
	u32 ratio;

	memset(out, 0, sizeof(*out));
	out->direct_maps = direct_field.direct_maps;
	out->direct_bytes = direct_field.direct_bytes;
	out->cached_maps = direct_field.cached_maps;
	out->coherence_ops = direct_field.coherence_ops;

	total = direct_field.direct_maps + direct_field.cached_maps;
	if (total)
		ratio = (u32)div_u64(direct_field.direct_maps * KILROY_SCALE_MICRO, total);
	else
		ratio = KILROY_SCALE_MICRO;
	out->direct_ratio_micro = ratio;
}