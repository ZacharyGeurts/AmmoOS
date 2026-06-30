/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _KILROY_BOOT_H
#define _KILROY_BOOT_H

#include <linux/types.h>

enum kilroy_grok_security {
	KILROY_GROK_SECURITY_UNKNOWN = 0,
	KILROY_GROK_SECURITY_STRICT,
	KILROY_GROK_SECURITY_WAIVED,
};

#ifdef CONFIG_RTX_FIELD_DIE

void kilroy_boot_init(void);
enum kilroy_grok_security kilroy_grok_security_mode(void);
bool kilroy_field_boot_flag(void);
const char *kilroy_grok_security_name(void);

#else

static inline void kilroy_boot_init(void) {}
static inline enum kilroy_grok_security kilroy_grok_security_mode(void)
{
	return KILROY_GROK_SECURITY_UNKNOWN;
}
static inline bool kilroy_field_boot_flag(void) { return false; }
static inline const char *kilroy_grok_security_name(void) { return "unknown"; }

#endif

#endif /* _KILROY_BOOT_H */