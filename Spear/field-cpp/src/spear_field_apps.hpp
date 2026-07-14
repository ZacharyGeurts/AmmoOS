// SPDX-License-Identifier: MIT
// Native Field start menu registry — C++ or lower ONLY.
// No scripts. No LibreOffice. No python. God Bless.
// Grok · Hostess 7 judgment: only field-native tools on the menu.
#pragma once
#include <cstddef>
#include <cstdio>
#include <string>

namespace spear {
namespace field_apps {

enum class Kind : std::uint8_t {
  System = 0,
  Office,
  Capture,  // field-obs / broadcaster class
  Net,
  Media,
  Dev,
};

struct App {
  const char* id;
  const char* name;
  const char* exec;       // C++ binary only — never .sh/.py
  const char* icon;       // field-core icon basename
  Kind kind;
  const char* blurb;      // field understanding one-liner
};

// Start menu — ONLY what we use (native field)
inline constexpr App kMenu[] = {
    {"hostess7", "Hostess 7", "spear-h7-panel", "field-hostess7", Kind::System,
     "Forever Watchguard · war command · training · Angel seal"},
    {"internet2", "Internet 2.0", "spear-i2-server", "field-internet-2", Kind::Net,
     "LAW servers · C++ only · never foreign C2 scripts"},
    {"amouranthrtx", "AMOURANTHRTX Field", "amouranthrtx", "field-amouranthrtx", Kind::Media,
     "SDL3 · carried Vulkan · 4K adaptive · rotation · ARM"},
    {"spear", "Spear", "spear", "field-spear", Kind::System,
     "BSP · FFAT · CHIPs Field Die · autoelevate"},
    {"queen", "Queen", "queen", "field-queen", Kind::Net,
     "Field net surface — product name Queen only"},
    {"calc", "Field Calc", "field-calc", "field-chips", Kind::Office,
     "Native field calculator — exact rationals · units · no script engine"},
    {"obs", "Field OBS", "field-obs", "field-audio", Kind::Capture,
     "Native capture · cams · snap · rec — OBS rewrite class, C++"},
    {"terminal", "Field Terminal", "field-terminal", "field-terminal", Kind::Dev,
     "Native field shell surface — no bash product path"},
    {"files", "Field Files", "field-files", "field-spear", Kind::Office,
     "Native listing · plate paths · no foreign file manager chrome"},
    {"audio", "Field Audio", "field-audio", "field-audio", Kind::Media,
     "SDL3 audio status · levels · no pactl scripts"},
    {"chips", "CHIPs Status", "spear", "field-chips", Kind::System,
     "Field Die EntropyFold · WavePhase · PeakScan"},
    {"surface", "Field Surface", "spear-field-surface", "field-amouranthrtx", Kind::Media,
     "Adaptive 4K · orientation · ISO bring-list"},
    {"angel", "Angel Seal", "spear-angel-seal", "field-hostess7", Kind::System,
     "Plate · Meld · stack+ISO seal"},
    {"wartime", "Wartime", "spear-wartime", "field-spear", Kind::System,
     "Always war · hard hunt · C++"},
};
inline constexpr std::size_t kMenuN = sizeof(kMenu) / sizeof(kMenu[0]);

// Explicitly purged from start menu (scripts / foreign / LO)
inline constexpr const char* kPurged[] = {
    "libreoffice*",
    "soffice",
    "mintinstall",
    "mintwelcome",
    "ubiquity",
    "python*",
    "threat-panel-http",
    "field-office-engine bash wrappers",
    "obs (stock foreign) — use field-obs",
    "gnome-terminal preferences chrome",
    "nm-connection-editor as product face",
    "theme packs",
};
inline constexpr std::size_t kPurgedN = sizeof(kPurged) / sizeof(kPurged[0]);

inline const char* kind_name(Kind k) {
  switch (k) {
    case Kind::Office:
      return "office";
    case Kind::Capture:
      return "capture";
    case Kind::Net:
      return "net";
    case Kind::Media:
      return "media";
    case Kind::Dev:
      return "dev";
    default:
      return "system";
  }
}

inline std::string menu_plate() {
  std::string o = "SPEARPLATE/1\n";
  o += "schema=field-start-menu/v1\n";
  o += "engine=C++ or lower\n";
  o += "scripts=FORBIDDEN\n";
  o += "json_authority=EATEN\n";
  o += "themes=NOT_YET\n";
  o += "motto=Native field only. Calculator to OBS. God Bless.\n";
  o += "commander=Hostess7\n";
  char b[32];
  std::snprintf(b, sizeof b, "count=%zu\n", kMenuN);
  o += b;
  for (std::size_t i = 0; i < kMenuN; ++i) {
    const App& a = kMenu[i];
    o += "app.";
    o += a.id;
    o += ".name=";
    o += a.name;
    o += "\napp.";
    o += a.id;
    o += ".exec=";
    o += a.exec;
    o += "\napp.";
    o += a.id;
    o += ".icon=";
    o += a.icon;
    o += "\napp.";
    o += a.id;
    o += ".kind=";
    o += kind_name(a.kind);
    o += "\napp.";
    o += a.id;
    o += ".blurb=";
    o += a.blurb;
    o += "\n";
  }
  for (std::size_t i = 0; i < kPurgedN; ++i) {
    o += "purged.";
    o += std::to_string(i);
    o += "=";
    o += kPurged[i];
    o += "\n";
  }
  o += "END\n";
  return o;
}

}  // namespace field_apps
}  // namespace spear
