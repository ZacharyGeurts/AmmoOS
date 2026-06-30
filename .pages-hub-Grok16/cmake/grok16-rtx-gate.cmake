# G16 RTX Gate — queen_rtx / vulkan_rtx require RTX-class GPU (override: G16_RTX_GATE_FORCE=1)

set(G16_RTX_GATE_SATISFIED OFF CACHE BOOL "RTX GPU detected for gated profiles")
set(G16_RTX_GATE_FORCED OFF CACHE BOOL "RTX gate forced via G16_RTX_GATE_FORCE")

if(DEFINED ENV{G16_RTX_GATE_FORCE} AND NOT "$ENV{G16_RTX_GATE_FORCE}" STREQUAL "")
  if("$ENV{G16_RTX_GATE_FORCE}" STREQUAL "1" OR "$ENV{G16_RTX_GATE_FORCE}" STREQUAL "true" OR "$ENV{G16_RTX_GATE_FORCE}" STREQUAL "yes")
    set(G16_RTX_GATE_FORCED ON CACHE BOOL "" FORCE)
    set(G16_RTX_GATE_SATISFIED ON CACHE BOOL "" FORCE)
  endif()
endif()

if(NOT G16_RTX_GATE_SATISFIED AND EXISTS "${GROK16_ROOT}/forge/rtx_gate.py")
  find_program(_G16_GPY16 NAMES gpy-16 pythong)
  if(_G16_GPY16)
    execute_process(
      COMMAND ${_G16_GPY16} "${GROK16_ROOT}/forge/rtx_gate.py" satisfied
      OUTPUT_VARIABLE _G16_RTX_SAT
      OUTPUT_STRIP_TRAILING_WHITESPACE
      ERROR_QUIET
      TIMEOUT 12
    )
    if(_G16_RTX_SAT STREQUAL "1")
      set(G16_RTX_GATE_SATISFIED ON CACHE BOOL "" FORCE)
    endif()
  endif()
endif()

if((GROK16_FIELD_PROFILE STREQUAL "queen_rtx" OR GROK16_FIELD_PROFILE STREQUAL "vulkan_rtx")
    AND NOT G16_RTX_GATE_SATISFIED AND NOT G16_RTX_GATE_FORCED)
  message(WARNING "G16 RTX gate: no RTX GPU detected — profile '${GROK16_FIELD_PROFILE}' downgraded to field_opt (set G16_RTX_GATE_FORCE=1 to override)")
  set(GROK16_FIELD_PROFILE "field_opt" CACHE STRING "Grok16 field cmake profile" FORCE)
elseif(GROK16_FIELD_PROFILE STREQUAL "queen_rtx" OR GROK16_FIELD_PROFILE STREQUAL "vulkan_rtx")
  message(STATUS "G16 RTX gate: satisfied — profile=${GROK16_FIELD_PROFILE}")
endif()