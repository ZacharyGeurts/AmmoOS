/* SPDX-License-Identifier: GPL-2.0 WITH Linux-syscall-note */
/*
 * KILROY Field OS — native Field Die UAPI.
 * Linux-compatible userspace ABI; Field-native kernel identity.
 * Units: micro (1e-6) primary, submicro (1e-9) precision fields.
 * Legacy milli accepted on /proc writes when values < 10000.
 */
#ifndef _UAPI_KILROY_RTX_FIELD_H
#define _UAPI_KILROY_RTX_FIELD_H

#include <linux/ioctl.h>
#include <linux/types.h>

#define KILROY_OS_NAME			"KILROY"
#define KILROY_FIELD_NAME		KILROY_OS_NAME
#define KILROY_FIELD_CODENAME		"Field"
#define KILROY_COMPAT_SUBSTRATE		"linux-7.1.1"
#define KILROY_VERSION_MAJOR		1
#define KILROY_VERSION_MINOR		0
#define KILROY_VERSION_STRING		"1.0"
#define KILROY_FIELD_ABI		"kilroy-field-1.0"
#define KILROY_FIELD_MAGIC		0x4B494C52u /* 'KILR' */
#define KILROY_FIELD_PHI_MICRO		618000u
#define KILROY_FIELD_PHI_SUBMICRO	618000000u
#define KILROY_LAYOUT_VERSION		9
#define KILROY_SLOT_COUNT		8

#define KILROY_SLOT_TIME		0
#define KILROY_SLOT_RAM			1
#define KILROY_SLOT_THERMO		2
#define KILROY_SLOT_CONTEXT		3
#define KILROY_SLOT_CPU			4
#define KILROY_SLOT_FLOW		5
#define KILROY_SLOT_CACHE		6
#define KILROY_SLOT_DIRECT		7

#define KILROY_FCC_AGGRESSIVE_THRESH_MICRO	920000u
#define KILROY_FCC_SCALE_MAX_MICRO		1000000u

#define KILROY_VOLT_CRYO	0
#define KILROY_VOLT_ECO		1
#define KILROY_VOLT_NOM		2
#define KILROY_VOLT_BURST	3

/* Legacy milli #defines — numeric only, for old userspace compile */
#define KILROY_FIELD_PHI_MILLI		618
#define RTX_FIELD_MAGIC			KILROY_FIELD_MAGIC
#define RTX_FIELD_ABI			KILROY_FIELD_ABI
#define RTX_FIELD_PHI_MILLI		618
#define RTX_LAYOUT_VERSION		KILROY_LAYOUT_VERSION
#define RTX_SLOT_COUNT			KILROY_SLOT_COUNT
#define KILROY_FCC_AGGRESSIVE_THRESH_MILLI	920
#define KILROY_FCC_SCALE_MAX_MILLI		1000

struct kilroy_field_cpu {
	__u32 online_cpus;
	__u32 active_cpu;
	__u8  volt_tier;
	__u8  burst_ready;
	__u16 pad;
	__u32 max_khz;
	__u64 fabric_ops;
	__u64 syscall_total;
	__u32 syscall_rate_submicro;
	__u32 phi_coupling_micro;
};

struct kilroy_field_ram {
	__u64 total_pages;
	__u64 allocated_pages;
	__u64 usable_pages;
	__u64 mmap_ops;
	__u64 brk_ops;
	__u32 zmm_entropy;
	__u32 pressure_submicro;
	__u32 bandwidth_micro;
	__u32 safety_margin_mb;
};

struct kilroy_field_thermo {
	__u32 entropy_micro;
	__u32 boundary_thermo_micro;
	__u32 prev_maint_micro;
	__u32 free_energy_micro;
	__u32 steps;
	__u32 host_heat_micro;
	__u32 phi_micro;
	__u32 entropy_floor_submicro;
};

struct kilroy_field_fcc {
	__u32 time_scale_micro;
	__u32 thermo_alpha_micro;
	__u32 wave_speed_micro;
	__u32 gate_fidelity_micro;
	__u32 entropy_floor_submicro;
	__u32 inject_strength_micro;
	__u32 propalactic_micro;
	__u32 field_coupling_micro;
	__u32 tesla_bias_micro;
};

struct kilroy_field_slots {
	__u64 time_genesis_ns;
	__u64 time_sealed_ns;
	__u64 time_entropy;
	__u8  time_sealed;
	__u64 mem_total_pages;
	__u64 mem_allocated_pages;
	__u64 mem_usable_pages;
	__u64 mem_mmap_ops;
	__u32 thermo_budget_micro;
	__u32 fcc_guard_scale_micro;
	__u32 context_magic;
	__u32 context_pid;
	__u64 context_generation;
	__u64 context_seal_hash;
	__u32 layout_version;
	__u32 cpu_fabric_ops;
	__u32 ram_pressure_submicro;
};

