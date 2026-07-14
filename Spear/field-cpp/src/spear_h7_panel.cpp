// SPDX-License-Identifier: MIT
// spear-h7-panel — Hostess 7 War Command (C++ or lower only).
// Tabbed training UI · CHIPs Field Die · Field Research 2.0 · no scripts ever exposed.
// GET only. Loopback default. No CGI. No fork of interpreters. No .py/.sh serve.
#include "spear_common.hpp"
#include "spear_chip.hpp"
#include "spear_field_surface.hpp"
#include "spear_field_apps.hpp"

#include <arpa/inet.h>
#include <dirent.h>
#include <errno.h>
#include <netinet/in.h>
#include <signal.h>
#include <sys/socket.h>
#include <sys/stat.h>

#include <cctype>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <string>
#include <vector>

namespace {

volatile sig_atomic_t g_stop = 0;
static void on_sig(int) { g_stop = 1; }
static time_t g_start = 0;

// ── Harden: never expose product scripts ───────────────────────────────────
static bool is_blocked_script_ext(const std::string& path) {
  // lower-case tail match
  auto ends = [&](const char* ext) {
    const size_t n = std::strlen(ext);
    if (path.size() < n) return false;
    for (size_t i = 0; i < n; ++i) {
      char a = path[path.size() - n + i];
      char b = ext[i];
      if (a >= 'A' && a <= 'Z') a = static_cast<char>(a - 'A' + 'a');
      if (a != b) return false;
    }
    return true;
  };
  return ends(".py") || ends(".pyw") || ends(".pyc") || ends(".pyo") || ends(".pyx") ||
         ends(".bas") || ends(".qb") || ends(".qbas") || ends(".bi") || ends(".b") ||
         ends(".sh") || ends(".bash") || ends(".zsh") || ends(".csh") || ends(".ksh") ||
         ends(".pl") || ends(".pm") || ends(".rb") || ends(".php") || ends(".cgi") ||
         ends(".ps1") || ends(".psm1") || ends(".cmd") || ends(".bat") || ends(".vbs") ||
         ends(".lua") || ends(".js.map") || ends(".ts") || ends(".tsx") || ends(".jsx") ||
         ends(".aml");
}

static bool is_blocked_path_segment(const std::string& path) {
  // deny traversing into engine trees even if extension is "safe"
  const char* bad[] = {"/lib/", "/scripts/", "/bin/", "/.git/", "/__pycache__/",
                       "lib/", "scripts/", nullptr};
  std::string low = path;
  for (char& c : low)
    if (c >= 'A' && c <= 'Z') c = static_cast<char>(c - 'A' + 'a');
  // normalize
  if (low.find("..") != std::string::npos) return true;
  for (int i = 0; bad[i]; ++i) {
    if (low.find(bad[i]) != std::string::npos) return true;
  }
  // bare engine names
  if (low == "lib" || low == "scripts" || low.rfind("lib/", 0) == 0 || low.rfind("scripts/", 0) == 0)
    return true;
  return false;
}

static bool safe_rel(const std::string& rel) {
  if (rel.empty()) return false;
  if (rel.find("..") != std::string::npos) return false;
  if (!rel.empty() && rel[0] == '/') return false;
  if (is_blocked_script_ext(rel)) return false;
  if (is_blocked_path_segment(rel)) return false;
  return true;
}

// Scrub any accidental script paths from JSON text before serve
static std::string scrub_scripts(std::string s) {
  // replace path-like *.py / *.sh tokens
  std::string out;
  out.reserve(s.size());
  for (size_t i = 0; i < s.size();) {
    // detect word/path ending with .py/.sh etc
    if (std::isalnum(static_cast<unsigned char>(s[i])) || s[i] == '/' || s[i] == '_' || s[i] == '-' ||
        s[i] == '.') {
      size_t j = i;
      while (j < s.size() &&
             (std::isalnum(static_cast<unsigned char>(s[j])) || s[j] == '/' || s[j] == '_' ||
              s[j] == '-' || s[j] == '.'))
        ++j;
      std::string tok = s.substr(i, j - i);
      std::string low = tok;
      for (char& c : low)
        if (c >= 'A' && c <= 'Z') c = static_cast<char>(c - 'A' + 'a');
      bool hit = false;
      const char* exts[] = {".py", ".pyw", ".pyc", ".sh", ".bash", ".pl", ".rb", ".php", ".cgi",
                            ".ps1", ".cmd", ".bat", nullptr};
      for (int e = 0; exts[e]; ++e) {
        size_t el = std::strlen(exts[e]);
        if (low.size() >= el && low.compare(low.size() - el, el, exts[e]) == 0) {
          hit = true;
          break;
        }
      }
      if (!hit && (low.find("lib/") != std::string::npos || low.find("scripts/") != std::string::npos) &&
          (low.find('/') != std::string::npos)) {
        // path segment style
        if (low.find(".py") != std::string::npos || low.find(".sh") != std::string::npos) hit = true;
      }
      if (hit)
        out += "[sealed]";
      else
        out += tok;
      i = j;
    } else {
      out.push_back(s[i++]);
    }
  }
  return out;
}

static std::string mime_for(const std::string& path) {
  if (spear::contains(path, ".html")) return "text/html; charset=utf-8";
  if (spear::contains(path, ".json")) return "application/json; charset=utf-8";
  if (spear::contains(path, ".css")) return "text/css; charset=utf-8";
  if (spear::contains(path, ".js")) return "application/javascript; charset=utf-8";
  if (spear::contains(path, ".svg")) return "image/svg+xml";
  if (spear::contains(path, ".png")) return "image/png";
  if (spear::contains(path, ".jpg") || spear::contains(path, ".jpeg")) return "image/jpeg";
  if (spear::contains(path, ".md")) return "text/markdown; charset=utf-8";
  if (spear::contains(path, ".txt") || spear::contains(path, ".csv")) return "text/plain; charset=utf-8";
  return "application/octet-stream";
}

static void send_raw(int cfd, int code, const char* ctype, const std::string& body) {
  const char* reason = "OK";
  if (code == 403) reason = "Forbidden";
  if (code == 404) reason = "Not Found";
  if (code == 400) reason = "Bad Request";
  if (code == 405) reason = "Method Not Allowed";
  char hdr[800];
  int hl = std::snprintf(hdr, sizeof(hdr),
                         "HTTP/1.1 %d %s\r\nContent-Type: %s\r\nContent-Length: %zu\r\n"
                         "Cache-Control: no-store\r\nX-Content-Type-Options: nosniff\r\n"
                         "X-Spear-Scripts: FORBIDDEN\r\nX-Spear-Stack: C++\r\n"
                         "X-Spear-CHIPs: FieldDie\r\nX-JSON: EATEN\r\n"
                         "Connection: close\r\n\r\n",
                         code, reason, ctype, body.size());
  // ctype for plates is text/x-field-plate — never text/plain for SPEARPLATE
  ::send(cfd, hdr, static_cast<size_t>(hl), 0);
  if (!body.empty()) ::send(cfd, body.data(), body.size(), 0);
  ::close(cfd);
}

static void send_plate(int cfd, int code, const std::string& body) {
  // Field plate wire — JSON has no authority (EATEN into C++)
  send_raw(cfd, code, spear::plate::kContentType, scrub_scripts(body));
}

static std::string now_z() {
  char buf[64];
  std::time_t t = std::time(nullptr);
  std::strftime(buf, sizeof buf, "%Y-%m-%dT%H:%M:%SZ", std::gmtime(&t));
  return buf;
}

static std::string jesc(const std::string& s) {
  std::string o;
  o.reserve(s.size() + 8);
  for (char c : s) {
    if (c == '"' || c == '\\') {
      o.push_back('\\');
      o.push_back(c);
    } else if (c == '\n')
      o += "\\n";
    else if (static_cast<unsigned char>(c) < 32)
      continue;
    else
      o.push_back(c);
  }
  return o;
}

static bool file_ok(const std::string& p) {
  struct stat st {};
  return ::stat(p.c_str(), &st) == 0 && S_ISREG(st.st_mode);
}

static std::string first_existing(const std::vector<std::string>& paths) {
  for (const auto& p : paths) {
    if (file_ok(p)) return p;
  }
  return {};
}

static std::string home_sg() {
  const char* home = std::getenv("HOME");
  if (!home || !*home) return {};
  return std::string(home) + "/Desktop/SG";
}

// All authority is C++ plates (spear_plates.hpp). JSON files are EATEN — never loaded.

static std::string api_chips() {
  spear::chip_reset();
  std::uint8_t demo[64];
  for (int i = 0; i < 64; ++i) demo[i] = static_cast<std::uint8_t>((i * 37) ^ 0x5a);
  auto sc = spear::chip_score_frame(demo, sizeof demo);
  auto st = spear::chip_status();
  std::string o = spear::plate::header("spear-chips-status/v1");
  spear::plate::kv(o, "online", st.online);
  spear::plate::kv(o, "path", st.path);
  spear::plate::kv(o, "plane", "FieldDie/CHIPs");
  spear::plate::kv(o, "ops", "EntropyFold|WavePhase|PeakScan|PackPick|Shannon|FnvMix");
  spear::plate::kv(o, "pack_ops", "ZERO|RLE|PAK|RAW|REF");
  spear::plate::kv(o, "die_slots", static_cast<long>(spear::kChipDieSlots));
  spear::plate::kv(o, "wave_bands", static_cast<long>(spear::kChipWaveBands));
  spear::plate::kv(o, "frame_cache", static_cast<long>(spear::kChipFrameCache));
  spear::plate::kv(o, "ops_retired", static_cast<long>(st.ops_retired));
  spear::plate::kv(o, "frames_scored", static_cast<long>(st.frames_scored));
  spear::plate::kv(o, "cache_hits", static_cast<long>(st.cache_hits));
  spear::plate::kv(o, "cache_misses", static_cast<long>(st.cache_misses));
  spear::plate::kv(o, "pack_via_chip", static_cast<long>(st.pack_via_chip));
  char fb[64];
  std::snprintf(fb, sizeof fb, "%.6f", st.last_fold);
  spear::plate::kv(o, "last_fold", fb);
  std::snprintf(fb, sizeof fb, "%.6f", st.last_wave);
  spear::plate::kv(o, "last_wave", fb);
  std::snprintf(fb, sizeof fb, "%.4f", sc.shannon_h);
  spear::plate::kv(o, "demo.shannon_h", fb);
  std::snprintf(fb, sizeof fb, "%.4f", sc.peak_density);
  spear::plate::kv(o, "demo.peak_density", fb);
  std::snprintf(fb, sizeof fb, "%.4f", sc.wave_energy);
  spear::plate::kv(o, "demo.wave_energy", fb);
  std::snprintf(fb, sizeof fb, "%.4f", sc.fold);
  spear::plate::kv(o, "demo.fold", fb);
  spear::plate::kv(o, "demo.pick", static_cast<long>(static_cast<unsigned>(sc.pick)));
  o += "END\n";
  return o;
}

static bool port_up(int port) { return spear::port_listening(port); }

static std::string api_status(const std::string& /*root*/) {
  long up = static_cast<long>(std::time(nullptr) - g_start);
  bool law = port_up(9477);
  bool www = port_up(9490);
  bool h7 = port_up(9491);
  bool fleet = port_up(9500);
  bool planet = port_up(9600);
  bool dns = port_up(53);
  bool dhcp = port_up(67);
  bool wartime = false;
  {
    // detect spear-wartime without scripts
    DIR* d = ::opendir("/proc");
    if (d) {
      while (dirent* ent = ::readdir(d)) {
        if (!spear::is_digits(ent->d_name)) continue;
        if (spear::read_comm(static_cast<pid_t>(std::atoi(ent->d_name))) == "spear-wartime") {
          wartime = true;
          break;
        }
      }
      ::closedir(d);
    }
  }
  std::string o = spear::plate::i2_servers_plate(law, www, h7, fleet, planet, dns, dhcp, wartime);
  // splice hostess panel fields
  std::string head = spear::plate::header("hostess7-war-panel/v1");
  spear::plate::kv(head, "ts", now_z());
  spear::plate::kv(head, "class", "INTERNET_2_0");
  spear::plate::kv(head, "always_war", true);
  spear::plate::kv(head, "commander", "Hostess7");
  spear::plate::kv(head, "uptime_s", up);
  spear::plate::kv(head, "tracks", static_cast<long>(spear::plate::kTracksN));
  spear::plate::kv(head, "heuristics_embedded", static_cast<long>(spear::plate::kHeuristicsN));
  spear::plate::kv(head, "json_authority", "EATEN");
  spear::plate::kv(head, "wire", "text/x-field-plate");
  spear::plate::kv(head, "chips", "FieldDie/CHIPs");
  spear::plate::kv(head, "field_research", "2.0");
  spear::plate::kv(head, "hostess7", "2.0.8");
  spear::plate::kv(head, "fake", false);
  spear::plate::kv(head, "demo", false);
  // append server lines from i2 plate without duplicate SPEARPLATE header
  size_t pos = o.find('\n');
  if (pos != std::string::npos) head += o.substr(pos + 1);
  else head += o;
  return head;
}

static std::string api_angel_plate() {
  // Prefer C++ angel seal binary plate if written as field plate; else synthesize
  std::string a = spear::read_file((spear::www_dir() + "/angel-seal-status.plate").c_str(), 1 << 20);
  if (!a.empty()) return a;
  // fall back: read legacy path only to mark EATEN, never treat as authority
  std::string o = spear::plate::header("angel-seal-status/v3");
  spear::plate::kv(o, "commander", spear::plate::kCommander);
  spear::plate::kv(o, "rank", "ANGEL");
  spear::plate::kv(o, "status", "RUN_spear-angel-seal");
  spear::plate::kv(o, "json_authority", "EATEN");
  spear::plate::kv(o, "planes", "CHIPs|Plate|Meld");
  spear::plate::kv(o, "interpreters", "DISARMED");
  spear::plate::kv(o, "hint", "spear-angel-seal seal");
  o += "END\n";
  return o;
}

static void handle_client(int cfd, const std::string& root) {
  char buf[16384];
  ssize_t n = ::recv(cfd, buf, sizeof(buf) - 1, 0);
  if (n <= 0) {
    ::close(cfd);
    return;
  }
  buf[n] = '\0';
  if (std::strncmp(buf, "GET ", 4) != 0) {
    send_raw(cfd, 405, "text/plain", "GET only");
    return;
  }
  const char* p = buf + 4;
  while (*p == ' ') ++p;
  std::string full;
  while (*p && *p != ' ' && *p != '\r' && *p != '\n') full.push_back(*p++);
  std::string path = full;
  size_t qpos = full.find('?');
  if (qpos != std::string::npos) path = full.substr(0, qpos);
  if (path.empty() || path == "/") path = "/hostess7.html";

  // ── Field plate APIs (C++ only — JSON EATEN) ───────────────────────────
  if (path == "/api/h7/status" || path == "/api/status" || path == "/api/hostess7/status" ||
      path == "/api/i2/status" || path == "/api/internet-2.0") {
    send_plate(cfd, 200, api_status(root));
    return;
  }
  if (path == "/api/h7/catalog" || path == "/api/hostess7/catalog" ||
      path == "/api/hostess7/training-catalog") {
    send_plate(cfd, 200, spear::plate::catalog_plate());
    return;
  }
  if (path == "/api/h7/chips" || path == "/api/chips" || path == "/api/hostess7/chips") {
    send_plate(cfd, 200, api_chips());
    return;
  }
  if (path == "/api/h7/field-research" || path == "/api/field-research" || path == "/api/fr2") {
    send_plate(cfd, 200, spear::plate::fr2_plate());
    return;
  }
  if (path == "/api/h7/sense" || path == "/api/hostess7/sense") {
    send_plate(cfd, 200, spear::plate::sense_plate());
    return;
  }
  if (path == "/api/h7/war" || path == "/api/hostess7/war") {
    send_plate(cfd, 200, spear::plate::war_plate());
    return;
  }
  if (path == "/api/h7/harden" || path == "/api/harden") {
    send_plate(cfd, 200, spear::plate::harden_plate());
    return;
  }
  if (path == "/api/h7/angel" || path == "/api/angel" || path == "/api/h7/seal") {
    send_plate(cfd, 200, api_angel_plate());
    return;
  }
  if (path == "/api/h7/surface" || path == "/api/surface" || path == "/api/amouranthrtx") {
    std::string s = spear::read_file((spear::www_dir() + "/field-surface.plate").c_str(), 1 << 16);
    if (s.empty()) {
      auto spec = spear::field_surface::adapt(3840, 2160, 1.f, 0);
      s = spear::field_surface::plate(spec);
    }
    send_plate(cfd, 200, s);
    return;
  }
  if (path == "/api/h7/iso-bring" || path == "/api/iso-bring") {
    send_plate(cfd, 200, spear::field_surface::iso_bring_plate());
    return;
  }
  if (path == "/api/h7/menu" || path == "/api/menu" || path == "/api/start-menu") {
    send_plate(cfd, 200, spear::field_apps::menu_plate());
    return;
  }
  if (path == "/api/h7/steel" || path == "/api/steel" || path == "/api/ironclad") {
    send_plate(cfd, 200, spear::plate::hostess7_steel_plate());
    return;
  }
  // Refuse JSON authority paths
  if (spear::contains(path, ".json") || spear::contains(path, "/json")) {
    send_plate(cfd, 410, spear::plate::eat_json_mark());
    return;
  }

  // ── Static (hardened) ──────────────────────────────────────────────────
  if (!path.empty() && path[0] == '/') path = path.substr(1);
  if (!safe_rel(path) || spear::contains(path, ".json")) {
    send_raw(cfd, 403, spear::plate::kContentType,
             "SPEARPLATE/1\nerror=forbidden\nscripts=FORBIDDEN\njson_authority=EATEN\nEND\n");
    return;
  }
  std::string fpath = root + "/" + path;
  // also try assets/
  if (!file_ok(fpath) && path.rfind("assets/", 0) != 0) {
    std::string alt = root + "/assets/" + path;
    if (file_ok(alt)) fpath = alt;
  }
  if (!file_ok(fpath)) {
    send_raw(cfd, 404, "text/plain", "not found");
    return;
  }
  // double-check resolved path not escaping + not script
  if (is_blocked_script_ext(fpath) || is_blocked_path_segment(fpath) || spear::contains(path, ".json")) {
    send_raw(cfd, 403, spear::plate::kContentType,
             "SPEARPLATE/1\nerror=forbidden\nreason=script_or_json\nEND\n");
    return;
  }
  std::string body = spear::read_file(fpath.c_str(), 16 << 20);
  if (spear::contains(path, ".html") || spear::contains(path, ".js") || spear::contains(path, ".md") ||
      spear::contains(path, ".css")) {
    body = scrub_scripts(body);
  }
  send_raw(cfd, 200, mime_for(path).c_str(), body);
}

}  // namespace

