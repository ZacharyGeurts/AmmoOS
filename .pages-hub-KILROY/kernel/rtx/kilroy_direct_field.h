/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _KILROY_DIRECT_FIELD_H
#define _KILROY_DIRECT_FIELD_H

#include <linux/types.h>
#include <uapi/kilroy/rtx_field.h>

struct pt_regs;

#ifdef CONFIG_RTX_FIELD_DIRECT_SLOT

void kilroy_direct_field_init(void);
void kilroy_direct_field_tick(u32 nr);
void kilroy_direct_field_post_mmap(const struct pt_regs *regs, long ret);
void kilroy_direct_field_fill(struct kilroy_field_direct *out);

#else

static inline void kilroy_direct_field_init(void) {}
static inline void kilroy_direct_field_tick(u32 nr) {}
static inline void kilroy_direct_field_post_mmap(const struct pt_regs *regs, long ret) {}
static inline void kilroy_direct_field_fill(struct kilroy_field_direct *out) {}

#endif

#endif /* _KILROY_DIRECT_FIELD_H */