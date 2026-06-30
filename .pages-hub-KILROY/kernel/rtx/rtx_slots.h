/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _RTX_SLOTS_H
#define _RTX_SLOTS_H

#include <linux/types.h>
#include <uapi/kilroy/rtx_field.h>

#define RTX_SLOT_TIME		0
#define RTX_SLOT_MEMORY		1
#define RTX_SLOT_THERMO		2
#define RTX_SLOT_CONTEXT	3

#define RTX_ENTROPY_XOR_MASK	0x9E37AF18C64D8A17ULL
#define RTX_ZMM_ROWS		32
#define RTX_ZMM_COLS		32
#define RTX_MEMORY_SAFETY_MB	256

struct rtx_slot_time {
	u64 genesis_ns;
	u64 sealed_ns;
	u64 entropy;
	u64 entropy_check;
	u8  sealed;
	u8  pad[7];
};

struct rtx_slot_memory {
	u32 zmm[RTX_ZMM_ROWS][RTX_ZMM_COLS];
	u64 total_pages;
	u64 allocated_pages;
	u64 safety_margin_pages;
	u64 usable_pages;
	u64 mmap_ops;
};

struct rtx_slot_thermo {
	struct kilroy_field_thermo acct;
	u32 budget_micro;
	u32 fcc_guard_scale_micro;
};

struct rtx_slot_context {
	u32 magic;
	u32 pid;
	u64 syscall_generation;
	u64 seal_hash;
	u32 layout_version;
	u32 pad;
};

struct rtx_four_slots {
	struct rtx_slot_time time;
	struct rtx_slot_memory memory;
	struct rtx_slot_thermo thermo;
	struct rtx_slot_context context;
};

#ifdef CONFIG_RTX_FIELD_DIE

struct rtx_four_slots *rtx_slots(void);
void rtx_slots_init(void);
void rtx_slots_seal_time(void);
int rtx_slots_verify(void);
void rtx_slots_account_mmap(u64 len);
void rtx_slots_account_munmap(u64 len);
void rtx_slots_account_brk(u64 new_brk);
void rtx_zmm_touch(u32 row, u32 col, u32 delta);
int rtx_slots_tamper_action(void);
void rtx_slots_context_tick(u32 nr);
bool rtx_is_memory_syscall(u32 nr);

#else

static inline struct rtx_four_slots *rtx_slots(void) { return NULL; }
static inline void rtx_slots_init(void) {}
static inline void rtx_slots_seal_time(void) {}
static inline int rtx_slots_verify(void) { return 0; }
static inline void rtx_slots_account_mmap(u64 len) {}
static inline void rtx_slots_account_munmap(u64 len) {}
static inline void rtx_slots_account_brk(u64 new_brk) {}
static inline void rtx_zmm_touch(u32 row, u32 col, u32 delta) {}
static inline int rtx_slots_tamper_action(void) { return 0; }
static inline void rtx_slots_context_tick(u32 nr) {}
static inline bool rtx_is_memory_syscall(u32 nr) { return false; }

#endif

#endif /* _RTX_SLOTS_H */