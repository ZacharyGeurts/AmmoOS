/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _RTX_HW_FIELD_H
#define _RTX_HW_FIELD_H

#include <linux/types.h>
#include <uapi/kilroy/rtx_field.h>

#ifdef CONFIG_RTX_FIELD_DIE

DECLARE_PER_CPU(u8, rtx_ram_field_hint);

void kilroy_hw_fields_init(void);
void kilroy_cpu_field_tick(u32 nr, bool fabric);
void kilroy_ram_field_pre_touch(u32 nr);
void kilroy_ram_field_post_touch(u32 nr, long ret, const struct pt_regs *regs);
void kilroy_cpu_field_sync_power(u8 tier, unsigned int max_khz, bool burst_ready);
void kilroy_ram_field_fill(struct kilroy_field_ram *out);
void kilroy_cpu_field_fill(struct kilroy_field_cpu *out);
u32 kilroy_ram_pressure_submicro(void);

#else

static inline void kilroy_hw_fields_init(void) {}
static inline void kilroy_cpu_field_tick(u32 nr, bool fabric) {}
static inline void kilroy_ram_field_pre_touch(u32 nr) {}
static inline void kilroy_ram_field_post_touch(u32 nr, long ret,
					       const struct pt_regs *regs) {}
static inline void kilroy_cpu_field_sync_power(u8 tier, unsigned int max_khz,
					       bool burst_ready) {}
static inline void kilroy_ram_field_fill(struct kilroy_field_ram *out) {}
static inline void kilroy_cpu_field_fill(struct kilroy_field_cpu *out) {}
static inline u32 kilroy_ram_pressure_submicro(void) { return 0; }

#endif

#endif /* _RTX_HW_FIELD_H */