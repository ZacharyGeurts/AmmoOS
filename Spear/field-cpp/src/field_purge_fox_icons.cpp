// field-purge-fox-icons — C++ only. Deletes Firefox/Mozilla icon files from the system.
// Requires euid 0 for /usr. User-level paths always cleaned.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <dirent.h>
#include <ftw.h>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

static int removed = 0;
static int failed = 0;

static bool name_is_fox(const char* name) {
  if (!name) return false;
  // case-insensitive contains firefox or mozilla-firefox
  std::string s(name);
  for (char& c : s) if (c >= 'A' && c <= 'Z') c = char(c - 'A' + 'a');
  return s.find("firefox") != std::string::npos || s.find("mozilla-firefox") != std::string::npos;
}

static int wipe_cb(const char* fpath, const struct stat* sb, int typeflag, struct FTW*) {
  if (typeflag != FTW_F && typeflag != FTW_SL) return 0;
  const char* base = strrchr(fpath, '/');
  base = base ? base + 1 : fpath;
  if (!name_is_fox(base)) return 0;
  // only icon-like suffixes
  const char* dot = strrchr(base, '.');
  if (dot) {
    std::string ext(dot);
    for (char& c : ext) if (c >= 'A' && c <= 'Z') c = char(c - 'A' + 'a');
    if (!(ext == ".png" || ext == ".svg" || ext == ".xpm" || ext == ".ico" ||
          ext == ".svgz" || ext == ".jpg" || ext == ".jpeg"))
      return 0;
  }
  if (::unlink(fpath) == 0) {
    std::printf("removed %s\n", fpath);
    ++removed;
  } else {
    std::printf("FAIL %s\n", fpath);
    ++failed;
  }
  (void)sb;
  return 0;
}

static void walk(const char* root) {
  struct stat st {};
  if (stat(root, &st) != 0) return;
  nftw(root, wipe_cb, 64, FTW_PHYS);
}

int main() {
  const uid_t e = geteuid();
  std::printf("field-purge-fox-icons euid=%d\n", (int)e);

  const char* home = getenv("HOME");
  if (home && *home) {
    std::string h(home);
    walk((h + "/.local/share/icons").c_str());
    walk((h + "/.local/share/pixmaps").c_str());
    walk((h + "/.icons").c_str());
  }

  // System trees — only when elevated
  if (e == 0) {
    walk("/usr/share/icons");
    walk("/usr/share/pixmaps");
    walk("/usr/lib/firefox/browser/chrome/icons");
    walk("/usr/lib/firefox/icons");
    walk("/usr/share/applications"); // only if icon files wrongly placed
    // refresh system hicolor cache
    system("gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null");
    system("gtk-update-icon-cache -f -t /usr/share/icons/Mint-Y 2>/dev/null");
    system("gtk-update-icon-cache -f -t /usr/share/icons/Mint-X 2>/dev/null");
  } else {
    std::printf("note: not euid0 — system /usr icons still present; user overrides applied separately\n");
  }

  if (home && *home) {
    std::string cmd = std::string("gtk-update-icon-cache -f -t ") + home + "/.local/share/icons/hicolor 2>/dev/null";
    system(cmd.c_str());
  }

  std::printf("DONE removed=%d failed=%d\n", removed, failed);
  return failed ? 1 : 0;
}
