#include "znetwork/negotiation_guard.hpp"

#include <sstream>

namespace znet {

NegotiationAssessment assess_negotiation(bool enforce) {
  NegotiationAssessment a;
  a.policy = NegotiationPolicy{};
  a.status = enforce ? "enforce" : "review";
  a.detail =
      "TLS>=1.2, block downgrade, DNS via field resolver, ALPN inspect — "
      "negotiation receipts to packet-field";
  return a;
}

std::string negotiation_to_json(const NegotiationAssessment& a) {
  std::ostringstream o;
  o << "{\n";
  o << "  \"schema\": \"" << a.schema << "\",\n";
  o << "  \"status\": \"" << a.status << "\",\n";
  o << "  \"detail\": \"" << a.detail << "\",\n";
  o << "  \"policy\": {\"min_tls\": \"" << a.policy.min_tls
    << "\", \"block_tls_downgrade\": true, \"dns_only_field_resolver\": true}\n";
  o << "}\n";
  return o.str();
}

}  // namespace znet