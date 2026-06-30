// SPDX-License-Identifier: GPL-2.0-only
/* 64-bit system call dispatch */

#include <linux/errno.h>
#include <linux/linkage.h>
#include <linux/percpu.h>
#include <linux/sys.h>
#include <linux/syscalls.h>
#include <linux/entry-common.h>
#include <linux/nospec.h>
#include <asm/syscall.h>
#include <asm/rtx_field.h>

#ifdef CONFIG_RTX_FIELD_DIE
#include "kilroy_cache_field.h"
#include "kilroy_direct_field.h"
#include "kilroy_flow.h"
#include "kilroy_nexus_guard.h"
#include "rtx_core.h"
#include "rtx_fcc.h"
#include "rtx_hw_field.h"
#include "rtx_power.h"
#include "rtx_slots.h"

static inline void kilroy_power_kick_fabric(bool fabric)
{
	if (fabric)
		rtx_power_kick();
}
#endif

#define __SYSCALL(nr, sym) extern long __x64_##sym(const struct pt_regs *);
#define __SYSCALL_NORETURN(nr, sym) extern long __noreturn __x64_##sym(const struct pt_regs *);
#include <asm/syscalls_64.h>
#ifdef CONFIG_X86_X32_ABI
#include <asm/syscalls_x32.h>
#endif
#undef  __SYSCALL

#undef  __SYSCALL_NORETURN
#define __SYSCALL_NORETURN __SYSCALL

/*
 * The sys_call_table[] is no longer used for system calls, but
 * kernel/trace/trace_syscalls.c still wants to know the system
 * call address.
 */
#define __SYSCALL(nr, sym) __x64_##sym,
const sys_call_ptr_t sys_call_table[] = {
#include <asm/syscalls_64.h>
};
#undef  __SYSCALL

#define __SYSCALL(nr, sym) case nr: return __x64_##sym(regs);
long x64_sys_call(const struct pt_regs *regs, unsigned int nr)
{
	switch (nr) {
	#include <asm/syscalls_64.h>
	default: return __x64_sys_ni_syscall(regs);
	}
}

#ifdef CONFIG_X86_X32_ABI
long x32_sys_call(const struct pt_regs *regs, unsigned int nr)
{
	switch (nr) {
	#include <asm/syscalls_x32.h>
	default: return __x64_sys_ni_syscall(regs);
	}
}
#endif

static __always_inline bool do_syscall_x64(struct pt_regs *regs, int nr)
{
	unsigned int unr = nr;

	if (likely(unr < NR_syscalls)) {
		unr = array_index_nospec(unr, NR_syscalls);
		regs->ax = x64_sys_call(regs, unr);
		return true;
	}
	return false;
}

static __always_inline bool do_syscall_x32(struct pt_regs *regs, int nr)
{
	unsigned int xnr = nr - __X32_SYSCALL_BIT;

	if (IS_ENABLED(CONFIG_X86_X32_ABI) && likely(xnr < X32_NR_syscalls)) {
		xnr = array_index_nospec(xnr, X32_NR_syscalls);
		regs->ax = x32_sys_call(regs, xnr);
		return true;
	}
	return false;
}

#ifdef CONFIG_RTX_FIELD_DIE
static void rtx_post_syscall_memory(const struct pt_regs *regs, unsigned int nr)
{
	switch (nr) {
	case 214: /* brk */
		if (regs->ax >= 0)
			rtx_slots_account_brk((u64)regs->ax);
		break;
	case 215: /* munmap */
		if (regs->ax >= 0)
			rtx_slots_account_munmap((u64)regs->si);
		break;
	case 222: /* mmap */
		if (regs->ax >= 0) {
			rtx_slots_account_mmap((u64)regs->si);
			kilroy_direct_field_post_mmap(regs, regs->ax);
		}
		break;
	default:
		break;
	}
}
#endif

