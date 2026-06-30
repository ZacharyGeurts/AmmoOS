// SPDX-License-Identifier: GPL-2.0
// KILROY ThermoAccountant — fabric syscall classification.

#include <linux/kernel.h>
#include <linux/types.h>

#include "rtx_core.h"

bool rtx_is_fabric_syscall(u32 nr)
{
	switch (nr) {
	case 123: /* sched_getaffinity */
	case 124: /* sched_yield */
	case 165: /* getrusage */
	case 261: /* prlimit64 */
	case 278: /* getrandom */
		return true;
	default:
		return false;
	}
}