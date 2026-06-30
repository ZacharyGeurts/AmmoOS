cmake_minimum_required(VERSION 3.16)
project(KILROY VERSION 1.0.0 LANGUAGES C CXX)

set(KILROY_ROOT "${CMAKE_SOURCE_DIR}")
set(KILROY_COMPAT_SRC "${KILROY_COMPAT_SRC}" CACHE PATH
    "Linux-compatible compat substrate (default: ../compat/linux-7.1.1)")
if(NOT KILROY_COMPAT_SRC)
    if(EXISTS "${KILROY_ROOT}/../compat/linux-7.1.1/Makefile")
        set(KILROY_COMPAT_SRC "${KILROY_ROOT}/../compat/linux-7.1.1")
    else()
        set(KILROY_COMPAT_SRC "${KILROY_ROOT}/../linux-kernel/linux-7.1.1")
    endif()
endif()
set(KILROY_KERNEL_SRC "${KILROY_COMPAT_SRC}" CACHE PATH "" FORCE)
set(KILROY_BUILD_DIR "${CMAKE_BINARY_DIR}")
set(KILROY_OUT_DIR "${KILROY_ROOT}/build")
set(KILROY_JOBS "$ENV{KILROY_JOBS}" CACHE STRING "Parallel make jobs (empty=auto)")

# ── Menu: CPU / GPU (AUTO detects host) ─────────────────────────────────────
set(KILROY_CPU_VENDOR "AUTO" CACHE STRING "CPU vendor profile: AUTO|INTEL|AMD")
set_property(CACHE KILROY_CPU_VENDOR PROPERTY STRINGS AUTO INTEL AMD)
set(KILROY_GPU_VENDOR "AUTO" CACHE STRING "GPU driver profile: AUTO|NVIDIA|AMD|INTEL|NONE")
set_property(CACHE KILROY_GPU_VENDOR PROPERTY STRINGS AUTO NVIDIA AMD INTEL NONE)

# ── Field Die core ────────────────────────────────────────────────────────────
option(KILROY_ENABLE_FIELD_DIE "Native Field Die (Phi/Thermo/Flow)" ON)
option(KILROY_ENABLE_ASM_GATE "ASM fabric classify + inline thermo debit" ON)
option(KILROY_ENABLE_4SLOT_SECURITY "4-slot tamper verify" ON)
option(KILROY_ENABLE_FCC_GUARD "FCC harmonics whole-kernel guard" ON)
option(KILROY_ENABLE_FCC_SYSCALL "Amortized per-syscall FCC touch" ON)
option(KILROY_ENABLE_POWER_TIERS "DVFS cryo/eco/nom/burst tiers" ON)

# ── Physics enhancements (from research / Grok backlog) ─────────────────────
option(KILROY_ENABLE_FLOW_SLOT "FLOW slot — Tesla valve momentum tracking" ON)
option(KILROY_ENABLE_THERMO_IDLE_CREDIT "Idle CPU thermo credit (reduces EAGAIN stalls)" ON)
option(KILROY_ENABLE_ZMM_HOTPATH "ZMM1024 touch on mmap hot path" ON)
option(KILROY_ENABLE_TESLA_BIAS "Tesla forward/reverse flow bias coupling" ON)
option(KILROY_ENABLE_NEXUS_GUARD "NEXUS-inspired behavioral guard (amortized)" ON)
option(KILROY_ENABLE_UTS_NAME "uname sysname KILROY" ON)
option(KILROY_ENABLE_CACHE_SLOT "CACHE field — shed legacy retention" ON)
option(KILROY_ENABLE_DIRECT_SLOT "DIRECT field — map coherence telemetry" ON)
option(KILROY_ENABLE_CHARDEV "ioctl ABI /dev/kilroy_field" ON)
option(KILROY_ENABLE_DRM_FCC "GPU FCC mirror via PCI display" ON)
option(KILROY_ENABLE_NOCACHE_FRAG "nocache config (THP off, SLUB_TINY)" OFF)

