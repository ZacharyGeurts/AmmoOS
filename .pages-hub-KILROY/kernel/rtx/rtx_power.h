/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _RTX_POWER_H
#define _RTX_POWER_H

#include <linux/types.h>
#include <uapi/kilroy/rtx_field.h>

#ifdef CONFIG_RTX_FIELD_POWER

int __init rtx_power_init(void);
void rtx_power_exit(void);
void rtx_power_set_force_tier(u8 tier);
u8 rtx_power_voltage_tier(void);
unsigned int rtx_power_last_max_khz(void);
bool rtx_power_is_auto(void);
void rtx_power_fill_abi(struct kilroy_field_power *out);
void rtx_power_kick(void);

#else

static inline int rtx_power_init(void) { return 0; }
static inline void rtx_power_exit(void) {}
static inline void rtx_power_set_force_tier(u8 tier) {}
static inline u8 rtx_power_voltage_tier(void) { return 0; }
static inline unsigned int rtx_power_last_max_khz(void) { return 0; }
static inline bool rtx_power_is_auto(void) { return true; }
static inline void rtx_power_fill_abi(struct kilroy_field_power *out) {}
static inline void rtx_power_kick(void) {}

#endif /* CONFIG_RTX_FIELD_POWER */

#endif /* _RTX_POWER_H */