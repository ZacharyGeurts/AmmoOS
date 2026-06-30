# Master Coder

Web: [master-coder.html](https://zacharygeurts.github.io/Grok16/master-coder.html) · Distro **2.0.0** · g16 @ **16.2.0** · single fabric

Ordered index of every Grok16 command and function. Short tooltip per row; click for the detailed manual section.

**Web (with anchors):** [master-coder.html](https://zacharygeurts.github.io/Grok16/master-coder.html)

## 1 — Toolchain commands (`grok16-toolchain.sh`)

| # | Command | Tooltip | Detail |
|---|---------|---------|--------|
| 1 | [bootstrap](https://zacharygeurts.github.io/Grok16/getting-started.html#bootstrap) | Fetch GCC, host build, install | Getting Started |
| 2 | [rebuild](https://zacharygeurts.github.io/Grok16/getting-started.html#rebuild) | Self-host with g16/g++16 | Getting Started |
| 3 | [install](https://zacharygeurts.github.io/Grok16/reference.html#cmd-install) | Write metadata (needs bin/g++16) | Reference |
| 4 | [verify](https://zacharygeurts.github.io/Grok16/getting-started.html#verify) | Compile smoke test | Getting Started |
| 5 | [status](https://zacharygeurts.github.io/Grok16/reference.html#cmd-status) | Ready check | Reference |
| 6 | [field-bench](https://zacharygeurts.github.io/Grok16/performance.html#field-bench) | Field-Opt benchmark | Performance |
| 7 | [bench](https://zacharygeurts.github.io/Grok16/performance.html#bench) | Single profile bench | Performance |
| 8 | [bench-all](https://zacharygeurts.github.io/Grok16/performance.html#bench-all) | All profile benches | Performance |
| 9 | [profile](https://zacharygeurts.github.io/Grok16/performance.html#pgo) | PGO training run | Performance |
| 10 | [paths](https://zacharygeurts.github.io/Grok16/reference.html#cmd-paths) | Resolved paths/env | Reference |
| 11 | [config](https://zacharygeurts.github.io/Grok16/reference.html#cmd-config) | Paths + config template | Reference |
| 12 | [manifest](https://zacharygeurts.github.io/Grok16/reference.html#cmd-manifest) | Regenerate cmake + JSON | Reference |
| 13 | [consolidate](https://zacharygeurts.github.io/Grok16/integration.html#queen) | Queen → Grok16 migration | Integration |

## 2 — Forge (`grok16-forge.py`)

| # | Invocation | Tooltip | Detail |
|---|------------|---------|--------|
| 1 | [status](https://zacharygeurts.github.io/Grok16/reference.html#forge-status) | Toolchain state JSON | Reference |
| 2 | [run gcc_fetch](https://zacharygeurts.github.io/Grok16/architecture.html#forge-flow) | Fetch upstream GCC | Architecture |
| 3 | [run gcc_prereqs](https://zacharygeurts.github.io/Grok16/architecture.html#forge-flow) | GCC prerequisites | Architecture |
| 4 | [run gcc_configure](https://zacharygeurts.github.io/Grok16/architecture.html#forge-flow) | Host configure | Architecture |
| 5 | [run gcc_build](https://zacharygeurts.github.io/Grok16/architecture.html#forge-flow) | Host build + install | Architecture |
| 6 | [run gcc_rebuild](https://zacharygeurts.github.io/Grok16/getting-started.html#rebuild) | Self-host rebuild | Getting Started |
| 7 | [run gcc](https://zacharygeurts.github.io/Grok16/getting-started.html#bootstrap) | Full bootstrap pipeline | Getting Started |

## 3 — Profile flags (`grok16-profile-flags.py`)

| # | Mode | Tooltip | Detail |
|---|------|---------|--------|
| 1 | [PROFILE cxx](https://zacharygeurts.github.io/Grok16/profiles.html#flags-cxx) | Compile flags + defs | Profiles |
| 2 | [PROFILE link](https://zacharygeurts.github.io/Grok16/profiles.html#flags-link) | Link flags | Profiles |
| 3 | [PROFILE source](https://zacharygeurts.github.io/Grok16/profiles.html#flags-source) | Bench source path | Profiles |
| 4 | [PROFILE defs](https://zacharygeurts.github.io/Grok16/profiles.html#flags-defs) | Definition flags only | Profiles |
| 5 | [PROFILE cxx_pgo_gen](https://zacharygeurts.github.io/Grok16/performance.html#pgo) | PGO generate flags | Performance |
| 6 | [PROFILE cxx_pgo_use](https://zacharygeurts.github.io/Grok16/performance.html#pgo) | PGO use flags | Performance |

## 4 — Shell functions

| # | Function | Tooltip | Detail |
|---|----------|---------|--------|
| 1 | [_grok16_config_resolve](https://zacharygeurts.github.io/Grok16/architecture.html#scripts) | Path/env resolution | Architecture |
| 2 | [grok16_driver_extra_flags](https://zacharygeurts.github.io/Grok16/reference.html#fn-driver-extra) | Dev layout driver -B flag | Reference |
| 3 | [grok16_ready](https://zacharygeurts.github.io/Grok16/reference.html#fn-ready) | Compiler ready probe | Reference |
| 4 | [_bench_run_one](https://zacharygeurts.github.io/Grok16/performance.html#bench) | Internal bench runner | Performance |
| 5 | [g16_field_mandate](https://zacharygeurts.github.io/Grok16/profiles.html#mandate) | CMake security function | Profiles |

## 5 — Build profiles

| # | Profile | Tooltip | Detail |
|---|---------|---------|--------|
| 1 | [field_opt](https://zacharygeurts.github.io/Grok16/profiles.html#field-opt) | Primary Field throughput | Profiles |
| 2 | [ai](https://zacharygeurts.github.io/Grok16/profiles.html#ai) | NEXUS / matrix | Profiles |
| 3 | [field_compute](https://zacharygeurts.github.io/Grok16/profiles.html#field-compute) | Field compute kernels | Profiles |
| 4 | [vulkan_rtx](https://zacharygeurts.github.io/Grok16/profiles.html#vulkan-rtx) | RTX-oriented SIMD | Profiles |

## 6 — Environment variables

| # | Variable | Tooltip | Detail |
|---|----------|---------|--------|
| 1 | [GROK16_ROOT](https://zacharygeurts.github.io/Grok16/reference.html#env-grok16-root) | Repo root | Reference |
| 2 | [G16_PREFIX](https://zacharygeurts.github.io/Grok16/reference.html#env-g16-prefix) | Install prefix | Reference |
| 3 | [GROK16_GCC_SRC](https://zacharygeurts.github.io/Grok16/reference.html#env-gcc-src) | GCC source tree | Reference |
| 4 | [GROK16_GCC_BUILD](https://zacharygeurts.github.io/Grok16/reference.html#env-gcc-build) | GCC build tree | Reference |
| 5 | [GROK16_QUEEN_ROOT](https://zacharygeurts.github.io/Grok16/integration.html#queen) | Queen path | Integration |
| 6 | [G16_CXX_STD](https://zacharygeurts.github.io/Grok16/field-primer.html#standard) | C++ standard | Field Primer |
| 7 | [G16_PKGVERSION](https://zacharygeurts.github.io/Grok16/reference.html#env-pkgversion) | Pkgversion stamp | Reference |
| 8 | [GROK16_BUILD_JOBS](https://zacharygeurts.github.io/Grok16/performance.html#forge-speed) | Parallel make jobs | Performance |
| 9 | [G16_FAST_REBUILD](https://zacharygeurts.github.io/Grok16/getting-started.html#rebuild) | Incremental rebuild | Getting Started |
| 10 | [G16_FULL_REBUILD](https://zacharygeurts.github.io/Grok16/getting-started.html#rebuild) | Full bootstrap rebuild | Getting Started |
| 11 | [G16_RELEASE_PROFILE](https://zacharygeurts.github.io/Grok16/performance.html#forge-speed) | Production profile | Performance |
| 12 | [G16_FIELD_SPEED](https://zacharygeurts.github.io/Grok16/profiles.html#field-opt) | Field-Opt enable | Profiles |
| 13 | [G16_ENABLE_LTO](https://zacharygeurts.github.io/Grok16/performance.html#forge-speed) | Link-time optimization | Performance |
| 14 | [G16_ENABLE_PGO](https://zacharygeurts.github.io/Grok16/performance.html#pgo) | PGO use | Performance |
| 15 | [G16_PGO_GENERATE](https://zacharygeurts.github.io/Grok16/performance.html#pgo) | PGO generate | Performance |
| 16 | [GROK16_USE_CCACHE](https://zacharygeurts.github.io/Grok16/performance.html#forge-speed) | ccache wrapper | Performance |
| 17 | [G16_DISABLE_BOOTSTRAP](https://zacharygeurts.github.io/Grok16/getting-started.html#rebuild) | Skip 3-stage | Getting Started |
| 18 | [G16_BENCH_PROFILE](https://zacharygeurts.github.io/Grok16/profiles.html#bench) | Bench profile name | Profiles |
| 19 | [WRDT_G16_PREFIX](https://zacharygeurts.github.io/Grok16/integration.html#env) | WRDT prefix override | Integration |
| 20 | [WRDT_G16_TOOLCHAIN](https://zacharygeurts.github.io/Grok16/integration.html#env) | WRDT script override | Integration |

## 7 — Forge Python (key)

| # | Function | Tooltip | Detail |
|---|----------|---------|--------|
| 1 | [g16_status](https://zacharygeurts.github.io/Grok16/reference.html#py-g16-status) | Status dict builder | Reference |
| 2 | [patch_gcc_field_version](https://zacharygeurts.github.io/Grok16/architecture.html#forge-flow) | Field version patch | Architecture |
| 3 | [write_selfhost_stamp](https://zacharygeurts.github.io/Grok16/architecture.html#selfhost) | Self-host JSON stamp | Architecture |
| 4 | [write_manifest](https://zacharygeurts.github.io/Grok16/reference.html#py-manifest) | JSON manifest | Reference |
| 5 | [write_cmake_toolchain](https://zacharygeurts.github.io/Grok16/reference.html#py-cmake) | CMake toolchain file | Reference |
| 6 | [resolve_lto_flag](https://zacharygeurts.github.io/Grok16/profiles.html#flags-link) | LTO flag resolver | Profiles |
| 7 | [verify_g16_install](https://zacharygeurts.github.io/Grok16/reference.html#py-verify) | Install verification | Reference |

## 8 — Integration gates (World_Redata)

| # | Command | Tooltip | Detail |
|---|---------|---------|--------|
| 1 | [build-cpp.sh](https://zacharygeurts.github.io/Grok16/integration.html#gates) | Build L2 engine | Integration |
| 2 | [redata.cli parity](https://zacharygeurts.github.io/Grok16/integration.html#gates) | Format parity gate | Integration |
| 3 | [redata.cli security](https://zacharygeurts.github.io/Grok16/integration.html#gates) | Security gate | Integration |
| 4 | [redata.cli mandate](https://zacharygeurts.github.io/Grok16/integration.html#gates) | Mandate gate | Integration |