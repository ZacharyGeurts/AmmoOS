# Credits

Grok16 is beta packaging and tooling around a self-hosted **G16** (`g16` / `g++16`)
field build. All software here is under the **GNU General Public License v3**
unless a file states otherwise.

## GNU Compiler Collection (GCC)

- **Project:** [GNU Compiler Collection](https://gcc.gnu.org/)
- **Source repository:** https://gcc.gnu.org/git/gcc.git
- **Branch used:** `releases/gcc-15` (field rewrite → G16 @ 16.0.0)
- **Copyright:** Free Software Foundation, Inc. and GCC contributors
- **License:** GPLv3; runtime components may use the [GCC Runtime Library Exception](https://www.gnu.org/licenses/gcc-exception-3.1.html)

Grok16 does not replace or subsume GCC — it configures, self-hosts, and installs
a field build with `g16` / `g++16` program names and pkgversion `Grok16-16.0.0`.

## Free Software Foundation

Thank you to the **Free Software Foundation** for GCC, the GPL, and decades of
free software infrastructure.

## Grok16 maintainers

- **Zachary Geurts** — Grok16 scripts, toolchain layout, Queen forge integration (2026)

## Third-party tools (build-time)

Building GCC typically also uses **GMP**, **MPFR**, and **MPC** (their respective
GNU or LGPL licenses apply via the GCC prerequisite bundle). Queen forge handles
fetching prerequisites from the upstream GCC `contrib/download_prerequisites` flow.

## Distribution compliance

- **Modify and use:** GPLv3 explicitly allows running, modifying, and redistributing
  GCC-derived compilers. You do not need to remove GNU code to stay compliant.
- **Keep the compiler:** Grok16 bootstraps upstream GCC/Binutils with documented
  field deltas (`patches/`, forge configure). Rewriting a full compiler from scratch
  is not required for license compliance.
- **Binary distributions:** ship [SOURCE-OFFER.txt](SOURCE-OFFER.txt) with install
  tarballs or prefix copies so recipients can obtain Corresponding Source (GPL §6).
- **Your glue stays yours:** `driver/`, `forge/`, `cmake/`, and `scripts/` are
  original Grok16 work (GPLv3). Using `g16`/`g++16` to compile MIT or commercial
  projects does not infect those projects — the compiler is a separate tool.