/* SPDX-License-Identifier: GPL-2.0 */
/* KILROY (AmouranthOS) — ASM fabric + RAM field classify, thermo debit (micro). */
#include <linux/linkage.h>
#include <asm/errno.h>
#include <asm/percpu.h>
#include <asm/rtx_field.h>

	.section .entry.text, "ax"

	.align 4
SYM_FUNC_START_NOALIGN(rtx_syscall_preflight)
	mov	%edi, %eax
	cmp	$RTX_NR_BRK, %eax
	je	.Lram
	cmp	$RTX_NR_MUNMAP, %eax
	je	.Lram
	cmp	$RTX_NR_MMAP, %eax
	je	.Lram
	cmp	$RTX_NR_MPROTECT, %eax
	je	.Lram
	movb	$0, PER_CPU_VAR(rtx_ram_field_hint)
	jmp	.Lclassify
.Lram:
	movb	$1, PER_CPU_VAR(rtx_ram_field_hint)
.Lclassify:
	mov	%edi, %eax
	cmp	$RTX_NR_SCHED_GETAFFINITY, %eax
	je	.Lfabric
	cmp	$RTX_NR_SCHED_YIELD, %eax
	je	.Lfabric
	cmp	$RTX_NR_GETRUSAGE, %eax
	je	.Lfabric
	cmp	$RTX_NR_PRLIMIT64, %eax
	je	.Lfabric
	cmp	$RTX_NR_GETRANDOM, %eax
	je	.Lfabric
	movb	$0, PER_CPU_VAR(rtx_fabric_hint)
	xor	%eax, %eax
	ret

.Lfabric:
	movb	$1, PER_CPU_VAR(rtx_fabric_hint)
	mov	PER_CPU_VAR(rtx_thermo_budget_micro), %eax
	cmp	$RTX_ENTROPY_FLOOR_MICRO, %eax
	jle	.Ldeny
	sub	$RTX_FABRIC_DEBIT_ASM_MICRO, %eax
	mov	%eax, PER_CPU_VAR(rtx_thermo_budget_micro)
	xor	%eax, %eax
	ret
.Ldeny:
	mov	$-EAGAIN, %eax
	ret
SYM_FUNC_END(rtx_syscall_preflight)