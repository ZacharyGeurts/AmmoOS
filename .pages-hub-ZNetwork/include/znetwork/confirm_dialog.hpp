#pragma once

#include "slide_in.hpp"

#include <optional>
#include <string>

namespace znet {

struct TakeoverOffer {
  std::string title{"ZNetwork — Field Secure Network"};
  std::string connection_line;
  std::vector<std::string> will_disable;
  std::vector<std::string> will_replace_with;
  std::string preserve_note;
  std::string warning{
      "Connection stays up during handoff. Rollback restores the native manager."};
};

enum class DialogChoice { Yes, No, Skip, Unavailable };

TakeoverOffer build_takeover_offer(const SlideInPlan& plan);

std::string offer_message_text(const TakeoverOffer& offer);

/** Startup dialog: Yes / No / Skip (not recommended). */
DialogChoice show_startup_dialog(const TakeoverOffer& offer);

/** Legacy yes/no popup. nullopt = cancelled / no display server. */
std::optional<bool> show_confirm_dialog(const TakeoverOffer& offer);

const char* dialog_choice_name(DialogChoice c);

}  // namespace znet