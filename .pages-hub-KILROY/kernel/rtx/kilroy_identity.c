// SPDX-License-Identifier: GPL-2.0-only
/* KILROY Field OS — exported identity strings */
#include <linux/export.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <uapi/kilroy/rtx_field.h>

const char kilroy_field_os_name[] = KILROY_OS_NAME;
const char kilroy_field_codename[] = KILROY_FIELD_CODENAME;
const char kilroy_field_abi[] = KILROY_FIELD_ABI;
const char kilroy_field_compat[] = KILROY_COMPAT_SUBSTRATE;

EXPORT_SYMBOL_GPL(kilroy_field_os_name);
EXPORT_SYMBOL_GPL(kilroy_field_codename);
EXPORT_SYMBOL_GPL(kilroy_field_abi);
EXPORT_SYMBOL_GPL(kilroy_field_compat);

static int __init kilroy_identity_init(void)
{
	pr_info("KILROY identity: %s (%s) abi=%s compat=%s layout=v%u\n",
		kilroy_field_os_name, kilroy_field_codename,
		kilroy_field_abi, kilroy_field_compat, KILROY_LAYOUT_VERSION);
	return 0;
}
late_initcall(kilroy_identity_init);