# Grok16 Field compute profile — FieldX86 / CANVAS CPU kernels
if(NOT GROK16_PROFILE STREQUAL "field_compute")
  set(GROK16_PROFILE "field_compute" CACHE STRING "Grok16 build profile" FORCE)
endif()
set(GROK16_CXX_STD "gnu++26" CACHE STRING "Grok16 C++ standard" FORCE)
add_compile_definitions(GROK16_PROFILE_FIELD=1 FIELD_X86_DIE=1 FIELD_ENTROPY_DISPATCH=1)
add_compile_options(
  -std=gnu++26 -O3 -march=native
  -fopenmp-simd -fvect-cost-model=unlimited -fno-trapping-math
)
add_link_options(-fopenmp)