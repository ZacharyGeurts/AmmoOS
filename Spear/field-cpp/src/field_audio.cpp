// SPDX-License-Identifier: MIT
// field-audio — Native SDL3-class audio status (C++). No pactl scripts.
// Reports plate; full mixer lives in AMOURANTHRTX SDL3 when linked.
#include "spear_common.hpp"

#include <cstdio>
#include <cstring>

int main(int argc, char** argv) {
  if (argc >= 2 && std::strcmp(argv[1], "--version") == 0) {
    std::puts("field-audio 1.0.0 native C++ · SDL3 field path · no scripts");
    return 0;
  }
  std::string o = "SPEARPLATE/1\n";
  o += "schema=field-audio/v1\n";
  o += "engine=C++\n";
  o += "scripts=FORBIDDEN\n";
  o += "backend=SDL3\n";
  o += "frequency=48000\n";
  o += "path=AMOURANTHRTX/Navigator Options::SDL3\n";
  o += "status=native_field\n";
  o += "note=Full mixer in AMOURANTHRTX SDL3; this binary is the menu entry and plate\n";
  o += "END\n";
  spear::mirror_www("field-audio.plate", o);
  if (argc >= 2 && std::strcmp(argv[1], "--quiet") == 0) return 0;
  std::fputs(o.c_str(), stdout);
  return 0;
}
