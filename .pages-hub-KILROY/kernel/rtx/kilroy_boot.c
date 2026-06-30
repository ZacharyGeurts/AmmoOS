// SPDX-License-Identifier: GPL-2.0-only
/* Grok bootloader handoff — parse grok.security= / kilroy.field= cmdline */
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/string.h>

#include "kilroy_boot.h"

static enum kilroy_grok_security grok_security = KILROY_GROK_SECURITY_UNKNOWN;
static bool field_boot;

static int __init kilroy_parse_grok_security(char *str)
{
	if (!str || !*str)
		return 0;
	if (!strcmp(str, "strict"))
		grok_security = KILROY_GROK_SECURITY_STRICT;
	else if (!strcmp(str, "waived"))
		grok_security = KILROY_GROK_SECURITY_WAIVED;
	else
		pr_warn("kilroy_field: unknown grok.security=%s (use strict|waived)\n", str);
	return 0;
}
__setup("grok.security=", kilroy_parse_grok_security);

static int __init kilroy_parse_field_boot(char *str)
{
	field_boot = true;
	return 0;
}
__setup("kilroy.field=", kilroy_parse_field_boot);

enum kilroy_grok_security kilroy_grok_security_mode(void)
{
	return grok_security;
}
EXPORT_SYMBOL_GPL(kilroy_grok_security_mode);

bool kilroy_field_boot_flag(void)
{
	return field_boot;
}
EXPORT_SYMBOL_GPL(kilroy_field_boot_flag);

const char *kilroy_grok_security_name(void)
{
	switch (grok_security) {
	case KILROY_GROK_SECURITY_STRICT:
		return "strict";
	case KILROY_GROK_SECURITY_WAIVED:
		return "waived";
	default:
		return "unknown";
	}
}
EXPORT_SYMBOL_GPL(kilroy_grok_security_name);

void kilroy_boot_init(void)
{
	if (grok_security == KILROY_GROK_SECURITY_WAIVED)
		pr_alert("KILROY: Grok security WAIVED — fix BIOS (see /proc/kilroy_field/boot)\n");
	else if (grok_security == KILROY_GROK_SECURITY_STRICT)
		pr_info("KILROY: Grok strict security handoff\n");
	if (field_boot)
		pr_info("KILROY: Field Die boot flag set (Grok chain)\n");
}