/* Returns true to return using SYSRET, or false to use IRET */
__visible noinstr bool do_syscall_64(struct pt_regs *regs, int nr)
{
	nr = syscall_enter_from_user_mode(regs, nr);

	instrumentation_begin();
	add_random_kstack_offset();

#ifdef CONFIG_RTX_FIELD_DIE
	{
		const unsigned int unr = (unsigned int)nr;
		bool fabric;
		int sec;

#ifdef CONFIG_RTX_FIELD_4SLOT_SECURITY
		sec = rtx_slots_verify();
		if (sec < 0) {
			regs->ax = rtx_slots_tamper_action();
			instrumentation_end();
			syscall_exit_to_user_mode(regs);
			return true;
		}
#endif

		rtx_slots_context_tick(unr);
#ifdef CONFIG_RTX_FIELD_NEXUS_GUARD
		{
			int ngx = kilroy_nexus_guard_evaluate();

			if (ngx < 0) {
				regs->ax = ngx;
				instrumentation_end();
				syscall_exit_to_user_mode(regs);
				return true;
			}
		}
#endif
		kilroy_ram_field_pre_touch(unr);
		kilroy_cache_field_tick(unr);
		kilroy_direct_field_tick(unr);
		rtx_fcc_syscall_touch();

#ifdef CONFIG_RTX_FIELD_ASM_GATE
		fabric = this_cpu_read(rtx_fabric_hint);
		if (fabric && !rtx_fcc_fabric_voltage_ok()) {
			regs->ax = -EAGAIN;
			instrumentation_end();
			syscall_exit_to_user_mode(regs);
			return true;
		}
		if (fabric && this_cpu_read(rtx_thermo_budget_micro) <= RTX_ENTROPY_FLOOR_MICRO) {
			regs->ax = -EAGAIN;
			instrumentation_end();
			syscall_exit_to_user_mode(regs);
			return true;
		}
#else
		fabric = rtx_is_fabric_syscall(unr);
		if (fabric && !rtx_fcc_fabric_voltage_ok()) {
			regs->ax = -EAGAIN;
			instrumentation_end();
			syscall_exit_to_user_mode(regs);
			return true;
		}
		if (fabric && rtx_thermo_debit() < 0) {
			regs->ax = -EAGAIN;
			instrumentation_end();
			syscall_exit_to_user_mode(regs);
			return true;
		}
#endif
		rtx_account_syscall(unr, fabric);
		kilroy_power_kick_fabric(fabric);
	}
#endif

	if (!do_syscall_x64(regs, nr) && !do_syscall_x32(regs, nr) && nr != -1) {
		regs->ax = __x64_sys_ni_syscall(regs);
	}

#ifdef CONFIG_RTX_FIELD_DIE
	{
		const unsigned int unr = (unsigned int)nr;
		bool fabric_post = false;

#ifdef CONFIG_RTX_FIELD_ASM_GATE
		fabric_post = this_cpu_read(rtx_fabric_hint);
#else
		fabric_post = rtx_is_fabric_syscall(unr);
#endif
		if (rtx_is_memory_syscall(unr)) {
			rtx_post_syscall_memory(regs, unr);
			kilroy_ram_field_post_touch(unr, regs->ax, regs);
		}
		kilroy_flow_tick(unr, fabric_post, regs->ax);
	}
#endif

	instrumentation_end();
	syscall_exit_to_user_mode(regs);

	if (cpu_feature_enabled(X86_FEATURE_XENPV))
		return false;

	if (unlikely(regs->cx != regs->ip || regs->r11 != regs->flags))
		return false;

	if (unlikely(regs->cs != __USER_CS || regs->ss != __USER_DS))
		return false;

	if (unlikely(regs->ip >= TASK_SIZE_MAX))
		return false;

	if (unlikely(regs->flags & (X86_EFLAGS_RF | X86_EFLAGS_TF)))
		return false;

	return true;
}