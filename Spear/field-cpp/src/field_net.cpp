// SPDX-License-Identifier: MIT
// field-net — Native C++ Internet 2.0 net tools (replaces bash field-ping/curl/…).
// No scripts. Loopback/field-safe defaults. God Bless.
#include "spear_common.hpp"

#include <arpa/inet.h>
#include <netdb.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>

namespace {

void usage(const char* argv0) {
  std::fprintf(stderr,
               "%s — native FieldNet (C++)\n"
               "  %s ping HOST [count]\n"
               "  %s tcp HOST PORT     (field-telnet/nc class)\n"
               "  %s resolve HOST\n"
               "  %s law               (probe Internet 2.0 local court)\n"
               "  %s status\n"
               "Scripts FORBIDDEN. Use this binary, not field-*.sh.\n",
               argv0, argv0, argv0, argv0, argv0, argv0);
}

bool tcp_probe(const char* host, int port, int timeout_ms, std::string& err) {
  addrinfo hints {};
  hints.ai_family = AF_UNSPEC;
  hints.ai_socktype = SOCK_STREAM;
  addrinfo* res = nullptr;
  char portstr[16];
  std::snprintf(portstr, sizeof portstr, "%d", port);
  int ga = ::getaddrinfo(host, portstr, &hints, &res);
  if (ga != 0) {
    err = gai_strerror(ga);
    return false;
  }
  bool ok = false;
  for (addrinfo* ai = res; ai; ai = ai->ai_next) {
    int fd = ::socket(ai->ai_family, ai->ai_socktype, ai->ai_protocol);
    if (fd < 0) continue;
    // nonblock-ish: short connect via alarm-free SO_SNDTIMEO
    timeval tv {};
    tv.tv_sec = timeout_ms / 1000;
    tv.tv_usec = (timeout_ms % 1000) * 1000;
    ::setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof tv);
    ::setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof tv);
    if (::connect(fd, ai->ai_addr, ai->ai_addrlen) == 0) {
      ok = true;
      ::close(fd);
      break;
    }
    err = std::strerror(errno);
    ::close(fd);
  }
  ::freeaddrinfo(res);
  return ok;
}

int cmd_law() {
  // Internet 2.0 LAW ports only
  struct {
    const char* name;
    int port;
  } ports[] = {{"i2-law", 9477}, {"www", 9490}, {"h7", 9491}, {"fleet", 9500}, {"planet", 9600}};
  // Probe field bind — prefer SPEAR_ADVERTISE/hostname, then 0.0.0.0 via localhost still works
  // when server is on 0.0.0.0; use advertise host for display
  const std::string host = spear::field_advertise_host();
  const char* probe = "127.0.0.1";  // connect target; servers listen on 0.0.0.0
  std::string o = "SPEARPLATE/1\nschema=field-net-law/v1\nengine=C++\nscripts=FORBIDDEN\n";
  o += "advertise=";
  o += host;
  o += "\nbind=";
  o += spear::field_bind_ip();
  o += "\n";
  int pass = 0;
  for (auto& p : ports) {
    std::string err;
    bool ok = tcp_probe(probe, p.port, 400, err);
    o += "port.";
    o += p.name;
    o += "=";
    o += ok ? "up" : "down";
    o += "\n";
    if (ok) ++pass;
    std::printf("%-10s %s:%-5d  %s\n", p.name, host.c_str(), p.port, ok ? "UP" : "DOWN");
  }
  o += "pass=";
  o += std::to_string(pass);
  o += "\nEND\n";
  spear::mirror_www("field-net-law.plate", o);
  return pass >= 2 ? 0 : 1;
}

int cmd_resolve(const char* host) {
  if (!host || !*host) {
    std::fputs("field-dig: host required\n", stderr);
    return 1;
  }
  // Numeric IP: print as-is (no stuffed dig / getaddrinfo games)
  {
    in_addr a4 {};
    in6_addr a6 {};
    if (::inet_pton(AF_INET, host, &a4) == 1 || ::inet_pton(AF_INET6, host, &a6) == 1) {
      std::puts(host);
      return 0;
    }
  }
  addrinfo hints {};
  hints.ai_family = AF_UNSPEC;
  hints.ai_socktype = SOCK_STREAM;
  hints.ai_flags = AI_ADDRCONFIG;
  addrinfo* res = nullptr;
  int ga = ::getaddrinfo(host, nullptr, &hints, &res);
  if (ga != 0) {
    // retry without ADDRCONFIG (some chroot/containers)
    hints.ai_flags = 0;
    ga = ::getaddrinfo(host, nullptr, &hints, &res);
  }
  if (ga != 0) {
    std::fprintf(stderr, "field-dig: %s (%s)\n", host, gai_strerror(ga));
    return 1;
  }
  int n = 0;
  for (addrinfo* ai = res; ai; ai = ai->ai_next) {
    char buf[INET6_ADDRSTRLEN];
    void* addr = nullptr;
    if (ai->ai_family == AF_INET) addr = &reinterpret_cast<sockaddr_in*>(ai->ai_addr)->sin_addr;
    else if (ai->ai_family == AF_INET6)
      addr = &reinterpret_cast<sockaddr_in6*>(ai->ai_addr)->sin6_addr;
    if (addr && ::inet_ntop(ai->ai_family, addr, buf, sizeof buf)) {
      std::puts(buf);
      ++n;
    }
  }
  ::freeaddrinfo(res);
  return n > 0 ? 0 : 1;
}

