# Hostess 7 secure profile — memory-safe C/C++ flags (pairs with g16-field-mandate.cmake)
include("${CMAKE_CURRENT_LIST_DIR}/g16-field-mandate.cmake")

set(GROK16_PROFILE "hostess_secure" CACHE STRING "Grok16 profile" FORCE)
add_compile_definitions(
  GROK16_HOSTESS_SECURE=1
  HOSTESS_TRUTH_FLOOR=58
  G16_FIELD_SANITY=1
  G16_FIELD_SANITY_INTEGRAL=1
  G16_IRONCLAD_MELD=1
  G16_IRONCLAD_MELD_CITATION="ironclad:meld:2"
)
add_compile_options(
  -O2
  -fstack-protector-strong
  -fstack-clash-protection
  -fcf-protection=full
  -fno-strict-aliasing
  -D_FORTIFY_SOURCE=3
  -fPIE
  -Wformat -Wformat-security -Werror=format-security
)
add_link_options(-Wl,-z,relro -Wl,-z,now -Wl,-z,noexecstack -pie)