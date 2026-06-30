#include "znetwork/platform.hpp"

#include <array>
#include <cstdio>
#include <memory>
#include <sstream>

#if defined(__linux__)
#include <sys/utsname.h>
#endif

namespace znet {

std::string detect_os() {
#if defined(ZNETWORK_LINUX)
  return "linux";
#elif defined(ZNETWORK_WIN)
  return "windows";
#elif defined(ZNETWORK_DARWIN)
  return "darwin";
#else
  return "unknown";
#endif
}

std::string detect_arch() {
#if defined(__x86_64__) || defined(_M_X64)
  return "x86_64";
#elif defined(__aarch64__) || defined(_M_ARM64)
  return "aarch64";
#else
  return "unknown";
#endif
}

std::optional<std::string> run_capture(const std::string& cmd) {
  std::array<char, 256> buf{};
  std::string out;
  std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(cmd.c_str(), "r"), pclose);
  if (!pipe) return std::nullopt;
  while (fgets(buf.data(), static_cast<int>(buf.size()), pipe.get())) {
    out += buf.data();
  }
  if (out.empty()) return std::nullopt;
  return out;
}

std::vector<std::string> split_lines(std::string_view text) {
  std::vector<std::string> lines;
  std::istringstream iss{std::string{text}};
  std::string line;
  while (std::getline(iss, line)) {
    if (!line.empty() && line.back() == '\r') line.pop_back();
    lines.push_back(line);
  }
  return lines;
}

std::string trim(std::string_view s) {
  auto b = s.find_first_not_of(" \t\r\n");
  if (b == std::string_view::npos) return {};
  auto e = s.find_last_not_of(" \t\r\n");
  return std::string{s.substr(b, e - b + 1)};
}

bool file_exists(const std::string& path) {
  FILE* f = fopen(path.c_str(), "r");
  if (!f) return false;
  fclose(f);
  return true;
}

}  // namespace znet