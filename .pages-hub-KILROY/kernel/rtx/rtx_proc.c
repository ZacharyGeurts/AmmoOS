// SPDX-License-Identifier: GPL-2.0
// /proc/kilroy_field — KILROY Field OS telemetry.
// Units: micro primary, submicro precision; legacy milli accepted on writes < 10000.

#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>
#include <linux/uaccess.h>
#include <linux/utsname.h>

#include "kilroy_boot.h"
#include "kilroy_cache_field.h"
#include "kilroy_direct_field.h"
#include "kilroy_drm_field.h"
#include "kilroy_flow.h"
#include "kilroy_field_stack_proc.h"
#include "kilroy_ai_field.h"
#include "kilroy_comfort_field.h"
#include "kilroy_physics_field.h"
#include "kilroy_sdf_field.h"
#include "kilroy_nexus_guard.h"
#include "kilroy_units.h"
#include "rtx_core.h"
#include "rtx_fcc.h"
#include "rtx_hw_field.h"
#include "rtx_power.h"
#include "rtx_slots.h"

static struct proc_dir_entry *kilroy_proc_root;

static void kilroy_proc_fill_slots(struct kilroy_field_slots *out)
{
	struct rtx_four_slots *s = rtx_slots();

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
	{
		struct kilroy_field_cpu cpu;

		kilroy_cpu_field_fill(&cpu);
		out->cpu_fabric_ops = (u32)cpu.fabric_ops;
	}
	out->ram_pressure_submicro = kilroy_ram_pressure_submicro();
}

static int kilroy_status_show(struct seq_file *m, void *v)
{
	struct rtx_global *g = rtx_global_state();
	struct rtx_four_slots *s = rtx_slots();
	struct kilroy_field_cpu cpu;
	struct kilroy_field_ram ram;
	struct kilroy_field_cache cache;
	struct kilroy_field_direct direct;

	kilroy_cpu_field_fill(&cpu);
	kilroy_ram_field_fill(&ram);
	kilroy_cache_field_fill(&cache);
	kilroy_direct_field_fill(&direct);

	seq_printf(m,
		   "name=%s codename=%s compat=%s magic=0x%x active=%u abi=%s layout=v%u\n"
		   "syscall_total=%llu fabric_total=%llu host_passthrough=%llu\n"
		   "slot0_time_sealed=%u sealed_ns=%llu entropy=0x%016llx\n"
		   "slot1_mem_alloc=%llu usable=%llu mmap_ops=%llu zmm[0][0]=0x%x\n"
		   "slot2_thermo_budget_micro=%u legacy_milli=%u fcc_guard_micro=%u\n"
		   "slot3_ctx_gen=%llu pid=%u seal=0x%016llx\n"
		   "entropy_micro=%u boundary_thermo_micro=%u prev_maint_micro=%u\n"
		   "free_energy_micro=%u steps=%u phi_micro=%u floor_submicro=%u\n"
		   "fcc time_micro=%u thermo_alpha_micro=%u wave_micro=%u gate_micro=%u inject_micro=%u\n"
		   "cpu_field: fabric_ops=%llu rate_submicro=%u burst_ready=%u phi_coupling_micro=%u\n"
		   "ram_field: pressure_submicro=%u legacy_permille=%u zmm_entropy=0x%x bandwidth_micro=%u\n"
		   "slot6_cache: shed=%u bypass=%u retention_micro=%u pressure_micro=%u\n"
		   "slot7_direct: maps=%llu bytes=%llu ratio_micro=%u coherence_ops=%llu\n"
		   "volt_tier=%u max_khz=%u fcc_aggressive_thresh_micro=%u legacy_milli=%u\n",
		   KILROY_FIELD_NAME, KILROY_FIELD_CODENAME, KILROY_COMPAT_SUBSTRATE,
		   KILROY_FIELD_MAGIC, g->active, KILROY_FIELD_ABI, KILROY_LAYOUT_VERSION,
		   g->syscall_total, g->fabric_total, g->host_passthrough,
		   s->time.sealed, s->time.sealed_ns, s->time.entropy,
		   s->memory.allocated_pages, s->memory.usable_pages,
		   s->memory.mmap_ops, s->memory.zmm[0][0],
		   s->thermo.budget_micro,
		   kilroy_micro_to_legacy_milli(s->thermo.budget_micro),
		   s->thermo.fcc_guard_scale_micro,
		   s->context.syscall_generation, s->context.pid, s->context.seal_hash,
		   g->thermo.entropy_micro, g->thermo.boundary_thermo_micro,
		   g->thermo.prev_maint_micro, g->thermo.free_energy_micro,
		   g->thermo.steps, g->thermo.phi_micro, g->thermo.entropy_floor_submicro,
		   g->fcc.time_scale_micro, g->fcc.thermo_alpha_micro,
		   g->fcc.wave_speed_micro, g->fcc.gate_fidelity_micro,
		   g->fcc.inject_strength_micro,
		   cpu.fabric_ops, cpu.syscall_rate_submicro, cpu.burst_ready,
		   cpu.phi_coupling_micro,
		   ram.pressure_submicro,
		   ram.pressure_submicro / KILROY_SUBMICRO_PER_MICRO,
		   ram.zmm_entropy, ram.bandwidth_micro,
		   cache.shed_count, cache.bypass_ops,
		   cache.retention_micro, cache.pressure_micro,
		   direct.direct_maps, direct.direct_bytes,
		   direct.direct_ratio_micro, direct.coherence_ops,
		   rtx_power_voltage_tier(), rtx_power_last_max_khz(),
		   KILROY_FCC_AGGRESSIVE_THRESH_MICRO,
		   KILROY_FCC_AGGRESSIVE_THRESH_MILLI);
	return 0;
}

