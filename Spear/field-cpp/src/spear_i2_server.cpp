// SPDX-License-Identifier: MIT
// spear-i2-server — Internet 2.0 LAW server (C++ or lower). Port 9477.
// NEVER scripts. NEVER JSON authority. Field plates only.
// Ironclad 302 → Hostess 7 panel (Host header · field advertise · no 127 crap).
#include "spear_common.hpp"
#include "spear_chip.hpp"

#include <arpa/inet.h>
#include <dirent.h>
#include <errno.h>
#include <netinet/in.h>
#include <signal.h>
#include <sys/socket.h>
#include <sys/stat.h>

#include <cctype>
#include <cstdio>
#include <cstring>
#include <string>

namespace {

volatile sig_atomic_t g_stop = 0;
static void on_sig(int) { g_stop = 1; }

static bool port_up(int p) { return spear::port_listening(p); }

static bool proc_running(const char* name) {
  DIR* d = ::opendir("/proc");
  if (!d) return false;
  bool f = false;
  while (dirent* e = ::readdir(d)) {
    if (!spear::is_digits(e->d_name)) continue;
    if (spear::read_comm(static_cast<pid_t>(std::atoi(e->d_name))) == name) {
      f = true;
      break;
    }
  }
  ::closedir(d);
  return f;
}

static void send_raw(int cfd, int code, const char* ctype, const std::string& body) {
  const char* reason = "OK";
  if (code == 302) reason = "Found";
  if (code == 404) reason = "Not Found";
  if (code == 403) reason = "Forbidden";
  if (code == 405) reason = "Method Not Allowed";
  if (code == 410) reason = "Gone";
  char hdr[768];
  int hl = std::snprintf(hdr, sizeof hdr,
                         "HTTP/1.1 %d %s\r\nContent-Type: %s\r\nContent-Length: %zu\r\n"
                         "Cache-Control: no-store\r\nX-Spear-Scripts: FORBIDDEN\r\n"
                         "X-Spear-Stack: C++\r\nX-Internet: 2.0\r\nX-JSON: EATEN\r\n"
                         "X-Ironclad: 1\r\nConnection: close\r\n\r\n",
                         code, reason, ctype, body.size());
  if (hl > 0) ::send(cfd, hdr, static_cast<size_t>(hl), 0);
  if (!body.empty()) ::send(cfd, body.data(), body.size(), 0);
  ::close(cfd);
}

static void send_plate(int cfd, int code, const std::string& body) {
  send_raw(cfd, code, spear::plate::kContentType, body);
}

// Ironclad 302 — absolute Location with Host: from request (strip :9477 → :9491)
static void send_302_h7(int cfd, const std::string& req) {
  std::string host;
  // Case-insensitive Host header
  std::string low = req;
  for (char& c : low)
    if (c >= 'A' && c <= 'Z') c = static_cast<char>(c - 'A' + 'a');
  size_t hp = low.find("\r\nhost:");
  if (hp == std::string::npos) hp = low.find("\nhost:");
  if (hp != std::string::npos) {
    size_t start = req.find(':', hp);
    if (start != std::string::npos) {
      ++start;
      while (start < req.size() && (req[start] == ' ' || req[start] == '\t')) ++start;
      size_t end = start;
      while (end < req.size() && req[end] != '\r' && req[end] != '\n') ++end;
      host = req.substr(start, end - start);
      // trim
      while (!host.empty() && (host.back() == ' ' || host.back() == '\t')) host.pop_back();
    }
  }
  // Strip any existing port from Host
  if (!host.empty()) {
    // [ipv6]:port
    if (host[0] == '[') {
      size_t br = host.find(']');
      if (br != std::string::npos) host = host.substr(0, br + 1);
    } else {
      size_t col = host.rfind(':');
      if (col != std::string::npos && host.find(':') == col)  // single colon → host:port
        host = host.substr(0, col);
    }
  }
  if (host.empty() || host == "0.0.0.0" || host == "*" || host == "[::]")
    host = spear::field_advertise_host();
  if (host.empty() || host == "field") {
    // last resort: still valid absolute URL for local field
    host = "localhost";
  }

  std::string loc = "http://" + host + ":9491/hostess7.html";
  char hdr[900];
  int hl = std::snprintf(hdr, sizeof hdr,
                         "HTTP/1.1 302 Found\r\n"
                         "Location: %s\r\n"
                         "Content-Type: text/plain; charset=utf-8\r\n"
                         "Content-Length: 0\r\n"
                         "Cache-Control: no-store\r\n"
                         "X-Spear-Scripts: FORBIDDEN\r\n"
                         "X-Spear-Stack: C++\r\n"
                         "X-Internet: 2.0\r\n"
                         "X-Ironclad: 1\r\n"
                         "Connection: close\r\n"
                         "\r\n",
                         loc.c_str());
  if (hl > 0) ::send(cfd, hdr, static_cast<size_t>(hl), 0);
  ::close(cfd);
}

static std::string status_plate() {
  std::string o = spear::plate::i2_servers_plate(port_up(9477), port_up(9490), port_up(9491),
                                                 port_up(9500), port_up(9600), port_up(53), port_up(67),
                                                 proc_running("spear-wartime"));
  // ironclad redirect plate note
  size_t endp = o.rfind("END\n");
  std::string extra;
  spear::plate::kv(extra, "redirect_hostess7", "/hostess7 → :9491/hostess7.html");
  spear::plate::kv(extra, "ironclad", true);
  spear::plate::kv(extra, "ammoos", "AMOURANTHRTX SDL3");
  if (endp != std::string::npos) o.insert(endp, extra);
  return o;
}

static void handle(int cfd) {
  char buf[16384];
  ssize_t n = ::recv(cfd, buf, sizeof(buf) - 1, 0);
  if (n <= 0) {
    ::close(cfd);
    return;
  }
  buf[n] = 0;
  std::string req(buf, static_cast<size_t>(n));

  if (std::strncmp(buf, "GET ", 4) != 0 && std::strncmp(buf, "HEAD ", 5) != 0) {
    send_plate(cfd, 405, "SPEARPLATE/1\nerror=GET_only\nEND\n");
    return;
  }
  const char* p = buf;
  if (std::strncmp(p, "GET ", 4) == 0)
    p += 4;
  else if (std::strncmp(p, "HEAD ", 5) == 0)
    p += 5;
  while (*p == ' ') ++p;
  std::string path;
  while (*p && *p != ' ' && *p != '\r' && *p != '\n') path.push_back(*p++);
  size_t q = path.find('?');
  if (q != std::string::npos) path = path.substr(0, q);

  if (path.empty() || path == "/" || path == "/field" || path == "/status" || path == "/api/status" ||
      path == "/api/i2/status" || path == "/api/internet-2.0") {
    send_plate(cfd, 200, status_plate());
    return;
  }
  if (path == "/api/harden" || path == "/harden") {
    send_plate(cfd, 200, spear::plate::harden_plate());
    return;
  }
  if (path == "/api/chips" || path == "/chips") {
    spear::chip_reset();
    auto st = spear::chip_status();
    std::string o = spear::plate::header("spear-chips-status/v1");
    spear::plate::kv(o, "path", st.path);
    spear::plate::kv(o, "online", st.online);
    spear::plate::kv(o, "ops_retired", static_cast<long>(st.ops_retired));
    o += "END\n";
    send_plate(cfd, 200, o);
    return;
  }
  // Ironclad redirect to Hostess 7 panel
  if (path == "/hostess7" || path == "/h7" || path == "/hostess7/" || path == "/h7/" ||
      path == "/hostess7.html") {
    send_302_h7(cfd, req);
    return;
  }
  if (spear::contains(path, ".json") || spear::contains(path, ".py") || spear::contains(path, ".sh")) {
    send_plate(cfd, 410, spear::plate::eat_json_mark());
    return;
  }
  send_plate(cfd, 404, "SPEARPLATE/1\nerror=not_found\nironclad=1\nEND\n");
}

}  // namespace