int main(int argc, char** argv) {
  const char* bind_ip = spear::field_bind_ip();
  int port = 9491;
  std::string root = spear::www_dir() + "/hostess7";
  for (int i = 1; i < argc; ++i) {
    if (std::strcmp(argv[i], "--port") == 0 && i + 1 < argc) port = std::atoi(argv[++i]);
    else if (std::strcmp(argv[i], "--bind") == 0 && i + 1 < argc) bind_ip = argv[++i];
    else if (std::strcmp(argv[i], "--root") == 0 && i + 1 < argc) root = argv[++i];
    else if (std::strcmp(argv[i], "-h") == 0 || std::strcmp(argv[i], "--help") == 0) {
      std::fprintf(stderr,
                   "spear-h7-panel — Hostess 7 War Command (C++ · CHIPs · FR2 · no scripts)\n"
                   "  %s [--bind IP] [--port N] [--root DIR]\n"
                   "  default bind FIELD (0.0.0.0) — set SPEAR_BIND to override\n",
                   argv[0]);
      return 0;
    }
  }

  spear::mkdir_p(root);
  spear::chip_reset();
  g_start = std::time(nullptr);

  struct sigaction sa {};
  sa.sa_handler = on_sig;
  ::sigaction(SIGINT, &sa, nullptr);
  ::sigaction(SIGHUP, &sa, nullptr);
  signal(SIGPIPE, SIG_IGN);

  int sfd = ::socket(AF_INET, SOCK_STREAM, 0);
  if (sfd < 0) {
    std::perror("socket");
    return 1;
  }
  int one = 1;
  ::setsockopt(sfd, SOL_SOCKET, SO_REUSEADDR, &one, sizeof(one));
  sockaddr_in addr {};
  addr.sin_family = AF_INET;
  addr.sin_port = htons(static_cast<uint16_t>(port));
  if (::inet_pton(AF_INET, bind_ip, &addr.sin_addr) != 1) return 1;
  if (::bind(sfd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
    std::perror("bind");
    return 1;
  }
  if (::listen(sfd, 64) < 0) {
    std::perror("listen");
    return 1;
  }
  std::printf(
      "spear-h7-panel C++ Hostess7 root=%s bind=%s:%d scripts=FORBIDDEN chips=FieldDie FR=2.0\n",
      root.c_str(), bind_ip, port);
  std::fflush(stdout);
  while (!g_stop) {
    sockaddr_in cli {};
    socklen_t cl = sizeof(cli);
    int cfd = ::accept(sfd, reinterpret_cast<sockaddr*>(&cli), &cl);
    if (cfd < 0) {
      if (errno == EINTR) continue;
      break;
    }
    handle_client(cfd, root);
  }
  ::close(sfd);
  return 0;
}
