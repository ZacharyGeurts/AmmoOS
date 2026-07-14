// SPDX-License-Identifier: MIT
// amouranthrtx / field-amouranthrtx — native launcher (C++). No linux.sh product path.
#include "spear_common.hpp"
#include "spear_field_surface.hpp"

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <unistd.h>
#include <sys/stat.h>

static bool is_exe(const std::string& p) {
  struct stat st {};
  return ::stat(p.c_str(), &st) == 0 && (st.st_mode & S_IXUSR) && S_ISREG(st.st_mode);
}

static std::string find_engine() {
  const char* home = std::getenv("HOME");
  std::string h = home ? home : "";
  const char* cands[] = {
      "Navigator/build/AMOURANTHRTX",
      "Navigator/build/amouranthrtx",
      "build/AMOURANTHRTX",
      "build/linux/AMOURANTHRTX",
      "out/AMOURANTHRTX",
      nullptr,
  };
  const char* roots[] = {
      "/usr/local/bin/amouranthrtx",
      nullptr,
  };
  if (is_exe("/usr/local/bin/amouranthrtx")) return "/usr/local/bin/amouranthrtx";
  if (is_exe(h + "/.local/bin/amouranthrtx-engine")) return h + "/.local/bin/amouranthrtx-engine";

  std::string trees[] = {
      h + "/Desktop/SG/NewLatest/AMOURANTHRTX",
      h + "/Desktop/SG/AMOURANTHRTX",
      h + "/Desktop/AMOURANTHRTX",
      "/usr/local/share/amouranthrtx",
  };
  for (const auto& root : trees) {
    for (int i = 0; cands[i]; ++i) {
      std::string p = root + "/" + cands[i];
      if (is_exe(p)) return p;
    }
  }
  return {};
}

int main(int argc, char** argv) {
  if (argc >= 2 && (std::strcmp(argv[1], "--version") == 0 || std::strcmp(argv[1], "-V") == 0)) {
    std::puts(
        "amouranthrtx / AmmoOS 1.0.0 · AMOURANTHRTX SDL3 field desktop · Vulkan-carried · "
        "no 127-only · no scripts");
    return 0;
  }
  if (argc >= 2 && (std::strcmp(argv[1], "--plate") == 0 || std::strcmp(argv[1], "status") == 0)) {
    auto spec = spear::field_surface::adapt(3840, 2160, 1.f, 0);
    std::string p = spear::field_surface::plate(spec);
    spear::mirror_www("amouranthrtx-surface.plate", p);
    std::fputs(p.c_str(), stdout);
    return 0;
  }
  // refuse scripts
  for (int i = 1; i < argc; ++i) {
    if (spear::contains(std::string(argv[i]), ".sh") || spear::contains(std::string(argv[i]), ".py")) {
      std::fputs("amouranthrtx: REFUSED script argument\n", stderr);
      return 2;
    }
  }
  std::string eng = find_engine();
  if (eng.empty()) {
    std::fputs(
        "amouranthrtx: engine binary not built yet — surface plate only\n"
        "  build Navigator (SDL3+Vulkan) then re-run\n"
        "  or: amouranthrtx --plate\n",
        stderr);
    auto spec = spear::field_surface::adapt(3840, 2160, 1.f, 0);
    std::fputs(spear::field_surface::plate(spec).c_str(), stdout);
    return 1;
  }
  std::vector<char*> av;
  av.push_back(const_cast<char*>(eng.c_str()));
  for (int i = 1; i < argc; ++i) av.push_back(argv[i]);
  av.push_back(nullptr);
  ::execv(eng.c_str(), av.data());
  std::perror("amouranthrtx exec");
  return 127;
}
