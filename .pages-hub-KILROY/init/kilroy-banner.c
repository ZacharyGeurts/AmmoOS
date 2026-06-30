// SPDX-License-Identifier: GPL-2.0-only
/* KILROY Field OS boot banner — Linux-compatible substrate */
#include <generated/compile.h>
#include <generated/utsrelease.h>
#include <linux/init.h>
#include <linux/utsname.h>

#ifdef CONFIG_RTX_FIELD_DIE
const char kilroy_field_banner[] __initconst =
	"KILROY Field OS " UTS_RELEASE " — codename Field, Linux-compatible\n";
#endif