/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _KILROY_COMFORT_FIELD_H
#define _KILROY_COMFORT_FIELD_H

#include <linux/proc_fs.h>

#ifdef CONFIG_RTX_FIELD_HOSTESS_COMFORT

void kilroy_comfort_field_init(void);
int kilroy_comfort_proc_init(struct proc_dir_entry *parent);

#else

static inline void kilroy_comfort_field_init(void) {}
static inline int kilroy_comfort_proc_init(struct proc_dir_entry *p) { return 0; }

#endif

#endif /* _KILROY_COMFORT_FIELD_H */