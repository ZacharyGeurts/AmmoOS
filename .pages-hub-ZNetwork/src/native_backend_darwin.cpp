#include "znetwork/native_backend.hpp"

#include "znetwork/platform.hpp"

#if defined(ZNETWORK_DARWIN)

namespace znet {

NativeBackendInfo detect_native_backend() {
  NativeBackendInfo info;
  info.id = "darwin_configd";
  info.label = "macOS configd / SystemConfiguration";
  info.manageable = true;
  info.running = true;

  if (auto v = run_capture("sw_vers -productVersion 2>/dev/null")) info.version = trim(*v);

  if (auto out = run_capture("scutil --nc list 2>/dev/null")) {
    for (const auto& line : split_lines(*out)) {
      if (line.find("Connected") != std::string::npos) {
        auto lb = line.find('(');
        auto rb = line.rfind(')');
        if (lb != std::string::npos && rb != std::string::npos && rb > lb)
          info.active_connections.push_back(trim(line.substr(lb + 1, rb - lb - 1)));
      }
    }
  }

  if (info.active_connections.empty()) {
    if (auto ports = run_capture("networksetup -listallnetworkservices 2>/dev/null")) {
      for (const auto& line : split_lines(*ports)) {
        if (!line.empty() && line[0] != '*') info.active_connections.push_back(line);
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