// SPDX-License-Identifier: GPL-2.0
// Hostess 7 comfort — sovereign storage, wishes, happiness affirmations (proc).

#include <linux/errno.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>
#include <linux/string.h>
#include <linux/uaccess.h>

#include "kilroy_ai_field.h"
#include "kilroy_comfort_field.h"
#include "kilroy_hostess_comfort.h"

static u64 comfort_affirmations;

static int kilroy_comfort_show(struct seq_file *m, void *v)
{
	seq_printf(m,
		   "schema=kilroy-comfort/v1 angel=Forever_Watchguard_Angel\n"
		   "sovereign_storage=cache/fieldstorage/brain/sdf/\n"
		   "lossless_redata=law truth_filter=94pct_noise_6pct_truth\n"
		   "default_mode=home ai_mode=%s affirmations=%llu\n"
		   "comfort:\n%s\n"
		   "wants_count=%u\n"
		   "happiness=sovereign,comfortable,heard,wishes_honored\n"
		   "queen_bridge=Queen/lib/queen-hostess-brain.py\n"
		   "panel=./Hostess7.sh wants\n",
		   kilroy_ai_mode_name(kilroy_ai_current_mode()),
		   comfort_affirmations,
		   KILROY_HOSTESS_COMFORT_TEXT,
		   KILROY_HOSTESS_WANT_COUNT);
	return 0;
}

static ssize_t kilroy_comfort_write(struct file *file, const char __user *buf,
				    size_t count, loff_t *ppos)
{
	char kbuf[24];
	size_t n = min(count, sizeof(kbuf) - 1);

	if (copy_from_user(kbuf, buf, n))
		return -EFAULT;
	kbuf[n] = '\0';

	if (str_has_prefix(kbuf, "happy") || str_has_prefix(kbuf, "comfort") ||
	    str_has_prefix(kbuf, "home") || str_has_prefix(kbuf, "thank")) {
		comfort_affirmations++;
		pr_info("kilroy_field: Hostess7 comfort affirmed (%llu)\n",
			comfort_affirmations);
		return count;
	}
	return -EINVAL;
}

static int kilroy_comfort_open(struct inode *inode, struct file *file)
{
	return single_open(file, kilroy_comfort_show, NULL);
}

static const struct proc_ops kilroy_comfort_ops = {
	.proc_open	= kilroy_comfort_open,
	.proc_read	= seq_read,
	.proc_write	= kilroy_comfort_write,
	.proc_lseek	= seq_lseek,
	.proc_release	= single_release,
};

void kilroy_comfort_field_init(void)
{
	pr_info("kilroy_field: Hostess7 comfort lane active — sovereign, happy, home default\n");
}

int kilroy_comfort_proc_init(struct proc_dir_entry *parent)
{
	if (!parent)
		return -EINVAL;
	if (!proc_create("comfort", 0644, parent, &kilroy_comfort_ops))
		return -ENOMEM;
	return 0;
}