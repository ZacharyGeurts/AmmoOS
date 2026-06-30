# Grok16 Field-Opt profile — entropy/oracle hot paths, wave dispatch, FieldX86 throughput
if(NOT GROK16_PROFILE STREQUAL "field_opt")
  set(GROK16_PROFILE "field_opt" CACHE STRING "Grok16 build profile" FORCE)
endif()
set(GROK16_CXX_STD "gnu++26" CACHE STRING "Grok16 C++ standard" FORCE)
add_compile_definitions(
  GROK16_PROFILE_FIELD_OPT=1
  G16_FIELD_SPEED=1
  FIELD_ENTROPY_DISPATCH=1
  FIELD_X86_DIE=1
  FIELD_WAVE_PHASE=1
)
add_compile_options(
  $<$<COMPILE_LANGUAGE:CXX>:-std=gnu++26>
  $<$<COMPILE_LANGUAGE:C>:-std=gnu17>
  -O3 -march=native -mtune=native
  -ftree-vectorize -fvect-cost-model=unlimited
  -funroll-loops -finline-functions -fomit-frame-pointer
  -ffast-math -fno-trapping-math -fopenmp-simd
)
add_link_options(-flto)