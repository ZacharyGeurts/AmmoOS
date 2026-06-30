#include "znetwork/connection_snapshot.hpp"

#include <sstream>

namespace znet {

#if !defined(ZNETWORK_LINUX) && !defined(ZNETWORK_WIN) && !defined(ZNETWORK_DARWIN)
ConnectionSnapshot detect_current_connection_platform() {
  ConnectionSnapshot snap;
  snap.os = detect_os();
  snap.state = "unsupported_platform";
  return snap;
}
#endif

namespace {

std::string json_escape(std::string_view s) {
  std::string o;
  for (char c : s) {
    switch (c) {
      case '"': o += "\\\""; break;
      case '\\': o += "\\\\"; break;
      case '\n': o += "\\n"; break;
      default: o += c;
    }
  }
  return o;
}

}  // namespace

std::string snapshot_to_json(const ConnectionSnapshot& snap) {
  std::ostringstream o;
  o << "{\n";
  o << "  \"os\": \"" << json_escape(snap.os) << "\",\n";
  o << "  \"platform_backend\": \"" << json_escape(snap.platform_backend) << "\",\n";
  o << "  \"iface\": \"" << json_escape(snap.iface) << "\",\n";
  o << "  \"iface_type\": \"" << json_escape(snap.iface_type) << "\",\n";
  o << "  \"mac\": \"" << json_escape(snap.mac) << "\",\n";
  o << "  \"ipv4\": \"" << json_escape(snap.ipv4) << "\",\n";
  o << "  \"gateway\": \"" << json_escape(snap.gateway) << "\",\n";
  o << "  \"ssid\": \"" << json_escape(snap.ssid) << "\",\n";
  o << "  \"connection_name\": \"" << json_escape(snap.connection_name) << "\",\n";
  o << "  \"state\": \"" << json_escape(snap.state) << "\",\n";
  o << "  \"is_default_route\": " << (snap.is_default_route ? "true" : "false") << ",\n";
  o << "  \"dns\": [";
  for (std::size_t i = 0; i < snap.dns.size(); ++i) {
    if (i) o << ", ";
    o << "{\"address\": \"" << json_escape(snap.dns[i].address) << "\", \"source\": \""
      << json_escape(snap.dns[i].source) << "\"}";
  }
  o << "]\n}\n";
  return o.str();
}

}  // namespace znet