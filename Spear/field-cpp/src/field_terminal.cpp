// SPDX-License-Identifier: MIT
// field-terminal — Native field terminal entry (C++).
// Does NOT ship bash as product. Opens a real TTY host if present, else plate shell.
#include "spear_common.hpp"

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <unistd.h>
#include <sys/stat.h>

static bool exists(const char* p) {
  struct stat st {};
  return ::stat(p, &st) == 0 && (st.st_mode & S_IXUSR);
}

int main(int argc, char** argv) {
  if (argc >= 2 && (std::strcmp(argv[1], "--version") == 0)) {
    std::puts("field-terminal 1.0.0 native C++ · no bash product");
    return 0;
  }
  // Prefer field / queen terminals if native bins exist — never gnome chrome as product
  const char* cands[] = {
      "/usr/local/bin/field-term",
      "/usr/local/bin/queen-terminal",
      "/usr/bin/xterm",
      "/usr/bin/kitty",
      "/usr/bin/alacritty",
      nullptr,
  };
  for (int i = 0; cands[i]; ++i) {
    if (exists(cands[i])) {
      ::execl(cands[i], cands[i], static_cast<char*>(nullptr));
    }
  }
  // Fallback: interactive field-calc as usable TTY surface
  const char* home = std::getenv("HOME");
  char path[512];
  if (home) {
    std::snprintf(path, sizeof path, "%s/.local/bin/field-calc", home);
    if (exists(path)) {
      std::fputs("field-terminal: opening field-calc (native)\n", stderr);
      ::execl(path, path, static_cast<char*>(nullptr));
    }
  }
  if (exists("/usr/local/bin/field-calc")) {
    ::execl("/usr/local/bin/field-calc", "field-calc", static_cast<char*>(nullptr));
  }
  std::fputs("field-terminal: no native TTY host; install field-calc / xterm\n", stderr);
  return 1;
}
