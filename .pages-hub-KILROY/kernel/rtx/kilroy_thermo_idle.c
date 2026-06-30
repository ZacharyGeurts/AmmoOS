// SPDX-License-Identifier: GPL-2.0
// KILROY thermo idle credit — recover budget from idle CPUs (reduces EAGAIN).

#include <linux/cpu.h>
#include <linux/kernel.h>
#include <linux/minmax.h>
#include <linux/percpu.h>
#include <linux/workqueue.h>

#include "kilroy_ai_field.h"
#include "kilroy_thermo_idle.h"
#include "kilroy_units.h"
#include "rtx_core.h"
#include "rtx_slots.h"

#ifdef CONFIG_RTX_FIELD_THERMO_IDLE_CREDIT

#define KILROY_IDLE_INTERVAL_MS	1000
#define KILROY_IDLE_CREDIT_MICRO	KILROY_MICRO_FROM_MILLI(5)

static struct delayed_work kilroy_idle_dwork;

static void kilroy_idle_credit_fn(struct work_struct *work)
{
	unsigned int cpu;
	u32 credited = 0;

	for_each_online_cpu(cpu) {
		u32 *budget = per_cpu_ptr(&rtx_thermo_budget_micro, cpu);

		if (*budget < KILROY_THERMO_CREDIT_CAP_MICRO) {
			u32 add = KILROY_IDLE_CREDIT_MICRO +
				KILROY_MICRO_FROM_MILLI(kilroy_ai_thermo_idle_bonus_milli());

			*budget = min_t(u32, *budget + add, KILROY_THERMO_CREDIT_CAP_MICRO);
			credited += add;
		}
	}
	if (credited) {
		struct rtx_four_slots *s = rtx_slots();

		s->thermo.budget_micro = max_t(u32, s->thermo.budget_micro,
					       KILROY_THERMO_INIT_MICRO);
	}
	schedule_delayed_work(&kilroy_idle_dwork,
			      msecs_to_jiffies(KILROY_IDLE_INTERVAL_MS));
}

void kilroy_thermo_idle_init(void)
{
	INIT_DELAYED_WORK(&kilroy_idle_dwork, kilroy_idle_credit_fn);
	schedule_delayed_work(&kilroy_idle_dwork,
			      msecs_to_jiffies(KILROY_IDLE_INTERVAL_MS));
}

void kilroy_thermo_idle_exit(void)
{
	cancel_delayed_work_sync(&kilroy_idle_dwork);
}

#endif /* CONFIG_RTX_FIELD_THERMO_IDLE_CREDIT */