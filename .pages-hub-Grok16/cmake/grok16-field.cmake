# Grok16 Field CMake — canonical project bootstrap (g16 owns configure + compile flags)
# Use: -DCMAKE_TOOLCHAIN_FILE=$GROK16_ROOT/cmake/grok16-toolchain.cmake
#      -DCMAKE_PROJECT_INCLUDE=$GROK16_ROOT/cmake/grok16-field.cmake
#
# Optional env/cache:
#   GROK16_FIELD_PROFILE = field_opt | field_physics | ai | field_compute | vulkan_rtx | queen_rtx

if(NOT DEFINED GROK16_ROOT)
  if(DEFINED ENV{GROK16_ROOT} AND NOT "$ENV{GROK16_ROOT}" STREQUAL "")
    set(GROK16_ROOT "$ENV{GROK16_ROOT}")
  else()
    get_filename_component(GROK16_ROOT "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)
  endif()
endif()
set(GROK16_ROOT "${GROK16_ROOT}" CACHE PATH "Grok16 install root")

if(NOT DEFINED GROK16_FIELD_PROFILE)
  if(DEFINED ENV{GROK16_FIELD_PROFILE} AND NOT "$ENV{GROK16_FIELD_PROFILE}" STREQUAL "")
    set(GROK16_FIELD_PROFILE "$ENV{GROK16_FIELD_PROFILE}")
  else()
    set(GROK16_FIELD_PROFILE "belt_2_0")
  endif()
endif()
set(GROK16_FIELD_PROFILE "${GROK16_FIELD_PROFILE}" CACHE STRING "Grok16 field cmake profile")

if(GROK16_FIELD_PROFILE STREQUAL "belt_2_0")
  set(GROK16_PROFILE "belt_2_0" CACHE STRING "Grok16 belt profile" FORCE)
endif()

if(EXISTS "${GROK16_ROOT}/cmake/grok16-rtx-gate.cmake")
  include("${GROK16_ROOT}/cmake/grok16-rtx-gate.cmake")
endif()

set(_GROK16_PROFILE_CMAKE "${GROK16_ROOT}/cmake/grok16-profile-${GROK16_FIELD_PROFILE}.cmake")
if(GROK16_FIELD_PROFILE STREQUAL "field_opt")
  set(_GROK16_PROFILE_CMAKE "${GROK16_ROOT}/cmake/grok16-profile-field-opt.cmake")
elseif(GROK16_FIELD_PROFILE STREQUAL "field_compute")
  set(_GROK16_PROFILE_CMAKE "${GROK16_ROOT}/cmake/grok16-profile-field.cmake")
elseif(GROK16_FIELD_PROFILE STREQUAL "vulkan_rtx")
  set(_GROK16_PROFILE_CMAKE "${GROK16_ROOT}/cmake/grok16-profile-vulkan.cmake")
elseif(GROK16_FIELD_PROFILE STREQUAL "ai")
  set(_GROK16_PROFILE_CMAKE "${GROK16_ROOT}/cmake/grok16-profile-ai.cmake")
elseif(GROK16_FIELD_PROFILE STREQUAL "queen_rtx")
  set(_GROK16_PROFILE_CMAKE "${GROK16_ROOT}/cmake/grok16-profile-field-opt.cmake")
elseif(GROK16_FIELD_PROFILE STREQUAL "field_physics")
  set(_GROK16_PROFILE_CMAKE "${GROK16_ROOT}/cmake/grok16-profile-field-physics.cmake")
elseif(GROK16_FIELD_PROFILE STREQUAL "belt_2_0")
  set(_GROK16_PROFILE_CMAKE "${GROK16_ROOT}/cmake/grok16-profile-belt-2.cmake")
elseif(GROK16_FIELD_PROFILE STREQUAL "belt_1_0")
  set(_GROK16_PROFILE_CMAKE "${GROK16_ROOT}/cmake/grok16-profile-belt.cmake")
endif()

if(EXISTS "${_GROK16_PROFILE_CMAKE}")
  include("${_GROK16_PROFILE_CMAKE}")
else()
  message(WARNING "Grok16 field profile missing: ${_GROK16_PROFILE_CMAKE}")
endif()

if(EXISTS "${GROK16_ROOT}/cmake/g16-field-mandate.cmake")
  include("${GROK16_ROOT}/cmake/g16-field-mandate.cmake")
endif()

if(EXISTS "${GROK16_ROOT}/cmake/g16-linker-mandate.cmake")
  include("${GROK16_ROOT}/cmake/g16-linker-mandate.cmake")
endif()

if(EXISTS "${GROK16_ROOT}/cmake/grok16-chips-field-opt.cmake")
  include("${GROK16_ROOT}/cmake/grok16-chips-field-opt.cmake")
endif()

if(GROK16_FIELD_PROFILE STREQUAL "queen_rtx" AND EXISTS "${GROK16_ROOT}/cmake/grok16-field-queen-rtx.cmake")
  include("${GROK16_ROOT}/cmake/grok16-field-queen-rtx.cmake")
endif()

if(EXISTS "${GROK16_ROOT}/cmake/grok16-thermal-guard.cmake")
  include("${GROK16_ROOT}/cmake/grok16-thermal-guard.cmake")
endif()

if(EXISTS "${GROK16_ROOT}/data/g16-field-sanity-doctrine.json")
  set(G16_FIELD_SANITY_DOCTRINE "${GROK16_ROOT}/data/g16-field-sanity-doctrine.json" CACHE FILEPATH "Grok16 integral field sanity doctrine")
endif()
if(EXISTS "${GROK16_ROOT}/data/g16-ironclad-meld.json")
  set(G16_IRONCLAD_MELD_MANIFEST "${GROK16_ROOT}/data/g16-ironclad-meld.json" CACHE FILEPATH "Ironclad meld manifest for G16")
endif()

# Project-wide Ironclad + field sanity — every target in a G16 field build inherits the meld
if(NOT G16_IRONCLAD_SANITY_DISABLED)
  add_compile_definitions(
    G16_FIELD_SANITY=1
    G16_FIELD_SANITY_INTEGRAL=1
    G16_IRONCLAD_MELD=1
    G16_IRONCLAD_MELD_CITATION="${G16_IRONCLAD_MELD_CITATION}"
    _FORTIFY_SOURCE=3
    G16_FIELD_MANDATE=1
  )
  add_compile_options(
    -fstack-protector-strong
    -fstack-clash-protection
    -fcf-protection=full
    -fno-strict-aliasing
    -Wformat -Wformat-security
    -Werror=format-security
    -fPIE
  )
  if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_C_COMPILER_ID STREQUAL "GNU")
    add_link_options(-Wl,-z,relro -Wl,-z,now -Wl,-z,noexecstack -pie)
  endif()
endif()

message(STATUS "Grok16 field cmake — root=${GROK16_ROOT} profile=${GROK16_FIELD_PROFILE} rtx_gate=${G16_RTX_GATE_SATISFIED} ironclad_sanity=1")