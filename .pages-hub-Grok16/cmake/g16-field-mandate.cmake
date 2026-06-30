# G16 Field Safety Mandate — mandatory for all G16 field targets (WRDT, FieldX86, …)
# Rust-grade discipline: fortify, stack protection, RELRO+NOW, PIE. No opt-out in release.

set(G16_FIELD_MANDATE_ID "G16_FIELD_SAFETY_MANDATE_v1" CACHE STRING "G16 safety mandate version")
set(G16_IRONCLAD_MELD_CITATION "ironclad:meld:2" CACHE STRING "Ironclad meld citation for G16 targets")

function(_g16_field_mandate_security target)
  target_compile_definitions(${target} PRIVATE _FORTIFY_SOURCE=3 G16_FIELD_MANDATE=1)
  target_compile_options(${target} PRIVATE
    -fstack-protector-strong
    -fstack-clash-protection
    -fcf-protection=full
    -fno-strict-aliasing
    -Wformat -Wformat-security
    -Werror=format-security
    -fPIE
  )
  if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_C_COMPILER_ID STREQUAL "GNU")
    target_link_options(${target} PRIVATE -Wl,-z,relro -Wl,-z,now -Wl,-z,noexecstack -pie)
  endif()
endfunction()

# Ironclad + field sanity — integral meld on every G16 field target (subsidiary truth, sealed doctrine untouched)
function(g16_ironclad_sanity_meld target)
  if(NOT TARGET ${target})
    message(FATAL_ERROR "g16_ironclad_sanity_meld: unknown target ${target}")
  endif()
  _g16_field_mandate_security(${target})
  target_compile_definitions(${target} PRIVATE
    G16_FIELD_SANITY=1
    G16_FIELD_SANITY_INTEGRAL=1
    G16_IRONCLAD_MELD=1
    G16_IRONCLAD_MELD_CITATION="${G16_IRONCLAD_MELD_CITATION}"
  )
  if(COMMAND g16_linker_mandate)
    g16_linker_mandate(${target})
  endif()
endfunction()

function(g16_field_mandate target)
  g16_ironclad_sanity_meld(${target})
endfunction()