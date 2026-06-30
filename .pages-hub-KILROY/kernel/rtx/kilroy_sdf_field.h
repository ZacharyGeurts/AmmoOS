/* SPDX-License-Identifier: GPL-2.0 */
/* SDF brain imaging telemetry — zero-cost hot path (proc read only). */

#ifndef _KILROY_SDF_FIELD_H
#define _KILROY_SDF_FIELD_H

struct proc_dir_entry;

int kilroy_sdf_proc_init(struct proc_dir_entry *parent);

#endif