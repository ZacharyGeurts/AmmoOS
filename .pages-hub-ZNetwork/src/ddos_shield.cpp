#include "znetwork/ddos_shield.hpp"

#include <sstream>

namespace znet {

DDoSAssessment assess_ddosshield(bool active_enforce) {
  DDoSAssessment a;
  a.policy = DDoSPolicy{};
  a.status = active_enforce ? "active_enforce" : "armed_review";
  a.recommendation =
      active_enforce
          ? "Enforce syn/token-bucket via nftables znetwork table"
          : "Review sysctl net.ipv4.tcp_syncookies=1 and per-src limits before ACTIVE";
  return a;
}

std::string ddos_to_json(const DDoSAssessment& a) {
  std::ostringstream o;
  o << "{\n";
  o << "  \"schema\": \"" << a.schema << "\",\n";
  o << "  \"status\": \"" << a.status << "\",\n";
  o << "  \"recommendation\": \"" << a.recommendation << "\",\n";
  o << "  \"policy\": {\n";
  o << "    \"syn_per_src_per_sec\": " << a.policy.syn_per_src_per_sec << ",\n";
  o << "    \"global_syn_per_sec\": " << a.policy.global_syn_per_sec << ",\n";
  o << "    \"syn_cookies_recommended\": "
    << (a.policy.syn_cookies_recommended ? "true" : "false") << "\n";
  o << "  }\n}\n";
  return o.str();
}

}  // namespace znet