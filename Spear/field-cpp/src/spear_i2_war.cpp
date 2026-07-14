// SPDX-License-Identifier: MIT
// spear-i2-war — War device Internet 2.0 stack ensure (C++ only).
// Starts/checks C++ war services. Reports DNS/DHCP honestly (no fake up).
// Hostess 7 war posture plate + Field Law court awareness.
#include "spear_common.hpp"

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <dirent.h>
#include <fcntl.h>
#include <string>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>
#include <vector>

namespace {

bool port_up(int port) { return spear::port_listening(port); }

bool bin_exists(const char* p) {
  struct stat st {};
  return ::stat(p, &st) == 0 && (st.st_mode & S_IXUSR);
}

// Spawn detached if not already running (match by basenames in /proc)
bool proc_running(const char* needle) {
  DIR* d = ::opendir("/proc");
  if (!d) return false;
  bool found = false;
  while (dirent* ent = ::readdir(d)) {
    if (!spear::is_digits(ent->d_name)) continue;
    pid_t pid = static_cast<pid_t>(std::atoi(ent->d_name));
    std::string comm = spear::read_comm(pid);
    if (comm == needle) {
      found = true;
      break;
    }
  }
  ::closedir(d);
  return found;
}

int spawn_bg(const char* path, const std::vector<const char*>& args) {
  if (!bin_exists(path)) return 127;
  pid_t p = ::fork();
  if (p < 0) return 1;
  if (p == 0) {
    ::setsid();
    int devnull = ::open("/dev/null", O_RDWR);
    if (devnull >= 0) {
      ::dup2(devnull, 0);
      ::dup2(devnull, 1);
      ::dup2(devnull, 2);
      if (devnull > 2) ::close(devnull);
    }
    std::vector<char*> argv;
    argv.push_back(const_cast<char*>(path));
    for (const char* a : args) argv.push_back(const_cast<char*>(a));
    argv.push_back(nullptr);
    ::execv(path, argv.data());
    _exit(127);
  }
  return 0;
}

std::string now_z() {
  char buf[64];
  std::time_t t = std::time(nullptr);
  std::strftime(buf, sizeof buf, "%Y-%m-%dT%H:%M:%SZ", std::gmtime(&t));
  return buf;
}

const char* pick_bin(const char* name) {
  static char path[512];
  const char* homes[] = {"/usr/local/bin/", "/usr/bin/", nullptr};
  // also $HOME/.local/bin
  const char* home = std::getenv("HOME");
  if (home && *home) {
    std::snprintf(path, sizeof path, "%s/.local/bin/%s", home, name);
    if (bin_exists(path)) return path;
  }
  for (int i = 0; homes[i]; ++i) {
    std::snprintf(path, sizeof path, "%s%s", homes[i], name);
    if (bin_exists(path)) return path;
  }
  return nullptr;
}

}  // namespace

