// SPDX-License-Identifier: GPL-2.0
// /proc/kilroy_field/stack — ecosystem Field stack (#1 mandate)

#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>

#include "kilroy_field_stack.h"
#include "kilroy_field_stack_proc.h"
#include "rtx_core.h"

static int kilroy_stack_show(struct seq_file *m, void *v)
{
	struct rtx_global *g = rtx_global_state();

	seq_printf(m,
		   "schema=kilroy-field-stack/v1 rank=1\n"
		   "motto=%s\n"
		   "compiler=%s\n"
		   "abi=%s layout=v%u active=%u\n"
		   "repos:\n%s"
		   "github:\n%s"
		   "fieldc_targets:\n%s"
		   "recompile=scripts/field-recompile.sh\n"
		   "proc_nodes=status,security,stack,boot,power,thermo,flow,cache,direct,gpu\n",
		   KILROY_STACK_MOTTO,
		   KILROY_STACK_COMPILER,
		   KILROY_FIELD_ABI, KILROY_LAYOUT_VERSION,
		   g ? g->active : 0u,
		   KILROY_STACK_REPOS,
		   KILROY_STACK_GITHUB,
		   KILROY_STACK_FIELDC);
	return 0;
}

static int kilroy_stack_open(struct inode *inode, struct file *file)
{
	return single_open(file, kilroy_stack_show, NULL);
}

static const struct proc_ops kilroy_stack_ops = {
	.proc_open	= kilroy_stack_open,
	.proc_read	= seq_read,
	.proc_lseek	= seq_lseek,
	.proc_release	= single_release,
};

int kilroy_field_stack_proc_init(struct proc_dir_entry *parent)
{
	if (!parent)
		return -EINVAL;
	if (!proc_create("stack", 0444, parent, &kilroy_stack_ops))
		return -ENOMEM;
	return 0;
}