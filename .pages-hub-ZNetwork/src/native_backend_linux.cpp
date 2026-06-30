#include "znetwork/native_backend.hpp"

#include "znetwork/platform.hpp"

#if defined(ZNETWORK_LINUX)

namespace znet {

namespace {

std::vector<std::string> split_fields(std::string_view line, char sep = ':') {
  std::vector<std::string> out;
  std::string cur;
  for (char c : line) {
    if (c == sep) {
      out.push_back(cur);
      cur.clear();
    } else {
      cur += c;
    }
  }
  out.push_back(cur);
  return out;
}

}  // namespace

NativeBackendInfo detect_native_backend() {
  NativeBackendInfo info;
  if (run_capture("systemctl is-active NetworkManager 2>/dev/null").value_or("") == "active\n" ||
      run_capture("systemctl is-active NetworkManager 2>/dev/null").value_or("").find("active") != std::string::npos) {
    info.id = "networkmanager";
    info.label = "NetworkManager";
    info.running = true;
    info.manageable = true;
    if (auto v = run_capture("nmcli --version 2>/dev/null")) info.version = trim(*v);
  } else if (run_capture("systemctl is-active systemd-networkd 2>/dev/null").value_or("").find("active") != std::string::npos) {
    info.id = "systemd-networkd";
    info.label = "systemd-networkd";
    info.running = true;
    info.manageable = true;
  } else if (file_exists("/etc/netplan") || run_capture("test -d /etc/netplan && ls /etc/netplan/*.yaml 2>/dev/null | head -1").value_or("").find(".yaml") != std::string::npos) {
    info.id = "netplan";
    info.label = "netplan / systemd-networkd";
    info.running = true;
    info.manageable = false;
  } else {
    info.id = "linux_manual";
    info.label = "manual/iproute2";
    info.running = false;
    info.manageable = false;
  }
  if (auto out = run_capture("nmcli -t -f NAME con show --active 2>/dev/null")) {
    for (const auto& line : split_lines(*out)) {
      if (!trim(line).empty()) info.active_connections.push_back(trim(line));
    }
  }
  return info;
}

std::vector<ConnectionSnapshot> list_connections() {
  std::vector<ConnectionSnapshot> list;
  auto primary = detect_current_connection();
  if (!primary.iface.empty()) list.push_back(primary);
  return list;
}

}  // namespace znet

#endif