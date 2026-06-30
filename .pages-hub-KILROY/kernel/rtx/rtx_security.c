// SPDX-License-Identifier: GPL-2.0
// KILROY slot3 context seal — per-syscall generation hash + NEXUS chain.

#include <linux/pid.h>
#include <linux/sched.h>

#include "kilroy_nexus_guard.h"
#include "rtx_slots.h"

void rtx_slots_context_tick(u32 nr)
{
	struct rtx_slot_context *ctx = &rtx_slots()->context;

	ctx->syscall_generation++;
	ctx->pid = task_pid_nr(current);
	ctx->seal_hash = (ctx->seal_hash * 0x5851F42D4C957F2DULL) ^
			 nr ^ ctx->syscall_generation ^ KILROY_FIELD_MAGIC;
#ifdef CONFIG_RTX_FIELD_NEXUS_GUARD
	kilroy_nexus_guard_tick(nr);
#endif
}