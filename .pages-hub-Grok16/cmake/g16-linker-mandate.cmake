# G16 Linker Mandate — field link pass on every G16 target (silicon + Ironclad witness)
# Pairs with g16-field-mandate.cmake compile pass.

set(G16_LINKER_MANDATE_ID "G16_LINKER_MANDATE_v1" CACHE STRING "G16 linker mandate version")
set(G16_LINKER_DRIVER "g16-ld" CACHE STRING "G16 field linker driver")

function(g16_linker_mandate target)
  if(NOT TARGET ${target})
    message(FATAL_ERROR "g16_linker_mandate: unknown target ${target}")
  endif()
  if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_C_COMPILER_ID STREQUAL "GNU")
    target_link_options(${target} PRIVATE
      -Wl,-z,relro
      -Wl,-z,now
      -Wl,-z,noexecstack
      -pie
    )
  endif()
  target_compile_definitions(${target} PRIVATE
    G16_LINKER_MANDATE=1
    G16_LINKER_PASS=1
    G16_IRONCLAD_LINK_MELD=1
    G16_IRONCLAD_MELD_CITATION="${G16_IRONCLAD_MELD_CITATION}"
  )
  if(EXISTS "${GROK16_ROOT}/data/g16-linker-doctrine.json")
    set_property(TARGET ${target} PROPERTY G16_LINKER_DOCTRINE "${GROK16_ROOT}/data/g16-linker-doctrine.json")
  endif()
endfunction()

function(g16_ironclad_sanity_link target)
  g16_linker_mandate(${target})
endfunction()