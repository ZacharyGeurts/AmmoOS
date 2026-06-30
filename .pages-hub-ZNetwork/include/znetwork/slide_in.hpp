#pragma once

#include "connection_snapshot.hpp"
#include "mode.hpp"
#include "native_backend.hpp"

#include <string>
#include <vector>

namespace znet {

struct SlideInStep {
  int order{0};
  std::string phase;
  std::string action;
  std::string risk;   // none, low, medium, high
  bool executed{false};
  std::string detail;
};

struct SlideInPlan {
  RunMode mode{RunMode::ReviewOnly};
  NativeBackendInfo backend;
  ConnectionSnapshot primary;
  std::vector<SlideInStep> steps;
  std::vector<std::string> will_disable;
  std::vector<std::string> will_replace_with;
  bool would_interrupt{false};
  std::string verdict;  // READY_FOR_REVIEW, BLOCKED_ACTIVE, ...
};

/** Build handoff plan — steps marked executed only in ACTIVE+approved. */
SlideInPlan build_slide_in_plan(RunMode mode, const ConnectionSnapshot& snap,
                                const NativeBackendInfo& backend);

/** Apply plan — NO-OP unless ACTIVE+approved; SHADOW only logs. */
SlideInPlan execute_slide_in(const SlideInPlan& plan, RunMode effective_mode);

std::string plan_to_json(const SlideInPlan& plan);

}  // namespace znet