int main(int argc, char** argv) {
  const char* cmd = (argc >= 2) ? argv[1] : "ensure";
  const bool force = (argc >= 3 && std::strcmp(argv[2], "--force") == 0);

  // Ensure C++ war daemons
  struct Svc {
    const char* name;
    const char* bin;
    int port;  // 0 = no port check
    std::vector<const char*> args;
  };
  std::vector<Svc> svcs = {
      {"spear-wartime", "spear-wartime", 0, {}},
      // Internet 2.0 LAW — field bind (0.0.0.0) · AmmoOS/SDL face separate
      {"spear-i2-server", "spear-i2-server", 9477, {"--bind", "0.0.0.0", "--port", "9477"}},
      {"spear-www", "spear-www", 9490, {"--bind", "0.0.0.0", "--port", "9490", "--root",
                                       "/tmp/spear-swallows-www"}},
      {"spear-fleet-link", "spear-fleet-link", 9500, {"--interval-ms", "2500", "--port", "9500"}},
      {"spear-planet", "spear-planet", 9600, {"--port", "9600", "--root", "/tmp/spear-swallows-www"}},
      {"spear-h7-panel", "spear-h7-panel", 9491, {"--bind", "0.0.0.0", "--port", "9491", "--root",
                                                 "/tmp/spear-swallows-www/hostess7"}},
  };

  if (std::strcmp(cmd, "status") != 0) {
    // ensure www root exists for field-law
    ::mkdir("/tmp/spear-swallows-www", 0755);
    for (const auto& s : svcs) {
      if (proc_running(s.name) && !force) continue;
      const char* path = pick_bin(s.bin);
      if (!path) {
        std::printf("missing %s\n", s.bin);
        continue;
      }
      if (proc_running(s.name)) continue;
      // rebuild argv with actual root if custom
      std::vector<const char*> args = s.args;
      spawn_bg(path, args);
      std::printf("spawn %s\n", s.bin);
    }
    // one hunt pass
    if (const char* hd = pick_bin("spear-hard-dispose")) {
      pid_t p = ::fork();
      if (p == 0) {
        ::execl(hd, hd, static_cast<char*>(nullptr));
        _exit(127);
      }
      if (p > 0) {
        int st = 0;
        ::waitpid(p, &st, 0);
      }
    }
    // Angel seal stack + ISO (CHIPs · Plate · Meld) — C++ only
    if (const char* as = pick_bin("spear-angel-seal")) {
      pid_t p = ::fork();
      if (p == 0) {
        ::execl(as, as, "seal", "--quiet", static_cast<char*>(nullptr));
        _exit(127);
      }
      if (p > 0) {
        int st = 0;
        ::waitpid(p, &st, 0);
        std::printf("angel-seal %s\n", WIFEXITED(st) && WEXITSTATUS(st) == 0 ? "SEALED_UP" : "PARTIAL");
      }
    }
  }

  // Honest listeners
  const bool c2 = port_up(9477);
  const bool www = port_up(9490);
  const bool h7 = port_up(9491);
  const bool fleet = port_up(9500);
  const bool planet = port_up(9600);
  const bool truth_dns = port_up(53);
  const bool field_dhcp = port_up(67);
  const bool wartime = proc_running("spear-wartime");
  // angel seal plate present?
  bool angel = false;
  {
    std::string ap = spear::www_dir() + "/angel-seal-status.json";
    struct stat st {};
    if (::stat(ap.c_str(), &st) == 0) angel = true;
    if (const char* home = std::getenv("HOME")) {
      std::string p = std::string(home) + "/.local/share/spear/angel-seal-status.json";
      if (::stat(p.c_str(), &st) == 0) angel = true;
    }
  }

  // Hostess7 war plate present?
  bool h7_war = false;
  const char* h7paths[] = {
      "/usr/local/share/spear/hostess7/hostess7-war-system-doctrine.json",
      "/usr/local/share/hostess7/data/hostess7-war-system-doctrine.json",
      nullptr};
  if (const char* home = std::getenv("HOME")) {
    std::string p = std::string(home) + "/Desktop/SG/NewLatest/data/hostess7-war-system-doctrine.json";
    struct stat st {};
    if (::stat(p.c_str(), &st) == 0) h7_war = true;
  }
  for (int i = 0; h7paths[i]; ++i) {
    struct stat st {};
    if (::stat(h7paths[i], &st) == 0) h7_war = true;
  }

  // Write posture (honest)
  std::string body;
  // Field plate (JSON EATEN — no JSON authority)
  body = spear::plate::i2_servers_plate(c2, www, h7, fleet, planet, truth_dns, field_dhcp, wartime);
  // extra keys
  {
    std::string extra;
    spear::plate::kv(extra, "ts", now_z());
    spear::plate::kv(extra, "hostess7_war_doctrine", h7_war);
    spear::plate::kv(extra, "angel_seal", angel);
    spear::plate::kv(extra, "bsp", true);
    spear::plate::kv(extra, "json_authority", "EATEN");
    size_t endpos = body.rfind("END\n");
    if (endpos != std::string::npos) body.insert(endpos, extra);
    else body += extra + "END\n";
  }

  spear::write_file((spear::www_dir() + "/war-device-posture.plate").c_str(), body);
  spear::write_file((spear::www_dir() + "/internet-2.0-servers.plate").c_str(), body);
  if (const char* home = std::getenv("HOME")) {
    std::string st = std::string(home) + "/.local/share/spear/war-device-posture.plate";
    spear::write_file(st.c_str(), body);
  }

  std::fputs(body.c_str(), stdout);

  // Gate: war core must be up; DNS/DHCP honest may be down until elev serve
  const bool core = wartime && www && fleet;
  return core ? 0 : 1;
}
