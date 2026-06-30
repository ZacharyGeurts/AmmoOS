#pragma once

#include <string>

namespace znet {

struct NegotiationPolicy {
  std::string min_tls{"1.2"};
  bool block_tls_downgrade{true};
  bool dns_only_field_resolver{true};
  bool tcp_fast_open_allowed{false};
  bool require_sni{true};
  bool inspect_alpn{true};
};

struct NegotiationAssessment {
  std::string schema{"znetwork-negotiation/v1"};
  NegotiationPolicy policy;
  std::string status;
  std::string detail;
};

NegotiationAssessment assess_negotiation(bool enforce);

std::string negotiation_to_json(const NegotiationAssessment& a);

}  // namespace znet