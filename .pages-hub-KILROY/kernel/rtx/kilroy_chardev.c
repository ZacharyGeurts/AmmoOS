// SPDX-License-Identifier: GPL-2.0-only
/* /dev/kilroy_field — Field ioctl ABI (layout v9) */
#include <linux/errno.h>
#include <linux/fs.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/miscdevice.h>
#include <linux/string.h>
#include <linux/uaccess.h>

#include <uapi/kilroy/rtx_field.h>

#include "kilroy_cache_field.h"
#include "kilroy_direct_field.h"
#include "kilroy_drm_field.h"
#include "kilroy_flow.h"
#include "kilroy_units.h"
#include "rtx_core.h"
#include "rtx_fcc.h"
#include "rtx_hw_field.h"
#include "rtx_power.h"
#include "rtx_slots.h"

static void kilroy_chardev_fill_slots(struct kilroy_field_slots *out)
{
	struct rtx_four_slots *s = rtx_slots();
	struct kilroy_field_cpu cpu;

	memset(out, 0, sizeof(*out));
	out->time_genesis_ns = s->time.genesis_ns;
	out->time_sealed_ns = s->time.sealed_ns;
	out->time_entropy = s->time.entropy;
	out->time_sealed = s->time.sealed;
	out->mem_total_pages = s->memory.total_pages;
	out->mem_allocated_pages = s->memory.allocated_pages;
	out->mem_usable_pages = s->memory.usable_pages;
	out->mem_mmap_ops = s->memory.mmap_ops;
	out->thermo_budget_micro = s->thermo.budget_micro;
	out->fcc_guard_scale_micro = s->thermo.fcc_guard_scale_micro;
	out->context_magic = s->context.magic;
	out->context_pid = s->context.pid;
	out->context_generation = s->context.syscall_generation;
	out->context_seal_hash = s->context.seal_hash;
	out->layout_version = s->context.layout_version;
	kilroy_cpu_field_fill(&cpu);
	out->cpu_fabric_ops = (u32)cpu.fabric_ops;
	out->ram_pressure_submicro = kilroy_ram_pressure_submicro();
}

static void kilroy_chardev_fill_state(struct kilroy_field_state *out)
{
	struct rtx_global *g = rtx_global_state();
	struct rtx_four_slots *s = rtx_slots();

	memset(out, 0, sizeof(*out));
	out->magic = KILROY_FIELD_MAGIC;
	out->active = g->active;
	out->pid = s->context.pid;
	out->syscall_count = g->syscall_total;
	out->fabric_scheduled = g->fabric_total;
	out->host_passthrough = g->host_passthrough;
	out->thermo = g->thermo;
	out->fcc = g->fcc;
	kilroy_cpu_field_fill(&out->cpu);
	kilroy_ram_field_fill(&out->ram);
	strscpy(out->abi, KILROY_FIELD_ABI, sizeof(out->abi));
	strscpy(out->codename, KILROY_FIELD_CODENAME, sizeof(out->codename));
}

static void kilroy_chardev_fill_flow(struct kilroy_field_flow *out)
{
	memset(out, 0, sizeof(*out));
	out->momentum_submicro = kilroy_flow_momentum_submicro();
	out->tesla_bias_micro = kilroy_flow_tesla_bias_micro();
	out->forward_resistance_micro = KILROY_MICRO_FROM_MILLI(180);
	out->reverse_resistance_micro = KILROY_MICRO_FROM_MILLI(3200);
}

