# CHIPS emulator silicon — Grok16 field_opt compile flags (canonical, was Queen/cmake)

if(NOT DEFINED G16_PREFIX)
  if(DEFINED ENV{G16_PREFIX} AND NOT "$ENV{G16_PREFIX}" STREQUAL "")
    set(G16_PREFIX "$ENV{G16_PREFIX}")
  elseif(DEFINED GROK16_PREFIX)
    set(G16_PREFIX "${GROK16_PREFIX}")
  endif()
endif()

set(CHIPS_G16_PROFILE "field_opt" CACHE STRING "Grok16 profile for CHIPS hot paths")
set(CHIPS_G16_CXX_FLAGS
  -O3 -march=native -flto -ffast-math
  -DGROK16_PROFILE_FIELD_OPT=1
  -DFIELD_ENTROPY_DISPATCH=1
  -DCHIPS_G16_ACCURATE=1
)

function(queen_chips_apply_g16 target)
  if(TARGET ${target})
    target_compile_options(${target} PRIVATE ${CHIPS_G16_CXX_FLAGS})
  endif()
endfunction()

# Queen-browser build disables LTO globally — apply field_opt defines without -flto.
function(queen_chips_apply_g16_nolto target)
  if(TARGET ${target})
    target_compile_definitions(${target} PRIVATE
      GROK16_PROFILE_FIELD_OPT=1
      FIELD_ENTROPY_DISPATCH=1
      CHIPS_G16_ACCURATE=1
    )
    target_compile_options(${target} PRIVATE
      -O3 -ffast-math -march=native
    )
  endif()
endfunction()