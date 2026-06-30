# Grok16 AI profile — include after grok16-toolchain.cmake
# Usage: -DCMAKE_TOOLCHAIN_FILE=.../grok16-toolchain.cmake -DGROK16_PROFILE=ai
if(NOT GROK16_PROFILE STREQUAL "ai")
  set(GROK16_PROFILE "ai" CACHE STRING "Grok16 build profile" FORCE)
endif()
set(GROK16_CXX_STD "gnu++26" CACHE STRING "Grok16 C++ standard" FORCE)
add_compile_definitions(GROK16_PROFILE_AI=1 FIELD_ENTROPY_DISPATCH=1)
add_compile_options(
  -std=gnu++26 -O3 -march=native -mtune=native
  -ffast-math -funroll-loops -finline-functions -fomit-frame-pointer
)
add_link_options(-flto)