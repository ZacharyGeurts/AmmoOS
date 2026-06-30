#pragma once

#include "connection_snapshot.hpp"

#include <string>

namespace znet {

struct FieldSecurityPosture {
  std::string schema{"znetwork-field-security/v1"};
  bool gatekeeper{true};
  bool truth_dns{true};
  bool packet_field{true};
  bool trust_strike{true};
  bool connection_iff{true};
  std::string nexus_install;   // SG/NewLatest
  std::string state_dir;
  std::string socket_path;     // field control IPC
};

FieldSecurityPosture default_field_posture();

/** Hooks for NEXUS slices — review build writes posture JSON only. */
std::string field_posture_json(const FieldSecurityPosture& p,
                               const ConnectionSnapshot& snap);

}  // namespace znet