// SPDX-License-Identifier: GPL-2.0
// KILROY FCC harmonics guard — micro/submicro units.

#include <linux/kernel.h>
#include <linux/minmax.h>
#include <linux/percpu.h>

#include "kilroy_units.h"
#include "rtx_core.h"
#include "rtx_fcc.h"
#include "rtx_power.h"
#include "rtx_slots.h"

#define RTX_FCC_WAVE_MAX_MICRO		KILROY_MICRO_FROM_MILLI(2000)
#define RTX_FCC_THERMO_MAX_MICRO	KILROY_MICRO_FROM_MILLI(3500)
#define RTX_FCC_INJECT_MAX_MICRO	KILROY_MICRO_FROM_MILLI(8000)
#define RTX_FCC_COUPLING_MAX_MICRO	KILROY_MICRO_FROM_MILLI(2000)
#define RTX_FCC_TIME_MAX_MICRO		KILROY_MICRO_FROM_MILLI(4000)
#define RTX_FCC_CLAMP_THRESH_MICRO	KILROY_MICRO_FROM_MILLI(980)

static u32 rtx_fcc_compute_scale(const struct kilroy_field_fcc *fcc)
{
	u32 scale = KILROY_FCC_SCALE_MAX_MICRO;

	if (!fcc)
		return scale;

	if (fcc->wave_speed_micro > RTX_FCC_WAVE_MAX_MICRO)
		scale = min(scale, (RTX_FCC_WAVE_MAX_MICRO * KILROY_SCALE_MICRO) /
					      fcc->wave_speed_micro);
	if (fcc->thermo_alpha_micro > RTX_FCC_THERMO_MAX_MICRO)
		scale = min(scale, (RTX_FCC_THERMO_MAX_MICRO * KILROY_SCALE_MICRO) /
					      fcc->thermo_alpha_micro);
	if (fcc->inject_strength_micro > RTX_FCC_INJECT_MAX_MICRO)
		scale = min(scale, (RTX_FCC_INJECT_MAX_MICRO * KILROY_SCALE_MICRO) /
					      fcc->inject_strength_micro);
	if (fcc->field_coupling_micro > RTX_FCC_COUPLING_MAX_MICRO)
		scale = min(scale, (RTX_FCC_COUPLING_MAX_MICRO * KILROY_SCALE_MICRO) /
					      fcc->field_coupling_micro);
	if (fcc->time_scale_micro > RTX_FCC_TIME_MAX_MICRO)
		scale = min(scale, (RTX_FCC_TIME_MAX_MICRO * KILROY_SCALE_MICRO) /
					      fcc->time_scale_micro);

	{
		struct rtx_four_slots *s = rtx_slots();
		u32 ent = s->thermo.acct.entropy_micro;

		if (ent > KILROY_MICRO_FROM_MILLI(400))
			scale = min(scale, KILROY_MICRO_FROM_MILLI(850));
		if (ent > KILROY_MICRO_FROM_MILLI(800))
			scale = min(scale, KILROY_MICRO_FROM_MILLI(700));
	}

	return scale;
}

void rtx_fcc_harmonics_guard(struct kilroy_field_fcc *fcc)
{
	u32 scale;

	if (!fcc)
		return;

	scale = rtx_fcc_compute_scale(fcc);

	if (scale < RTX_FCC_CLAMP_THRESH_MICRO) {
		fcc->wave_speed_micro = (u64)fcc->wave_speed_micro * scale / KILROY_SCALE_MICRO;
		fcc->thermo_alpha_micro = (u64)fcc->thermo_alpha_micro * scale / KILROY_SCALE_MICRO;
		fcc->inject_strength_micro = (u64)fcc->inject_strength_micro * scale / KILROY_SCALE_MICRO;
		fcc->field_coupling_micro = (u64)fcc->field_coupling_micro * scale / KILROY_SCALE_MICRO;
		fcc->time_scale_micro = (u64)fcc->time_scale_micro * scale / KILROY_SCALE_MICRO;
		fcc->propalactic_micro = (u64)fcc->propalactic_micro * scale / KILROY_SCALE_MICRO;
	}

	rtx_slots()->thermo.fcc_guard_scale_micro = scale;
}

void rtx_fcc_guard_kernel_global(void)
{
	struct rtx_global *g = rtx_global_state();
	struct rtx_four_slots *s = rtx_slots();
	u32 scale;
	u32 floor_micro = KILROY_ENTROPY_FLOOR_SUBMICRO / KILROY_SUBMICRO_PER_MICRO;

	rtx_fcc_harmonics_guard(&g->fcc);
	scale = s->thermo.fcc_guard_scale_micro;

	if (scale < RTX_FCC_AGGRESSIVE_THRESH) {
		u32 *budget = this_cpu_ptr(&rtx_thermo_budget_micro);
		u32 gap = KILROY_FCC_SCALE_MAX_MICRO - scale;
		u32 floor = floor_micro + gap / (4 * KILROY_MICRO_PER_MILLI);

		if (*budget > floor + KILROY_MICRO_FROM_MILLI(20))
			*budget = max(floor + KILROY_MICRO_FROM_MILLI(20),
				      *budget - gap / (8 * KILROY_MICRO_PER_MILLI));
		s->thermo.budget_micro = *budget;
	}
}

#ifdef CONFIG_RTX_FIELD_FCC_SYSCALL
void rtx_fcc_syscall_touch(void)
{
	struct rtx_four_slots *s = rtx_slots();
	u32 gen = (u32)s->context.syscall_generation;
	u32 floor_micro = KILROY_ENTROPY_FLOOR_SUBMICRO / KILROY_SUBMICRO_PER_MICRO;

	if ((gen & (CONFIG_RTX_FIELD_FCC_TOUCH_MASK)) == 0) {
		rtx_fcc_guard_kernel_global();
		return;
	}

	if (s->thermo.fcc_guard_scale_micro < RTX_FCC_AGGRESSIVE_THRESH) {
		u32 *budget = this_cpu_ptr(&rtx_thermo_budget_micro);
		u32 gap = RTX_FCC_AGGRESSIVE_THRESH - s->thermo.fcc_guard_scale_micro;

		if (*budget > floor_micro + gap / (2 * KILROY_MICRO_PER_MILLI))
			*budget -= max(KILROY_MICRO_FROM_MILLI(1),
				       gap / (32 * KILROY_MICRO_PER_MILLI));
		s->thermo.budget_micro = *budget;
	}
}

bool rtx_fcc_fabric_voltage_ok(void)
{
	struct rtx_four_slots *s = rtx_slots();

	if (s->thermo.fcc_guard_scale_micro < KILROY_MICRO_FROM_MILLI(850))
		return false;
#ifdef CONFIG_RTX_FIELD_POWER
	if (rtx_power_voltage_tier() == KILROY_VOLT_CRYO &&
	    s->thermo.budget_micro < KILROY_MICRO_FROM_MILLI(120))
		return false;
#endif
	return true;
}
#endif /* CONFIG_RTX_FIELD_FCC_SYSCALL */