/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _KILROY_THERMO_IDLE_H
#define _KILROY_THERMO_IDLE_H

#ifdef CONFIG_RTX_FIELD_THERMO_IDLE_CREDIT
void kilroy_thermo_idle_init(void);
void kilroy_thermo_idle_exit(void);
#else
static inline void kilroy_thermo_idle_init(void) {}
static inline void kilroy_thermo_idle_exit(void) {}
#endif

#endif /* _KILROY_THERMO_IDLE_H */