struct kilroy_field_cache {
	__u32 shed_count;
	__u32 bypass_ops;
	__u32 slab_drops;
	__u32 lru_drains;
	__u32 retention_micro;
	__u32 pressure_micro;
};

struct kilroy_field_direct {
	__u64 direct_maps;
	__u64 direct_bytes;
	__u64 cached_maps;
	__u64 coherence_ops;
	__u32 direct_ratio_micro;
	__u32 pad;
};

struct kilroy_field_power {
	__u8  tier;
	__u8  auto_mode;
	__u16 pad;
	__u32 max_khz;
	__u32 fcc_guard_scale_micro;
	__u32 ram_pressure_submicro;
	__u32 cpu_burst_ready;
};

struct kilroy_field_flow {
	__u32 momentum_submicro;
	__u32 tesla_bias_micro;
	__u32 forward_resistance_micro;
	__u32 reverse_resistance_micro;
};

struct kilroy_field_gpu {
	__u32 gpu_count;
	__u32 active_cards;
	__u32 fcc_coupling_micro;
	__u32 tesla_bias_micro;
};

struct kilroy_field_state {
	__u32 magic;
	__u32 active;
	__u32 pid;
	__u64 syscall_count;
	__u64 fabric_scheduled;
	__u64 host_passthrough;
	struct kilroy_field_thermo thermo;
	struct kilroy_field_fcc fcc;
	struct kilroy_field_cpu cpu;
	struct kilroy_field_ram ram;
	char abi[32];
	char codename[16];
};

#define rtx_field_thermo	kilroy_field_thermo
#define rtx_field_fcc		kilroy_field_fcc
#define rtx_field_slots		kilroy_field_slots
#define rtx_field_state		kilroy_field_state

#define KILROY_IOC_MAGIC	'K'
#define KILROY_IOC_ACTIVATE	_IO(KILROY_IOC_MAGIC, 1)
#define KILROY_IOC_DEACTIVATE	_IO(KILROY_IOC_MAGIC, 2)
#define KILROY_IOC_GET_ABI	_IOR(KILROY_IOC_MAGIC, 3, char[32])
#define KILROY_IOC_GET_STATE	_IOR(KILROY_IOC_MAGIC, 4, struct kilroy_field_state)
#define KILROY_IOC_SET_THERMO	_IOW(KILROY_IOC_MAGIC, 5, struct kilroy_field_thermo)
#define KILROY_IOC_SET_FCC	_IOW(KILROY_IOC_MAGIC, 6, struct kilroy_field_fcc)
#define KILROY_IOC_GET_SLOTS	_IOR(KILROY_IOC_MAGIC, 7, struct kilroy_field_slots)
#define KILROY_IOC_GET_POWER	_IOR(KILROY_IOC_MAGIC, 8, struct kilroy_field_power)
#define KILROY_IOC_GET_CPU	_IOR(KILROY_IOC_MAGIC, 9, struct kilroy_field_cpu)
#define KILROY_IOC_GET_RAM	_IOR(KILROY_IOC_MAGIC, 10, struct kilroy_field_ram)
#define KILROY_IOC_GET_CACHE	_IOR(KILROY_IOC_MAGIC, 11, struct kilroy_field_cache)
#define KILROY_IOC_GET_DIRECT	_IOR(KILROY_IOC_MAGIC, 12, struct kilroy_field_direct)
#define KILROY_IOC_GET_FLOW	_IOR(KILROY_IOC_MAGIC, 13, struct kilroy_field_flow)
#define KILROY_IOC_GET_GPU	_IOR(KILROY_IOC_MAGIC, 14, struct kilroy_field_gpu)

#define RTX_IOC_MAGIC		KILROY_IOC_MAGIC
#define RTX_IOC_ACTIVATE	KILROY_IOC_ACTIVATE
#define RTX_IOC_DEACTIVATE	KILROY_IOC_DEACTIVATE
#define RTX_IOC_GET_ABI		KILROY_IOC_GET_ABI
#define RTX_IOC_GET_STATE	KILROY_IOC_GET_STATE
#define RTX_IOC_SET_THERMO	KILROY_IOC_SET_THERMO
#define RTX_IOC_SET_FCC		KILROY_IOC_SET_FCC
#define RTX_IOC_GET_SLOTS	KILROY_IOC_GET_SLOTS

#endif /* _UAPI_KILROY_RTX_FIELD_H */