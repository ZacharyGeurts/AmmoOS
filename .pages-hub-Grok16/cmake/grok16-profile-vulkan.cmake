# Grok16 Vulkan/RTX-oriented CPU kernel profile (AMOURANTHRTX-style prep)
# G14 — SPIR-V / shader compile lane only; Queen owns GPU; no libvulkan link
if(NOT GROK16_PROFILE STREQUAL "vulkan_rtx")
  set(GROK16_PROFILE "vulkan_rtx" CACHE STRING "Grok16 build profile" FORCE)
endif()
set(GROK16_CXX_STD "gnu++26" CACHE STRING "Grok16 C++ standard" FORCE)
set(GROK16_SPIRV_ONLY 1 CACHE BOOL "Emit .spv/.comp only — no libvulkan" FORCE)
set(GROK16_NO_LIBVULKAN 1 CACHE BOOL "Linker rejects libvulkan symbols" FORCE)
add_compile_definitions(
  GROK16_PROFILE_VULKAN=1
  GROK16_SPIRV_ONLY=1
  GROK16_NO_LIBVULKAN=1
  FIELD_X86_DIE=1
)
add_compile_options(
  -std=gnu++26 -O3 -march=native
  -msse4.2 -mavx2 -mfma -ffast-math -funroll-loops
)
# Thin LTO for CPU prep kernels only — shader objects (.spv) bypass host link
add_link_options(-flto=thin)
# Reject accidental Vulkan host link (G14)
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_C_COMPILER_ID STREQUAL "GNU")
  add_link_options(-Wl,--as-needed)
endif()