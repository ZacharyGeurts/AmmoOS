// SPDX-License-Identifier: MIT
// field-files — Native field file listing (C++). No foreign FM chrome.
#include "spear_common.hpp"

#include <cstdio>
#include <cstring>
#include <dirent.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string>
#include <vector>
#include <algorithm>

int main(int argc, char** argv) {
  if (argc >= 2 && std::strcmp(argv[1], "--version") == 0) {
    std::puts("field-files 1.0.0 native C++");
    return 0;
  }
  bool plate = false;
  const char* path = ".";
  for (int i = 1; i < argc; ++i) {
    if (std::strcmp(argv[i], "--plate") == 0) plate = true;
    else if (argv[i][0] != '-') path = argv[i];
  }
  DIR* d = ::opendir(path);
  if (!d) {
    std::perror("field-files");
    return 1;
  }
  std::vector<std::string> names;
  while (dirent* e = ::readdir(d)) {
    if (std::strcmp(e->d_name, ".") == 0 || std::strcmp(e->d_name, "..") == 0) continue;
    names.push_back(e->d_name);
  }
  ::closedir(d);
  std::sort(names.begin(), names.end());

  if (plate) {
    std::string o = "SPEARPLATE/1\nschema=field-files/v1\nengine=C++\nscripts=FORBIDDEN\npath=";
    o += path;
    o += "\n";
    for (const auto& n : names) {
      o += "entry=";
      o += n;
      o += "\n";
    }
    o += "END\n";
    spear::mirror_www("field-files-last.plate", o);
    std::fputs(o.c_str(), stdout);
    return 0;
  }
  for (const auto& n : names) {
    std::string full = std::string(path) + "/" + n;
    struct stat st {};
    char mark = ' ';
    if (::stat(full.c_str(), &st) == 0) {
      if (S_ISDIR(st.st_mode)) mark = '/';
      else if (st.st_mode & S_IXUSR) mark = '*';
    }
    std::printf("%s%c\n", n.c_str(), mark);
  }
  return 0;
}