static int kilroy_status_open(struct inode *inode, struct file *file)
{
	return single_open(file, kilroy_status_show, NULL);
}

static const struct proc_ops kilroy_status_ops = {
	.proc_open	= kilroy_status_open,
	.proc_read	= seq_read,
	.proc_lseek	= seq_lseek,
	.proc_release	= single_release,
};

static int kilroy_slots_show(struct seq_file *m, void *v)
{
	struct kilroy_field_slots sl;

	kilroy_proc_fill_slots(&sl);
	seq_printf(m,
		   "layout=%u time_sealed=%u genesis_ns=%llu sealed_ns=%llu\n"
		   "entropy=0x%016llx mem_alloc=%llu usable=%llu mmap_ops=%llu\n"
		   "thermo_budget_micro=%u fcc_guard_micro=%u ctx_gen=%llu ctx_pid=%u\n"
		   "cpu_fabric_ops=%u ram_pressure_submicro=%u\n"
		   "seal_hash=0x%016llx\n",
		   sl.layout_version, sl.time_sealed, sl.time_genesis_ns,
		   sl.time_sealed_ns, sl.time_entropy,
		   sl.mem_allocated_pages, sl.mem_usable_pages, sl.mem_mmap_ops,
		   sl.thermo_budget_micro, sl.fcc_guard_scale_micro,
		   sl.context_generation, sl.context_pid,
		   sl.cpu_fabric_ops, sl.ram_pressure_submicro,
		   sl.context_seal_hash);
	return 0;
}

static int kilroy_slots_open(struct inode *inode, struct file *file)
{
	return single_open(file, kilroy_slots_show, NULL);
}

static const struct proc_ops kilroy_slots_ops = {
	.proc_open	= kilroy_slots_open,
	.proc_read	= seq_read,
	.proc_lseek	= seq_lseek,
	.proc_release	= single_release,
};

