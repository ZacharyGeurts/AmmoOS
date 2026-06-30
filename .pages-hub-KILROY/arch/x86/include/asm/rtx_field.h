/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _ASM_RTX_FIELD_H
#define _ASM_RTX_FIELD_H

#define RTX_NR_SCHED_GETAFFINITY	123
#define RTX_NR_SCHED_YIELD		124
#define RTX_NR_GETRUSAGE		165
#define RTX_NR_PRLIMIT64		261
#define RTX_NR_GETRANDOM		278

#define RTX_NR_MMAP			222
#define RTX_NR_MUNMAP			215
#define RTX_NR_BRK			214
#define RTX_NR_MPROTECT			226

/* ASM hot path — submicro-precision debit (100µ per fabric syscall) */
#define RTX_ENTROPY_FLOOR_MICRO		2000
#define RTX_FABRIC_DEBIT_ASM_MICRO	100
#define RTX_FABRIC_DEBIT_MICRO		RTX_FABRIC_DEBIT_ASM_MICRO

#ifndef __ASSEMBLY__

#include <linux/types.h>

#ifdef CONFIG_RTX_FIELD_DIE

bool rtx_is_fabric_syscall(u32 nr);
int rtx_thermo_debit(void);
void rtx_account_syscall(u32 nr, bool fabric);
long rtx_syscall_preflight(unsigned int nr);

#else

static inline bool rtx_is_fabric_syscall(u32 nr) { return false; }
static inline int rtx_thermo_debit(void) { return 0; }
static inline void rtx_account_syscall(u32 nr, bool fabric) {}
static inline long rtx_syscall_preflight(unsigned int nr) { return 0; }

#endif /* CONFIG_RTX_FIELD_DIE */

#endif /* __ASSEMBLY__ */

#endif /* _ASM_RTX_FIELD_H */