/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _KILROY_NEXUS_GUARD_H
#define _KILROY_NEXUS_GUARD_H

#include <linux/types.h>

#ifdef CONFIG_RTX_FIELD_NEXUS_GUARD

void kilroy_nexus_guard_init(void);
void kilroy_nexus_guard_tick(u32 nr);
int kilroy_nexus_guard_evaluate(void);
u32 kilroy_nexus_behavior_score(void);
u32 kilroy_nexus_predictive_score(void);
u32 kilroy_nexus_alert_count(void);

#else

static inline void kilroy_nexus_guard_init(void) {}
static inline void kilroy_nexus_guard_tick(u32 nr) {}
static inline int kilroy_nexus_guard_evaluate(void) { return 0; }
static inline u32 kilroy_nexus_behavior_score(void) { return 0; }
static inline u32 kilroy_nexus_predictive_score(void) { return 0; }
static inline u32 kilroy_nexus_alert_count(void) { return 0; }

#endif

#endif /* _KILROY_NEXUS_GUARD_H */