static ssize_t kilroy_thermo_write(struct file *file, const char __user *buf,
				   size_t count, loff_t *ppos)
{
	struct kilroy_field_thermo thermo;
	char line[128];
	size_t len = min(count, sizeof(line) - 1);
	unsigned int vals[8];
	int n;

	if (copy_from_user(line, buf, len))
		return -EFAULT;
	line[len] = '\0';

	n = sscanf(line, "%u %u %u %u %u %u %u %u",
		   &vals[0], &vals[1], &vals[2], &vals[3],
		   &vals[4], &vals[5], &vals[6], &vals[7]);
	if (n < 2)
		return -EINVAL;

	thermo.entropy_micro = kilroy_norm_micro((u32)vals[0]);
	thermo.boundary_thermo_micro = kilroy_norm_micro((u32)vals[1]);
	thermo.prev_maint_micro = n > 2 ? kilroy_norm_micro((u32)vals[2]) : 0;
	thermo.free_energy_micro = n > 3 ? kilroy_norm_micro((u32)vals[3]) : 0;
	thermo.steps = n > 4 ? (u32)vals[4] : 0;
	thermo.host_heat_micro = n > 5 ? kilroy_norm_micro((u32)vals[5]) : 0;
	thermo.phi_micro = n > 6 ? kilroy_norm_micro((u32)vals[6]) : KILROY_FIELD_PHI_MICRO;
	thermo.entropy_floor_submicro = n > 7 ?
		kilroy_norm_submicro((u32)vals[7]) : KILROY_ENTROPY_FLOOR_SUBMICRO;

	rtx_global_state()->thermo = thermo;
	rtx_thermo_apply_userspace(&thermo);
	return count;
}

static ssize_t kilroy_fcc_write(struct file *file, const char __user *buf,
				size_t count, loff_t *ppos)
{
	struct kilroy_field_fcc fcc;
	char line[160];
	size_t len = min(count, sizeof(line) - 1);
	unsigned int vals[9];
	int n;

	if (copy_from_user(line, buf, len))
		return -EFAULT;
	line[len] = '\0';

	n = sscanf(line, "%u %u %u %u %u %u %u %u %u",
		   &vals[0], &vals[1], &vals[2], &vals[3], &vals[4],
		   &vals[5], &vals[6], &vals[7], &vals[8]);
	if (n < 4)
		return -EINVAL;

	fcc.time_scale_micro = kilroy_norm_micro((u32)vals[0]);
	fcc.thermo_alpha_micro = kilroy_norm_micro((u32)vals[1]);
	fcc.wave_speed_micro = kilroy_norm_micro((u32)vals[2]);
	fcc.gate_fidelity_micro = kilroy_norm_micro((u32)vals[3]);
	fcc.entropy_floor_submicro = n > 4 ?
		kilroy_norm_submicro((u32)vals[4]) : KILROY_SUBMICRO_FROM_MILLI(14);
	fcc.inject_strength_micro = n > 5 ?
		kilroy_norm_micro((u32)vals[5]) : KILROY_MICRO_FROM_MILLI(2800);
	fcc.propalactic_micro = n > 6 ?
		kilroy_norm_micro((u32)vals[6]) : KILROY_MICRO_FROM_MILLI(230);
	fcc.field_coupling_micro = n > 7 ?
		kilroy_norm_micro((u32)vals[7]) : KILROY_MICRO_FROM_MILLI(770);
	fcc.tesla_bias_micro = n > 8 ?
		kilroy_norm_micro((u32)vals[8]) : KILROY_SCALE_MICRO;

	rtx_fcc_harmonics_guard(&fcc);
	rtx_global_state()->fcc = fcc;
	return count;
}

static const struct proc_ops kilroy_thermo_ops = {
	.proc_write	= kilroy_thermo_write,
	.proc_lseek	= noop_llseek,
};

static const struct proc_ops kilroy_fcc_ops = {
	.proc_write	= kilroy_fcc_write,
	.proc_lseek	= noop_llseek,
};

static int kilroy_power_show(struct seq_file *m, void *v)
{
	static const char * const tier_names[] = { "cryo", "eco", "nom", "burst" };
	struct kilroy_field_power pwr;
	u8 tier;

	rtx_power_fill_abi(&pwr);
	tier = pwr.tier;

	seq_printf(m, "tier=%u (%s) max_khz=%u auto=%u fcc_guard_micro=%u\n"
		      "ram_pressure_submicro=%u cpu_burst_ready=%u\n"
		      "burst_needs: phi_micro>=%u thermo_micro>200000 entropy_micro<350000 fcc_micro>=%u\n"
		      "legacy_milli: phi>=%u thermo>200 entropy<350 fcc>=%u\n",
		   tier, tier <= KILROY_VOLT_BURST ? tier_names[tier] : "unknown",
		   pwr.max_khz, pwr.auto_mode, pwr.fcc_guard_scale_micro,
		   pwr.ram_pressure_submicro, pwr.cpu_burst_ready,
		   KILROY_FIELD_PHI_MICRO, KILROY_FCC_AGGRESSIVE_THRESH_MICRO,
		   KILROY_FIELD_PHI_MILLI, KILROY_FCC_AGGRESSIVE_THRESH_MILLI);
	return 0;
}

