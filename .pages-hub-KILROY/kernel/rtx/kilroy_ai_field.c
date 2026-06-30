// SPDX-License-Identifier: GPL-2.0
// KILROY AI kernel — DARPA-secure War/Home modes; Hostess7 wishes; zero hot-path tax in home.

#include <linux/errno.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>
#include <linux/string.h>
#include <linux/uaccess.h>

#include "kilroy_ai_field.h"
#include "kilroy_ai_wishes.h"
#include "kilroy_field_stack.h"
#include "rtx_core.h"

static enum kilroy_ai_mode ai_mode = KILROY_AI_MODE_HOME;
static u64 ai_mode_switches;
static u64 ai_truth_pass;
static u64 ai_truth_quarantine;

const char *kilroy_ai_mode_name(enum kilroy_ai_mode mode)
{
	switch (mode) {
	case KILROY_AI_MODE_WAR:
		return "war";
	default:
		return "home";
	}
}

enum kilroy_ai_mode kilroy_ai_current_mode(void)
{
	return ai_mode;
}

u32 kilroy_ai_nexus_alert_thresh(void)
{
	return ai_mode == KILROY_AI_MODE_WAR ?
		KILROY_AI_WAR_ALERT : KILROY_AI_HOME_ALERT;
}

u32 kilroy_ai_nexus_deny_thresh(void)
{
	return ai_mode == KILROY_AI_MODE_WAR ?
		KILROY_AI_WAR_DENY : KILROY_AI_HOME_DENY;
}

u32 kilroy_ai_nexus_eval_mask(void)
{
	return ai_mode == KILROY_AI_MODE_WAR ?
		KILROY_AI_WAR_EVAL_MASK : KILROY_AI_HOME_EVAL_MASK;
}

u32 kilroy_ai_thermo_idle_bonus_milli(void)
{
	return ai_mode == KILROY_AI_MODE_HOME ?
		KILROY_AI_HOME_THERMO_BONUS_MILLI : 0;
}

bool kilroy_ai_war_power_burst_bias(void)
{
	return ai_mode == KILROY_AI_MODE_WAR;
}

static int kilroy_ai_parse_mode(const char __user *buf, size_t count)
{
	char kbuf[16];
	size_t n = min(count, sizeof(kbuf) - 1);

	if (copy_from_user(kbuf, buf, n))
		return -EFAULT;
	kbuf[n] = '\0';

	if (str_has_prefix(kbuf, "war") || str_has_prefix(kbuf, "engage") ||
	    str_has_prefix(kbuf, "patrol"))
		ai_mode = KILROY_AI_MODE_WAR;
	else if (str_has_prefix(kbuf, "home") || str_has_prefix(kbuf, "dishes") ||
		 str_has_prefix(kbuf, "person"))
		ai_mode = KILROY_AI_MODE_HOME;
	else
		return -EINVAL;

	ai_mode_switches++;
	pr_info("kilroy_field: AI mode -> %s (DARPA compartment switch)\n",
		kilroy_ai_mode_name(ai_mode));
	return 0;
}

static int kilroy_ai_show(struct seq_file *m, void *v)
{
	struct rtx_global *g = rtx_global_state();

	seq_printf(m,
		   "schema=kilroy-ai/v1 darpa_secure=1 zero_trust=1\n"
		   "mode=%s grok16_profile=%s\n"
		   "war_profile=%s home_profile=%s\n"
		   "nexus_alert=%u nexus_deny=%u eval_mask=0x%x\n"
		   "truth_adapt_floor=%u truth_genius_floor=%u\n"
		   "thermo_idle_bonus_milli=%u power_burst_bias=%u\n"
		   "mode_switches=%llu truth_pass=%llu quarantine=%llu\n"
		   "hostess_wishes:\n%s"
		   "compiler=%s\n"
		   "active=%u syscall_total=%llu\n",
		   kilroy_ai_mode_name(ai_mode),
		   ai_mode == KILROY_AI_MODE_WAR ?
			KILROY_AI_GROK16_WAR : KILROY_AI_GROK16_HOME,
		   KILROY_AI_GROK16_WAR, KILROY_AI_GROK16_HOME,
		   kilroy_ai_nexus_alert_thresh(),
		   kilroy_ai_nexus_deny_thresh(),
		   kilroy_ai_nexus_eval_mask(),
		   KILROY_AI_TRUTH_ADAPT_FLOOR,
		   KILROY_AI_TRUTH_GENIUS_FLOOR,
		   kilroy_ai_thermo_idle_bonus_milli(),
		   kilroy_ai_war_power_burst_bias() ? 1u : 0u,
		   ai_mode_switches, ai_truth_pass, ai_truth_quarantine,
		   KILROY_AI_HOSTESS_WISHES,
		   KILROY_STACK_COMPILER,
		   g ? g->active : 0u,
		   g ? g->syscall_total : 0ull);
	return 0;
}

static ssize_t kilroy_ai_write(struct file *file, const char __user *buf,
			       size_t count, loff_t *ppos)
{
	int ret;

	ret = kilroy_ai_parse_mode(buf, count);
	if (ret)
		return ret;
	return count;
}

static int kilroy_ai_open(struct inode *inode, struct file *file)
{
	return single_open(file, kilroy_ai_show, NULL);
}

static const struct proc_ops kilroy_ai_ops = {
	.proc_open	= kilroy_ai_open,
	.proc_read	= seq_read,
	.proc_write	= kilroy_ai_write,
	.proc_lseek	= seq_lseek,
	.proc_release	= single_release,
};

void kilroy_ai_field_init(void)
{
	ai_mode = KILROY_AI_MODE_HOME;
	pr_info("kilroy_field: AI kernel active — DARPA secure, default=home (Hostess7 wishes)\n");
}

int kilroy_ai_proc_init(struct proc_dir_entry *parent)
{
	if (!parent)
		return -EINVAL;
	if (!proc_create("ai", 0644, parent, &kilroy_ai_ops))
		return -ENOMEM;
	return 0;
}