// SPDX-License-Identifier: GPL-2.0-only
/* KILROY Field OS — uname sysname identity (Linux-compatible release) */
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/string.h>
#include <linux/uts.h>
#include <linux/utsname.h>
#include <uapi/kilroy/rtx_field.h>

#ifdef CONFIG_RTX_FIELD_UTS_NAME

static int __init kilroy_uts_init(void)
{
	strscpy(init_uts_ns.name.sysname, KILROY_OS_NAME, __NEW_UTS_LEN);
	pr_info("KILROY: uname sysname=%s release=%s (Linux-compatible ABI)\n",
		init_uts_ns.name.sysname, init_uts_ns.name.release);
	return 0;
}
early_initcall(kilroy_uts_init);

#endif /* CONFIG_RTX_FIELD_UTS_NAME */