static int kilroy_power_open(struct inode *inode, struct file *file)
{
	return single_open(file, kilroy_power_show, NULL);
}

static ssize_t kilroy_power_write(struct file *file, const char __user *buf,
				  size_t count, loff_t *ppos)
{
	char line[32];
	size_t len = min(count, sizeof(line) - 1);
	unsigned int tier;

	if (copy_from_user(line, buf, len))
		return -EFAULT;
	line[len] = '\0';

	if (!strncmp(line, "auto", 4)) {
		rtx_power_set_force_tier(255);
		return count;
	}

	if (kstrtouint(line, 10, &tier) || tier > KILROY_VOLT_BURST)
		return -EINVAL;

	rtx_power_set_force_tier((u8)tier);
	return count;
}

static const struct proc_ops kilroy_power_ops = {
	.proc_open	= kilroy_power_open,
	.proc_read	= seq_read,
	.proc_write	= kilroy_power_write,
	.proc_lseek	= seq_lseek,
	.proc_release	= single_release,
};

static int kilroy_cpu_show(struct seq_file *m, void *v)
{
	struct kilroy_field_cpu cpu;

	kilroy_cpu_field_fill(&cpu);
	seq_printf(m,
		   "online=%u active=%u tier=%u max_khz=%u burst_ready=%u\n"
		   "fabric_ops=%llu syscall_total=%llu rate_submicro=%u phi_coupling_micro=%u\n",
		   cpu.online_cpus, cpu.active_cpu, cpu.volt_tier, cpu.max_khz,
		   cpu.burst_ready, cpu.fabric_ops, cpu.syscall_total,
		   cpu.syscall_rate_submicro, cpu.phi_coupling_micro);
	return 0;
}

static int kilroy_cpu_open(struct inode *inode, struct file *file)
{
	return single_open(file, kilroy_cpu_show, NULL);
}

static const struct proc_ops kilroy_cpu_ops = {
	.proc_open	= kilroy_cpu_open,
	.proc_read	= seq_read,
	.proc_lseek	= seq_lseek,
	.proc_release	= single_release,
};

static int kilroy_ram_show(struct seq_file *m, void *v)
{
	struct kilroy_field_ram ram;

	kilroy_ram_field_fill(&ram);
	seq_printf(m,
		   "total_pages=%llu alloc=%llu usable=%llu pressure_submicro=%u\n"
		   "mmap_ops=%llu brk_ops=%llu zmm_entropy=0x%x bandwidth_micro=%u\n"
		   "safety_margin_mb=%u legacy_pressure_permille=%u\n",
		   ram.total_pages, ram.allocated_pages, ram.usable_pages,
		   ram.pressure_submicro, ram.mmap_ops, ram.brk_ops,
		   ram.zmm_entropy, ram.bandwidth_micro, ram.safety_margin_mb,
		   ram.pressure_submicro / KILROY_SUBMICRO_PER_MICRO);
	return 0;
}

static int kilroy_ram_open(struct inode *inode, struct file *file)
{
	return single_open(file, kilroy_ram_show, NULL);
}

static const struct proc_ops kilroy_ram_ops = {
	.proc_open	= kilroy_ram_open,
	.proc_read	= seq_read,
	.proc_lseek	= seq_lseek,
	.proc_release	= single_release,
};

static int kilroy_flow_show(struct seq_file *m, void *v)
{
	seq_printf(m,
		   "momentum_submicro=%u tesla_bias_micro=%u\n"
		   "forward_resistance_micro=%u reverse_resistance_micro=%u\n",
		   kilroy_flow_momentum_submicro(), kilroy_flow_tesla_bias_micro(),
		   KILROY_MICRO_FROM_MILLI(180), KILROY_MICRO_FROM_MILLI(3200));
	return 0;
}

