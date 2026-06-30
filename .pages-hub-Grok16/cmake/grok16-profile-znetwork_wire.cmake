# Grok16 znetwork_wire profile — field-io-packet structs only; no GPU, no libvulkan
# Implements grok16-znetwork-field-wire-doctrine.json compile lane (G5)
if(NOT GROK16_PROFILE STREQUAL "znetwork_wire")
  set(GROK16_PROFILE "znetwork_wire" CACHE STRING "Grok16 build profile" FORCE)
endif()
set(GROK16_CXX_STD "gnu++26" CACHE STRING "Grok16 C++ standard" FORCE)
set(GROK16_C_STD "gnu17" CACHE STRING "Grok16 C standard" FORCE)
add_compile_definitions(
  GROK16_PROFILE_ZNETWORK_WIRE=1
  GROK16_BELT_2_0=1
  GROK16_HOSTESS_SECURE=1
  G16_FIELD_MANDATE=1
  FIELD_ENTROPY_DISPATCH=1
  FIELD_SINGLE_LOCATION_READ=1
  HOSTESS_TRUTH_FLOOR=58
  G16_ZNETWORK_WIRE=1
)
add_compile_options(
  $<$<COMPILE_LANGUAGE:CXX>:-std=gnu++26>
  $<$<COMPILE_LANGUAGE:C>:-std=gnu17>
  -O2 -pipe -march=native
  -fstack-protector-strong -fstack-clash-protection -fcf-protection=full
  -fno-strict-aliasing -D_FORTIFY_SOURCE=3 -fPIE
)
add_link_options(-Wl,-z,relro -Wl,-z,now -Wl,-z,noexecstack -pie)
# Explicit: no Vulkan / GPU link symbols in this profile
set(GROK16_NO_LIBVULKAN 1 CACHE BOOL "znetwork_wire forbids libvulkan" FORCE)