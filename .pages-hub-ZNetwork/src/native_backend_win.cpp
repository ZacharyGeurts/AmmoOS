#include "znetwork/native_backend.hpp"

#include "znetwork/platform.hpp"

#include <sstream>

#if defined(ZNETWORK_WIN)

namespace znet {

NativeBackendInfo detect_native_backend() {
  NativeBackendInfo info;
  info.id = "win_netsetup";
  info.label = "Windows NetSetup / WLAN AutoConfig";
  info.manageable = true;

  if (auto svc = run_capture("sc query WlanSvc 2>nul")) {
    info.running = svc->find("RUNNING") != std::string::npos;
    if (info.running) info.label = "WLAN AutoConfig (WlanSvc)";
  }
  if (!info.running) {
    if (auto dhcp = run_capture("sc query Dhcp 2>nul"))
      info.running = dhcp->find("RUNNING") != std::string::npos;
    info.label = "DHCP Client + NetSetup";
  }

  if (auto v = run_capture("ver 2>nul")) info.version = trim(split_lines(*v).empty() ? "" : split_lines(*v)[0]);

  if (auto out = run_capture("netsh interface show interface 2>nul")) {
    for (const auto& line : split_lines(*out)) {
      if (line.find("Connected") != std::string::npos) {
        std::istringstream iss(line);
        std::string tok;
        std::vector<std::string> cols;
        while (iss >> tok) cols.push_back(tok);
        if (!cols.empty()) info.active_connections.push_back(cols.back());
      }
    }
  }
  return info;
}

std::vector<ConnectionSnapshot> list_connections() {
  return {detect_current_connection()};
}

}  // namespace znet

#endif