static int kilroy_flow_open(struct inode *inode, struct file *file)
{
	return single_open(file, kilroy_flow_show, NULL);
}

static const struct proc_ops kilroy_flow_ops = {
	.proc_open	= kilroy_flow_open,
	.proc_read	= seq_read,
	.proc_lseek	= seq_lseek,
	.proc_release	= single_release,
};

static int kilroy_cache_show(struct seq_file *m, void *v)
{
	struct kilroy_field_cache cache;

	kilroy_cache_field_fill(&cache);
	seq_printf(m,
		   "shed_count=%u bypass_ops=%u slab_drops=%u lru_drains=%u\n"
		   "retention_micro=%u pressure_micro=%u\n"
		   "policy=field-direct shed=lru_add_drain+drop_slab\n",
		   cache.shed_count, cache.bypass_ops,
		   cache.slab_drops, cache.lru_drains,
		   cache.retention_micro, cache.pressure_micro);
	return 0;
}

static int kilroy_cache_open(struct inode *inode, struct file *file)
{
	return single_open(file, kilroy_cache_show, NULL);
}

static const struct proc_ops kilroy_cache_ops = {
	.proc_open	= kilroy_cache_open,
	.proc_read	= seq_read,
	.proc_lseek	= seq_lseek,
	.proc_release	= single_release,
};

static int kilroy_direct_show(struct seq_file *m, void *v)
{
	struct kilroy_field_direct direct;

	kilroy_direct_field_fill(&direct);
	seq_printf(m,
		   "direct_maps=%llu direct_bytes=%llu cached_maps=%llu\n"
		   "coherence_ops=%llu direct_ratio_micro=%u\n"
		   "policy=anonymous_maps_field_direct file_maps_cache_coupled\n",
		   direct.direct_maps, direct.direct_bytes, direct.cached_maps,
		   direct.coherence_ops, direct.direct_ratio_micro);
	return 0;
}

static int kilroy_direct_open(struct inode *inode, struct file *file)
{
	return single_open(file, kilroy_direct_show, NULL);
}

static const struct proc_ops kilroy_direct_ops = {
	.proc_open	= kilroy_direct_open,
	.proc_read	= seq_read,
	.proc_lseek	= seq_lseek,
	.proc_release	= single_release,
};

static int kilroy_gpu_show(struct seq_file *m, void *v)
{
	struct kilroy_field_gpu gpu;

	kilroy_drm_field_fill(&gpu);
	seq_printf(m,
		   "gpu_count=%u active_cards=%u fcc_coupling_micro=%u\n"
		   "tesla_bias_micro=%u policy=pci_vga_fcc_mirror\n",
		   gpu.gpu_count, gpu.active_cards, gpu.fcc_coupling_micro,
		   gpu.tesla_bias_micro);
	return 0;
}

static int kilroy_gpu_open(struct inode *inode, struct file *file)
{
	return single_open(file, kilroy_gpu_show, NULL);
}

static const struct proc_ops kilroy_gpu_ops = {
	.proc_open	= kilroy_gpu_open,
	.proc_read	= seq_read,
	.proc_lseek	= seq_lseek,
	.proc_release	= single_release,
};

static int kilroy_boot_show(struct seq_file *m, void *v)
{
	seq_printf(m,
		   "bootloader=Grok grok_version=1.1.0\n"
		   "uname_sysname=%s uname_release=%s\n"
		   "grok_security=%s field_boot=%u\n"
		   "grok_themes=field,midnight,dawn,mono\n"
		   "grok_audit=./scripts/grok-firmware-audit.sh\n"
		   "speedups=ReBAR,Above4G,NVMe_native,XMP\n"
		   "docs=/boot/grok/security/MANIFEST,/boot/grok/speedups/MANIFEST\n",
		   init_utsname()->sysname,
		   init_utsname()->release,
		   kilroy_grok_security_name(),
		   kilroy_field_boot_flag() ? 1u : 0u);
	return 0;
}