int main(int argc, char** argv) {
  const char* bind_ip = spear::field_bind_ip();
  int port = 9477;
  for (int i = 1; i < argc; ++i) {
    if (std::strcmp(argv[i], "--port") == 0 && i + 1 < argc) port = std::atoi(argv[++i]);
    else if (std::strcmp(argv[i], "--bind") == 0 && i + 1 < argc)
      bind_ip = argv[++i];
    else if (std::strcmp(argv[i], "-h") == 0 || std::strcmp(argv[i], "--help") == 0) {
      std::fprintf(stderr,
                   "spear-i2-server — Internet 2.0 LAW (C++) ironclad\n"
                   "  %s [--bind IP] [--port N]\n"
                   "  GET /hostess7 → 302 Hostess 7 panel :9491\n",
                   argv[0]);
      return 0;
    }
  }
  struct sigaction sa {};
  sa.sa_handler = on_sig;
  ::sigaction(SIGINT, &sa, nullptr);
  signal(SIGPIPE, SIG_IGN);

  int sfd = ::socket(AF_INET, SOCK_STREAM, 0);
  if (sfd < 0) return 1;
  int one = 1;
  ::setsockopt(sfd, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);
  sockaddr_in addr {};
  addr.sin_family = AF_INET;
  addr.sin_port = htons(static_cast<uint16_t>(port));
  if (::inet_pton(AF_INET, bind_ip, &addr.sin_addr) != 1) return 1;
  if (::bind(sfd, reinterpret_cast<sockaddr*>(&addr), sizeof addr) < 0) {
    std::perror("bind");
    return 1;
  }
  if (::listen(sfd, 64) < 0) return 1;
  spear::mirror_www("internet-2.0-servers.plate", status_plate());
  std::printf(
      "spear-i2-server Internet 2.0 LAW ironclad bind=%s:%d scripts=FORBIDDEN json=EATEN "
      "ammoos=SDL3\n",
      bind_ip, port);
  std::fflush(stdout);
  while (!g_stop) {
    int cfd = ::accept(sfd, nullptr, nullptr);
    if (cfd < 0) {
      if (errno == EINTR) continue;
      break;
    }
    handle(cfd);
  }
  ::close(sfd);
  return 0;
}