# ── Hidden / performance enhancements ───────────────────────────────────────
option(KILROY_ENABLE_PREEMPT "CONFIG_PREEMPT — lower syscall latency" ON)
option(KILROY_ENABLE_HZ_1000 "1000Hz tick — smoother DVFS/thermo" ON)
option(KILROY_ENABLE_NO_HZ_FULL "NO_HZ_FULL on idle CPUs (4+ cores)" ON)
option(KILROY_ENABLE_IO_URING "io_uring async I/O" ON)
option(KILROY_ENABLE_BBR "TCP BBR congestion control" ON)
option(KILROY_ENABLE_ZSTD "ZSTD kernel compression" ON)
option(KILROY_ENABLE_TRANSPARENT_HUGEPAGE "THP for large guest RAM" ON)

option(KILROY_BUILD_BZIMAGE "Build full bzImage (not just kernel/rtx)" ON)
option(KILROY_SYNC_DELTA "Sync SG/KILROY delta into kernel tree before build" ON)
option(KILROY_RUN_TESTS "Run test suite after build" ON)

set(KILROY_FCC_TOUCH_INTERVAL "32" CACHE STRING "FCC full guard every N syscalls (power of 2 mask)")

include("${KILROY_ROOT}/cmake/KILROYDetect.cmake")
include("${KILROY_ROOT}/cmake/KILROYFragments.cmake")

kilroy_detect_hardware()

message(STATUS "")
message(STATUS "=== KILROY ${PROJECT_VERSION} Field OS (Linux-compatible) CMake ===")
message(STATUS "  CPU detected: ${KILROY_DETECT_CPU_VENDOR} (${KILROY_DETECT_CPU_CORES} cores)")
message(STATUS "  CPU profile:  ${KILROY_CPU_VENDOR_DETECTED}")
message(STATUS "  GPU detected: ${KILROY_DETECT_GPU_VENDOR}")
message(STATUS "  GPU profile:  ${KILROY_GPU_VENDOR_DETECTED}")
message(STATUS "  RAM:          ${KILROY_DETECT_MEM_MB} MB")
message(STATUS "  Compat substrate: ${KILROY_COMPAT_SRC}")
message(STATUS "  Enhancements: FLOW=${KILROY_ENABLE_FLOW_SLOT} IDLE_CREDIT=${KILROY_ENABLE_THERMO_IDLE_CREDIT}")
message(STATUS "                ZMM=${KILROY_ENABLE_ZMM_HOTPATH} TESLA=${KILROY_ENABLE_TESLA_BIAS}")
message(STATUS "                PREEMPT=${KILROY_ENABLE_PREEMPT} HZ_1000=${KILROY_ENABLE_HZ_1000}")
message(STATUS "")

# Sync delta sources into kernel tree
set(_SYNC_STAMP "${KILROY_BUILD_DIR}/kilroy-sync.stamp")
add_custom_command(
    OUTPUT "${_SYNC_STAMP}"
    COMMAND "${CMAKE_COMMAND}" -E echo "Overlaying KILROY Field -> ${KILROY_COMPAT_SRC}"
    COMMAND "${KILROY_ROOT}/scripts/kilroy-become-substrate.sh"
    COMMAND "${CMAKE_COMMAND}" -E touch "${_SYNC_STAMP}"
    COMMENT "KILROY sync delta"
    VERBATIM
)

# Generate config fragments
set(_AUTO_FRAG "${KILROY_BUILD_DIR}/kilroy-auto.fragment")
set(_OPT_FRAG "${KILROY_BUILD_DIR}/kilroy-options.fragment")
set(_DETECT_REPORT "${KILROY_BUILD_DIR}/kilroy-detect.txt")
kilroy_write_detection_report("${_DETECT_REPORT}")
kilroy_generate_fragments("${_AUTO_FRAG}" "${_OPT_FRAG}")

