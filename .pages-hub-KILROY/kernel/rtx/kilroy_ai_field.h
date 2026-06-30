/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _KILROY_AI_FIELD_H
#define _KILROY_AI_FIELD_H

#include <linux/proc_fs.h>
#include <linux/types.h>

enum kilroy_ai_mode {
	KILROY_AI_MODE_HOME = 0,
	KILROY_AI_MODE_WAR = 1,
};

#ifdef CONFIG_RTX_FIELD_AI_KERNEL

void kilroy_ai_field_init(void);
int kilroy_ai_proc_init(struct proc_dir_entry *parent);

enum kilroy_ai_mode kilroy_ai_current_mode(void);
const char *kilroy_ai_mode_name(enum kilroy_ai_mode mode);

u32 kilroy_ai_nexus_alert_thresh(void);
u32 kilroy_ai_nexus_deny_thresh(void);
u32 kilroy_ai_nexus_eval_mask(void);
u32 kilroy_ai_thermo_idle_bonus_milli(void);
bool kilroy_ai_war_power_burst_bias(void);

#else

static inline void kilroy_ai_field_init(void) {}
static inline int kilroy_ai_proc_init(struct proc_dir_entry *parent) { return 0; }
static inline enum kilroy_ai_mode kilroy_ai_current_mode(void) { return KILROY_AI_MODE_HOME; }
static inline const char *kilroy_ai_mode_name(enum kilroy_ai_mode mode) { return "home"; }
static inline u32 kilroy_ai_nexus_alert_thresh(void) { return 45; }
static inline u32 kilroy_ai_nexus_deny_thresh(void) { return 72; }
static inline u32 kilroy_ai_nexus_eval_mask(void) { return 0x7f; }
static inline u32 kilroy_ai_thermo_idle_bonus_milli(void) { return 0; }
static inline bool kilroy_ai_war_power_burst_bias(void) { return false; }

#endif

#endif /* _KILROY_AI_FIELD_H */