#pragma once

#include <string>
#include <vector>

namespace znet {

struct DnsServer {
  std::string address;
  std::string source;  // resolvconf, systemd-resolved, nm, dhcp
};

struct RouteEntry {
  std::string destination;
  std::string gateway;
  std::string iface;
  int metric{0};
};

struct ConnectionSnapshot {
  std::string os;
  std::string platform_backend;  // NetworkManager, systemd-networkd, ...
  std::string iface;
  std::string iface_type;        // ethernet, wifi, loopback, unknown
  std::string mac;
  std::string ipv4;
  std::string ipv4_prefix;       // e.g. /24
  std::string ipv6;
  std::string gateway;
  std::string ssid;
  std::string bssid;
  std::string connection_name;   // NM profile name
  std::string connection_uuid;
  bool is_default_route{false};
  bool is_up{false};
  bool dhcp{true};
  std::vector<DnsServer> dns;
  std::vector<RouteEntry> routes;
  std::string state;             // connected, connecting, disconnected
};

ConnectionSnapshot detect_current_connection_platform();

/** Detect live connection without mutating system state. */
inline ConnectionSnapshot detect_current_connection() {
  return detect_current_connection_platform();
}

std::string snapshot_to_json(const ConnectionSnapshot& snap);

}  // namespace znet