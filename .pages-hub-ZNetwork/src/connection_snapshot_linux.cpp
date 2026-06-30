#include "znetwork/connection_snapshot.hpp"

#include "znetwork/platform.hpp"

#if defined(ZNETWORK_LINUX)

#include <ifaddrs.h>
#include <net/if.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sstream>

namespace znet {

namespace {

void fill_from_ip_addr(ConnectionSnapshot& snap) {
  struct ifaddrs* ifa = nullptr;
  if (getifaddrs(&ifa) != 0 || !ifa) return;
  for (auto* cur = ifa; cur; cur = cur->ifa_next) {
    if (!cur->ifa_addr || !cur->ifa_name) continue;
    if (snap.iface.empty()) snap.iface = cur->ifa_name;
    if (std::string(cur->ifa_name) != snap.iface) continue;
    if (cur->ifa_addr->sa_family == AF_INET) {
      char buf[INET_ADDRSTRLEN]{};
      auto* sin = reinterpret_cast<sockaddr_in*>(cur->ifa_addr);
      if (inet_ntop(AF_INET, &sin->sin_addr, buf, sizeof(buf)))
        snap.ipv4 = buf;
      snap.is_up = (cur->ifa_flags & IFF_UP) != 0;
    }
  }
  freeifaddrs(ifa);
}

void fill_routes(ConnectionSnapshot& snap) {
  if (auto route = run_capture("ip -4 route show default 2>/dev/null | head -1")) {
    std::istringstream iss(*route);
    std::string tok;
    while (iss >> tok) {
      if (tok == "dev" && iss >> tok) snap.iface = tok;
      if (tok == "via" && iss >> tok) snap.gateway = tok;
    }
    snap.is_default_route = !snap.gateway.empty();
  }
}

void fill_dns(ConnectionSnapshot& snap) {
  if (auto out = run_capture("resolvectl dns 2>/dev/null")) {
    for (const auto& line : split_lines(*out)) {
      auto pos = line.find(": ");
      if (pos == std::string::npos) continue;
      std::istringstream iss(line.substr(pos + 2));
      std::string ip;
      while (iss >> ip) snap.dns.push_back({ip, "systemd-resolved"});
    }
  }
  if (snap.dns.empty() && file_exists("/etc/resolv.conf")) {
    if (auto out = run_capture("grep -E '^nameserver' /etc/resolv.conf 2>/dev/null")) {
      for (const auto& line : split_lines(*out)) {
        auto pos = line.find(' ');
        if (pos != std::string::npos)
          snap.dns.push_back({trim(line.substr(pos + 1)), "resolv.conf"});
      }
    }
  }
}

void fill_nm(ConnectionSnapshot& snap) {
  snap.platform_backend = "NetworkManager";
  if (auto out = run_capture("nmcli -t -f DEVICE,TYPE,STATE,CONNECTION dev status 2>/dev/null")) {
    for (const auto& line : split_lines(*out)) {
      std::vector<std::string> f;
      std::string cur;
      for (char c : line) {
        if (c == ':') { f.push_back(cur); cur.clear(); }
        else cur += c;
      }
      f.push_back(cur);
      if (f.size() >= 4 && f[0] == snap.iface) {
        snap.iface_type = f[1];
        snap.state = f[2];
        snap.connection_name = f[3];
      }
    }
  }
  if (snap.iface_type == "wifi") {
    if (auto w = run_capture("nmcli -t -f ACTIVE,SSID,BSSID dev wifi 2>/dev/null")) {
      for (const auto& line : split_lines(*w)) {
        std::vector<std::string> f;
        std::string cur;
        for (char c : line) {
          if (c == ':') { f.push_back(cur); cur.clear(); }
          else cur += c;
        }
        f.push_back(cur);
        if (f.size() >= 3 && f[0] == "yes") {
          snap.ssid = f[1];
          snap.bssid = f[2];
        }
      }
    }
  }
  if (run_capture("systemctl is-active systemd-networkd 2>/dev/null").value_or("").find("active") != std::string::npos
      && !run_capture("systemctl is-active NetworkManager 2>/dev/null").value_or("").empty()) {
    if (auto nm = run_capture("systemctl is-active NetworkManager 2>/dev/null"); !nm || nm->find("active") == std::string::npos)
      snap.platform_backend = "systemd-networkd";
  }
}

}  // namespace

ConnectionSnapshot detect_current_connection_platform() {
  ConnectionSnapshot snap;
  snap.os = "linux";
  if (auto link = run_capture("ip -o -4 route show to default 2>/dev/null | awk '{print $5}' | head -1"))
    snap.iface = trim(*link);
  if (snap.iface.empty()) snap.iface = "eth0";
  fill_from_ip_addr(snap);
  fill_routes(snap);
  fill_dns(snap);
  fill_nm(snap);
  if (snap.state.empty()) snap.state = snap.is_up ? "connected" : "disconnected";
  if (auto mac = run_capture("cat /sys/class/net/" + snap.iface + "/address 2>/dev/null"))
    snap.mac = trim(*mac);
  return snap;
}

}  // namespace znet

#endif