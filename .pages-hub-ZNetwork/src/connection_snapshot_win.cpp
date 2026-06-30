#include "znetwork/connection_snapshot.hpp"

#include "znetwork/platform.hpp"

#if defined(ZNETWORK_WIN)

namespace znet {

ConnectionSnapshot detect_current_connection_platform() {
  ConnectionSnapshot snap;
  snap.os = "windows";
  snap.platform_backend = "WLAN AutoConfig / NetSetup";

  if (auto out = run_capture(
          "powershell -NoProfile -Command \""
          "Get-NetIPConfiguration | Where-Object {$_.IPv4DefaultGateway -ne $null} | "
          "Select-Object -First 1 | ForEach-Object { "
          "$_.InterfaceAlias + '|' + $_.IPv4Address.IPAddress + '|' + "
          "$_.IPv4DefaultGateway.NextHop + '|' + $_.DNSServer.ServerAddresses }\" 2>nul")) {
    const auto line = trim(split_lines(*out).empty() ? "" : split_lines(*out)[0]);
    std::vector<std::string> parts;
    std::string cur;
    for (char c : line) {
      if (c == '|') { parts.push_back(cur); cur.clear(); }
      else cur += c;
    }
    parts.push_back(cur);
    if (parts.size() >= 3) {
      snap.iface = parts[0];
      snap.ipv4 = parts[1];
      snap.gateway = parts[2];
      snap.is_default_route = true;
      snap.state = "connected";
      if (parts.size() >= 4 && !parts[3].empty())
        snap.dns.push_back({trim(parts[3]), "netsetup"});
    }
  }

  if (snap.iface.empty()) {
    if (auto out = run_capture("netsh interface ip show config name=\"Wi-Fi\" 2>nul")) {
      snap.iface = "Wi-Fi";
      snap.iface_type = "wifi";
      for (const auto& line : split_lines(*out)) {
        if (line.find("IP Address") != std::string::npos) {
          auto p = line.rfind(':');
          if (p != std::string::npos) snap.ipv4 = trim(line.substr(p + 1));
        }
        if (line.find("Default Gateway") != std::string::npos) {
          auto p = line.rfind(':');
          if (p != std::string::npos) snap.gateway = trim(line.substr(p + 1));
        }
      }
      snap.state = snap.ipv4.empty() ? "disconnected" : "connected";
    }
  }

  if (auto w = run_capture("netsh wlan show interfaces 2>nul")) {
    for (const auto& line : split_lines(*w)) {
      if (line.find("SSID") != std::string::npos && line.find("BSSID") == std::string::npos) {
        auto p = line.find(':');
        if (p != std::string::npos) snap.ssid = trim(line.substr(p + 1));
      }
      if (line.find("Physical address") != std::string::npos) {
        auto p = line.find(':');
        if (p != std::string::npos) snap.mac = trim(line.substr(p + 1));
      }
    }
    snap.iface_type = "wifi";
  }

  if (auto svc = run_capture("sc query WlanSvc 2>nul")) {
    snap.platform_backend = svc->find("RUNNING") != std::string::npos
        ? "WLAN AutoConfig (WlanSvc)"
        : "NetSetup / DHCP Client";
  }

  return snap;
}

}  // namespace znet

#endif