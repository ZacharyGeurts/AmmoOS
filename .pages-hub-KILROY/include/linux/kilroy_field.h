/* SPDX-License-Identifier: GPL-2.0 */
/*
 * KILROY Field OS — kernel identity exports.
 * Userspace ABI lives in <uapi/kilroy/rtx_field.h>.
 */
#ifndef _LINUX_KILROY_FIELD_H
#define _LINUX_KILROY_FIELD_H

#include <uapi/kilroy/rtx_field.h>

#ifdef CONFIG_RTX_FIELD_DIE
extern const char kilroy_field_os_name[];
extern const char kilroy_field_codename[];
extern const char kilroy_field_abi[];
extern const char kilroy_field_compat[];
#endif /* CONFIG_RTX_FIELD_DIE */

#endif /* _LINUX_KILROY_FIELD_H */