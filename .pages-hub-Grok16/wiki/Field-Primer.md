# Field Primer

Consumer requirements for Grok16 as the C/C++ toolchain.

## Checklist

1. Bootstrap; `verify` + `field-bench` pass.
2. Export `G16_PREFIX`.
3. CMake: `grok16-toolchain.cmake`.
4. Include `g16-field-mandate.cmake`.
5. Run `redata.cli parity` before push.

## Standard

`gnu++26` (`G16_CXX_STD`). World_Redata `field_g16.hh`: `__cplusplus >= 202400`.

## Profile map

| Workload | Profile |
|----------|---------|
| FieldX86 / entropy / NEXUS | field_opt |
| Matrix scoring | ai |
| CANVAS dispatch | field_compute |
| RTX CPU prep | vulkan_rtx |

## Rules

- Real ELF `g++16` @ 16.0.0 — no bash wrappers.
- Bounded I/O on untrusted paths.
- `-fcontracts` where mandated.