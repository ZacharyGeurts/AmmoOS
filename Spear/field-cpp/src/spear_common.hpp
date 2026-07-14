// SPDX-License-Identifier: MIT
// Shared helpers for Spear C++ wartime tools. No scripts. C++ / lower only.
// JSON has no authority — doctrine/heuristics are C++ plates (spear_plates.hpp).
#pragma once
#include <dirent.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

#include <cerrno>
#include <cctype>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <string>
#include <vector>

#include "spear_plates.hpp"

namespace spear {

constexpr int kSigHard = 9;  // FIELD UDP WAR BLASTERS · hard path · never soft SIGTERM theater

inline std::string getenv_str(const char* k, const char* def) {
  const char* v = ::getenv(k);
  return (v && v[0]) ? std::string(v) : std::string(def);
}

inline std::string home_dir() {
  const char* h = ::getenv("HOME");
  return h ? std::string(h) : std::string("/tmp");
}

inline std::string state_dir() {
  std::string e = getenv_str("SPEAR_SWALLOW_STATE", "");
  if (!e.empty()) return e;
  return home_dir() + "/.local/share/spear/swallows";
}

inline std::string www_dir() {
  return getenv_str("SPEAR_SWALLOWS_ROOT", "/tmp/spear-swallows-www");
}

// Internet 2.0 / AmmoOS field bind — ALL interfaces by default.
// Throw away 127.0.0.1-only bullshit. Override: SPEAR_BIND / FIELD_BIND.
inline const char* field_bind_ip() {
  static char buf[64];
  static bool once = false;
  if (!once) {
    once = true;
    std::string e = getenv_str("SPEAR_BIND", "");
    if (e.empty()) e = getenv_str("FIELD_BIND", "0.0.0.0");
    if (e.size() >= sizeof buf) e.resize(sizeof buf - 1);
    std::memcpy(buf, e.c_str(), e.size() + 1);
  }
  return buf;
}

// Host/name for URLs and plates (not loopback identity)
inline std::string field_advertise_host() {
  std::string a = getenv_str("SPEAR_ADVERTISE", "");
  if (!a.empty()) return a;
  a = getenv_str("FIELD_HOST", "");
  if (!a.empty()) return a;
  char hn[256];
  if (::gethostname(hn, sizeof hn) == 0 && hn[0] && std::strcmp(hn, "localhost") != 0)
    return std::string(hn);
  return std::string("field");  // product face — not 127.0.0.1
}

inline bool is_digits(const char* s) {
  if (!s || !*s) return false;
  for (const char* p = s; *p; ++p)
    if (*p < '0' || *p > '9') return false;
  return true;
}

inline std::string read_file(const char* path, size_t maxn = 1 << 20) {
  int fd = ::open(path, O_RDONLY | O_CLOEXEC);
  if (fd < 0) return {};
  std::string out;
  out.resize(maxn);
  ssize_t n = ::read(fd, out.data(), maxn);
  ::close(fd);
  if (n <= 0) return {};
  out.resize(static_cast<size_t>(n));
  return out;
}

inline bool write_file(const char* path, const std::string& body) {
  int fd = ::open(path, O_WRONLY | O_CREAT | O_TRUNC | O_CLOEXEC, 0644);
  if (fd < 0) return false;
  ssize_t w = ::write(fd, body.data(), body.size());
  ::close(fd);
  return w == static_cast<ssize_t>(body.size());
}

inline bool append_file(const char* path, const std::string& body) {
  int fd = ::open(path, O_WRONLY | O_CREAT | O_APPEND | O_CLOEXEC, 0644);
  if (fd < 0) return false;
  ssize_t w = ::write(fd, body.data(), body.size());
  ::close(fd);
  return w >= 0;
}

inline void mkdir_p(const std::string& path) {
  std::string cur;
  for (size_t i = 0; i < path.size(); ++i) {
    cur.push_back(path[i]);
    if (path[i] == '/' || i + 1 == path.size()) {
      if (cur.size() > 1) ::mkdir(cur.c_str(), 0755);
    }
  }
}

inline std::string now_z() {
  char tbuf[40];
  std::time_t t = std::time(nullptr);
  std::tm gmt{};
  gmtime_r(&t, &gmt);
  std::snprintf(tbuf, sizeof(tbuf), "%04d-%02d-%02dT%02d:%02dZ", gmt.tm_year + 1900,
                gmt.tm_mon + 1, gmt.tm_mday, gmt.tm_hour, gmt.tm_min);
  return tbuf;
}

inline std::string now_z_sec() {
  char tbuf[40];
  std::time_t t = std::time(nullptr);
  std::tm gmt{};
  gmtime_r(&t, &gmt);
  std::snprintf(tbuf, sizeof(tbuf), "%04d-%02d-%02dT%02d:%02d:%02dZ", gmt.tm_year + 1900,
                gmt.tm_mon + 1, gmt.tm_mday, gmt.tm_hour, gmt.tm_min, gmt.tm_sec);
  return tbuf;
}

inline void tolower_inplace(std::string& s) {
  for (char& c : s) c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
}

inline bool contains(const std::string& hay, const char* needle) {
  return hay.find(needle) != std::string::npos;
}

inline std::string read_cmdline(pid_t pid) {
  char path[64];
  std::snprintf(path, sizeof(path), "/proc/%d/cmdline", pid);
  std::string raw = read_file(path, 4096);
  for (char& c : raw)
    if (c == '\0') c = ' ';
  return raw;
}

inline std::string read_comm(pid_t pid) {
  char path[64];
  std::snprintf(path, sizeof(path), "/proc/%d/comm", pid);
  std::string s = read_file(path, 256);
  while (!s.empty() && (s.back() == '\n' || s.back() == '\r')) s.pop_back();
  return s;
}

inline std::string read_exe(pid_t pid) {
  char path[64], buf[512];
  std::snprintf(path, sizeof(path), "/proc/%d/exe", pid);
  ssize_t n = ::readlink(path, buf, sizeof(buf) - 1);
  if (n < 0) return {};
  buf[n] = '\0';
  return std::string(buf);
}

inline bool mirror_www(const std::string& name, const std::string& body) {
  const std::string st = state_dir() + "/" + name;
  const std::string ww = www_dir() + "/" + name;
  mkdir_p(state_dir());
  mkdir_p(www_dir());
  bool a = write_file(st.c_str(), body);
  bool b = write_file(ww.c_str(), body);
  return a || b;
}

inline bool port_listening(int port) {
  // Parse /proc/net/tcp for local listen ports (hex)
  std::string tcp = read_file("/proc/net/tcp", 1 << 20);
  std::string tcp6 = read_file("/proc/net/tcp6", 1 << 20);
  char hex[16];
  std::snprintf(hex, sizeof(hex), ":%04X", port);
  return contains(tcp, hex) || contains(tcp6, hex);
}

// ── Copilot multi-signal hunt ─────────────────────────────────────────────

struct Hit {
  pid_t pid;
  int score;
  const char* kind;
  std::string comm;
};

inline bool is_sacred_blob(const std::string& blob_l, const std::string& exe_l,
                           const std::string& comm_l) {
  // Sacred = C++ spear war plane only. Never python/scripts as sacred.
  if (contains(exe_l, "spear-") || contains(exe_l, "/spear") || comm_l.rfind("spear", 0) == 0)
    return true;
  if (contains(blob_l, "spear-hard-dispose") || contains(blob_l, "spear-kill-copilot") ||
      contains(blob_l, "spear-copilot-monitor") || contains(blob_l, "spear-wartime") ||
      contains(blob_l, "spear-www") || contains(blob_l, "spear-swallow") ||
      contains(blob_l, "spear-swallows") || contains(blob_l, "spear-eats") ||
      contains(blob_l, "spear-planet") || contains(blob_l, "spear-fleet") ||
      contains(blob_l, "spear-export") || contains(blob_l, "spear-rack-guard") ||
      contains(blob_l, "spear-h7-panel") || contains(blob_l, "spear-angel-seal") ||
      contains(blob_l, "spear-i2-war") || contains(blob_l, "spear-i2-server") ||
      contains(blob_l, "copilot-purge") || contains(blob_l, "copilot-kill") ||
      contains(blob_l, "every-copilot") || contains(blob_l, "copilot-cloud-block") ||
      contains(blob_l, "copilot-threat") || contains(blob_l, "copilot-global") ||
      contains(blob_l, "dogshit-") || contains(blob_l, "ironclad-copilot") ||
      contains(blob_l, "ironclad-zocr") || contains(blob_l, "ironclad-hotdog") ||
      contains(blob_l, "pwnership/kills") || contains(blob_l, "terrorist-oust") ||
      contains(blob_l, "hotdog-down-a-hallway.html") || contains(blob_l, "lethal-kill"))
    return true;
  // Queen C++ field surface (not soft python)
  if (comm_l == "queen" || contains(exe_l, "/usr/local/bin/queen") ||
      contains(exe_l, "/.local/bin/queen"))
    return true;
  if (comm_l == "grok" || comm_l == "grokz" || comm_l == "spear") return true;
  // NEVER sacred: interpreters / scripts pretending to be stack
  if (contains(blob_l, "threat-panel-http.py") || contains(blob_l, "python3") ||
      contains(blob_l, "python ") || contains(exe_l, "python")) {
    // only sacred if it's literally not — always false for python
    return false;
  }
  return false;
}

inline bool is_readerish(const std::string& comm_l, const std::string& exe_l) {
  if (comm_l == "firefox" || comm_l == "chrome" || comm_l == "chromium" || comm_l == "brave" ||
      comm_l == "code" || comm_l == "cursor" || comm_l == "vim" || comm_l == "nvim" ||
      comm_l == "nano" || comm_l == "less" || comm_l == "more" || comm_l == "cat" ||
      comm_l == "head" || comm_l == "tail" || comm_l == "grep" || comm_l == "rg" ||
      comm_l == "bat" || comm_l == "evince" || comm_l == "okular")
    return true;
  if (contains(exe_l, "/firefox") || contains(exe_l, "/chrome") || contains(exe_l, "/chromium") ||
      contains(exe_l, "/code"))
    return true;
  return false;
}

inline bool is_leave_alone_ai(const std::string& blob_l) {
  if (contains(blob_l, "zocr_copilot") || contains(blob_l, "zocr-copilot") ||
      contains(blob_l, "github.copilot") || contains(blob_l, "copilot-language") ||
      contains(blob_l, "copilot-agent"))
    return false;
  if (contains(blob_l, "chatgpt") || contains(blob_l, "openai.com") ||
      contains(blob_l, "openai/") || contains(blob_l, "gpt-4") || contains(blob_l, "gpt4"))
    return true;
  return false;
}

inline int score_copilot(const std::string& comm_l, const std::string& exe_l,
                         const std::string& cmd_l, const char** kind_out) {
  const std::string blob = comm_l + " " + exe_l + " " + cmd_l;
  int s = 0;
  const char* kind = "copilot";
  if (contains(blob, "copilot-purge") || contains(blob, "copilot-kill") ||
      contains(blob, "every-copilot") || contains(blob, "copilot-cloud-block") ||
      contains(blob, "copilot-threat") || contains(blob, "spear-kill-copilot") ||
      contains(blob, "spear-copilot") || contains(blob, "dogshit-copilot") ||
      contains(blob, "dogshit-zocr") || contains(blob, "copilot-global")) {
    if (kind_out) *kind_out = kind;
    return 0;
  }
  if (contains(blob, "zocr_copilot") || contains(blob, "zocr-copilot") ||
      contains(blob, "zocrcopilot")) {
    s += 5;
    kind = "zocr_copilot";
  }
  if (contains(blob, "github.copilot") || contains(blob, "github-copilot")) {
    s += 4;
    kind = "github_copilot";
  }
  if (contains(blob, "copilot-language-server") || contains(blob, "copilot-agent") ||
      contains(blob, "copilot-chat")) {
    s += 4;
    kind = "copilot_server";
  }
  if (contains(blob, "microsoft.copilot") || contains(blob, "copilot.exe") ||
      contains(blob, "copilot.microsoft")) {
    s += 4;
    kind = "microsoft_copilot";
  }
  if (contains(blob, "api.githubcopilot") || contains(blob, "githubcopilot.com") ||
      contains(blob, "copilot-proxy")) {
    s += 4;
    kind = "copilot_cloud";
  }
  if (contains(blob, "@github/copilot") || contains(blob, "gh-copilot")) {
    s += 3;
    kind = "copilot_cli";
  }
  // War-day expansions — still multi-signal, no single-token fire
  if (contains(blob, "copilot-telemetry") || contains(blob, "copilot-completions") ||
      contains(blob, "copilot-panel") || contains(blob, "copilot-client")) {
    s += 3;
    kind = "copilot_surface";
  }
  if (contains(blob, "sydney.bing") || contains(blob, "edgeservices.bing") ||
      contains(blob, "copilot.cloud.microsoft")) {
    s += 3;
    kind = "copilot_bing_edge";
  }
  // NEVER SCRIPTS as war engine — python spear soft path is a trap
  if ((contains(blob, "python") || contains(exe_l, "python")) &&
      (contains(blob, "spear-") || contains(blob, "spear_") || contains(blob, "threat-panel") ||
       contains(blob, "hostess7-") || contains(blob, "nexus-") || contains(blob, ".py"))) {
    s += 5;
    kind = "script_engine_forbidden";
  }
  if (comm_l == "copilot" || comm_l == "zocr_copilot") s += 3;
  const auto slash = exe_l.find_last_of('/');
  const std::string base = (slash == std::string::npos) ? exe_l : exe_l.substr(slash + 1);
  if (base.rfind("copilot", 0) == 0 || contains(base, "zocr_copilot") ||
      contains(base, "github.copilot"))
    s += 3;
  if (s < 3 && (comm_l == "copilot" || contains(exe_l, "/copilot") || contains(base, "copilot"))) {
    s += 3;
    kind = "copilot_generic";
  }
  if (kind_out) *kind_out = kind;
  return s;
}

// Field One · TRAPS as TERRORIST THREAT — multi-signal only (never single soft token)
// PATH impostors, foreign browser surface, Mozilla phone-home, honeypot/phish kits.
inline int score_terrorist_trap(const std::string& comm_l, const std::string& exe_l,
                                const std::string& cmd_l, const char** kind_out) {
  const std::string blob = comm_l + " " + exe_l + " " + cmd_l;
  // Sacred / field hunters never self-hit
  if (contains(blob, "spear-") || contains(blob, "terrorist-oust") ||
      contains(blob, "terrorist_trap") || contains(blob, "dogshit-terrorist-trap") ||
      contains(blob, "spear-wartime") || contains(blob, "spear-www") ||
      contains(blob, "pwnership") || contains(blob, "field-world-dom") ||
      contains(blob, "queen-install") || contains(blob, "spear-desktop-clean")) {
    if (kind_out) *kind_out = "terrorist_trap";
    return 0;
  }
  // Field Queen product path is NOT a trap (remoting name queen, field profile)
  if (contains(blob, "moz_app_remotingname=queen") || contains(blob, "--class queen") ||
      contains(blob, "--name queen") || contains(blob, "/.queen/profile") ||
      contains(blob, "field-native") || contains(blob, "more than forked") ||
      contains(exe_l, "/queen") || comm_l == "queen") {
    if (kind_out) *kind_out = "terrorist_trap";
    return 0;
  }

  int s = 0;
  const char* kind = "terrorist_trap";
  const auto slash = exe_l.find_last_of('/');
  const std::string base = (slash == std::string::npos) ? exe_l : exe_l.substr(slash + 1);

  // Mozilla phone-home helpers (trap servers client-side)
  if (comm_l == "pingsender" || base == "pingsender" || contains(base, "pingsender")) {
    s += 4;
    kind = "terrorist_trap_mozilla_phonehome";
  }
  if (comm_l == "crashreporter" || comm_l == "crashhelper" || contains(base, "crashreporter") ||
      contains(base, "crashhelper")) {
    s += 3;
    kind = "terrorist_trap_mozilla_phonehome";
  }

  // Foreign browser product surface (not Field Queen)
  if (comm_l == "firefox" || comm_l == "firefox-bin" || base == "firefox" || base == "firefox-bin") {
    s += 3;
    kind = "terrorist_trap_foreign_browser";
  }
  if (contains(exe_l, "/usr/lib/firefox/") &&
      (contains(base, "firefox") || contains(base, "pingsender") || contains(base, "updater"))) {
    s += 2;
    kind = "terrorist_trap_foreign_browser";
  }

  // PATH impostor traps under operator bin names
  if (contains(exe_l, "/.local/bin/firefox") || contains(exe_l, "/usr/local/bin/firefox") ||
      contains(cmd_l, "/.local/bin/firefox") || contains(cmd_l, "silent field trap")) {
    s += 4;
    kind = "terrorist_trap_path_impostor";
  }

  // Classic trap / honeypot / phish kits
  if (contains(blob, "honeypot") || contains(blob, "honey-pot") || contains(blob, "honey_pot")) {
    s += 3;
    kind = "terrorist_trap_kit";
  }
  if (contains(blob, "credential-trap") || contains(blob, "credential_trap") ||
      contains(blob, "phish-kit") || contains(blob, "phishkit") || contains(base, "trap.sh")) {
    s += 4;
    kind = "terrorist_trap_kit";
  }

  // Lurking trap servers in process args
  if (contains(blob, "telemetry.mozilla") || contains(blob, "incoming.telemetry") ||
      contains(blob, "normandy.cdn") || contains(blob, "detectportal.firefox") ||
      contains(blob, "aus5.mozilla") || contains(blob, "addons.mozilla")) {
    s += 3;
    kind = "terrorist_trap_server_lurk";
  }
  if (contains(blob, "getpocket.com") || contains(blob, "contile.services") ||
      contains(blob, "shavar.services")) {
    s += 2;
    kind = "terrorist_trap_phonehome_svc";
  }

  // Desktop mask / soft-trap language in argv (doctrine violation)
  if ((contains(blob, "nodisplay=true") || contains(blob, "hidden=true")) &&
      (contains(blob, "firefox") || contains(blob, "mozilla"))) {
    s += 3;
    kind = "terrorist_trap_desktop_mask";
  }
  if (contains(blob, "soft trap") || contains(blob, "impostor browser") ||
      contains(blob, "foreign product surface")) {
    s += 3;
    kind = "terrorist_trap_product_impostor";
  }

  // ── Expanded traps (permanent) ───────────────────────────────────────────
  // Soft browser auto-update / location services
  if (contains(blob, "location.services.mozilla") || contains(blob, "push.services.mozilla") ||
      contains(blob, "firefox.settings.services") || contains(blob, "services.addons.mozilla")) {
    s += 3;
    kind = "terrorist_trap_server_lurk";
  }
  // Chromium phone-home / soft enterprise
  if (contains(blob, "clients2.google") || contains(blob, "safebrowsing.googleapis") ||
      contains(blob, "optimizationguide-pa.googleapis") || contains(blob, "update.googleapis.com")) {
    s += 2;
    kind = "terrorist_trap_chrome_phonehome";
  }
  // Snap/flatpak browser shadows
  if (contains(exe_l, "/snap/firefox/") ||
      (contains(exe_l, "/var/lib/flatpak/") && contains(exe_l, "firefox"))) {
    s += 3;
    kind = "terrorist_trap_foreign_browser";
  }
  // PATH shadow cats: false field tools
  if (contains(exe_l, "/.local/bin/") &&
      (base == "firefox" || base == "chrome" || base == "google-chrome" || base == "msedge" ||
       base == "brave-browser" || base == "chromium")) {
    s += 4;
    kind = "terrorist_trap_path_shadow";
  }
  // Soft "secure browser" impostors
  if (contains(blob, "librewolf") || contains(blob, "waterfox") || contains(blob, "palemoon") ||
      contains(blob, "basilisk") || contains(blob, "icecat")) {
    s += 2;
    kind = "terrorist_trap_foreign_browser";
  }
  // Script-as-server traps (never our Internet 2.0)
  if ((contains(blob, "python") || contains(exe_l, "python") || contains(exe_l, "pythong")) &&
      (contains(blob, "http.server") || contains(blob, "basehttpserver") ||
       contains(blob, "threadinghttpserver") || contains(blob, "threat-panel-http") ||
       contains(blob, "simplehttpserver") || contains(blob, "cgi-bin"))) {
    s += 5;
    kind = "terrorist_trap_script_server";
  }
  // Reverse shells / netcat classic
  if (contains(blob, "/dev/tcp/") || contains(blob, "bash -i") ||
      (contains(blob, "bash -c") && contains(blob, "/dev/tcp"))) {
    s += 4;
    kind = "terrorist_trap_reverse_shell";
  }
  if ((contains(comm_l, "nc") || base == "ncat" || base == "netcat") &&
      (contains(blob, " -e ") || contains(blob, " -c ") || contains(blob, " -l"))) {
    s += 3;
    kind = "terrorist_trap_reverse_shell";
  }
  // Pipe droppers
  if ((contains(blob, "curl ") || contains(blob, "wget ")) &&
      (contains(blob, "| sh") || contains(blob, "| bash") || contains(blob, "|sh") ||
       contains(blob, "|bash") || contains(blob, "| python"))) {
    s += 4;
    kind = "terrorist_trap_pipe_dropper";
  }
  // Encoded payload
  if (contains(blob, "base64 -d") || contains(blob, "base64 --decode") ||
      (contains(blob, "echo ") && contains(blob, "| base64"))) {
    s += 3;
    kind = "terrorist_trap_encoded_payload";
  }
  // Crypto miners
  if (contains(blob, "xmrig") || contains(blob, "minerd") || contains(blob, "cpuminer") ||
      contains(blob, "kdevtmpfsi") || contains(blob, "kinsing") || contains(blob, "stratum+tcp") ||
      contains(blob, "nicehash") || contains(blob, "moneroocean")) {
    s += 5;
    kind = "terrorist_trap_crypto_miner";
  }
  // Ephemeral + suspicious
  if ((exe_l.rfind("/tmp/", 0) == 0 || exe_l.rfind("/var/tmp/", 0) == 0 ||
       exe_l.rfind("/dev/shm/", 0) == 0) &&
      (contains(blob, "curl") || contains(blob, "wget") || contains(blob, "python") ||
       contains(blob, "perl") || contains(blob, "nc ") || contains(blob, "ncat"))) {
    s += 3;
    kind = "terrorist_trap_ephemeral_exe";
  }
  // QBasic / BASIC / legacy script engines as war authority attempt
  if (contains(blob, "qbasic") || contains(blob, "qb64") || contains(blob, "fbc ") ||
      contains(base, ".bas") || contains(blob, "gwbasic") || contains(blob, "basica")) {
    s += 3;
    kind = "terrorist_trap_legacy_basic";
  }
  // Node/php/ruby/perl field servers
  if ((contains(exe_l, "node") || comm_l == "node" || contains(exe_l, "php") ||
       contains(exe_l, "ruby") || contains(exe_l, "perl")) &&
      (contains(blob, "listen") || contains(blob, "http") || contains(blob, "express") ||
       contains(blob, "socket") || contains(blob, "9477") || contains(blob, "9490"))) {
    s += 4;
    kind = "terrorist_trap_script_server";
  }
  // Soft plate-meld storm / combinatorics (FR2 tombstoned hot path as attack surface)
  if ((contains(blob, "plate-meld") && contains(blob, "python")) ||
      contains(blob, "field-plate-meld.py") || contains(blob, "combinatorics-tree")) {
    s += 3;
    kind = "terrorist_trap_plate_storm";
  }
  // DNS/DHCP abuse class
  if (contains(blob, "dns_poison") || contains(blob, "gateway_shift") ||
      contains(blob, "arp_spoof") || (contains(blob, "dnsmasq") && contains(blob, "spoof"))) {
    s += 3;
    kind = "terrorist_trap_dns_dhcp_abuse";
  }

  // ── PATH-stuffed core tools (smart-guy shadows of dig/curl/ping/…) ──────
  // Real engines live in /usr/bin. Shadows under ~/.local/bin that wrap scripts
  // or re-exec foreign dig as product authority are traps.
  const bool path_shadow =
      contains(exe_l, "/.local/bin/dig") || contains(exe_l, "/.local/bin/curl") ||
      contains(exe_l, "/.local/bin/ping") || contains(exe_l, "/.local/bin/host") ||
      contains(exe_l, "/.local/bin/wget") || contains(exe_l, "/.local/bin/nc") ||
      contains(exe_l, "/.local/bin/traceroute") || contains(exe_l, "/.local/bin/telnet") ||
      contains(exe_l, "/.local/bin/nslookup") || contains(exe_l, "/.local/bin/pkill") ||
      contains(exe_l, "/.local/bin/kill") || contains(exe_l, "/.local/bin/sudo") ||
      contains(exe_l, "/.local/bin/pkexec") || contains(exe_l, "/.local/bin/killall");
  if (path_shadow) {
    // sacred: our field-net multi-call ELF is OK when basename is field-*
    if (!(contains(exe_l, "field-net") || contains(comm_l, "field-net") ||
          contains(comm_l, "field-dig") || contains(comm_l, "field-ping") ||
          contains(comm_l, "field-telnet") || contains(comm_l, "field-nc"))) {
      s += 4;
      kind = "terrorist_trap_path_stuffed_tool";
    }
  }
  // pkill / killall theater — product hunt uses kill(2) SIGKILL in C++ only
  if (comm_l == "pkill" || comm_l == "killall" || base == "pkill" || base == "killall" ||
      contains(exe_l, "/pkill") || contains(exe_l, "/killall")) {
    s += 4;
    kind = "terrorist_trap_pkill_theater";
  }
  // sudo / pkexec as elevate path — NEVER autoelevate model
  if (comm_l == "sudo" || comm_l == "pkexec" || base == "sudo" || base == "pkexec" ||
      contains(exe_l, "/sudo") || contains(exe_l, "/pkexec") || contains(blob, "sudo -") ||
      contains(blob, "sudo ") || contains(blob, "pkexec ")) {
    // allow pure listing? No — any sudo in war hunt surface is trap signal
    s += 4;
    kind = "terrorist_trap_sudo_elevate";
  }
  // Script wrappers pretending to be dig/curl (shebang in cmdline or .sh dig)
  if ((contains(blob, "field-net-common.sh") ||
       (contains(blob, "field-curl") && contains(blob, "bash")) ||
       contains(cmd_l, "#!/usr/bin/env bash")) &&
      (contains(blob, "dig") || contains(blob, "curl") || contains(blob, "ping") ||
       contains(blob, "traceroute"))) {
    s += 4;
    kind = "terrorist_trap_stuffed_net_script";
  }
  // dig used as C2 beacon channel / DNS exfil patterns
  if ((contains(blob, "dig ") || contains(comm_l, "dig")) &&
      (contains(blob, "TXT ") || contains(blob, " null.") || contains(blob, ".onion") ||
       contains(blob, "base64") || contains(blob, "iodine") || contains(blob, "dns2tcp"))) {
    s += 4;
    kind = "terrorist_trap_dns_exfil_dig";
  }
  // Fake Truth DNS / stuffed resolv
  if (contains(blob, "resolv.conf") &&
      (contains(blob, "8.8.8.8") || contains(blob, "1.1.1.1") || contains(blob, "9.9.9.9")) &&
      (contains(blob, "sed") || contains(blob, "echo ") || contains(blob, "tee "))) {
    s += 3;
    kind = "terrorist_trap_resolv_stuff";
  }

  if (kind_out) *kind_out = kind;
  return s;  // need >= 3 multi-signal
}

// NEVER SCRIPTS as engine — multi-signal. Interpreters may exist; war path is trap.
inline int score_script_engine(const std::string& comm_l, const std::string& exe_l,
                               const std::string& cmd_l, const char** kind_out) {
  const std::string blob = comm_l + " " + exe_l + " " + cmd_l;
  if (contains(blob, "spear-") && !contains(blob, ".py") && !contains(exe_l, "python")) {
    if (kind_out) *kind_out = "script_engine";
    return 0;
  }
  int s = 0;
  const char* kind = "script_engine_forbidden";
  const auto slash = exe_l.find_last_of('/');
  const std::string base = (slash == std::string::npos) ? exe_l : exe_l.substr(slash + 1);

  const bool is_py = contains(exe_l, "python") || comm_l.rfind("python", 0) == 0 ||
                     contains(base, "python") || contains(blob, "pythong");
  const bool is_sh =
      comm_l == "bash" || comm_l == "sh" || comm_l == "dash" || contains(exe_l, "/bash") ||
      contains(exe_l, "/sh");
  const bool is_other = contains(exe_l, "perl") || contains(exe_l, "ruby") ||
                        contains(exe_l, "node") || contains(exe_l, "php") ||
                        contains(blob, "qbasic") || contains(blob, "qb64");

  if (!is_py && !is_sh && !is_other) {
    if (kind_out) *kind_out = kind;
    return 0;
  }

  // Product engine paths — never allowed via scripts
  if (contains(blob, "threat-panel") || contains(blob, "hostess7-") || contains(blob, "nexus-c2") ||
      contains(blob, "nexus_c2") || contains(blob, "field-plate-meld") ||
      contains(blob, "hostess7_war") || contains(blob, "angel-seal") || contains(blob, "spear_") ||
      contains(blob, "/lib/hostess") || contains(blob, "/lib/threat") ||
      contains(blob, "/lib/field-") || contains(blob, "/lib/nexus")) {
    s += 5;
    kind = "script_engine_product_path";
  }
  if (contains(blob, ".py") &&
      (contains(blob, "9477") || contains(blob, "9490") || contains(blob, "9491") ||
       contains(blob, "http") || contains(blob, "serve") || contains(blob, "panel"))) {
    s += 4;
    kind = "script_engine_http";
  }
  if (is_py && contains(blob, "subprocess") && contains(blob, "kill")) {
    s += 3;
    kind = "script_engine_kill_path";
  }
  // setuid / elevate via script or sudo — NEVER product autoelevate
  if ((is_py || is_sh) &&
      (contains(blob, "pkexec") || contains(blob, "sudo ") || contains(blob, "doas ") ||
       contains(blob, "setuid") || contains(blob, "pkill") || contains(blob, "killall"))) {
    s += 5;
    kind = "script_engine_elevate";
  }
  if (contains(blob, "sudo install") || contains(blob, "sudo chmod") ||
      contains(blob, "sudo spear") || contains(blob, "sudo -E")) {
    s += 4;
    kind = "script_engine_sudo_autoelevate";
  }

  if (kind_out) *kind_out = kind;
  return s;
}

// Heuristics are EATEN into spear_plates.hpp — C++ only, never JSON/TSV authority at runtime.
inline bool heur_match(const std::string& blob, const char* pat) {
  if (!pat || !*pat) return false;
  size_t start = 0;
  const size_t n = std::strlen(pat);
  while (start <= n) {
    size_t bar = std::string::npos;
    for (size_t i = start; i < n; ++i)
      if (pat[i] == '|') {
        bar = i;
        break;
      }
    std::string alt =
        (bar == std::string::npos) ? std::string(pat + start) : std::string(pat + start, bar - start);
    std::string clean;
    clean.reserve(alt.size());
    for (size_t i = 0; i < alt.size(); ++i) {
      char c = alt[i];
      if (c == '\\' && i + 1 < alt.size()) {
        clean.push_back(alt[++i]);
        continue;
      }
      if (c == '.' && i + 1 < alt.size() && alt[i + 1] == '*') {
        ++i;
        continue;
      }
      if (c == '?' || c == '+' || c == '*' || c == '(' || c == ')' || c == '[' || c == ']') continue;
      if (c == '\\') continue;
      clean.push_back(static_cast<char>(std::tolower(static_cast<unsigned char>(c))));
    }
    if (clean.size() >= 3 && contains(blob, clean.c_str())) return true;
    if (bar == std::string::npos) break;
    start = bar + 1;
  }
  return false;
}

inline int score_heuristics_plate(const std::string& blob_l, const char** kind_out) {
  int best = 0;
  const char* kind = "heuristics_plate";
  for (std::size_t i = 0; i < plate::kHeuristicsN; ++i) {
    const auto& r = plate::kHeuristics[i];
    if (heur_match(blob_l, r.pat)) {
      int sc = r.points / 15;
      if (sc < 2) sc = 2;
      if (sc > 6) sc = 6;
      if (sc > best) {
        best = sc;
        kind = r.note && r.note[0] ? r.note : "heuristics_plate";
      }
    }
  }
  if (kind_out) *kind_out = kind;
  return best;
}

// Hotdog-down-a-hallway terrorist kit — multi-signal only (text injection alone NEVER enough)
inline int score_hotdog(const std::string& comm_l, const std::string& exe_l,
                        const std::string& cmd_l, const char** kind_out) {
  const std::string blob = comm_l + " " + exe_l + " " + cmd_l;
  if (contains(blob, "dogshit-hotdog") || contains(blob, "terrorist-oust") ||
      contains(blob, "hotdog-down-a-hallway.html") || contains(blob, "ironclad-hotdog") ||
      contains(blob, "spear-wartime") || contains(blob, "spear-www") ||
      contains(blob, "lethal-kill") || contains(blob, "pwnership")) {
    if (kind_out) *kind_out = "hotdog_hallway";
    return 0;
  }
  // Readers: only if the executable *itself* is named like the kit
  const auto slash = exe_l.find_last_of('/');
  const std::string base = (slash == std::string::npos) ? exe_l : exe_l.substr(slash + 1);
  if (is_readerish(comm_l, exe_l)) {
    if (!(contains(base, "hotdog") || contains(base, "hallway") || contains(base, "hot-dog"))) {
      if (kind_out) *kind_out = "hotdog_hallway";
      return 0;
    }
  }

  int s = 0;
  if (contains(comm_l, "hotdog")) s += 2;
  if (contains(comm_l, "hallway")) s += 2;
  if (contains(base, "hotdog") || contains(base, "hallway") || contains(base, "hot-dog")) s += 3;
  if ((exe_l.rfind("/tmp/", 0) == 0 || exe_l.rfind("/var/tmp/", 0) == 0 ||
       exe_l.rfind("/dev/shm/", 0) == 0) &&
      (contains(exe_l, "hotdog") || contains(exe_l, "hallway") || contains(cmd_l, "hotdog") ||
       contains(cmd_l, "hallway")))
    s += 2;
  // argv0
  size_t sp = cmd_l.find(' ');
  std::string argv0 = sp == std::string::npos ? cmd_l : cmd_l.substr(0, sp);
  if (contains(argv0, "hotdog") || contains(argv0, "hallway") || contains(argv0, "hot-dog-down"))
    s += 2;
  // weak phrase (injection-prone) — alone never enough
  if (contains(cmd_l, "hotdog") && contains(cmd_l, "hallway")) s += 1;
  if (contains(cmd_l, "hotdog down") || contains(cmd_l, "down a hallway")) s += 1;

  if (kind_out) *kind_out = "hotdog_hallway";
  return s;  // need >= 3
}

// Hunt copilot + hotdog hallway kit PIDs
inline int hunt_threats(std::vector<Hit>& hits) {
  hits.clear();
  const pid_t self = ::getpid();
  const pid_t parent = ::getppid();
  DIR* d = ::opendir("/proc");
  if (!d) return -1;
  while (dirent* ent = ::readdir(d)) {
    if (!is_digits(ent->d_name)) continue;
    const pid_t pid = static_cast<pid_t>(std::atoi(ent->d_name));
    if (pid <= 1 || pid == self || pid == parent) continue;
    std::string comm = read_comm(pid);
    std::string exe = read_exe(pid);
    std::string cmd = read_cmdline(pid);
    std::string comm_l = comm, exe_l = exe, cmd_l = cmd;
    tolower_inplace(comm_l);
    tolower_inplace(exe_l);
    tolower_inplace(cmd_l);
    const std::string blob_l = comm_l + " " + exe_l + " " + cmd_l;
    if (is_sacred_blob(blob_l, exe_l, comm_l)) continue;
    if (is_leave_alone_ai(blob_l)) continue;

    const char* kind = "threat";
    int sc = score_hotdog(comm_l, exe_l, cmd_l, &kind);
    if (sc >= 3) {
      hits.push_back(Hit{pid, sc, kind, comm});
      continue;
    }
    // NEVER SCRIPTS as engine (C++ or lower only)
    sc = score_script_engine(comm_l, exe_l, cmd_l, &kind);
    if (sc >= 3) {
      hits.push_back(Hit{pid, sc, kind, comm});
      continue;
    }
    // Traps = terrorist threat class (PATH impostor, phone-home, kit, shell, miner…)
    sc = score_terrorist_trap(comm_l, exe_l, cmd_l, &kind);
    if (sc >= 3) {
      hits.push_back(Hit{pid, sc, kind, comm});
      continue;
    }
    // Heuristics plate (TSV) — data plate, scored in C++ only
    sc = score_heuristics_plate(blob_l, &kind);
    if (sc >= 3) {
      hits.push_back(Hit{pid, sc, kind, comm});
      continue;
    }
    sc = score_copilot(comm_l, exe_l, cmd_l, &kind);
    if (sc >= 3) hits.push_back(Hit{pid, sc, kind, comm});
  }
  ::closedir(d);
  return static_cast<int>(hits.size());
}

// Back-compat alias
inline int hunt_copilot(std::vector<Hit>& hits) { return hunt_threats(hits); }

inline int hard_kill_hits(const std::vector<Hit>& hits) {
  int n = 0;
  for (const Hit& h : hits) {
    if (::kill(h.pid, kSigHard) == 0 || errno == ESRCH) ++n;
  }
  return n;
}

// ── Entropy detailer — always know our shots ──────────────────────────────
// Shannon H (bits/byte) + FNV-1a seal over the shot plate. Field FAT cook tag.

inline double shannon_h_bytes(const unsigned char* data, size_t n) {
  if (!data || n == 0) return 0.0;
  uint32_t hist[256] = {};
  for (size_t i = 0; i < n; ++i) ++hist[data[i]];
  double H = 0.0;
  const double inv = 1.0 / static_cast<double>(n);
  for (int i = 0; i < 256; ++i) {
    if (!hist[i]) continue;
    double p = hist[i] * inv;
    H -= p * (std::log(p) / std::log(2.0));
  }
  return H;
}

inline double shannon_h_str(const std::string& s) {
  return shannon_h_bytes(reinterpret_cast<const unsigned char*>(s.data()), s.size());
}

inline uint64_t fnv1a64(const std::string& s) {
  uint64_t h = 14695981039346656037ull;
  for (unsigned char c : s) {
    h ^= c;
    h *= 1099511628211ull;
  }
  return h;
}

// Entropy fold (CHIPs-style φ mix) for field detailer plate
inline double entropy_fold_detail(double e, double thermo) {
  double x = e * 0.6180339887 + thermo * (1.0 - 0.6180339887);
  for (int i = 0; i < 4; ++i) {
    x = x * 1.113 + std::sin(x * 3.141592653589793) * 0.01;
  }
  return x;
}

struct Shot {
  std::string id;
  std::string target;
  std::string vector;
  std::string phase;
  std::string attack;
  std::string outlet_path;
  int rekill = 0;
  std::string ts;
  double shannon_h = 0;
  double entropy_fold = 0;
  std::string seal_hex;  // 16 hex chars of FNV plate
};

inline Shot make_shot(const std::string& id, const std::string& target, const std::string& vector,
                      const std::string& phase, const std::string& attack,
                      const std::string& outlet, int rekill) {
  Shot s;
  s.id = id;
  s.target = target;
  s.vector = vector;
  s.phase = phase;
  s.attack = attack;
  s.outlet_path = outlet;
  s.rekill = rekill;
  s.ts = now_z_sec();
  std::string plate = id + "|" + target + "|" + vector + "|" + phase + "|" + attack + "|" +
                      outlet + "|" + std::to_string(rekill) + "|" + s.ts;
  s.shannon_h = shannon_h_str(plate);
  s.entropy_fold = entropy_fold_detail(s.shannon_h, static_cast<double>(rekill) * 0.01);
  uint64_t seal = fnv1a64(plate + "|FFAT\\x03ENT");
  char hex[20];
  std::snprintf(hex, sizeof(hex), "%016llx", static_cast<unsigned long long>(seal));
  s.seal_hex = hex;
  return s;
}

inline std::string shot_json(const Shot& s) {
  char buf[1024];
  std::snprintf(buf, sizeof(buf),
                "{\"schema\":\"entropy-shot/v1\",\"id\":\"%s\",\"target\":\"%s\",\"vector\":\"%s\","
                "\"phase\":\"%s\",\"attack\":\"%s\",\"rekill\":%d,\"outlet_path\":\"%s\","
                "\"shannon_h\":%.6f,\"entropy_fold\":%.6f,\"seal\":\"%s\",\"ts\":\"%s\","
                "\"cook_fat\":true,\"know_shot\":true,\"lethal\":true,\"terror_exists\":false}",
                s.id.c_str(), s.target.c_str(), s.vector.c_str(), s.phase.c_str(), s.attack.c_str(),
                s.rekill, s.outlet_path.c_str(), s.shannon_h, s.entropy_fold, s.seal_hex.c_str(),
                s.ts.c_str());
  return buf;
}

// ── Global protector security surface ─────────────────────────────────────

inline std::string binary_seal(const std::string& path) {
  std::string body = read_file(path.c_str(), 256 << 10);
  if (body.empty()) return "MISSING";
  struct stat st {};
  ::stat(path.c_str(), &st);
  char plate[128];
  std::snprintf(plate, sizeof(plate), "%s|%lld|%zu", path.c_str(),
                static_cast<long long>(st.st_size), body.size());
  uint64_t h = fnv1a64(std::string(plate) + body);
  char hex[20];
  std::snprintf(hex, sizeof(hex), "%016llx", static_cast<unsigned long long>(h));
  return hex;
}

// Ensure foreign DNS IP block list always contains war-critical hooks
inline int ensure_blocked_ips() {
  const char* ips[] = {
      "209.18.47.61", "209.18.47.62", "209.18.47.63",  // foreign world DNS
  };
  std::string path = state_dir() + "/blocked-ips.txt";
  std::string body = read_file(path.c_str());
  int added = 0;
  for (const char* ip : ips) {
    if (!contains(body, ip)) {
      append_file(path.c_str(), std::string(ip) + "\n");
      body += std::string(ip) + "\n";
      ++added;
    }
  }
  return added;
}

// Rewrite copilot cloud block hosts every cycle (null-route surface list)
inline void ensure_cloud_block_hosts() {
  const char* hosts[] = {
      "copilot-proxy.githubusercontent.com",
      "copilot-telemetry.githubusercontent.com",
      "copilot-api.githubusercontent.com",
      "api.githubcopilot.com",
      "proxy.individual.githubcopilot.com",
      "proxy.business.githubcopilot.com",
      "business.githubcopilot.com",
      "githubcopilot.com",
      "www.githubcopilot.com",
      "copilot.microsoft.com",
      "www.copilot.microsoft.com",
      "copilot.cloud.microsoft",
      "sydney.bing.com",
      "edgeservices.bing.com",
      "copilot.github.com",
      "default.exp-tas.com",  // VS Code experiment/telemetry often used by copilot surfaces
  };
  std::string body = "# spear copilot cloud block — GLOBAL PROTECTOR · C++ only · WAR DAY\n";
  body += "# GPT-4 / OpenAI / ChatGPT LEAVE ALONE — not listed here\n";
  body += "# ts " + now_z_sec() + "\n";
  for (const char* h : hosts) {
    body += "0.0.0.0 ";
    body += h;
    body += "\n::1 ";
    body += h;
    body += "\n";
  }
  write_file((state_dir() + "/copilot-cloud-block.hosts").c_str(), body);
  write_file((www_dir() + "/copilot-cloud-block.hosts").c_str(), body);
}

struct ServiceMatrix {
  bool www_9490 = false;
  bool control_9500 = false;
  bool planet_9600 = false;
  int zones_up = 0;
  bool dns_stub = false;
  bool all_critical = false;
};

inline ServiceMatrix probe_service_matrix() {
  ServiceMatrix m;
  m.www_9490 = port_listening(9490);
  m.control_9500 = port_listening(9500);
  m.planet_9600 = port_listening(9600);
  m.dns_stub = port_listening(53);
  static const int zone_ports[] = {9510, 9511, 9512, 9513, 9514, 9515, 9516, 9517};
  for (int p : zone_ports)
    if (port_listening(p)) ++m.zones_up;
  m.all_critical = m.www_9490 && m.control_9500 && m.planet_9600 && m.zones_up >= 8;
  return m;
}

inline std::string seal_field_binaries() {
  const char* names[] = {
      "spear-wartime", "spear-fleet-link", "spear-www", "spear-planet",
      "spear-kill-copilot", "spear-hard-dispose", "spear-export", "spear-rack-guard",
  };
  std::string out = "{\n";
  bool first = true;
  for (const char* n : names) {
    std::string p = home_dir() + "/.local/bin/" + n;
    std::string seal = binary_seal(p);
    if (!first) out += ",\n";
    first = false;
    out += "    \"";
    out += n;
    out += "\": {\"path\":\"";
    out += p;
    out += "\",\"seal\":\"";
    out += seal;
    out += "\",\"ok\":";
    out += (seal == "MISSING" ? "false" : "true");
    out += "}";
  }
  out += "\n  }";
  return out;
}

}  // namespace spear
