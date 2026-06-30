# KILROY 1.0 — hardware auto-detection for kernel fragment generation

function(kilroy_detect_hardware)
    set(_cpu_vendor "UNKNOWN")
    set(_cpu_model "unknown")
    set(_cpu_cores 1)
    set(_cpu_flags "")
    set(_gpu_vendor "NONE")
    set(_gpu_model "none")
    set(_mem_mb 0)
    set(_nvme 0)
    set(_has_avx512 0)
    set(_has_aes 0)

    if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
        if(EXISTS "/proc/cpuinfo")
            file(READ "/proc/cpuinfo" _cpuinfo)
            if(_cpuinfo MATCHES "vendor_id[ \t]+: GenuineIntel")
                set(_cpu_vendor "INTEL")
            elseif(_cpuinfo MATCHES "vendor_id[ \t]+: AuthenticAMD")
                set(_cpu_vendor "AMD")
            elseif(_cpuinfo MATCHES "vendor_id[ \t]+: HygonGenuine")
                set(_cpu_vendor "AMD")
            endif()
            if(_cpuinfo MATCHES "model name[ \t]+: ([^\n]+)")
                set(_cpu_model "${CMAKE_MATCH_1}")
            endif()
            if(_cpuinfo MATCHES "flags[^\n]* avx512")
                set(_has_avx512 1)
            endif()
            if(_cpuinfo MATCHES "flags[^\n]* aes")
                set(_has_aes 1)
            endif()
        endif()
        if(EXISTS "/proc/meminfo")
            file(READ "/proc/meminfo" _meminfo)
            if(_meminfo MATCHES "MemTotal:[ \t]+([0-9]+) kB")
                math(EXPR _mem_mb "${CMAKE_MATCH_1} / 1024")
            endif()
        endif()
        execute_process(COMMAND nproc OUTPUT_VARIABLE _nc OUTPUT_STRIP_TRAILING_WHITESPACE ERROR_QUIET)
        if(_nc)
            set(_cpu_cores "${_nc}")
        endif()
        execute_process(
            COMMAND bash -c "lspci -nn 2>/dev/null | grep -iE 'vga|3d|display' | head -1"
            OUTPUT_VARIABLE _gpu_line OUTPUT_STRIP_TRAILING_WHITESPACE ERROR_QUIET
        )
        if(_gpu_line MATCHES "NVIDIA|GeForce|RTX|GTX")
            set(_gpu_vendor "NVIDIA")
            set(_gpu_model "${_gpu_line}")
        elseif(_gpu_line MATCHES "AMD/ATI|Radeon|AMD Radeon")
            set(_gpu_vendor "AMD")
            set(_gpu_model "${_gpu_line}")
        elseif(_gpu_line MATCHES "Intel|UHD|Iris|Arc")
            set(_gpu_vendor "INTEL")
            set(_gpu_model "${_gpu_line}")
        endif()
        execute_process(
            COMMAND bash -c "lspci -nn 2>/dev/null | grep -i nvme | head -1"
            OUTPUT_VARIABLE _nvme_line OUTPUT_STRIP_TRAILING_WHITESPACE ERROR_QUIET
        )
        if(_nvme_line)
            set(_nvme 1)
        endif()
    endif()

    if(KILROY_CPU_VENDOR STREQUAL "AUTO")
        set(KILROY_CPU_VENDOR_DETECTED "${_cpu_vendor}" PARENT_SCOPE)
    else()
        set(KILROY_CPU_VENDOR_DETECTED "${KILROY_CPU_VENDOR}" PARENT_SCOPE)
    endif()
    if(KILROY_GPU_VENDOR STREQUAL "AUTO")
        set(KILROY_GPU_VENDOR_DETECTED "${_gpu_vendor}" PARENT_SCOPE)
    else()
        set(KILROY_GPU_VENDOR_DETECTED "${KILROY_GPU_VENDOR}" PARENT_SCOPE)
    endif()

    set(KILROY_DETECT_CPU_VENDOR "${_cpu_vendor}" PARENT_SCOPE)
    set(KILROY_DETECT_CPU_MODEL "${_cpu_model}" PARENT_SCOPE)
    set(KILROY_DETECT_CPU_CORES "${_cpu_cores}" PARENT_SCOPE)
    set(KILROY_DETECT_CPU_AVX512 "${_has_avx512}" PARENT_SCOPE)
    set(KILROY_DETECT_CPU_AES "${_has_aes}" PARENT_SCOPE)
    set(KILROY_DETECT_GPU_VENDOR "${_gpu_vendor}" PARENT_SCOPE)
    set(KILROY_DETECT_GPU_MODEL "${_gpu_model}" PARENT_SCOPE)
    set(KILROY_DETECT_MEM_MB "${_mem_mb}" PARENT_SCOPE)
    set(KILROY_DETECT_NVME "${_nvme}" PARENT_SCOPE)
endfunction()

function(kilroy_write_detection_report out_file)
    file(WRITE "${out_file}"
"KILROY 1.0 Hardware Detection Report
=====================================
CPU vendor (raw):     ${KILROY_DETECT_CPU_VENDOR}
CPU vendor (build):   ${KILROY_CPU_VENDOR_DETECTED}
CPU model:            ${KILROY_DETECT_CPU_MODEL}
CPU cores:            ${KILROY_DETECT_CPU_CORES}
AVX-512:              ${KILROY_DETECT_CPU_AVX512}
AES-NI:               ${KILROY_DETECT_CPU_AES}
GPU vendor (raw):     ${KILROY_DETECT_GPU_VENDOR}
GPU vendor (build):   ${KILROY_GPU_VENDOR_DETECTED}
GPU device:           ${KILROY_DETECT_GPU_MODEL}
RAM (MB):             ${KILROY_DETECT_MEM_MB}
NVMe present:         ${KILROY_DETECT_NVME}
")
endfunction()