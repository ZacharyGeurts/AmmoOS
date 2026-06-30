// SPDX-License-Identifier: GPL-2.0
// KILROY CPU field power tiers — micro/submicro thresholds.

#ifdef CONFIG_RTX_FIELD_POWER

#include <linux/cpufreq.h>
#include <linux/delay.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/minmax.h>
#include <linux/module.h>
#include <linux/percpu.h>
#include <linux/string.h>
#include <linux/jiffies.h>
#include <linux/workqueue.h>

#include "kilroy_ai_field.h"
#include "kilroy_drm_field.h"
#include "kilroy_flow.h"
#include "kilroy_units.h"
#include "rtx_core.h"
#include "rtx_fcc.h"
#include "rtx_hw_field.h"
#include "rtx_power.h"
#include "rtx_slots.h"

#define RTX_POWER_FALLBACK_MS	30000
#define RTX_POWER_KICK_COALESCE_MS 250

static struct delayed_work rtx_power_dwork;
static unsigned long rtx_power_last_kick_jiffies;
static u8 rtx_volt_tier;
static u8 rtx_force_tier;
static unsigned int rtx_last_applied_max;

static bool rtx_needs_full_voltage(void)
{
	struct rtx_four_slots *s = rtx_slots();
	u32 thermo = s->thermo.budget_micro;
	u32 entropy = s->thermo.acct.entropy_micro;
	u32 phi = s->thermo.acct.phi_micro;
	u64 activity = s->context.syscall_generation;
	u32 scale = s->thermo.fcc_guard_scale_micro;

	return phi >= KILROY_FIELD_PHI_MICRO &&
	       thermo > KILROY_MICRO_FROM_MILLI(200) &&
	       entropy < KILROY_MICRO_FROM_MILLI(350) &&
	       scale >= KILROY_FCC_AGGRESSIVE_THRESH_MICRO &&
	       kilroy_flow_momentum_submicro() > KILROY_MICRO_FROM_MILLI(50) * KILROY_SUBMICRO_PER_MICRO &&
	       (activity % 1000) > 80;
}

static u8 rtx_select_voltage_tier(void)
{
	struct rtx_four_slots *s = rtx_slots();
	u32 thermo = s->thermo.budget_micro;
	u32 scale = s->thermo.fcc_guard_scale_micro;
	u32 mem_pct;

	if (rtx_force_tier <= KILROY_VOLT_BURST)
		return rtx_force_tier;

	if (rtx_needs_full_voltage())
		return KILROY_VOLT_BURST;

	if (kilroy_ai_war_power_burst_bias() &&
	    kilroy_flow_momentum_submicro() >
	    KILROY_MICRO_FROM_MILLI(30) * KILROY_SUBMICRO_PER_MICRO)
		return KILROY_VOLT_BURST;

	if (scale < KILROY_MICRO_FROM_MILLI(850) || thermo < KILROY_MICRO_FROM_MILLI(60))
		return KILROY_VOLT_CRYO;

	/* pressure_submicro encodes permille (0–1000); convert to percent */
	mem_pct = kilroy_ram_pressure_submicro() / (10 * KILROY_SUBMICRO_PER_MICRO);

	if (scale < KILROY_MICRO_FROM_MILLI(950) || thermo < KILROY_MICRO_FROM_MILLI(120) ||
	    mem_pct > 85)
		return KILROY_VOLT_ECO;

	if (thermo < KILROY_MICRO_FROM_MILLI(200))
		return KILROY_VOLT_NOM;

	return KILROY_VOLT_NOM;
}

static unsigned int rtx_max_freq_for_tier(struct cpufreq_policy *policy, u8 tier)
{
	unsigned int min_f = policy->cpuinfo.min_freq;
	unsigned int max_f = policy->cpuinfo.max_freq;
	unsigned int span = max_f - min_f;

	switch (tier) {
	case KILROY_VOLT_CRYO:
		return min_f + span / 8;
	case KILROY_VOLT_ECO:
		return min_f + span / 2;
	case KILROY_VOLT_NOM:
		return min_f + (span * 3) / 4;
	case KILROY_VOLT_BURST:
	default:
		return max_f;
	}
}