int cmd_tcp(const char* host, int port) {
  std::string err;
  auto t0 = std::chrono::steady_clock::now();
  bool ok = tcp_probe(host, port, 2000, err);
  auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - t0)
                .count();
  if (ok) {
    std::printf("field-net tcp %s:%d OPEN %ldms\n", host, port, static_cast<long>(ms));
    return 0;
  }
  std::printf("field-net tcp %s:%d CLOSED (%s)\n", host, port, err.c_str());
  return 1;
}

int cmd_ping(const char* host, int count) {
  // ICMP needs raw sockets — do TCP connect RTT to :80/:443/:9477 as field "ping"
  int ports[] = {9477, 80, 443};
  for (int c = 0; c < count; ++c) {
    bool any = false;
    for (int port : ports) {
      std::string err;
      auto t0 = std::chrono::steady_clock::now();
      bool ok = tcp_probe(host, port, 1500, err);
      auto ms =
          std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - t0)
              .count();
      if (ok) {
        std::printf("field-ping %s port %d time=%ld ms\n", host, port, static_cast<long>(ms));
        any = true;
        break;
      }
    }
    if (!any) std::printf("field-ping %s unreachable (tcp probe)\n", host);
  }
  return 0;
}

}  // namespace

int main(int argc, char** argv) {
  // Multi-call: argv0 basename may be field-ping, field-telnet, field-nc, …
  std::string base = argv[0] ? argv[0] : "field-net";
  auto slash = base.find_last_of('/');
  if (slash != std::string::npos) base = base.substr(slash + 1);

  const char* cmd = nullptr;
  int argi = 1;
  // multi-call via symlink basename (field-dig, field-ping, …)
  if (base == "field-ping")
    cmd = "ping";
  else if (base == "field-telnet" || base == "field-nc")
    cmd = "tcp";
  else if (base == "field-dig" || base == "field-host" || base == "field-nslookup")
    cmd = "resolve";
  else if (base == "field-internet-test")
    cmd = "law";
  else if (base == "field-curl")
    cmd = "law";
  else if (base == "field-network" || base == "field-display")
    cmd = "status";
  else if (base == "field-traceroute")
    cmd = "ping";  // path probe via tcp RTT class
  else {
    if (argc < 2) {
      usage(argv[0]);
      return 1;
    }
    cmd = argv[1];
    argi = 2;
  }

  // Skip redundant subcommand words: `field-dig resolve host` / `field-dig dig host`
  auto is_kw = [](const char* s, const char* a, const char* b = nullptr, const char* c = nullptr) {
    if (!s) return false;
    if (std::strcmp(s, a) == 0) return true;
    if (b && std::strcmp(s, b) == 0) return true;
    if (c && std::strcmp(s, c) == 0) return true;
    return false;
  };
  if (argi < argc) {
    if (std::strcmp(cmd, "resolve") == 0 && is_kw(argv[argi], "resolve", "dig", "host")) ++argi;
    else if (std::strcmp(cmd, "ping") == 0 && is_kw(argv[argi], "ping"))
      ++argi;
    else if (std::strcmp(cmd, "tcp") == 0 && is_kw(argv[argi], "tcp", "telnet", "nc"))
      ++argi;
    else if (std::strcmp(cmd, "law") == 0 && is_kw(argv[argi], "law", "test"))
      ++argi;
  }

  if (std::strcmp(cmd, "--version") == 0 || std::strcmp(cmd, "-V") == 0) {
    std::puts("field-net 1.0.1 native C++ · Internet 2.0 · dig/ping/tcp un-stuffed · scripts FORBIDDEN");
    return 0;
  }
  if (std::strcmp(cmd, "status") == 0) {
    std::puts("field-net 1.0.1 native C++ · Internet 2.0 · scripts FORBIDDEN");
    return cmd_law();
  }
  if (std::strcmp(cmd, "law") == 0 || std::strcmp(cmd, "test") == 0) return cmd_law();
  if (std::strcmp(cmd, "resolve") == 0 || std::strcmp(cmd, "dig") == 0) {
    if (argi >= argc) {
      std::fputs(
          "field-dig — native FieldNet resolve (C++)\n"
          "  field-dig HOST\n"
          "  field-dig resolve HOST\n"
          "  field-dig law\n"
          "Real /usr/bin/dig is untouched. Never PATH-shadow dig.\n",
          stderr);
      return 1;
    }
    return cmd_resolve(argv[argi]);
  }
  if (std::strcmp(cmd, "tcp") == 0 || std::strcmp(cmd, "telnet") == 0 || std::strcmp(cmd, "nc") == 0) {
    if (argi >= argc) return cmd_tcp("127.0.0.1", 9477);
    const char* host = argv[argi];
    int port = (argi + 1 < argc) ? std::atoi(argv[argi + 1]) : 9477;
    if (port <= 0) port = 9477;
    return cmd_tcp(host, port);
  }
  if (std::strcmp(cmd, "ping") == 0) {
    const char* host = (argi < argc) ? argv[argi] : "127.0.0.1";
    int count = (argi + 1 < argc) ? std::atoi(argv[argi + 1]) : 3;
    if (count <= 0) count = 3;
    return cmd_ping(host, count);
  }
  usage(argv[0]);
  return 1;
}
