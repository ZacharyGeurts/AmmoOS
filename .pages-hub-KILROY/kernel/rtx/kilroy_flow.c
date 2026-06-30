// SPDX-License-Identifier: GPL-2.0
// KILROY FLOW slot — propalactic momentum + Tesla valve bias (Field OS).

#include <linux/kernel.h>
#include <linux/minmax.h>

#include "kilroy_flow.h"
#include "kilroy_physics_field.h"
#include "kilroy_units.h"
#include "rtx_slots.h"

/* Tesla valve: forward low resistance, reverse high (FieldRtxFieldAbs ratios) */
#define KILROY_TESLA_FWD_MICRO		KILROY_MICRO_FROM_MILLI(180)
#define KILROY_TESLA_REV_MICRO		KILROY_MICRO_FROM_MILLI(3200)

static u32 flow_momentum_submicro;
static u32 flow_forward_ops;
static u32 flow_reverse_ops;
static u32 flow_tesla_bias_micro = KILROY_SCALE_MICRO;

void kilroy_flow_init(void)
{
	flow_momentum_submicro = 0;
	flow_forward_ops = 0;
	flow_reverse_ops = 0;
	flow_tesla_bias_micro = KILROY_SCALE_MICRO;
}

void kilroy_flow_tick(u32 nr, bool fabric, long ret)
{
	u32 delta;
	bool forward;

	if (ret < 0) {
		forward = false;
		flow_reverse_ops++;
	} else if (fabric) {
		forward = true;
		flow_forward_ops++;
	} else {
		forward = (nr == 222 || nr == 214); /* mmap/brk growth */
		if (forward)
			flow_forward_ops++;
		else
			flow_reverse_ops++;
	}

#ifdef CONFIG_RTX_FIELD_TESLA_BIAS
	if (forward)
		delta = KILROY_SUBMICRO_PER_MICRO * KILROY_TESLA_FWD_MICRO / KILROY_SCALE_MICRO;
	else
		delta = KILROY_SUBMICRO_PER_MICRO * KILROY_TESLA_REV_MICRO / KILROY_SCALE_MICRO;
	flow_tesla_bias_micro = forward ?
		min_t(u32, KILROY_FCC_SCALE_MAX_MICRO,
		      flow_tesla_bias_micro + KILROY_MICRO_FROM_MILLI(1)) :
		max_t(u32, KILROY_MICRO_FROM_MILLI(800),
		     flow_tesla_bias_micro - KILROY_MICRO_FROM_MILLI(2));
#else
	delta = KILROY_SUBMICRO_PER_MICRO;
#endif

	if (forward)
		flow_momentum_submicro = min_t(u32, KILROY_SCALE_SUBMICRO / 10,
					       flow_momentum_submicro + delta);
	else
		flow_momentum_submicro = (flow_momentum_submicro > delta) ?
			flow_momentum_submicro - delta : 0;

	rtx_slots()->context.pad = flow_momentum_submicro / KILROY_SUBMICRO_PER_MICRO;

	kilroy_physics_entropy_arrow(forward);
	kilroy_physics_reynolds_tick(flow_momentum_submicro);
}

u32 kilroy_flow_momentum_submicro(void)
{
	return flow_momentum_submicro;
}

u32 kilroy_flow_tesla_bias_micro(void)
{
	return flow_tesla_bias_micro;
}