configure_file(
    "${KILROY_ROOT}/cmake/kilroy_config.h.in"
    "${KILROY_BUILD_DIR}/include/kilroy_config.h"
    @ONLY
)

# Kernel configure
set(_KERNEL_CONFIG_STAMP "${KILROY_BUILD_DIR}/.config.stamp")
add_custom_command(
    OUTPUT "${_KERNEL_CONFIG_STAMP}"
    DEPENDS "${_SYNC_STAMP}" "${_AUTO_FRAG}" "${_OPT_FRAG}"
    COMMAND ${CMAKE_COMMAND} -E env KSRC="${KILROY_KERNEL_SRC}"
        "${KILROY_ROOT}/scripts/kilroy-kernel-config.sh"
        "${KILROY_KERNEL_SRC}" "${_AUTO_FRAG}" "${_OPT_FRAG}"
    COMMAND ${CMAKE_COMMAND} -E touch "${_KERNEL_CONFIG_STAMP}"
    WORKING_DIRECTORY "${KILROY_KERNEL_SRC}"
    COMMENT "KILROY Field OS substrate configure"
    VERBATIM
)

# Determine jobs
if(NOT KILROY_JOBS)
    include(ProcessorCount)
    ProcessorCount(_nc)
    if(NOT _nc)
        set(_nc 4)
    endif()
    set(KILROY_JOBS "${_nc}")
endif()

set(_MAKE_TARGETS "kernel/rtx/")
if(KILROY_BUILD_BZIMAGE)
    list(APPEND _MAKE_TARGETS "bzImage")
endif()

add_custom_target(kilroy_detect ALL
    COMMAND ${CMAKE_COMMAND} -E cat "${_DETECT_REPORT}"
    DEPENDS "${_DETECT_REPORT}"
    COMMENT "KILROY hardware detection report"
)

add_custom_target(kilroy_config ALL
    DEPENDS "${_KERNEL_CONFIG_STAMP}"
    COMMENT "KILROY Field OS configuration"
)

add_custom_command(
    OUTPUT "${KILROY_OUT_DIR}/bzImage"
    DEPENDS "${_KERNEL_CONFIG_STAMP}"
    COMMAND ${CMAKE_COMMAND} -E make_directory "${KILROY_OUT_DIR}"
    COMMAND make -j${KILROY_JOBS} ${_MAKE_TARGETS}
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "${KILROY_KERNEL_SRC}/arch/x86/boot/bzImage" "${KILROY_OUT_DIR}/bzImage"
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "${KILROY_KERNEL_SRC}/.config" "${KILROY_OUT_DIR}/config"
    WORKING_DIRECTORY "${KILROY_KERNEL_SRC}"
    COMMENT "Building KILROY Field OS (${_MAKE_TARGETS})"
    VERBATIM
)

add_custom_target(kilroy_kernel ALL
    DEPENDS "${KILROY_OUT_DIR}/bzImage"
)

if(KILROY_RUN_TESTS)
    add_custom_target(kilroy_test
        COMMAND ${CMAKE_COMMAND} -E env
            KSRC="${KILROY_KERNEL_SRC}" FULL_BUILD=0
            "${KILROY_ROOT}/scripts/test-all.sh"
        WORKING_DIRECTORY "${KILROY_ROOT}"
        COMMENT "KILROY test suite"
    )
    add_dependencies(kilroy_kernel kilroy_test)
endif()

add_custom_target(kilroy_benchmark
    COMMAND "${KILROY_ROOT}/scripts/kilroy-benchmark.sh"
        "${KILROY_BUILD_DIR}/benchmark.json"
    COMMENT "KILROY performance benchmark"
)

# User-facing summary target
add_custom_target(kilroy_report
    COMMAND "${KILROY_ROOT}/scripts/kilroy-report.sh"
        "${KILROY_BUILD_DIR}/benchmark.json"
    DEPENDS kilroy_benchmark
    COMMENT "KILROY performance report"
)