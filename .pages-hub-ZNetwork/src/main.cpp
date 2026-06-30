#include "znetwork/confirm_dialog.hpp"
#include "znetwork/connection_snapshot.hpp"
#include "znetwork/ddos_shield.hpp"
#include "znetwork/field_security.hpp"
#include "znetwork/mode.hpp"
#include "znetwork/native_backend.hpp"
#include "znetwork/negotiation_guard.hpp"
#include "znetwork/slide_in.hpp"

#include <cstdlib>
#include <iostream>
#include <string>

namespace {

std::string default_checklist_path() {
  const char* root = std::getenv("SG_ROOT");
  std::string base = root ? root : ".";
  return base + "/ZNetwork/data/review-checklist.json";
}

void usage() {
  std::cerr
      << "ZNetwork " << ZNETWORK_VERSION << " — field secure network manager\n"
      << "Usage:\n"
      << "  znetwork probe [--json]     Detect connection + backend (no mutation)\n"
      << "  znetwork plan [--json]        Slide-in handoff plan\n"
      << "  znetwork status [--json]      Full posture report\n"
      << "  znetwork mode <REVIEW|SHADOW|ACTIVE>  Show effective mode\n"
      << "  znetwork confirm              Yes/No popup — disable vs replace\n"
      << "  znetwork startup              Yes / No / Skip — when not running\n\n"
      << "Default: ACTIVE when checklist approved or ZNETWORK_OUTSIDE_LAB=1\n";
}

}  // namespace

#ifndef ZNETWORK_VERSION
#define ZNETWORK_VERSION "2.0.0-release"
#endif

int main(int argc, char** argv) {
  const std::string checklist = default_checklist_path();
  const char* cmd = argc > 1 ? argv[1] : "probe";

  if (std::string(cmd) == "-h" || std::string(cmd) == "--help" || std::string(cmd) == "help") {
    usage();
    return 0;
  }

  bool json_out = false;
  for (int i = 2; i < argc; ++i) {
    if (std::string(argv[i]) == "--json") json_out = true;
  }

  const auto snap = znet::detect_current_connection();
  const auto backend = znet::detect_native_backend();
  znet::RunMode requested = znet::RunMode::ReviewOnly;
  if (std::getenv("ZNETWORK_MODE"))
    requested = znet::parse_mode(std::getenv("ZNETWORK_MODE"));
  const auto effective = znet::resolve_effective_mode(requested, checklist);

  if (std::string(cmd) == "mode") {
    if (argc > 2) requested = znet::parse_mode(argv[2]);
    const auto eff = znet::resolve_effective_mode(requested, checklist);
    if (json_out) {
      std::cout << "{\"requested\":\"" << znet::mode_name(requested)
                << "\",\"effective\":\"" << znet::mode_name(eff)
                << "\",\"active_allowed\":"
                << (znet::active_mode_allowed(checklist) ? "true" : "false") << "}\n";
    } else {
      std::cout << "requested=" << znet::mode_name(requested)
                << " effective=" << znet::mode_name(eff) << "\n";
    }
    return 0;
  }

  if (std::string(cmd) == "probe") {
    if (json_out) {
      std::cout << "{\n\"connection\":\n" << znet::snapshot_to_json(snap)
                << ",\n\"backend\": {\"id\":\"" << backend.id << "\",\"label\":\""
                << backend.label << "\",\"running\":" << (backend.running ? "true" : "false")
                << "}\n}\n";
    } else {
      std::cout << "OS: " << snap.os << "\nBackend: " << backend.label
                << (backend.running ? " (running)" : "") << "\nIface: " << snap.iface
                << "\nIPv4: " << snap.ipv4 << "\nGateway: " << snap.gateway
                << "\nState: " << snap.state << "\n";
    }
    return 0;
  }

  if (std::string(cmd) == "confirm" || std::string(cmd) == "startup") {
    auto plan = znet::build_slide_in_plan(effective, snap, backend);
    const auto offer = znet::build_takeover_offer(plan);
    const bool startup = std::string(cmd) == "startup";
    if (json_out) {
      std::cout << "{\n  \"title\": \"" << offer.title << "\",\n";
      std::cout << "  \"connection\": \"" << offer.connection_line << "\",\n";
      std::cout << "  \"will_disable\": [";
      for (std::size_t i = 0; i < offer.will_disable.size(); ++i) {
        if (i) std::cout << ", ";
        std::cout << "\"" << offer.will_disable[i] << "\"";
      }
      std::cout << "],\n  \"will_replace_with\": [";
      for (std::size_t i = 0; i < offer.will_replace_with.size(); ++i) {
        if (i) std::cout << ", ";
        std::cout << "\"" << offer.will_replace_with[i] << "\"";
      }
      std::cout << "],\n  \"startup\": " << (startup ? "true" : "false") << "\n}\n";
      return 0;
    }
    if (startup) {
      const auto choice = znet::show_startup_dialog(offer);
      std::cout << "CHOICE=" << znet::dialog_choice_name(choice) << "\n";
      if (choice == znet::DialogChoice::Yes) return 0;
      if (choice == znet::DialogChoice::No) return 1;
      if (choice == znet::DialogChoice::Skip) return 2;
      std::cerr << "ZNetwork: no graphical dialog (install zenity, yad, or kdialog)\n";
      std::cerr << znet::offer_message_text(offer) << "\n";
      return 3;
    }
    const auto answer = znet::show_confirm_dialog(offer);
    if (!answer.has_value()) {
      std::cerr << "ZNetwork: no graphical dialog available (install zenity/kdialog or use DISPLAY)\n";
      std::cerr << znet::offer_message_text(offer) << "\n";
      return 3;
    }
    if (*answer) {
      std::cout << "CONFIRMED — operator accepted handoff plan (no mutation until review ACTIVE gate)\n";
      return 0;
    }
    std::cout << "CANCELLED — native network manager unchanged\n";
    return 1;
  }

  if (std::string(cmd) == "plan" || std::string(cmd) == "status") {
    auto plan = znet::build_slide_in_plan(effective, snap, backend);
    plan = znet::execute_slide_in(plan, effective);
    const auto field = znet::default_field_posture();
    const auto ddos = znet::assess_ddosshield(effective == znet::RunMode::Active);
    const auto neg = znet::assess_negotiation(effective == znet::RunMode::Active);

    if (json_out) {
      std::cout << "{\n";
      std::cout << "  \"schema\": \"znetwork-status/v1\",\n";
      std::cout << "  \"effective_mode\": \"" << znet::mode_name(effective) << "\",\n";
      std::cout << "  \"connection\": " << znet::snapshot_to_json(snap) << ",\n";
      std::cout << "  \"slide_in\": " << znet::plan_to_json(plan) << ",\n";
      std::cout << "  \"field_security\": " << znet::field_posture_json(field, snap) << ",\n";
      std::cout << "  \"ddos\": " << znet::ddos_to_json(ddos) << ",\n";
      std::cout << "  \"negotiation\": " << znet::negotiation_to_json(neg) << "\n";
      std::cout << "}\n";
    } else {
      std::cout << "ZNetwork status — mode " << znet::mode_name(effective) << "\n";
      std::cout << znet::plan_to_json(plan);
    }
    return 0;
  }

  usage();
  return 2;
}