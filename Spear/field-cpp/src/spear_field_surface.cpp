// SPDX-License-Identifier: MIT
// spear-field-surface — AMOURANTHRTX adaptive 4K / rotation / SDL3 / Vulkan carried.
// C++ only. Prints field plate. No scripts. No themes.
#include "spear_common.hpp"
#include "spear_field_surface.hpp"

#include <cstdlib>
#include <cstring>
#include <cstdio>

static int env_int(const char* k, int def) {
  const char* v = std::getenv(k);
  if (!v || !*v) return def;
  return std::atoi(v);
}

int main(int argc, char** argv) {
  const char* cmd = (argc >= 2) ? argv[1] : "plate";
  if (std::strcmp(cmd, "-h") == 0 || std::strcmp(cmd, "--help") == 0) {
    std::fprintf(stderr,
                 "spear-field-surface — AMOURANTHRTX SDL3 field surface\n"
                 "  %s [plate|adapt|iso-bring|icons]\n"
                 "  env: FIELD_W FIELD_H FIELD_DPI FIELD_ORIENT (0-3)\n"
                 "  audio=SDL3 video=SDL3+Vulkan-carried net=SDL3+I2 themes=NOT_YET\n",
                 argv[0]);
    return 0;
  }

  if (std::strcmp(cmd, "iso-bring") == 0) {
    const std::string p = spear::field_surface::iso_bring_plate();
    spear::mirror_www("iso-bring-list.plate", p);
    std::fputs(p.c_str(), stdout);
    return 0;
  }

  if (std::strcmp(cmd, "icons") == 0) {
    std::string o = "SPEARPLATE/1\nschema=field-core-icons/v1\nthemes=NOT_YET\n";
    o += "path=/usr/local/share/spear/icons/field-core/\n";
    for (std::size_t i = 0; i < spear::field_surface::kCoreIconsN; ++i) {
      o += "icon.";
      o += spear::field_surface::kCoreIcons[i];
      o += "=png\n";
    }
    o += "END\n";
    spear::mirror_www("field-core-icons.plate", o);
    std::fputs(o.c_str(), stdout);
    return 0;
  }

  int w = env_int("FIELD_W", env_int("AMOURANTHRTX_BENCH_W", spear::field_surface::kRefW));
  int h = env_int("FIELD_H", env_int("AMOURANTHRTX_BENCH_H", spear::field_surface::kRefH));
  float dpi = 1.f;
  if (const char* d = std::getenv("FIELD_DPI")) dpi = static_cast<float>(std::atof(d));
  int orient = env_int("FIELD_ORIENT", 0);
  // CLI overrides: adapt W H [dpi] [orient]
  if (std::strcmp(cmd, "adapt") == 0 && argc >= 4) {
    w = std::atoi(argv[2]);
    h = std::atoi(argv[3]);
    if (argc >= 5) dpi = static_cast<float>(std::atof(argv[4]));
    if (argc >= 6) orient = std::atoi(argv[5]);
  }

  auto spec = spear::field_surface::adapt(w, h, dpi, orient);
  const std::string p = spear::field_surface::plate(spec);
  spear::mirror_www("field-surface.plate", p);
  spear::mirror_www("amouranthrtx-surface.plate", p);
  if (const char* home = std::getenv("HOME")) {
    spear::mkdir_p(std::string(home) + "/.local/share/spear");
    spear::write_file((std::string(home) + "/.local/share/spear/field-surface.plate").c_str(), p);
  }
  // also ISO overlay
  spear::mkdir_p(spear::home_dir() + "/Desktop/SG/Spear/overlay/usr/local/share/spear");
  spear::write_file(
      (spear::home_dir() + "/Desktop/SG/Spear/overlay/usr/local/share/spear/field-surface.plate").c_str(),
      p);
  spear::write_file(
      (spear::home_dir() + "/Desktop/SG/Spear/overlay/usr/local/share/spear/iso-bring-list.plate").c_str(),
      spear::field_surface::iso_bring_plate());

  std::fputs(p.c_str(), stdout);
  return 0;
}
