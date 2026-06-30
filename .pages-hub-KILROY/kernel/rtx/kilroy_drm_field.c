// SPDX-License-Identifier: GPL-2.0-only
/* GPU FCC mirror — PCI display class → tesla_bias coupling */
#ifdef CONFIG_RTX_FIELD_DRM_FCC

#include <linux/kernel.h>
#include <linux/pci.h>

#include "kilroy_drm_field.h"
#include "kilroy_units.h"
#include "rtx_core.h"

struct kilroy_drm_state {
	u32 gpu_count;
	u32 active_cards;
	u32 fcc_coupling_micro;
};

static struct kilroy_drm_state drm_field;

static int kilroy_drm_count_gpus(void)
{
	struct pci_dev *pdev = NULL;
	int n = 0;

	while ((pdev = pci_get_class(PCI_CLASS_DISPLAY_VGA << 8, pdev)) != NULL)
		n++;
	return n;
}

void kilroy_drm_field_init(void)
{
	drm_field.gpu_count = kilroy_drm_count_gpus();
	drm_field.active_cards = drm_field.gpu_count;
	drm_field.fcc_coupling_micro = min_t(u32, KILROY_SCALE_MICRO,
		drm_field.gpu_count * KILROY_MICRO_FROM_MILLI(120));
	pr_info("kilroy_field: DRM FCC mirror — %u GPU(s) coupling_micro=%u\n",
		drm_field.gpu_count, drm_field.fcc_coupling_micro);
}

void kilroy_drm_fcc_mirror(struct kilroy_field_fcc *fcc)
{
	u32 bias;

	if (!fcc)
		return;

	drm_field.gpu_count = kilroy_drm_count_gpus();
	drm_field.active_cards = drm_field.gpu_count;
	drm_field.fcc_coupling_micro = min_t(u32, KILROY_SCALE_MICRO,
		drm_field.gpu_count * KILROY_MICRO_FROM_MILLI(120));

	bias = KILROY_SCALE_MICRO - min_t(u32, KILROY_MICRO_FROM_MILLI(200),
					  drm_field.fcc_coupling_micro);
	fcc->tesla_bias_micro = max_t(u32, bias, KILROY_MICRO_FROM_MILLI(400));
	fcc->field_coupling_micro = max_t(u32, fcc->field_coupling_micro,
					  drm_field.fcc_coupling_micro);
}

void kilroy_drm_field_fill(struct kilroy_field_gpu *out)
{
	memset(out, 0, sizeof(*out));
	out->gpu_count = drm_field.gpu_count;
	out->active_cards = drm_field.active_cards;
	out->fcc_coupling_micro = drm_field.fcc_coupling_micro;
	out->tesla_bias_micro = rtx_global_state()->fcc.tesla_bias_micro;
}

#endif /* CONFIG_RTX_FIELD_DRM_FCC */