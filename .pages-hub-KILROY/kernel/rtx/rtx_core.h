/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _RTX_CORE_H
#define _RTX_CORE_H

#include <linux/percpu.h>
#include <linux/types.h>
#include <uapi/kilroy/rtx_field.h>
#include "kilroy_units.h"

#define RTX_PHI_MICRO			KILROY_FIELD_PHI_MICRO
#define RTX_FABRIC_DEBIT_SUBMICRO	KILROY_FABRIC_DEBIT_SUBMICRO

struct rtx_global {
	struct kilroy_field_thermo thermo;
	struct kilroy_field_fcc fcc;
	u32 active;
	u64 syscall_total;
	u64 fabric_total;
	u64 host_passthrough;
};

#ifdef CONFIG_RTX_FIELD_DIE

DECLARE_PER_CPU(u32, rtx_thermo_budget_micro);
DECLARE_PER_CPU(u8, rtx_fabric_hint);

void rtx_core_init(void);
void rtx_core_exit(void);
void rtx_account_syscall(u32 nr, bool fabric);
int rtx_thermo_debit(void);
void rtx_thermo_credit(u32 micro);
void rtx_thermo_apply_userspace(const struct kilroy_field_thermo *t);
struct rtx_global *rtx_global_state(void);
bool rtx_is_fabric_syscall(u32 nr);

#else

static inline void rtx_core_init(void) {}
static inline void rtx_core_exit(void) {}
static inline void rtx_account_syscall(u32 nr, bool fabric) {}
static inline int rtx_thermo_debit(void) { return 0; }
static inline void rtx_thermo_credit(u32 micro) {}
static inline void rtx_thermo_apply_userspace(const struct kilroy_field_thermo *t) {}

#endif /* CONFIG_RTX_FIELD_DIE */

#endif /* _RTX_CORE_H */