// SPDX-License-Identifier: GPL-2.0
// NEXUS-inspired in-kernel guard — heightened security awareness, consumer-safe.
// Amortized scoring; event-driven on suspicious syscall NR; no peripheral breaks.

#include <linux/errno.h>
#include <linux/kernel.h>
#include <linux/minmax.h>
#include <linux/pid.h>
#include <linux/sched.h>

#include "kilroy_ai_field.h"
#include "kilroy_nexus_guard.h"
#include "rtx_slots.h"

#define KILROY_NEXUS_EVAL_MASK_DEFAULT	0x7f
#define KILROY_NEXUS_ALERT_DEFAULT	45
#define KILROY_NEXUS_DENY_DEFAULT	72

static u32 kilroy_nexus_eval_mask(void)
{
#ifdef CONFIG_RTX_FIELD_AI_KERNEL
	return kilroy_ai_nexus_eval_mask();
#else
	return KILROY_NEXUS_EVAL_MASK_DEFAULT;
#endif
}

static u32 kilroy_nexus_alert_thresh(void)
{
#ifdef CONFIG_RTX_FIELD_AI_KERNEL
	return kilroy_ai_nexus_alert_thresh();
#else
	return KILROY_NEXUS_ALERT_DEFAULT;
#endif
}

static u32 kilroy_nexus_deny_thresh(void)
{
#ifdef CONFIG_RTX_FIELD_AI_KERNEL
	return kilroy_ai_nexus_deny_thresh();
#else
	return KILROY_NEXUS_DENY_DEFAULT;
#endif
}

struct kilroy_nexus_state {
	u32 behavior_score;
	u32 predictive_score;
	u32 alert_count;
	u32 whitelisted_ticks;
	u64 last_suspicious_nr;
	u64 last_pid;
};

static struct kilroy_nexus_state nexus_guard;

static bool kilroy_nexus_whitelisted_nr(u32 nr)
{
	switch (nr) {
	case 0 ... 2:   /* read/write/open */
	case 3: case 8: case 9: case 10: case 11: case 12:
	case 16: case 21: case 22: case 23: case 24: case 25:
	case 32: case 39: case 41: case 42: case 43: case 44:
	case 45: case 46: case 47: /* epoll/poll/select/futex */
	case 202: case 203: case 204: case 228: case 230: case 231:
		return true;
	default:
		return false;
	}
}

static u32 kilroy_nexus_suspicious_score(u32 nr)
{
	switch (nr) {
	case 101: /* ptrace */
	case 310: /* process_vm_readv */
	case 311: /* process_vm_writev */
	case 250: /* keyctl */
	case 175: /* init_module */
	case 313: /* finit_module */
	case 321: /* bpf */
	case 298: /* perf_event_open */
	case 319: /* memfd_create */
	case 157: /* prctl */
	case 174: /* sysacct */
	case 272: /* unshare */
	case 165: /* mount */
	case 155: /* pivot_root */
		return 25;
	case 59:  /* execve */
	case 56:  /* clone */
	case 41:  /* socket */
		return 8;
	default:
		return 0;
	}
}

void kilroy_nexus_guard_init(void)
{
	memset(&nexus_guard, 0, sizeof(nexus_guard));
	pr_info("kilroy_field: NEXUS guard active (amortized, consumer-whitelist)\n");
}

void kilroy_nexus_guard_tick(u32 nr)
{
	u32 add;
	struct rtx_four_slots *s = rtx_slots();

	if (kilroy_nexus_whitelisted_nr(nr)) {
		nexus_guard.whitelisted_ticks++;
		if (nexus_guard.behavior_score > 0)
			nexus_guard.behavior_score--;
		return;
	}

	add = kilroy_nexus_suspicious_score(nr);
	if (add) {
		nexus_guard.behavior_score = min_t(u32, 100, nexus_guard.behavior_score + add);
		nexus_guard.last_suspicious_nr = nr;
		nexus_guard.last_pid = task_pid_nr(current);
	}

	if (s && s->context.syscall_generation) {
		u64 gen = s->context.syscall_generation;

		if ((gen & kilroy_nexus_eval_mask()) == 0)
			nexus_guard.predictive_score = min_t(u32, 100,
				nexus_guard.predictive_score + (add / 4));
	}
}

int kilroy_nexus_guard_evaluate(void)
{
	struct rtx_four_slots *s = rtx_slots();
	u64 gen = s ? s->context.syscall_generation : 0;

	if ((gen & kilroy_nexus_eval_mask()) != 0)
		return 0;

	if (nexus_guard.behavior_score >= kilroy_nexus_alert_thresh()) {
		nexus_guard.alert_count++;
		nexus_guard.predictive_score = min_t(u32, 100,
			nexus_guard.predictive_score + 10);
		pr_alert_ratelimited(
			"kilroy_field: NEXUS_BEHAVIOR_ALERT score=%u nr=%llu pid=%llu\n",
			nexus_guard.behavior_score,
			nexus_guard.last_suspicious_nr,
			nexus_guard.last_pid);
	}

	if (nexus_guard.predictive_score >= kilroy_nexus_deny_thresh()) {
		pr_alert("kilroy_field: NEXUS_PREDICTIVE_DENY score=%u behavior=%u\n",
			 nexus_guard.predictive_score, nexus_guard.behavior_score);
		return -EPERM;
	}

	if (nexus_guard.behavior_score >= 2)
		nexus_guard.behavior_score -= 2;
	else if (nexus_guard.behavior_score)
		nexus_guard.behavior_score = 0;

	if (nexus_guard.predictive_score)
		nexus_guard.predictive_score--;

	return 0;
}

u32 kilroy_nexus_behavior_score(void) { return nexus_guard.behavior_score; }
u32 kilroy_nexus_predictive_score(void) { return nexus_guard.predictive_score; }
u32 kilroy_nexus_alert_count(void) { return nexus_guard.alert_count; }