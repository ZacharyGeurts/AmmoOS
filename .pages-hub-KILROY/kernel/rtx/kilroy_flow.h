/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _KILROY_FLOW_H
#define _KILROY_FLOW_H

#include <linux/types.h>

#ifdef CONFIG_RTX_FIELD_FLOW_SLOT

void kilroy_flow_init(void);
void kilroy_flow_tick(u32 nr, bool fabric, long ret);
u32 kilroy_flow_momentum_submicro(void);
u32 kilroy_flow_tesla_bias_micro(void);

#else

static inline void kilroy_flow_init(void) {}
static inline void kilroy_flow_tick(u32 nr, bool fabric, long ret) {}
static inline u32 kilroy_flow_momentum_submicro(void) { return 0; }
static inline u32 kilroy_flow_tesla_bias_micro(void) { return 0; }

#endif

#endif /* _KILROY_FLOW_H */