static int kilroy_boot_open(struct inode *inode, struct file *file)
{
	return single_open(file, kilroy_boot_show, NULL);
}

static const struct proc_ops kilroy_boot_ops = {
	.proc_open	= kilroy_boot_open,
	.proc_read	= seq_read,
	.proc_lseek	= seq_lseek,
	.proc_release	= single_release,
};

static int kilroy_security_show(struct seq_file *m, void *v)
{
	seq_printf(m,
		   "grok_security=%s field_boot=%u\n"
		   "nexus_guard=1 ultra_stealth=1 consumer_whitelist=1\n"
		   "final_eye_seal=stoard zocr_security=python3_zocr_security.py_seal\n"
		   "behavior_score=%u predictive_score=%u alert_count=%u\n"
		   "4slot_security=%d fcc_guard=%d asm_gate=%d sdf_proc=1 hot_path_hooks=0\n"
		   "ai_kernel=%d ai_mode=%s darpa_secure=1\n",
		   kilroy_grok_security_name(),
		   kilroy_field_boot_flag() ? 1u : 0u,
		   kilroy_nexus_behavior_score(),
		   kilroy_nexus_predictive_score(),
		   kilroy_nexus_alert_count(),
#ifdef CONFIG_RTX_FIELD_4SLOT_SECURITY
		   1,
#else
		   0,
#endif
#ifdef CONFIG_RTX_FIELD_FCC_GUARD
		   1,
#else
		   0,
#endif
#ifdef CONFIG_RTX_FIELD_ASM_GATE
		   1,
#else
		   0,
#endif
#ifdef CONFIG_RTX_FIELD_AI_KERNEL
		   1, kilroy_ai_mode_name(kilroy_ai_current_mode()));
#else
		   0, "off");
#endif
	return 0;
}

static int kilroy_security_open(struct inode *inode, struct file *file)
{
	return single_open(file, kilroy_security_show, NULL);
}

static const struct proc_ops kilroy_security_ops = {
	.proc_open	= kilroy_security_open,
	.proc_read	= seq_read,
	.proc_lseek	= seq_lseek,
	.proc_release	= single_release,
};

static int __init kilroy_field_init(void)
{
	int ret;

	rtx_core_init();
	ret = rtx_power_init();
	if (ret)
		return ret;
	kilroy_proc_root = proc_mkdir("kilroy_field", NULL);
	if (!kilroy_proc_root)
		return -ENOMEM;
	proc_create("status", 0444, kilroy_proc_root, &kilroy_status_ops);
	proc_create("slots", 0444, kilroy_proc_root, &kilroy_slots_ops);
	proc_create("thermo", 0222, kilroy_proc_root, &kilroy_thermo_ops);
	proc_create("fcc", 0222, kilroy_proc_root, &kilroy_fcc_ops);
	proc_create("power", 0644, kilroy_proc_root, &kilroy_power_ops);
	proc_create("cpu", 0444, kilroy_proc_root, &kilroy_cpu_ops);
	proc_create("ram", 0444, kilroy_proc_root, &kilroy_ram_ops);
	proc_create("flow", 0444, kilroy_proc_root, &kilroy_flow_ops);
	proc_create("cache", 0444, kilroy_proc_root, &kilroy_cache_ops);
	proc_create("direct", 0444, kilroy_proc_root, &kilroy_direct_ops);
	proc_create("gpu", 0444, kilroy_proc_root, &kilroy_gpu_ops);
	proc_create("boot", 0444, kilroy_proc_root, &kilroy_boot_ops);
	proc_create("security", 0444, kilroy_proc_root, &kilroy_security_ops);
	kilroy_field_stack_proc_init(kilroy_proc_root);
	kilroy_sdf_proc_init(kilroy_proc_root);
	kilroy_ai_proc_init(kilroy_proc_root);
	kilroy_physics_proc_init(kilroy_proc_root);
	kilroy_comfort_proc_init(kilroy_proc_root);
	kilroy_boot_init();
	return 0;
}

fs_initcall(kilroy_field_init);