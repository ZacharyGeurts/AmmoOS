/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _KILROY_CACHE_FIELD_H
#define _KILROY_CACHE_FIELD_H

#include <linux/types.h>
#include <uapi/kilroy/rtx_field.h>

#ifdef CONFIG_RTX_FIELD_CACHE_SLOT

void kilroy_cache_field_init(void);
void kilroy_cache_field_tick(u32 nr);
void kilroy_cache_field_fill(struct kilroy_field_cache *out);

#else

static inline void kilroy_cache_field_init(void) {}
static inline void kilroy_cache_field_tick(u32 nr) {}
static inline void kilroy_cache_field_fill(struct kilroy_field_cache *out) {}

#endif

#endif /* _KILROY_CACHE_FIELD_H */