// SPDX-License-Identifier: MIT
// Field surface plane — AMOURANTHRTX · SDL3 · own Vulkan · adaptive 4K.
// C++ or lower. No scripts. No themes. Rotation + mobile/ARM + desktop.
// Networking: SDL3 sockets / field net path (with legacy fallbacks).
// Sub-micron class: field die / CHIPs fidelity, not a vendor SDK claim.
#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <string>

namespace spear {
namespace field_surface {

// ── Identity ──────────────────────────────────────────────────────────────
inline constexpr const char* kProduct = "AMOURANTHRTX Field Surface";
inline constexpr const char* kEngine = "C++ or lower";
inline constexpr const char* kAudio = "SDL3";
inline constexpr const char* kVideo = "SDL3 + Vulkan (carried)";
inline constexpr const char* kNet = "SDL3 net + Internet 2.0 C++ servers";
inline constexpr const char* kRefRes = "3840x2160";  // 4K field default (v2.01 / RTD)
inline constexpr int kRefW = 3840;
inline constexpr int kRefH = 2160;
inline constexpr int kAudioHz = 48000;
inline constexpr int kAudioCh = 2;
inline constexpr float kMinUiScale = 0.75f;
inline constexpr float kUiBoost = 1.35f;

// Orientation (SDL display / mobile rotation)
enum class Orient : std::uint8_t {
  Landscape = 0,  // natural 4K
  Portrait = 1,   // phone / rotate 90
  LandscapeFlipped = 2,
  PortraitFlipped = 3,
  Unknown = 255,
};

struct SurfaceSpec {
  int pixel_w = kRefW;
  int pixel_h = kRefH;
  int logical_w = kRefW;
  int logical_h = kRefH;
  float ui_scale = 1.35f;   // aosUiScale lineage
  float dpi_scale = 1.f;
  Orient orient = Orient::Landscape;
  bool rotated = false;
  bool is_mobile_class = false;  // phone/tablet-like short edge
  bool is_arm = false;
  bool vulkan_ok = true;         // carried stack; llvmpipe allowed
  bool sdl3_audio = true;
  bool sdl3_net = true;
  const char* vulkan_path = "FieldDie/Vulkan-carried";  // not host-only casual
  const char* backend = "SDL3";
};

// Detect crude arch at compile time
inline constexpr bool compile_is_arm() {
#if defined(__aarch64__) || defined(__arm__) || defined(_M_ARM64) || defined(_M_ARM)
  return true;
#else
  return false;
#endif
}

// Sub-micron class scale factor — denser UI chrome on high-DPI / field die path
inline float submicron_density(float dpi_scale, bool field_die) {
  float d = std::max(1.f, dpi_scale);
  if (field_die) d *= 1.08f;  // slightly denser when CHIPs/field die hot
  // clamp — never cartoon scale
  if (d < 1.f) d = 1.f;
  if (d > 3.f) d = 3.f;
  return d;
}

// Adaptive viewport from raw display mode (SDL_GetCurrentDisplayMode numbers)
inline SurfaceSpec adapt(int display_w, int display_h, float dpi_scale = 1.f,
                         int orientation_hint = 0 /* 0=land 1=port 2=landflip 3=portflip */) {
  SurfaceSpec s;
  s.is_arm = compile_is_arm();
  s.dpi_scale = dpi_scale > 0.f ? dpi_scale : 1.f;
  if (display_w <= 0) display_w = kRefW;
  if (display_h <= 0) display_h = kRefH;

  // Normalize orientation
  switch (orientation_hint) {
    case 1:
      s.orient = Orient::Portrait;
      s.rotated = true;
      break;
    case 2:
      s.orient = Orient::LandscapeFlipped;
      s.rotated = true;
      break;
    case 3:
      s.orient = Orient::PortraitFlipped;
      s.rotated = true;
      break;
    default:
      s.orient = Orient::Landscape;
      s.rotated = false;
      break;
  }
  // Auto portrait if tall
  if (display_h > display_w && s.orient == Orient::Landscape) {
    s.orient = Orient::Portrait;
    s.rotated = true;
  }

  s.pixel_w = display_w;
  s.pixel_h = display_h;
  const int short_e = std::min(display_w, display_h);
  const int long_e = std::max(display_w, display_h);
  s.is_mobile_class = short_e <= 1200 || (s.is_arm && short_e <= 1600);

  // Logical canvas stays 4K-class in landscape; swap for portrait logical
  if (s.orient == Orient::Portrait || s.orient == Orient::PortraitFlipped) {
    s.logical_w = kRefH;  // 2160
    s.logical_h = kRefW;  // 3840
  } else {
    s.logical_w = kRefW;
    s.logical_h = kRefH;
  }

  // UI scale from AMOURANTHRTX aosUiScale lineage: max(w/3840, 0.75) * 1.35
  const float ref = static_cast<float>(s.logical_w);
  const float w = static_cast<float>(long_e);
  float scale = std::max(w / ref, kMinUiScale) * kUiBoost;
  scale *= submicron_density(s.dpi_scale, /*field_die=*/true);
  if (s.is_mobile_class) scale = std::max(scale, 1.1f);  // readable on phone
  if (scale > 4.f) scale = 4.f;
  s.ui_scale = scale;

  s.vulkan_ok = true;  // we carry stack; runtime may set false if no device
  s.sdl3_audio = true;
  s.sdl3_net = true;
  s.backend = "SDL3";
  s.vulkan_path = "FieldDie/Vulkan-carried";
  return s;
}

// Field plate export (no JSON authority)
inline std::string plate(const SurfaceSpec& s) {
  auto o = std::string("SPEARPLATE/1\n");
  o += "schema=amouranthrtx-field-surface/v1\n";
  o += "product=";
  o += kProduct;
  o += "\nammoos=AMOURANTHRTX/AmmoOS (SDL3 shell · start menu · taskbar)\n";
  o += "engine=";
  o += kEngine;
  o += "\naudio=";
  o += kAudio;
  o += "\nvideo=";
  o += kVideo;
  o += "\nnet=";
  o += kNet;
  o += "\nbind=0.0.0.0 (field — not 127-only)\n";
  o += "scripts=FORBIDDEN\njson_authority=EATEN\nthemes=NOT_YET\n";
  char b[128];
  std::snprintf(b, sizeof b, "pixel=%dx%d\n", s.pixel_w, s.pixel_h);
  o += b;
  std::snprintf(b, sizeof b, "logical=%dx%d\n", s.logical_w, s.logical_h);
  o += b;
  std::snprintf(b, sizeof b, "ui_scale=%.4f\n", s.ui_scale);
  o += b;
  std::snprintf(b, sizeof b, "dpi_scale=%.4f\n", s.dpi_scale);
  o += b;
  o += "orient=";
  switch (s.orient) {
    case Orient::Portrait:
      o += "portrait\n";
      break;
    case Orient::LandscapeFlipped:
      o += "landscape_flipped\n";
      break;
    case Orient::PortraitFlipped:
      o += "portrait_flipped\n";
      break;
    default:
      o += "landscape\n";
      break;
  }
  o += "rotated=";
  o += s.rotated ? "true\n" : "false\n";
  o += "mobile_class=";
  o += s.is_mobile_class ? "true\n" : "false\n";
  o += "arm=";
  o += s.is_arm ? "true\n" : "false\n";
  o += "vulkan=";
  o += s.vulkan_path;
  o += "\nvulkan_ok=";
  o += s.vulkan_ok ? "true\n" : "false\n";
  o += "sdl3_audio=";
  o += s.sdl3_audio ? "true\n" : "false\n";
  o += "sdl3_net=";
  o += s.sdl3_net ? "true\n" : "false\n";
  o += "ref_4k=";
  o += kRefRes;
  o += "\nsub_micron=FieldDie/CHIPs\n";
  o += "iso_role=full_system_field_face\n";
  o += "END\n";
  return o;
}

// ISO bring-list — ONLY what we use (no theme packs, no foreign browsers)
struct BringItem {
  const char* id;
  const char* path_or_bin;
  const char* why;
};

inline constexpr BringItem kIsoBring[] = {
    {"spear", "spear", "Field BSP · FFAT · CHIPs · elevate"},
    {"spear-wartime", "spear-wartime", "Always war hunt"},
    {"spear-www", "spear-www", "Internet 2.0 field panels"},
    {"spear-i2-server", "spear-i2-server", "Internet 2.0 LAW :9477"},
    {"spear-h7-panel", "spear-h7-panel", "Hostess 7 command UI"},
    {"spear-angel-seal", "spear-angel-seal", "Angel Plate+Meld seal"},
    {"spear-planet", "spear-planet", "Planet live"},
    {"spear-fleet-link", "spear-fleet-link", "Fleet mesh"},
    {"spear-hard-dispose", "spear-hard-dispose", "Hard hunt dispose"},
    {"queen", "queen", "Field net surface (product Queen only)"},
    {"amouranthrtx", "AMOURANTHRTX/Navigator", "SDL3+Vulkan field face 4K adaptive"},
    {"sdl3", "libSDL3 (carried)", "Audio · window · input · net"},
    {"vulkan_carried", "FieldDie/Vulkan", "Own Vulkan needs — Mesa/NVK/RADV/ANV/llvmpipe"},
    {"chips", "FieldDie/CHIPs", "EntropyFold·WavePhase·PeakScan·PackPick"},
    {"field_law", "field-law", "Internet 2.0 local court"},
    {"icons_core", "icons/field-core/", "New icons — only used apps"},
    {"field-calc", "field-calc", "Native calculator — no LibreOffice"},
    {"field-obs", "field-obs", "Native capture — not stock OBS chrome"},
    {"field-menu", "field-menu", "Native start menu — C++ only"},
    {"field-terminal", "field-terminal", "Native terminal entry"},
    {"field-files", "field-files", "Native file listing"},
    {"field-audio", "field-audio", "SDL3 audio plate"},
};
inline constexpr std::size_t kIsoBringN = sizeof(kIsoBring) / sizeof(kIsoBring[0]);

// Explicitly NOT brought (yet / never)
inline constexpr const char* kIsoNotYet[] = {
    "theme packs",
    "foreign browser product surface",
    "python panel / threat-panel-http",
    "JSON authority plates",
    "combinatorics plate-meld storm",
    "demo war fakes",
};
inline constexpr std::size_t kIsoNotYetN = sizeof(kIsoNotYet) / sizeof(kIsoNotYet[0]);

inline std::string iso_bring_plate() {
  std::string o = "SPEARPLATE/1\nschema=iso-bring-list/v1\n";
  o += "rule=ONLY_WHAT_WE_USE\n";
  o += "themes=NOT_YET\n";
  o += "engine=C++ or lower\n";
  o += "scripts=FORBIDDEN\n";
  o += "json_authority=EATEN\n";
  o += "surface=AMOURANTHRTX+SDL3+Vulkan-carried+4K-adaptive\n";
  o += "audio=SDL3\n";
  o += "net=SDL3+Internet2.0\n";
  for (std::size_t i = 0; i < kIsoBringN; ++i) {
    o += "bring.";
    o += kIsoBring[i].id;
    o += "=";
    o += kIsoBring[i].path_or_bin;
    o += " # ";
    o += kIsoBring[i].why;
    o += "\n";
  }
  for (std::size_t i = 0; i < kIsoNotYetN; ++i) {
    o += "not.";
    o += std::to_string(i);
    o += "=";
    o += kIsoNotYet[i];
    o += "\n";
  }
  o += "END\n";
  return o;
}

// Core icon IDs we ship (new set — no theme pack)
inline constexpr const char* kCoreIcons[] = {
    "field-hostess7",     // Hostess 7 war command
    "field-internet-2",   // Internet 2.0 LAW
    "field-amouranthrtx", // AMOURANTHRTX field face
    "field-chips",        // CHIPs / Field Die
    "field-spear",        // Spear war
    "field-queen",        // Queen surface
    "field-terminal",     // Field terminal
    "field-audio",        // SDL3 audio
};
inline constexpr std::size_t kCoreIconsN = sizeof(kCoreIcons) / sizeof(kCoreIcons[0]);

}  // namespace field_surface
}  // namespace spear
