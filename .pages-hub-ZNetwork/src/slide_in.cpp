#include "znetwork/slide_in.hpp"

#include "znetwork/platform.hpp"

#include <sstream>

namespace znet {

namespace {

std::string json_escape(std::string_view s) {
  std::string o;
  for (char c : s) {
    if (c == '"') o += "\\\"";
    else if (c == '\\') o += "\\\\";
    else o += c;
  }
  return o;
}

void add_step(SlideInPlan& plan, int order, std::string phase, std::string action,
              std::string risk, std::string detail) {
  plan.steps.push_back(SlideInStep{order, std::move(phase), std::move(action),
                                   std::move(risk), false, std::move(detail)});
}

}  // namespace

namespace {

void fill_disable_replace(SlideInPlan& plan, const NativeBackendInfo& backend,
                          const ConnectionSnapshot& snap) {
#if defined(ZNETWORK_LINUX)
  plan.will_disable = {
      backend.label + " policy daemon (after stable handoff)",
      "systemd-resolved as default client (resolver redirected to field-dns)",
      "Unmanaged OS DNS negotiation on " + snap.iface,
  };
  if (backend.id == "networkmanager") {
    plan.will_disable.push_back("NetworkManager.service — masked after 30s probe");
    plan.will_disable.push_back("nmcli managed mode on " + snap.iface);
  } else if (backend.id == "systemd-networkd") {
    plan.will_disable.push_back("systemd-networkd.service — masked after handoff");
  }
  plan.will_replace_with = {
      "ZNetwork field policy daemon (connection owner)",
      "Field DNS — truth resolver + gatekeeper IFF",
      "Connection gatekeeper — 10-axis per-flow scoring",
      "Packet-field — per-navigation receipts",
      "DDoS shield — SYN/token-bucket + RST flood detect",
      "Negotiation guard — TLS 1.2+, no downgrade, field DNS only",
      "Trust-strike + field-attack-kit hostile interdict",
  };
#elif defined(ZNETWORK_WIN)
  plan.will_disable = {
      "WLAN AutoConfig (WlanSvc) policy ownership",
      "NetSetup / DHCP client DNS path on " + snap.iface,
      "Windows native Wi-Fi profile manager for active session",
  };
  plan.will_replace_with = {
      "ZNetwork field policy service (WFP filters + policy owner)",
      "Field DNS resolver shim",
      "Connection gatekeeper + DDoS shield",
      "Negotiation guard + packet-field receipts",
  };
#elif defined(ZNETWORK_DARWIN)
  plan.will_disable = {
      "configd / SystemConfiguration network preferences",
      "networksetup authoritative DNS on " + snap.iface,
      "Apple captive-portal resolver bypass path",
  };
  plan.will_replace_with = {
      "ZNetwork field policy agent (NetworkExtension track)",
      "Field DNS + gatekeeper IFF",
      "DDoS shield + negotiation guard",
      "Packet-field + trust-strike integration",
  };
#else
  plan.will_disable = {backend.label};
  plan.will_replace_with = {"ZNetwork field secure stack"};
#endif
}

}  // namespace

SlideInPlan build_slide_in_plan(RunMode mode, const ConnectionSnapshot& snap,
                                const NativeBackendInfo& backend) {
  SlideInPlan plan;
  plan.mode = mode;
  plan.backend = backend;
  plan.primary = snap;
  plan.would_interrupt = false;
  fill_disable_replace(plan, backend, snap);

  add_step(plan, 1, "discover", "snapshot_live_connection", "none",
           "Read iface/IP/DNS/gateway without link down");
  add_step(plan, 2, "mirror", "clone_profile_to_znetwork", "none",
           "Hold equivalent L3 profile in ZNetwork state machine");
  add_step(plan, 3, "attach", "field_nftables_hooks", "low",
           "Attach gatekeeper + DDoS hooks on existing iface — no carrier drop");
  add_step(plan, 4, "attach", "truth_dns_redirect", "low",
           "Point resolver to field-dns via loopback — preserve caches");
  add_step(plan, 5, "handoff", "set_native_unmanaged", "medium",
           "nmcli dev set " + snap.iface + " managed no — session preserved");
  add_step(plan, 6, "handoff", "znetwork_policy_owner", "medium",
           "ZNetwork becomes policy owner; wpa_supplicant session unchanged");
  add_step(plan, 7, "retire", "mask_native_manager", "high",
           "Mask NetworkManager only after 30s stable probe — reversible");

  if (mode == RunMode::ReviewOnly) {
    plan.verdict = "READY_FOR_REVIEW";
  } else if (mode == RunMode::Shadow) {
    plan.verdict = "SHADOW_ATTACH_ONLY";
    plan.steps[2].detail += " (shadow: log only)";
    plan.steps[3].detail += " (shadow: log only)";
  } else {
    plan.verdict = "ACTIVE_PLANNED";
  }
  return plan;
}

SlideInPlan execute_slide_in(const SlideInPlan& plan, RunMode effective_mode) {
  SlideInPlan out = plan;
  if (effective_mode == RunMode::ReviewOnly) {
    out.verdict = "REVIEW_ONLY_NO_MUTATION";
    return out;
  }
  if (effective_mode == RunMode::Shadow) {
    for (auto& s : out.steps) {
      if (s.phase == "attach") {
        s.executed = false;
        s.detail += " [shadow: not executed]";
      }
    }
    out.verdict = "SHADOW_COMPLETE";
    return out;
  }
  // ACTIVE without sudo — user-space supersession (Python handler-retire owns policy).
  const char* no_sudo = std::getenv("NEXUS_ZNETWORK_NO_SUDO");
  const bool user_space = no_sudo && no_sudo[0] && no_sudo[0] != '0';
  if (user_space) {
    for (auto& s : out.steps) {
      if (s.phase == "discover" || s.phase == "mirror" || s.phase == "attach") {
        s.executed = true;
        s.detail += " [user-space: no sudo]";
      } else if (s.phase == "handoff" || s.phase == "retire") {
        s.executed = false;
        s.detail += " [deferred: OS manager left up; ZNetwork supersedes policy]";
      }
    }
    out.verdict = "ACTIVE_USER_SPACE_SUPERSEDES";
    return out;
  }
  out.verdict = "ACTIVE_BLOCKED_IMPLEMENTATION";
  for (auto& s : out.steps) {
    if (s.phase == "retire" || s.phase == "handoff") s.executed = false;
  }
  return out;
}

std::string plan_to_json(const SlideInPlan& plan) {
  std::ostringstream o;
  o << "{\n";
  o << "  \"mode\": \"" << mode_name(plan.mode) << "\",\n";
  o << "  \"verdict\": \"" << json_escape(plan.verdict) << "\",\n";
  o << "  \"would_interrupt\": " << (plan.would_interrupt ? "true" : "false") << ",\n";
  o << "  \"backend\": \"" << json_escape(plan.backend.label) << "\",\n";
  o << "  \"iface\": \"" << json_escape(plan.primary.iface) << "\",\n";
  o << "  \"steps\": [\n";
  for (std::size_t i = 0; i < plan.steps.size(); ++i) {
    const auto& s = plan.steps[i];
    if (i) o << ",\n";
    o << "    {\"order\": " << s.order << ", \"phase\": \"" << json_escape(s.phase)
      << "\", \"action\": \"" << json_escape(s.action) << "\", \"risk\": \""
      << json_escape(s.risk) << "\", \"executed\": " << (s.executed ? "true" : "false")
      << ", \"detail\": \"" << json_escape(s.detail) << "\"}";
  }
  o << "\n  ]\n}\n";
  return o.str();
}

}  // namespace znet