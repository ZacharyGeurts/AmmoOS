#include "znetwork/connection_snapshot.hpp"

#include "znetwork/platform.hpp"

#if defined(ZNETWORK_DARWIN)

namespace znet {

ConnectionSnapshot detect_current_connection_platform() {
  ConnectionSnapshot snap;
  snap.os = "darwin";
  snap.platform_backend = "Apple SystemConfiguration / configd";

  if (auto out = run_capture("route -n get default 2>/dev/null")) {
    for (const auto& line : split_lines(*out)) {
      if (line.find("interface:") != std::string::npos) {
        auto p = line.find(':');
        if (p != std::string::npos) snap.iface = trim(line.substr(p + 1));
      }
      if (line.find("gateway:") != std::string::npos) {
        auto p = line.find(':');
        if (p != std::string::npos) snap.gateway = trim(line.substr(p + 1));
      }
    }
    snap.is_default_route = !snap.gateway.empty();
  }

  if (snap.iface.empty()) snap.iface = "en0";

  if (auto ip = run_capture("ipconfig getifaddr " + snap.iface + " 2>/dev/null"))
    snap.ipv4 = trim(*ip);

  if (auto svc = run_capture("networksetup -listallhardwareports 2>/dev/null")) {
    std::string current_port;
    for (const auto& line : split_lines(*svc)) {
      if (line.find("Hardware Port:") != std::string::npos) {
        auto p = line.find(':');
        current_port = p != std::string::npos ? trim(line.substr(p + 1)) : "";
      }
      if (line.find("Device:") != std::string::npos) {
        auto p = line.find(':');
        const auto dev = p != std::string::npos ? trim(line.substr(p + 1)) : "";
        if (dev == snap.iface) {
          snap.connection_name = current_port;
          snap.iface_type = (current_port.find("Wi-Fi") != std::string::npos) ? "wifi" : "ethernet";
        }
      }
    }
  }

  if (snap.iface_type == "wifi") {
    if (auto w = run_capture("/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I 2>/dev/null")) {
      for (const auto& line : split_lines(*w)) {
        if (line.find(" SSID:") != std::string::npos) {
          auto p = line.find(':');
          if (p != std::string::npos) snap.ssid = trim(line.substr(p + 1));
        }
        if (line.find(" BSSID:") != std::string::npos) {
          auto p = line.find(':');
          if (p != std::string::npos) snap.bssid = trim(line.substr(p + 1));
        }
      }
    }
  }

  if (auto dns = run_capture("scutil --dns 2>/dev/null | grep 'nameserver\\[[0-9]*\\]' | head -3")) {
    for (const auto& line : split_lines(*dns)) {
      auto p = line.find(':');
      if (p != std::string::npos)
        snap.dns.push_back({trim(line.substr(p + 1)), "scutil"});
    }
  }

  snap.state = snap.ipv4.empty() ? "disconnected" : "connected";
  snap.is_up = !snap.ipv4.empty();

  if (auto nc = run_capture("scutil --nc list 2>/dev/null | grep Connected")) {
    if (!nc->empty()) snap.platform_backend = "NetworkExtension / configd";
  }

  return snap;
}

}  // namespace znet

#endif