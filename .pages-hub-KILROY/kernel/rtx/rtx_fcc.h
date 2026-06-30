/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _RTX_FCC_H
#define _RTX_FCC_H

#include <linux/types.h>
#include <uapi/kilroy/rtx_field.h>
#include "kilroy_units.h"

#define RTX_FCC_AGGRESSIVE_THRESH	KILROY_FCC_AGGRESSIVE_THRESH_MICRO

#ifdef CONFIG_RTX_FIELD_DIE

void rtx_fcc_harmonics_guard(struct kilroy_field_fcc *fcc);
void rtx_fcc_guard_kernel_global(void);

#ifdef CONFIG_RTX_FIELD_FCC_SYSCALL
void rtx_fcc_syscall_touch(void);
bool rtx_fcc_fabric_voltage_ok(void);
#else
static inline void rtx_fcc_syscall_touch(void) {}
static inline bool rtx_fcc_fabric_voltage_ok(void) { return true; }
#endif

#else

static inline void rtx_fcc_harmonics_guard(struct kilroy_field_fcc *fcc) {}
static inline void rtx_fcc_guard_kernel_global(void) {}
static inline void rtx_fcc_syscall_touch(void) {}

#endif /* CONFIG_RTX_FIELD_DIE */

#endif /* _RTX_FCC_H */