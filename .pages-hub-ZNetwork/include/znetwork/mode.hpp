#pragma once

#include <cstdlib>
#include <string>
#include <string_view>

namespace znet {

enum class RunMode {
  ReviewOnly,  // default — detect + plan, no mutation
  Shadow,      // observe + field receipts, native manager stays up
  Active,      // takeover — blocked until review approved
};

inline std::string_view mode_name(RunMode m) noexcept {
  switch (m) {
    case RunMode::ReviewOnly: return "REVIEW_ONLY";
    case RunMode::Shadow: return "SHADOW";
    case RunMode::Active: return "ACTIVE";
  }
  return "UNKNOWN";
}

inline RunMode parse_mode(std::string_view s) noexcept {
  if (s == "SHADOW" || s == "shadow") return RunMode::Shadow;
  if (s == "ACTIVE" || s == "active") return RunMode::Active;
  return RunMode::ReviewOnly;
}

/** ACTIVE requires env ZNETWORK_REVIEW_APPROVED=1 and checklist file. */
bool active_mode_allowed(const std::string& checklist_path);

/** SHADOW requires env ZNETWORK_LAB_GATE_OK=1 (test battery passed). */
bool shadow_mode_allowed();

RunMode resolve_effective_mode(RunMode requested, const std::string& checklist_path);

}  // namespace znet