# Grok16 single-fabric link profile — belt_2_0 + ammoos + vulkan_rtx one graph (G13)
# Profile switch at link time; compile units tagged per consumer lane
if(NOT GROK16_PROFILE STREQUAL "single_fabric")
  set(GROK16_PROFILE "single_fabric" CACHE STRING "Grok16 build profile" FORCE)
endif()
set(GROK16_CXX_STD "gnu++26" CACHE STRING "Grok16 C++ standard" FORCE)
set(GROK16_C_STD "gnu17" CACHE STRING "Grok16 C standard" FORCE)

include("${CMAKE_CURRENT_LIST_DIR}/grok16-profile-belt-2.cmake")

add_compile_definitions(
  G16_SINGLE_FABRIC=1
  GROK16_SINGLE_FABRIC_LINK=1
  GROK16_PROFILE_AMMOOS=1
  GROK16_PROFILE_VULKAN=1
  G16_IRONCLAD_MELD=1
)
# Link-time profile lanes — ninja selects consumer without full recompile
set(GROK16_SINGLE_FABRIC_LANES "belt_2_0;ammoos;vulkan_rtx" CACHE STRING "Single-fabric link lanes" FORCE)