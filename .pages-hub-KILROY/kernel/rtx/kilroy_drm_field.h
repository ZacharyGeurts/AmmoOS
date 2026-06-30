/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _KILROY_DRM_FIELD_H
#define _KILROY_DRM_FIELD_H

#include <linux/types.h>
#include <uapi/kilroy/rtx_field.h>

#ifdef CONFIG_RTX_FIELD_DRM_FCC

void kilroy_drm_field_init(void);
void kilroy_drm_fcc_mirror(struct kilroy_field_fcc *fcc);
void kilroy_drm_field_fill(struct kilroy_field_gpu *out);

#else

static inline void kilroy_drm_field_init(void) {}
static inline void kilroy_drm_fcc_mirror(struct kilroy_field_fcc *fcc) {}
static inline void kilroy_drm_field_fill(struct kilroy_field_gpu *out) {}

#endif

#endif /* _KILROY_DRM_FIELD_H */