# Grok16 Belt 2.0 profile — chunked redata belt, wave-massive, single-location reads
if(NOT GROK16_PROFILE STREQUAL "belt_2_0")
  set(GROK16_PROFILE "belt_2_0" CACHE STRING "Grok16 build profile" FORCE)
endif()
set(GROK16_CXX_STD "gnu++26" CACHE STRING "Grok16 C++ standard" FORCE)
add_compile_definitions(
  GROK16_BELT_2_0=1
  GROK16_DISTRO_2_0=1
  GROK16_PROFILE_FIELD_OPT=1
  G16_FIELD_SPEED=1
  FIELD_BELT_DIE=67108864
  FIELD_DATA_BUS=64
  FIELD_REDATA_CHUNK=8192
  FIELD_BELT_WAVE_MASSIVE=1
  FIELD_SINGLE_LOCATION_READ=1
  FIELD_ENTROPY_DISPATCH=1
  FIELD_X86_DIE=1
  FIELD_WAVE_PHASE=1
  HOSTESS_TRUTH_FLOOR=58
)
add_compile_options(
  $<$<COMPILE_LANGUAGE:CXX>:-std=gnu++26>
  $<$<COMPILE_LANGUAGE:C>:-std=gnu17>
  -O3 -march=native -mtune=native
  -fstack-protector-strong -fstack-clash-protection -fcf-protection=full
  -ftree-vectorize -fvect-cost-model=unlimited
  -funroll-loops -finline-functions -fomit-frame-pointer
  -ffast-math -fno-trapping-math -fopenmp -fopenmp-simd -fipa-pta
  -D_FORTIFY_SOURCE=3 -fPIE
)
add_link_options(-flto=thin -fopenmp -Wl,-z,relro -Wl,-z,now -Wl,-z,noexecstack -pie)