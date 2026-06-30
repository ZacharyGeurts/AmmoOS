#pragma once

#include "connection_snapshot.hpp"

#include <string>
#include <vector>

namespace znet {

struct NativeBackendInfo {
  std::string id;           // networkmanager, systemd-networkd, winwlan, darwin
  std::string label;
  bool running{false};
  bool manageable{false}; // can be set unmanaged in ACTIVE (not in REVIEW)
  std::string version;
  std::vector<std::string> active_connections;
};

/** Probe which OS network manager is authoritative. */
NativeBackendInfo detect_native_backend();

/** List connection profiles (read-only). */
std::vector<ConnectionSnapshot> list_connections();

}  // namespace znet