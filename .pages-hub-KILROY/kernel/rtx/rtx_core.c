// SPDX-License-Identifier: GPL-2.0
// KILROY Field OS — native Field Die core (Linux-compatible substrate).

#include <linux/errno.h>
#include <linux/export.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/minmax.h>
#include <linux/percpu.h>
#include <linux/string.h>

#include "kilroy_ai_field.h"
#include "kilroy_comfort_field.h"
#include "kilroy_physics_field.h"
#include "kilroy_cache_field.h"
#include "kilroy_direct_field.h"
#include "kilroy_drm_field.h"
#include "kilroy_flow.h"
#include "kilroy_nexus_guard.h"
#include "kilroy_thermo_idle.h"
#include "rtx_core.h"
#include "rtx_hw_field.h"
#include "rtx_slots.h"

static struct rtx_global rtx_state;

DEFINE_PER_CPU(u32, rtx_thermo_budget_micro) = KILROY_THERMO_INIT_MICRO;
DEFINE_PER_CPU(u8, rtx_fabric_hint);
EXPORT_PER_CPU_SYMBOL(rtx_fabric_hint);
EXPORT_PER_CPU_SYMBOL(rtx_thermo_budget_micro);

static void rtx_seed_defaults(void)
{
	memset(&rtx_state, 0, sizeof(rtx_state));
	rtx_state.active = 1;
	rtx_state.thermo.boundary_thermo_micro = KILROY_THERMO_INIT_MICRO;
	rtx_state.thermo.entropy_floor_submicro = KILROY_ENTROPY_FLOOR_SUBMICRO;
	rtx_state.thermo.phi_micro = KILROY_FIELD_PHI_MICRO;
	rtx_state.fcc.time_scale_micro = KILROY_SCALE_MICRO;
	rtx_state.fcc.thermo_alpha_micro = KILROY_MICRO_FROM_MILLI(860);
	rtx_state.fcc.wave_speed_micro = KILROY_MICRO_FROM_MILLI(710);
	rtx_state.fcc.gate_fidelity_micro = KILROY_FIELD_PHI_MICRO;
	rtx_state.fcc.entropy_floor_submicro = KILROY_SUBMICRO_FROM_MILLI(14);
	rtx_state.fcc.inject_strength_micro = KILROY_MICRO_FROM_MILLI(2800);
	rtx_state.fcc.propalactic_micro = KILROY_MICRO_FROM_MILLI(230);
	rtx_state.fcc.field_coupling_micro = KILROY_MICRO_FROM_MILLI(770);
	rtx_state.fcc.tesla_bias_micro = KILROY_SCALE_MICRO;
}

struct rtx_global *rtx_global_state(void)
{
	return &rtx_state;
}

void rtx_account_syscall(u32 nr, bool fabric)
{
	rtx_state.syscall_total++;
	if (fabric)
		rtx_state.fabric_total++;
	else
		rtx_state.host_passthrough++;
	kilroy_cpu_field_tick(nr, fabric);
}

int rtx_thermo_debit(void)
{
	u32 *budget = this_cpu_ptr(&rtx_thermo_budget_micro);
	u32 floor_micro = KILROY_ENTROPY_FLOOR_SUBMICRO / KILROY_SUBMICRO_PER_MICRO;

	if (*budget <= floor_micro)
		return -EAGAIN;
	*budget -= KILROY_FABRIC_DEBIT_SUBMICRO / KILROY_SUBMICRO_PER_MICRO;
	if (*budget < floor_micro)
		*budget = KILROY_THERMO_INIT_MICRO;
	return 0;
}

void rtx_thermo_credit(u32 micro)
{
	u32 *budget = this_cpu_ptr(&rtx_thermo_budget_micro);

	*budget = min_t(u32, *budget + micro, KILROY_THERMO_CREDIT_CAP_MICRO);
}

void rtx_thermo_apply_userspace(const struct kilroy_field_thermo *t)
{
	u32 *budget;
	struct rtx_four_slots *slots = rtx_slots();

	if (!t)
		return;
	rtx_state.thermo = *t;
	slots->thermo.acct = *t;
	budget = this_cpu_ptr(&rtx_thermo_budget_micro);
	if (t->boundary_thermo_micro) {
		*budget = t->boundary_thermo_micro;
		slots->thermo.budget_micro = t->boundary_thermo_micro;
	}
}

void rtx_core_init(void)
{
	rtx_seed_defaults();
	rtx_slots_init();
	rtx_slots_seal_time();
	kilroy_hw_fields_init();
	kilroy_flow_init();
	kilroy_cache_field_init();
	kilroy_direct_field_init();
	kilroy_drm_field_init();
	kilroy_nexus_guard_init();
	kilroy_ai_field_init();
	kilroy_physics_field_init();
	kilroy_comfort_field_init();
	kilroy_thermo_idle_init();
	pr_info("kilroy_field: %s Field OS %s — codename=%s compat=%s abi=%s layout=v%u\n",
		KILROY_OS_NAME, KILROY_VERSION_STRING, KILROY_FIELD_CODENAME,
		KILROY_COMPAT_SUBSTRATE, KILROY_FIELD_ABI, KILROY_LAYOUT_VERSION);
}

void rtx_core_exit(void)
{
	kilroy_thermo_idle_exit();
	pr_info("kilroy_field: %s Field OS unloaded\n", KILROY_OS_NAME);
}