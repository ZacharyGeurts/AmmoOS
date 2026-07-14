// SPDX-License-Identifier: MIT
// field-menu / spear-field-menu — Native Field Start Menu (C++).
// Lists and launches ONLY native field apps. Scripts FORBIDDEN.
#include "spear_common.hpp"
#include "spear_field_apps.hpp"

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/stat.h>

namespace {

bool bin_ok(const char* name) {
  const char* home = std::getenv("HOME");
  char path[512];
  if (home) {
    std::snprintf(path, sizeof path, "%s/.local/bin/%s", home, name);
    struct stat st {};
    if (::stat(path, &st) == 0 && (st.st_mode & S_IXUSR)) return true;
  }
  const char* dirs[] = {"/usr/local/bin/", "/usr/bin/", nullptr};
  for (int i = 0; dirs[i]; ++i) {
    std::snprintf(path, sizeof path, "%s%s", dirs[i], name);
    struct stat st {};
    if (::stat(path, &st) == 0 && (st.st_mode & S_IXUSR)) return true;
  }
  return false;
}

const char* resolve(const char* name) {
  static char path[512];
  const char* home = std::getenv("HOME");
  if (home) {
    std::snprintf(path, sizeof path, "%s/.local/bin/%s", home, name);
    struct stat st {};
    if (::stat(path, &st) == 0 && (st.st_mode & S_IXUSR)) return path;
  }
  const char* dirs[] = {"/usr/local/bin/", "/usr/bin/", nullptr};
  for (int i = 0; dirs[i]; ++i) {
    std::snprintf(path, sizeof path, "%s%s", dirs[i], name);
    struct stat st {};
    if (::stat(path, &st) == 0 && (st.st_mode & S_IXUSR)) return path;
  }
  return nullptr;
}

int launch(const char* exec_name, char** extra_argv, int extra_n) {
  // refuse scripts
  std::string e = exec_name;
  if (spear::contains(e, ".py") || spear::contains(e, ".sh") || spear::contains(e, ".bash")) {
    std::fprintf(stderr, "field-menu: REFUSED script path: %s\n", exec_name);
    return 2;
  }
  const char* path = resolve(exec_name);
  if (!path) {
    std::fprintf(stderr, "field-menu: missing native bin: %s\n", exec_name);
    return 1;
  }
  // strip leading "--" and empty args (smart-guy GNU noise)
  std::vector<char*> cleaned;
  for (int i = 0; i < extra_n; ++i) {
    if (!extra_argv[i] || !extra_argv[i][0]) continue;
    if (std::strcmp(extra_argv[i], "--") == 0) continue;
    cleaned.push_back(extra_argv[i]);
  }
  pid_t p = ::fork();
  if (p < 0) return 1;
  if (p == 0) {
    // special cases with args
    if (std::strcmp(exec_name, "spear") == 0 && cleaned.empty()) {
      ::execl(path, path, "chip-status", static_cast<char*>(nullptr));
    } else if (std::strcmp(exec_name, "spear-h7-panel") == 0) {
      ::execl(path, path, "--bind", spear::field_bind_ip(), "--port", "9491", "--root",
              "/tmp/spear-swallows-www/hostess7", static_cast<char*>(nullptr));
    } else if (std::strcmp(exec_name, "spear-i2-server") == 0) {
      ::execl(path, path, "--bind", spear::field_bind_ip(), "--port", "9477",
              static_cast<char*>(nullptr));
    } else if (std::strcmp(exec_name, "amouranthrtx") == 0) {
      // AmmoOS field face — SDL3, not a 127 browser
      ::execl(path, path, static_cast<char*>(nullptr));
    } else if (!cleaned.empty()) {
      std::vector<char*> av;
      av.push_back(const_cast<char*>(path));
      for (char* a : cleaned) av.push_back(a);
      av.push_back(nullptr);
      ::execv(path, av.data());
    } else {
      ::execl(path, path, static_cast<char*>(nullptr));
    }
    _exit(127);
  }
  // don't wait for long-running servers
  if (std::strcmp(exec_name, "spear-h7-panel") == 0 || std::strcmp(exec_name, "spear-i2-server") == 0 ||
      std::strcmp(exec_name, "spear-wartime") == 0 || std::strcmp(exec_name, "amouranthrtx") == 0 ||
      std::strcmp(exec_name, "queen") == 0) {
    std::printf("field-menu: spawned %s\n", exec_name);
    return 0;
  }
  int st = 0;
  ::waitpid(p, &st, 0);
  return WIFEXITED(st) ? WEXITSTATUS(st) : 1;
}

void list_text() {
  std::printf("Field Start Menu — native C++ only · scripts FORBIDDEN\n");
  std::printf("%-14s %-22s %-18s %s\n", "ID", "NAME", "EXEC", "STATUS");
  for (std::size_t i = 0; i < spear::field_apps::kMenuN; ++i) {
    const auto& a = spear::field_apps::kMenu[i];
    std::printf("%-14s %-22s %-18s %s\n", a.id, a.name, a.exec, bin_ok(a.exec) ? "OK" : "MISSING");
  }
}

}  // namespace

int main(int argc, char** argv) {
  const char* cmd = (argc >= 2) ? argv[1] : "list";
  if (std::strcmp(cmd, "-h") == 0 || std::strcmp(cmd, "--help") == 0) {
    std::fputs(
        "field-menu — Native Field Start Menu (C++)\n"
        "  field-menu list|plate|launch <id>|run <exec>\n"
        "  God Bless. No scripts. No LibreOffice.\n",
        stdout);
    return 0;
  }
  if (std::strcmp(cmd, "list") == 0 || std::strcmp(cmd, "ls") == 0) {
    list_text();
    return 0;
  }
  if (std::strcmp(cmd, "plate") == 0) {
    std::string p = spear::field_apps::menu_plate();
    spear::mirror_www("field-start-menu.plate", p);
    std::fputs(p.c_str(), stdout);
    return 0;
  }
  if (std::strcmp(cmd, "launch") == 0 && argc >= 3) {
    const char* id = argv[2];
    for (std::size_t i = 0; i < spear::field_apps::kMenuN; ++i) {
      if (std::strcmp(spear::field_apps::kMenu[i].id, id) == 0) {
        return launch(spear::field_apps::kMenu[i].exec, argv + 3, argc - 3);
      }
    }
    std::fprintf(stderr, "field-menu: unknown id %s\n", id);
    return 1;
  }
  if (std::strcmp(cmd, "run") == 0 && argc >= 3) {
    return launch(argv[2], argv + 3, argc - 3);
  }
  // default list
  list_text();
  return 0;
}
