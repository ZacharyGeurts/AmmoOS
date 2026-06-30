#pragma once

#include <optional>
#include <string>
#include <vector>

namespace znet {

std::string detect_os();
std::string detect_arch();

/** Run command, capture stdout; empty if missing/fail. */
std::optional<std::string> run_capture(const std::string& cmd);

std::vector<std::string> split_lines(std::string_view text);
std::string trim(std::string_view s);
bool file_exists(const std::string& path);

}  // namespace znet