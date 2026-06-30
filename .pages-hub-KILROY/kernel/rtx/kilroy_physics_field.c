// SPDX-License-Identifier: GPL-2.0
// Hostess7 physics breakthroughs — entropy arrow, Reynolds gate, field_canvas phi doctrine.

#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/minmax.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>

#include "kilroy_physics_field.h"
#include "kilroy_units.h"
#include "rtx_core.h"
#include "rtx_slots.h"

#define KILROY_RE_LAMINAR_SUBMICRO	(KILROY_MICRO_FROM_MILLI(30) * KILROY_SUBMICRO_PER_MICRO)
#define KILROY_RE_TURBULENT_SUBMICRO	(KILROY_MICRO_FROM_MILLI(120) * KILROY_SUBMICRO_PER_MICRO)

static u64 entropy_arrow_total;
static u8 reynolds_regime; /* 0=laminar 1=transitional 2=turbulent */

void kilroy_physics_entropy_arrow(bool forward)
{
	struct rtx_global *g = rtx_global_state();
	struct rtx_four_slots *s = rtx_slots();
	u32 ent, cap;

	if (!forward || !g)
		return;

	ent = g->thermo.entropy_micro;
	cap = KILROY_MICRO_FROM_MILLI(999);
	if (ent >= cap)
		return;

	g->thermo.entropy_micro = ent + 1;
	if (s)
		s->thermo.acct.entropy_micro = g->thermo.entropy_micro;
	entropy_arrow_total++;
}

void kilroy_physics_reynolds_tick(u32 momentum_submicro)
{
	if (momentum_submicro >= KILROY_RE_TURBULENT_SUBMICRO)
		reynolds_regime = 2;
	else if (momentum_submicro >= KILROY_RE_LAMINAR_SUBMICRO)
		reynolds_regime = 1;
	else
		reynolds_regime = 0;
}

u8 kilroy_physics_reynolds_regime(void)
{
	return reynolds_regime;
}

u64 kilroy_physics_entropy_arrow_total(void)
{
	return entropy_arrow_total;
}

static const char *reynolds_name(u8 r)
{
	switch (r) {
	case 2: return "turbulent";
	case 1: return "transitional";
	default: return "laminar";
	}
}

static int kilroy_physics_show(struct seq_file *m, void *v)
{
	struct rtx_global *g = rtx_global_state();
	struct rtx_four_slots *s = rtx_slots();

	seq_printf(m,
		   "schema=kilroy-physics/v1 source=hostess7_field_canvas_physics\n"
		   "breakthroughs=entropy_arrow,phi_coupling,tesla_reynolds,wave_persist,spatial_seal\n"
		   "entropy_arrow_forward=%llu entropy_micro=%u phi_micro=%u\n"
		   "reynolds_regime=%s momentum_submicro=%u\n"
		   "tesla_fwd_milli=180 tesla_rev_milli=3200\n"
		   "wave_persist=field_wave.persist resonance=FCC_harmonics\n"
		   "field_canvas=phi_dispatch entropy_fabric_predict analog_die\n"
		   "corpus=Hostess7/cache/fieldstorage/brain/physics/corpus.json\n"
		   "domains=13 kinematics..field_canvas_physics\n"
		   "active=%u syscall_total=%llu\n",
		   entropy_arrow_total,
		   g ? g->thermo.entropy_micro : 0u,
		   g ? g->thermo.phi_micro : 0u,
		   reynolds_name(reynolds_regime),
		   s ? s->context.pad * KILROY_SUBMICRO_PER_MICRO : 0u,
		   g ? g->active : 0u,
		   g ? g->syscall_total : 0ull);
	return 0;
}

static int kilroy_physics_open(struct inode *inode, struct file *file)
{
	return single_open(file, kilroy_physics_show, NULL);
}

static const struct proc_ops kilroy_physics_ops = {
	.proc_open	= kilroy_physics_open,
	.proc_read	= seq_read,
	.proc_lseek	= seq_lseek,
	.proc_release	= single_release,
};

void kilroy_physics_field_init(void)
{
	entropy_arrow_total = 0;
	reynolds_regime = 0;
	pr_info("kilroy_field: physics breakthroughs — entropy arrow + Reynolds gate (Hostess7)\n");
}

int kilroy_physics_proc_init(struct proc_dir_entry *parent)
{
	if (!parent)
		return -EINVAL;
	if (!proc_create("physics", 0444, parent, &kilroy_physics_ops))
		return -ENOMEM;
	return 0;
}