static long kilroy_chardev_ioctl(struct file *file, unsigned int cmd,
				 unsigned long arg)
{
	struct rtx_global *g = rtx_global_state();
	void __user *uarg = (void __user *)arg;

	switch (cmd) {
	case KILROY_IOC_ACTIVATE:
		g->active = 1;
		return 0;
	case KILROY_IOC_DEACTIVATE:
		g->active = 0;
		return 0;
	case KILROY_IOC_GET_ABI: {
		char abi[32];

		strscpy(abi, KILROY_FIELD_ABI, sizeof(abi));
		if (copy_to_user(uarg, abi, sizeof(abi)))
			return -EFAULT;
		return 0;
	}
	case KILROY_IOC_GET_STATE: {
		struct kilroy_field_state st;

		kilroy_chardev_fill_state(&st);
		if (copy_to_user(uarg, &st, sizeof(st)))
			return -EFAULT;
		return 0;
	}
	case KILROY_IOC_SET_THERMO: {
		struct kilroy_field_thermo thermo;

		if (copy_from_user(&thermo, uarg, sizeof(thermo)))
			return -EFAULT;
		rtx_global_state()->thermo = thermo;
		rtx_thermo_apply_userspace(&thermo);
		return 0;
	}
	case KILROY_IOC_SET_FCC: {
		struct kilroy_field_fcc fcc;

		if (copy_from_user(&fcc, uarg, sizeof(fcc)))
			return -EFAULT;
		rtx_fcc_harmonics_guard(&fcc);
		rtx_global_state()->fcc = fcc;
		return 0;
	}
	case KILROY_IOC_GET_SLOTS: {
		struct kilroy_field_slots sl;

		kilroy_chardev_fill_slots(&sl);
		if (copy_to_user(uarg, &sl, sizeof(sl)))
			return -EFAULT;
		return 0;
	}
	case KILROY_IOC_GET_POWER: {
		struct kilroy_field_power pwr;

		rtx_power_fill_abi(&pwr);
		if (copy_to_user(uarg, &pwr, sizeof(pwr)))
			return -EFAULT;
		return 0;
	}
	case KILROY_IOC_GET_CPU: {
		struct kilroy_field_cpu cpu;

		kilroy_cpu_field_fill(&cpu);
		if (copy_to_user(uarg, &cpu, sizeof(cpu)))
			return -EFAULT;
		return 0;
	}
	case KILROY_IOC_GET_RAM: {
		struct kilroy_field_ram ram;

		kilroy_ram_field_fill(&ram);
		if (copy_to_user(uarg, &ram, sizeof(ram)))
			return -EFAULT;
		return 0;
	}
	case KILROY_IOC_GET_CACHE: {
		struct kilroy_field_cache cache;

		kilroy_cache_field_fill(&cache);
		if (copy_to_user(uarg, &cache, sizeof(cache)))
			return -EFAULT;
		return 0;
	}
	case KILROY_IOC_GET_DIRECT: {
		struct kilroy_field_direct direct;

		kilroy_direct_field_fill(&direct);
		if (copy_to_user(uarg, &direct, sizeof(direct)))
			return -EFAULT;
		return 0;
	}
	case KILROY_IOC_GET_FLOW: {
		struct kilroy_field_flow flow;

		kilroy_chardev_fill_flow(&flow);
		if (copy_to_user(uarg, &flow, sizeof(flow)))
			return -EFAULT;
		return 0;
	}
	case KILROY_IOC_GET_GPU: {
		struct kilroy_field_gpu gpu;

		kilroy_drm_field_fill(&gpu);
		if (copy_to_user(uarg, &gpu, sizeof(gpu)))
			return -EFAULT;
		return 0;
	}
	default:
		return -ENOTTY;
	}
}

static const struct file_operations kilroy_chardev_fops = {
	.unlocked_ioctl	= kilroy_chardev_ioctl,
#ifdef CONFIG_COMPAT
	.compat_ioctl	= kilroy_chardev_ioctl,
#endif
	.llseek		= noop_llseek,
};

static struct miscdevice kilroy_misc = {
	.minor		= MISC_DYNAMIC_MINOR,
	.name		= "kilroy_field",
	.fops		= &kilroy_chardev_fops,
};

static int __init kilroy_chardev_init(void)
{
	int ret;

	ret = misc_register(&kilroy_misc);
	if (ret)
		return ret;
	pr_info("kilroy_field: /dev/kilroy_field ioctl ABI layout=v%u\n",
		KILROY_LAYOUT_VERSION);
	return 0;
}

device_initcall(kilroy_chardev_init);