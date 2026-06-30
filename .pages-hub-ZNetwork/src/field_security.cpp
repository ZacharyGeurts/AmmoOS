#include "znetwork/field_security.hpp"

#include "znetwork/platform.hpp"

#include <cstdlib>
#include <sstream>

namespace znet {

FieldSecurityPosture default_field_posture() {
  FieldSecurityPosture p;
  const char* install = std::getenv("NEXUS_INSTALL_ROOT");
  const char* state = std::getenv("NEXUS_STATE_DIR");
  p.nexus_install = install ? install : "SG/NewLatest";
  p.state_dir = state ? state : "SG/NewLatest/Queen/.nexus-state";
  p.socket_path = p.state_dir + "/znetwork-field.sock";
  return p;
}

std::string field_posture_json(const FieldSecurityPosture& p,
                               const ConnectionSnapshot& snap) {
  std::ostringstream o;
  o << "{\n";
  o << "  \"schema\": \"" << p.schema << "\",\n";
  o << "  \"gatekeeper\": true,\n";
  o << "  \"truth_dns\": true,\n";
  o << "  \"packet_field\": true,\n";
  o << "  \"trust_strike\": true,\n";
  o << "  \"connection_iff\": true,\n";
  o << "  \"nexus_install\": \"" << p.nexus_install << "\",\n";
  o << "  \"state_dir\": \"" << p.state_dir << "\",\n";
  o << "  \"socket_path\": \"" << p.socket_path << "\",\n";
  o << "  \"monitored_iface\": \"" << snap.iface << "\",\n";
  o << "  \"bridges\": {\n";
  o << "    \"connection_gatekeeper\": \"lib/connection-gatekeeper.py\",\n";
  o << "    \"field_dns\": \"lib/field-dns.py\",\n";
  o << "    \"packet_field\": \"lib/packet-field.py\",\n";
  o << "    \"trust_strike\": \"lib/trust-strike-engine.py\",\n";
  o << "    \"attack_kit\": \"lib/field-attack-kit.py\",\n";
  o << "    \"hostile_threat\": \"lib/znetwork-hostile-threat.py\"\n";
  o << "  },\n";
  o << "  \"hostile_threat\": {\n";
  o << "    \"schema\": \"znetwork-hostile-threat/v1\",\n";
  o << "    \"immediate_detection\": true,\n";
  o << "    \"zero_hesitation_interdict\": true\n";
  o << "  }\n}\n";
  return o.str();
}

}  // namespace znet