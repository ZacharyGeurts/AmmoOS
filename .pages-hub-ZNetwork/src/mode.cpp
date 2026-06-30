#include "znetwork/mode.hpp"

#include "znetwork/platform.hpp"

#include <fstream>
#include <sstream>

namespace znet {

namespace {

bool json_has_approved_true(const std::string& path) {
  if (!file_exists(path)) return false;
  std::ifstream in(path);
  if (!in) return false;
  std::ostringstream ss;
  ss << in.rdbuf();
  const std::string doc = ss.str();
  return doc.find("\"approved\"") != std::string::npos &&
         (doc.find("\"approved\": true") != std::string::npos ||
          doc.find("\"approved\":true") != std::string::npos);
}

}  // namespace

bool active_mode_allowed(const std::string& checklist_path) {
  const char* no_review = std::getenv("ZNETWORK_NO_REVIEW");
  if (no_review && no_review[0] == '1') return true;
  const char* outside = std::getenv("ZNETWORK_OUTSIDE_LAB");
  if (outside && outside[0] == '1') {
    if (!json_has_approved_true(checklist_path)) return false;
    const char* env = std::getenv("ZNETWORK_REVIEW_APPROVED");
    return env && env[0] == '1';
  }
  if (json_has_approved_true(checklist_path)) return true;
  const char* env = std::getenv("ZNETWORK_REVIEW_APPROVED");
  return env && env[0] == '1';
}

bool shadow_mode_allowed() {
  const char* no_review = std::getenv("ZNETWORK_NO_REVIEW");
  if (no_review && no_review[0] == '1') return true;
  const char* gate = std::getenv("ZNETWORK_LAB_GATE_OK");
  return gate && gate[0] == '1';
}

RunMode resolve_effective_mode(RunMode requested, const std::string& checklist_path) {
  if (requested == RunMode::Active) {
    if (!active_mode_allowed(checklist_path)) return RunMode::ReviewOnly;
    return RunMode::Active;
  }
  if (requested == RunMode::Shadow) {
    if (!shadow_mode_allowed()) return RunMode::ReviewOnly;
    return RunMode::Shadow;
  }
  return requested;
}

}  // namespace znet