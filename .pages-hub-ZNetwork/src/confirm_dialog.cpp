#include "znetwork/confirm_dialog.hpp"

#include "znetwork/platform.hpp"

#include <iostream>
#include <sstream>

#if defined(ZNETWORK_WIN)
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#endif

namespace znet {

TakeoverOffer build_takeover_offer(const SlideInPlan& plan) {
  TakeoverOffer o;
  const auto& s = plan.primary;
  o.connection_line = s.iface + " · " + s.ipv4 + " · gw " + s.gateway;
  if (!s.ssid.empty()) o.connection_line += " · " + s.ssid;
  o.will_disable = plan.will_disable;
  o.will_replace_with = plan.will_replace_with;
  o.preserve_note =
      "Your current IP, gateway, and link stay active — no intentional disconnect.";
  return o;
}

std::string offer_message_text(const TakeoverOffer& offer) {
  std::ostringstream msg;
  msg << "Current connection:\n  " << offer.connection_line << "\n\n";
  msg << "ZNetwork will DISABLE (native manager — not your link):\n";
  for (const auto& line : offer.will_disable) msg << "  • " << line << "\n";
  msg << "\nZNetwork will REPLACE WITH (field secure stack):\n";
  for (const auto& line : offer.will_replace_with) msg << "  • " << line << "\n";
  msg << "\n" << offer.preserve_note << "\n\n" << offer.warning;
  return msg.str();
}

const char* dialog_choice_name(DialogChoice c) {
  switch (c) {
    case DialogChoice::Yes:
      return "yes";
    case DialogChoice::No:
      return "no";
    case DialogChoice::Skip:
      return "skip";
    case DialogChoice::Unavailable:
    default:
      return "unavailable";
  }
}

namespace {

std::string shell_escape_single(std::string_view s) {
  std::string o = "'";
  for (char c : s) {
    if (c == '\'') o += "'\\''";
    else o += c;
  }
  o += "'";
  return o;
}

std::string startup_message_text(const TakeoverOffer& offer) {
  return offer_message_text(offer) +
         "\n\nZNetwork is not running. Start field secure network handoff?";
}

#if defined(ZNETWORK_LINUX)

DialogChoice startup_linux(const std::string& title, const std::string& body) {
  const std::string esc_title = shell_escape_single(title);
  const std::string esc_body = shell_escape_single(body);
  if (run_capture("command -v yad 2>/dev/null")) {
    const std::string cmd =
        "yad --question --title=" + esc_title + " --text=" + esc_body +
        " --button='Yes:0' --button='No:1' --button='Skip (not recommended):2' "
        "--width=560 --wrap 2>/dev/null; echo $?";
    if (auto code = run_capture(cmd)) {
      const std::string t = trim(*code);
      if (t == "0") return DialogChoice::Yes;
      if (t == "1") return DialogChoice::No;
      if (t == "2") return DialogChoice::Skip;
    }
  }
  if (run_capture("command -v zenity 2>/dev/null")) {
    const std::string cmd =
        "zenity --question --title=" + esc_title + " --text=" + esc_body +
        " --ok-label='Yes' --cancel-label='No' "
        "--extra-button='Skip (not recommended)' --width=560 2>/dev/null; echo $?";
    if (auto code = run_capture(cmd)) {
      const std::string t = trim(*code);
      if (t == "0") return DialogChoice::Yes;
      if (t == "1") return DialogChoice::No;
      if (t == "2") return DialogChoice::Skip;
    }
  }
  if (run_capture("command -v kdialog 2>/dev/null")) {
    const std::string cmd =
        "kdialog --title " + esc_title +
        " --menu 'ZNetwork startup' yes 'Yes — start field network' "
        "no 'No — keep native manager' skip 'Skip (not recommended)' 2>/dev/null";
    if (auto pick = run_capture(cmd)) {
      const std::string t = trim(*pick);
      if (t == "yes") return DialogChoice::Yes;
      if (t == "no") return DialogChoice::No;
      if (t == "skip") return DialogChoice::Skip;
    }
  }
  if (const char* d = std::getenv("DISPLAY"); !d || !d[0]) return DialogChoice::Unavailable;
  std::cerr << body << "\n[Yes / No / Skip (not recommended)] y/n/s: ";
  std::string line;
  if (!std::getline(std::cin, line)) return DialogChoice::Unavailable;
  if (line == "y" || line == "Y" || line == "yes") return DialogChoice::Yes;
  if (line == "s" || line == "S" || line == "skip") return DialogChoice::Skip;
  return DialogChoice::No;
}

std::optional<bool> confirm_linux(const std::string& title, const std::string& body) {
  const std::string esc_title = shell_escape_single(title);
  const std::string esc_body = shell_escape_single(body);
  if (run_capture("command -v zenity 2>/dev/null")) {
    const std::string cmd =
        "zenity --question --title=" + esc_title + " --text=" + esc_body +
        " --ok-label='Yes, proceed' --cancel-label='No' --width=520 2>/dev/null; echo $?";
    if (auto code = run_capture(cmd)) {
      return trim(*code) == "0";
    }
  }
  if (run_capture("command -v kdialog 2>/dev/null")) {
    const std::string cmd = "kdialog --title " + esc_title + " --yesno " + esc_body +
                            " --yes-label 'Yes' --no-label 'No' 2>/dev/null; echo $?";
    if (auto code = run_capture(cmd)) return trim(*code) == "0";
  }
  const auto choice = startup_linux(title, body);
  if (choice == DialogChoice::Unavailable) return std::nullopt;
  return choice == DialogChoice::Yes;
}

#endif

#if defined(ZNETWORK_DARWIN)

DialogChoice startup_darwin(const std::string& title, const std::string& body) {
  std::string escaped;
  for (char c : body) {
    if (c == '"') escaped += "\\\"";
    else if (c == '\n') escaped += "\\n";
    else escaped += c;
  }
  std::string script = R"(osascript -e 'display dialog ")" + escaped +
                       R"(" with title ")" + title +
                       R"(" buttons {"Skip (not recommended)", "No", "Yes"} default button "Yes" cancel button "No"' 2>/dev/null)";
  if (auto out = run_capture(script)) {
    if (out->find("Yes") != std::string::npos) return DialogChoice::Yes;
    if (out->find("Skip") != std::string::npos) return DialogChoice::Skip;
    if (out->find("No") != std::string::npos) return DialogChoice::No;
  }
  return DialogChoice::Unavailable;
}

std::optional<bool> confirm_darwin(const std::string& title, const std::string& body) {
  const auto c = startup_darwin(title, body + "\n\nProceed?");
  if (c == DialogChoice::Unavailable) return std::nullopt;
  return c == DialogChoice::Yes;
}

#endif

#if defined(ZNETWORK_WIN)

DialogChoice startup_win(const std::string& title, const std::string& body) {
  const std::string msg = body + "\n\nYes = start ZNetwork\nNo = keep native manager\n"
                          "Cancel = Skip (not recommended)";
  const int r = MessageBoxA(nullptr, msg.c_str(), title.c_str(),
                              MB_YESNOCANCEL | MB_ICONQUESTION | MB_TOPMOST);
  if (r == IDYES) return DialogChoice::Yes;
  if (r == IDNO) return DialogChoice::No;
  if (r == IDCANCEL) return DialogChoice::Skip;
  return DialogChoice::Unavailable;
}

std::optional<bool> confirm_win(const std::string& title, const std::string& body) {
  const auto c = startup_win(title, body + "\n\nProceed?");
  if (c == DialogChoice::Unavailable) return std::nullopt;
  return c == DialogChoice::Yes;
}

#endif

}  // namespace

DialogChoice show_startup_dialog(const TakeoverOffer& offer) {
  const std::string msg = startup_message_text(offer);
#if defined(ZNETWORK_LINUX)
  return startup_linux(offer.title, msg);
#elif defined(ZNETWORK_DARWIN)
  return startup_darwin(offer.title, msg);
#elif defined(ZNETWORK_WIN)
  return startup_win(offer.title, msg);
#else
  (void)offer;
  return DialogChoice::Unavailable;
#endif
}

std::optional<bool> show_confirm_dialog(const TakeoverOffer& offer) {
  const std::string msg = offer_message_text(offer) + "\n\nProceed?";
#if defined(ZNETWORK_LINUX)
  return confirm_linux(offer.title, msg);
#elif defined(ZNETWORK_DARWIN)
  return confirm_darwin(offer.title, msg);
#elif defined(ZNETWORK_WIN)
  return confirm_win(offer.title, msg);
#else
  (void)offer;
  return std::nullopt;
#endif
}

}  // namespace znet