static void rtx_apply_cpufreq_tier(u8 tier)
{
	unsigned int cpu;

	for_each_online_cpu(cpu) {
		struct cpufreq_policy *policy = cpufreq_cpu_get(cpu);
		unsigned int target;

		if (!policy)
			continue;

		target = rtx_max_freq_for_tier(policy, tier);
		target = clamp(target, policy->cpuinfo.min_freq, policy->cpuinfo.max_freq);

		if (policy->max != target) {
			down_write(&policy->rwsem);
			policy->max = target;
			cpufreq_update_policy(cpu);
			up_write(&policy->rwsem);
			rtx_last_applied_max = target;
		}
		cpufreq_cpu_put(policy);
	}
}

static void rtx_power_apply(void)
{
	bool burst;
	struct kilroy_field_fcc *fcc = &rtx_global_state()->fcc;

	rtx_fcc_guard_kernel_global();
	kilroy_drm_fcc_mirror(fcc);
	rtx_volt_tier = rtx_select_voltage_tier();
	rtx_apply_cpufreq_tier(rtx_volt_tier);
	burst = (rtx_volt_tier == KILROY_VOLT_BURST);
	kilroy_cpu_field_sync_power(rtx_volt_tier, rtx_last_applied_max, burst);
}

static void rtx_power_work_fn(struct work_struct *work)
{
	rtx_power_apply();
	schedule_delayed_work(&rtx_power_dwork, msecs_to_jiffies(RTX_POWER_FALLBACK_MS));
}

void rtx_power_kick(void)
{
	if (time_in_range(jiffies, rtx_power_last_kick_jiffies,
			  rtx_power_last_kick_jiffies +
			  msecs_to_jiffies(RTX_POWER_KICK_COALESCE_MS)))
		return;
	rtx_power_last_kick_jiffies = jiffies;
	cancel_delayed_work(&rtx_power_dwork);
	schedule_delayed_work(&rtx_power_dwork, 0);
}

void rtx_power_set_force_tier(u8 tier)
{
	if (tier > KILROY_VOLT_BURST)
		rtx_force_tier = 255;
	else
		rtx_force_tier = tier;
}

u8 rtx_power_voltage_tier(void)
{
	return rtx_volt_tier;
}

unsigned int rtx_power_last_max_khz(void)
{
	return rtx_last_applied_max;
}

bool rtx_power_is_auto(void)
{
	return rtx_force_tier > KILROY_VOLT_BURST;
}

void rtx_power_fill_abi(struct kilroy_field_power *out)
{
	struct rtx_four_slots *s;

	if (!out)
		return;

	memset(out, 0, sizeof(*out));
	out->tier = rtx_volt_tier;
	out->auto_mode = rtx_power_is_auto() ? 1 : 0;
	out->max_khz = rtx_last_applied_max;
	s = rtx_slots();
	if (s)
		out->fcc_guard_scale_micro = s->thermo.fcc_guard_scale_micro;
	out->ram_pressure_submicro = kilroy_ram_pressure_submicro();
	{
		struct kilroy_field_cpu cpu;

		kilroy_cpu_field_fill(&cpu);
		out->cpu_burst_ready = cpu.burst_ready;
	}
}

int __init rtx_power_init(void)
{
	INIT_DELAYED_WORK(&rtx_power_dwork, rtx_power_work_fn);
	rtx_force_tier = 255;
	schedule_delayed_work(&rtx_power_dwork, msecs_to_jiffies(500));
	pr_info("kilroy_field: %s CPU field power — micro/submicro DVFS\n",
		KILROY_FIELD_CODENAME);
	return 0;
}

void rtx_power_exit(void)
{
	cancel_delayed_work_sync(&rtx_power_dwork);
}

#endif /* CONFIG_RTX_FIELD_POWER */