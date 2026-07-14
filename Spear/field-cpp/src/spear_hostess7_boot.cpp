// SPDX-License-Identifier: MIT
// spear-hostess7-boot — FAST · HARD path straight to Hostess 7 (C++ only).
// Called from init / systemd after kernel. No scripts. No sudo. No pkill.
// God Bless.
#include "spear_common.hpp"
#include "spear_field_apps.hpp"

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <fcntl.h>

namespace {

bool exists_x(const char* p) {
  struct stat st {};
  return ::stat(p, &st) == 0 && (st.st_mode & S_IXUSR);
}

const char* pick(const char* name) {
  static char path[512];
  const char* home = std::getenv("HOME");
  if (home && *home) {
    std::snprintf(path, sizeof path, "%s/.local/bin/%s", home, name);
    if (exists_x(path)) return path;
  }
  std::snprintf(path, sizeof path, "/usr/local/bin/%s", name);
  if (exists_x(path)) return path;
  std::snprintf(path, sizeof path, "/usr/bin/%s", name);
  if (exists_x(path)) return path;
  return nullptr;
}

// Detach spawn — never pkill, never sudo
void spawn(const char* name, const char* const* args) {
  const char* bin = pick(name);
  if (!bin) {
    std::printf("  [skip] %s missing\n", name);
    return;
  }
  pid_t p = ::fork();
  if (p < 0) return;
  if (p == 0) {
    ::setsid();
    int dn = ::open("/dev/null", O_RDWR);
    if (dn >= 0) {
      ::dup2(dn, 0);
      // keep stdout/stderr for first boot visibility on console? optional null
      if (dn > 2) ::close(dn);
    }
    // build argv
    char* argv[16];
    int n = 0;
    argv[n++] = const_cast<char*>(bin);
    if (args) {
      for (int i = 0; args[i] && n < 14; ++i) argv[n++] = const_cast<char*>(args[i]);
    }
    argv[n] = nullptr;
    ::execv(bin, argv);
    _exit(127);
  }
  std::printf("  [up] %s\n", name);
}

void banner() {
  std::fputs(
      "\n"
      "\033[1;33m══════════════════════════════════════════════════════\033[0m\n"
      "\033[1;33m  HOSTESS 7  ·  FOREVER WATCHGUARD  ·  ALWAYS WAR\033[0m\n"
      "\033[1;32m  FAST · HARD · C++ only  ·  Internet 2.0 LAW\033[0m\n"
      "\033[1;33m══════════════════════════════════════════════════════\033[0m\n"
      "\n",
      stdout);
}

}  // namespace

int main(int argc, char** argv) {
  const char* cmd = (argc >= 2) ? argv[1] : "boot";
  if (std::strcmp(cmd, "--help") == 0 || std::strcmp(cmd, "-h") == 0) {
    std::fputs("spear-hostess7-boot [boot|status|banner]\n  ROM→kernel→Hostess7 hard path\n",
               stdout);
    return 0;
  }
  if (std::strcmp(cmd, "banner") == 0) {
    banner();
    return 0;
  }

  banner();
  std::printf(">>> Hostess 7 boot · never sudo · never pkill · C++ stack\n");

  // Field bind — AmmoOS / Internet 2.0 on all ifaces (not 127-only)
  const char* bind = spear::field_bind_ip();
  std::printf("  bind=%s advertise=%s  AmmoOS+SDL3 face=AMOURANTHRTX\n", bind,
              spear::field_advertise_host().c_str());

  // Order: wartime → www → i2 LAW → h7 panel → angel seal → field surface plate
  {
    const char* a[] = {nullptr};
    spawn("spear-wartime", a);
  }
  {
    const char* a[] = {"--bind", bind, "--port", "9490", "--root", "/tmp/spear-swallows-www", nullptr};
    spawn("spear-www", a);
  }
  {
    const char* a[] = {"--bind", bind, "--port", "9477", nullptr};
    spawn("spear-i2-server", a);
  }
  {
    const char* a[] = {"--bind", bind, "--port", "9491", "--root",
                       "/tmp/spear-swallows-www/hostess7", nullptr};
    spawn("spear-h7-panel", a);
  }
  {
    const char* a[] = {"--interval-ms", "2500", "--port", "9500", nullptr};
    spawn("spear-fleet-link", a);
  }
  {
    const char* a[] = {"--port", "9600", "--root", "/tmp/spear-swallows-www", nullptr};
    spawn("spear-planet", a);
  }

  // sync ensure + seal (wait)
  if (const char* i2 = pick("spear-i2-war")) {
    pid_t p = ::fork();
    if (p == 0) {
      ::execl(i2, i2, "ensure", static_cast<char*>(nullptr));
      _exit(127);
    }
    if (p > 0) {
      int st = 0;
      ::waitpid(p, &st, 0);
      std::printf("  [ok] spear-i2-war ensure\n");
    }
  }
  if (const char* as = pick("spear-angel-seal")) {
    pid_t p = ::fork();
    if (p == 0) {
      ::execl(as, as, "seal", "--quiet", static_cast<char*>(nullptr));
      _exit(127);
    }
    if (p > 0) {
      int st = 0;
      ::waitpid(p, &st, 0);
      std::printf("  [ok] angel-seal\n");
    }
  }
  if (const char* fs = pick("spear-field-surface")) {
    pid_t p = ::fork();
    if (p == 0) {
      ::execl(fs, fs, "plate", static_cast<char*>(nullptr));
      _exit(127);
    }
    if (p > 0) {
      int st = 0;
      ::waitpid(p, &st, 0);
    }
  }

  // plate mark for benches
  const std::string ready =
      "SPEARPLATE/1\nschema=hostess7-boot/v1\nstatus=READY\n"
      "always_war=true\nengine=C++\nscripts=FORBIDDEN\n"
      "i2=9477\nh7=9491\nwww=9490\nEND\n";
  spear::mkdir_p("/run");
  spear::write_file("/run/hostess7-boot.ready", ready);
  spear::mirror_www("hostess7-boot.ready", ready);

  const std::string host = spear::field_advertise_host();
  std::printf("\n>>> Hostess 7 READY · AmmoOS on AMOURANTHRTX (SDL3)\n");
  std::printf("    Internet 2.0 LAW  http://%s:9477/\n", host.c_str());
  std::printf("    Hostess 7 panel   http://%s:9491/hostess7.html\n", host.c_str());
  std::printf("    Field surface     amouranthrtx  (SDL3 · Vulkan-carried · 4K)\n");
  std::printf("    field-menu list   ·  field-calc  ·  field-obs\n");
  std::printf("    God Bless.\n\n");

  if (std::strcmp(cmd, "status") == 0) {
    std::string r = spear::read_file("/run/hostess7-boot.ready", 4096);
    std::fputs(r.c_str(), stdout);
  }
  return 0;
}
