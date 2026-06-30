/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _KILROY_UNITS_H
#define _KILROY_UNITS_H

#include <linux/types.h>
#include <uapi/kilroy/rtx_field.h>

/* KILROY fixed-point: micro = 1e-6 unity, submicro = 1e-9 unity */
#define KILROY_SCALE_MICRO		1000000u
#define KILROY_SCALE_SUBMICRO		1000000000u
#define KILROY_MICRO_PER_MILLI		1000u
#define KILROY_SUBMICRO_PER_MICRO	1000u

#define KILROY_MICRO_FROM_MILLI(m)	((u32)(m) * KILROY_MICRO_PER_MILLI)
#define KILROY_SUBMICRO_FROM_MILLI(m)	((u32)(m) * KILROY_MICRO_PER_MILLI * KILROY_SUBMICRO_PER_MICRO)
#define KILROY_MICRO_TO_SUBMICRO(u)	((u) * KILROY_SUBMICRO_PER_MICRO)

/* Kernel-internal defaults (micro/submicro) — PHI/FCC scale from UAPI */
#define KILROY_THERMO_INIT_MICRO	KILROY_MICRO_FROM_MILLI(310)
#define KILROY_THERMO_CREDIT_CAP_MICRO	KILROY_MICRO_FROM_MILLI(1500)

/* Submicro precision (floors, debits, rates) */
#define KILROY_ENTROPY_FLOOR_SUBMICRO	KILROY_SUBMICRO_FROM_MILLI(2)
#define KILROY_FABRIC_DEBIT_SUBMICRO	KILROY_SUBMICRO_FROM_MILLI(1)

/* Legacy milli names — same numeric literals, compat headers only */
#define KILROY_FIELD_PHI_MILLI		618
#define KILROY_FCC_AGGRESSIVE_THRESH_MILLI 920
#define KILROY_FCC_SCALE_MAX_MILLI	1000
#define RTX_THERMO_INIT_MILLI		310
#define RTX_ENTROPY_FLOOR_MILLI		2
#define RTX_FABRIC_DEBIT_MILLI		1
#define RTX_PHI_MILLI			KILROY_FIELD_PHI_MILLI

/* Proc/userspace write: values < 10000 treated as legacy milli */
static inline u32 kilroy_norm_micro(u32 v)
{
	if (v < 10000u)
		return KILROY_MICRO_FROM_MILLI(v);
	return v;
}

static inline u32 kilroy_norm_submicro(u32 v)
{
	/* Legacy milli (2, 14, …) only; native submicro passes through */
	if (v < 10000u)
		return KILROY_SUBMICRO_FROM_MILLI(v);
	return v;
}

static inline u32 kilroy_micro_to_legacy_milli(u32 micro)
{
	return micro / KILROY_MICRO_PER_MILLI;
}

#endif /* _KILROY_UNITS_H */