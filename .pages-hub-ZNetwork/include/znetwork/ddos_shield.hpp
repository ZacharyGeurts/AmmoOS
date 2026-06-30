#pragma once

#include <cstdint>
#include <string>

namespace znet {

struct DDoSPolicy {
  std::uint32_t syn_per_src_per_sec{64};
  std::uint32_t global_syn_per_sec{4096};
  std::uint32_t udp_flood_per_sec{2048};
  std::uint32_t hold_unknown_listeners{32};
  bool syn_cookies_recommended{true};
  bool rst_flood_detect{true};
};

struct DDoSAssessment {
  std::string schema{"znetwork-ddos/v1"};
  DDoSPolicy policy;
  std::string status;  // armed_review, shadow_watch, active_enforce
  std::string recommendation;
};

DDoSAssessment assess_ddosshield(bool active_enforce);

std::string ddos_to_json(const DDoSAssessment& a);

}  // namespace znet