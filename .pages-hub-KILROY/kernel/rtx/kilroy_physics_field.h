/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _KILROY_PHYSICS_FIELD_H
#define _KILROY_PHYSICS_FIELD_H

#include <linux/proc_fs.h>
#include <linux/types.h>

#ifdef CONFIG_RTX_FIELD_PHYSICS_BREAKTHROUGH

void kilroy_physics_field_init(void);
int kilroy_physics_proc_init(struct proc_dir_entry *parent);
void kilroy_physics_entropy_arrow(bool forward);
void kilroy_physics_reynolds_tick(u32 momentum_submicro);
u8 kilroy_physics_reynolds_regime(void);
u64 kilroy_physics_entropy_arrow_total(void);

#else

static inline void kilroy_physics_field_init(void) {}
static inline int kilroy_physics_proc_init(struct proc_dir_entry *p) { return 0; }
static inline void kilroy_physics_entropy_arrow(bool forward) { (void)forward; }
static inline void kilroy_physics_reynolds_tick(u32 m) { (void)m; }
static inline u8 kilroy_physics_reynolds_regime(void) { return 0; }
static inline u64 kilroy_physics_entropy_arrow_total(void) { return 0; }

#endif

#endif /* _KILROY_PHYSICS_FIELD_H */