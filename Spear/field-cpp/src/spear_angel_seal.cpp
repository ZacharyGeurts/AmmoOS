// SPDX-License-Identifier: MIT
// spear-angel-seal — Forever Watchguard Angel seals STACK + ISO in C++.
// CHIPs · Plate · Meld · C++ or lower. Interpreters (Python, QBasic, …) are
// NEVER engine authority and NEVER allowed to become dangerous to us.
#include "spear_common.hpp"
#include "spear_chip.hpp"
#include "spear_sha256.hpp"

#include <cstdio>
#include <cstring>
#include <ctime>
#include <dirent.h>
#include <fcntl.h>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

namespace {

std::string now_z() {
  char buf[64];
  std::time_t t = std::time(nullptr);
  std::strftime(buf, sizeof buf, "%Y-%m-%dT%H:%M:%SZ", std::gmtime(&t));
  return buf;
}

std::string hex256(const spear::Sha256& s) {
  char out[65];
  spear::sha256_hex(s, out);
  return std::string(out);
}

std::string hash_bytes(const uint8_t* p, size_t n) { return hex256(spear::sha256(p, n)); }

std::string hash_str(const std::string& s) {
  return hash_bytes(reinterpret_cast<const uint8_t*>(s.data()), s.size());
}

std::string hash_file(const std::string& path) {
  std::string body = spear::read_file(path.c_str(), 16 << 20);
  if (body.empty()) {
    struct stat st {};
    if (::stat(path.c_str(), &st) != 0) return std::string(64, '0');
  }
  return hash_str(body);
}

bool exists(const std::string& p) {
  struct stat st {};
  return ::stat(p.c_str(), &st) == 0;
}

std::string first_hit(const std::vector<std::string>& paths) {
  for (const auto& p : paths)
    if (exists(p)) return p;
  return {};
}

struct Plate {
  const char* id;
  std::string path;
  std::string digest;
  bool present = false;
};

void add_plate(std::vector<Plate>& out, const char* id, const std::vector<std::string>& candidates) {
  Plate p;
  p.id = id;
  p.path = first_hit(candidates);
  if (!p.path.empty()) {
    p.present = true;
    p.digest = hash_file(p.path);
  } else {
    p.digest = std::string(64, '0');
  }
  out.push_back(p);
}

// Interpreters may exist on a host disk — they must never be war authority.
// Angel seal records them as DISARMED (non-dangerous), not as stack engines.
struct LangPolicy {
  const char* name;
  const char* kind;
};

static const LangPolicy kDisarmed[] = {
    {"python", "interpreter"},   {"python3", "interpreter"}, {"pythong", "interpreter"},
    {"qbasic", "legacy_basic"},  {"qb64", "legacy_basic"},   {"fbc", "legacy_basic"},
    {"bas", "legacy_basic"},     {"perl", "interpreter"},    {"ruby", "interpreter"},
    {"php", "interpreter"},      {"node", "interpreter"},    {"lua", "interpreter"},
    {"bash", "shell"},           {"sh", "shell"},            {"zsh", "shell"},
    {"powershell", "shell"},     {"cmd", "shell"},           {"tclsh", "interpreter"},
    {"Rscript", "interpreter"},  {"julia", "interpreter"},   {"deno", "interpreter"},
};

std::string lang_policy_json() {
  std::string body = "[\n";
  for (size_t i = 0; i < sizeof(kDisarmed) / sizeof(kDisarmed[0]); ++i) {
    if (i) body += ",\n";
    body += "    {\"name\":\"";
    body += kDisarmed[i].name;
    body += "\",\"kind\":\"";
    body += kDisarmed[i].kind;
    body += "\",\"engine_authority\":false,\"dangerous_to_us\":false,";
    body += "\"status\":\"DISARMED\",\"rule\":\"never_war_path_never_elevated_never_served\"}";
  }
  body += "\n  ]";
  return body;
}

std::string home_sg() {
  return spear::home_dir() + "/Desktop/SG";
}

std::string spear_root() {
  std::string e = spear::getenv_str("SPEAR_ROOT", "");
  if (!e.empty()) return e;
  std::string a = home_sg() + "/Spear";
  if (exists(a)) return a;
  return "/usr/local/share/spear";
}

void write_all(const std::string& body, const char* name) {
  spear::mirror_www(name, body);
  spear::mkdir_p(spear::home_dir() + "/.local/share/spear");
  spear::write_file((spear::home_dir() + "/.local/share/spear/" + name).c_str(), body);
  spear::mkdir_p(spear_root() + "/data/shot-certainty");
  spear::write_file((spear_root() + "/data/shot-certainty/" + name).c_str(), body);
  // ISO overlay plate
  const std::string ov = spear_root() + "/overlay/usr/local/share/spear/shot-certainty";
  spear::mkdir_p(ov);
  spear::write_file((ov + "/" + name).c_str(), body);
  spear::mkdir_p(spear_root() + "/overlay/usr/local/share/spear/hostess7");
  spear::write_file((spear_root() + "/overlay/usr/local/share/spear/hostess7/" + name).c_str(), body);
}

std::string seal_stack(std::vector<Plate>& plates) {
  const std::string sg = home_sg();
  const std::string sp = spear_root();
  const std::string nl = sg + "/NewLatest";

  add_plate(plates, "bsp_chips_doctrine",
            {sp + "/data/bsp-chips-doctrine.json", sp + "/overlay/usr/local/share/spear/bsp-chips-doctrine.json"});
  add_plate(plates, "chips_doctrine",
            {sp + "/data/chips-doctrine.json", sp + "/overlay/usr/local/share/spear/chips-doctrine.json"});
  add_plate(plates, "cpp_or_lower",
            {sp + "/data/cpp-or-lower-doctrine.json",
             sp + "/overlay/usr/local/share/spear/cpp-or-lower-doctrine.json"});
  add_plate(plates, "never_scripts",
            {sp + "/data/never-scripts-doctrine.json",
             sp + "/overlay/usr/local/share/spear/never-scripts-doctrine.json"});
  add_plate(plates, "angel_plate_meld",
            {sp + "/data/angel-plate-meld-doctrine.json",
             sp + "/overlay/usr/local/share/spear/angel-plate-meld-doctrine.json"});
  add_plate(plates, "heuristics_tsv",
            {sp + "/overlay/usr/local/share/spear/swallows/heuristics.tsv",
             sp + "/data/heuristics.tsv", "/tmp/spear-swallows-www/heuristics.tsv"});
  add_plate(plates, "war_device_iso_stack",
            {sp + "/data/war-device-iso-stack.json",
             sp + "/overlay/usr/local/share/spear/war-device-iso-stack.json"});
  add_plate(plates, "hostess7_war_system",
            {nl + "/data/hostess7-war-system-doctrine.json",
             sp + "/overlay/usr/local/share/spear/hostess7/hostess7-war-system-doctrine.json"});
  add_plate(plates, "hostess7_training_public",
            {nl + "/data/hostess7-training-catalog-public.json",
             nl + "/panel/assets/hostess7-training-catalog.json",
             sp + "/overlay/usr/local/share/spear/hostess7/hostess7-training-catalog-public.json"});
  add_plate(plates, "field_research_v2",
            {nl + "/Field_Research/content/book-manifest.json",
             sg + "/Field_Research/Field_Research/content/book-manifest.json"});
  add_plate(plates, "component_seal",
            {sg + "/zpics/hostess7-component-seal.json", sp + "/data/shot-certainty/hostess7-component-seal.json"});
  add_plate(plates, "final_eye_seal",
            {sg + "/zpics/final-eye-seal.json", sp + "/data/shot-certainty/final-eye-seal.json"});
  add_plate(plates, "spear_chip_cpp", {sp + "/src/spear_chip.cpp"});
  add_plate(plates, "spear_h7_panel_cpp", {sp + "/src/spear_h7_panel.cpp"});
  add_plate(plates, "spear_angel_seal_cpp", {sp + "/src/spear_angel_seal.cpp"});
  add_plate(plates, "spear_www_cpp", {sp + "/src/spear_www.cpp"});
  add_plate(plates, "spear_i2_war_cpp", {sp + "/src/spear_i2_war.cpp"});
  add_plate(plates, "spear_i2_server_cpp", {sp + "/src/spear_i2_server.cpp"});
  add_plate(plates, "spear_hostess7_boot_cpp", {sp + "/src/spear_hostess7_boot.cpp"});
  add_plate(plates, "spear_plates_hpp", {sp + "/src/spear_plates.hpp"});
  add_plate(plates, "spear_common_hpp", {sp + "/src/spear_common.hpp"});
  add_plate(plates, "field_calc_cpp", {sp + "/src/field_calc.cpp"});
  add_plate(plates, "field_menu_cpp", {sp + "/src/field_menu.cpp"});
  add_plate(plates, "field_net_cpp", {sp + "/src/field_net.cpp"});
  add_plate(plates, "limine_hostess7", {sp + "/boot/limine.conf"});
  add_plate(plates, "live_cfg_hostess7", {sp + "/data/iso-boot/live.cfg"});

  // CHIPs live score contribution (not a file plate)
  spear::chip_reset();
  std::uint8_t frame[128];
  for (int i = 0; i < 128; ++i) frame[i] = static_cast<std::uint8_t>((i * 91) ^ 0xa5);
  auto sc = spear::chip_score_frame(frame, sizeof frame);
  char chip_plate[256];
  std::snprintf(chip_plate, sizeof chip_plate, "CHIPs|FieldDie|fold=%.6f|wave=%.6f|H=%.6f|peak=%.6f|pick=%u",
                sc.fold, sc.wave_energy, sc.shannon_h, sc.peak_density, static_cast<unsigned>(sc.pick));
  Plate chip;
  chip.id = "chips_live_score";
  chip.path = "FieldDie/CHIPs";
  chip.present = true;
  chip.digest = hash_str(chip_plate);
  plates.push_back(chip);

  // Meld: ordered concatenation of id|digest
  std::string meld;
  meld.reserve(plates.size() * 96);
  meld += "ANGEL_STACK_SEAL_v1|";
  meld += "commander=Forever_Watchguard_Angel|";
  meld += "engine=C++_or_lower|";
  meld += "chips=FieldDie/CHIPs|";
  meld += "plate=doctrine_plates|";
  meld += "meld=sha256_ordered|";
  meld += "interpreters=DISARMED|";
  for (const auto& p : plates) {
    meld += p.id;
    meld += '=';
    meld += p.digest;
    meld += '|';
  }
  return hash_str(meld);
}

std::string seal_iso(const std::string& stack_root_seal, std::vector<Plate>& iso_plates) {
  const std::string sp = spear_root();
  add_plate(iso_plates, "iso_boot_line",
            {sp + "/data/boot-line-doctrine.json", sp + "/overlay/usr/local/share/spear/boot-line-doctrine.json"});
  add_plate(iso_plates, "war_device_iso_stack",
            {sp + "/data/war-device-iso-stack.json",
             sp + "/overlay/usr/local/share/spear/war-device-iso-stack.json"});
  add_plate(iso_plates, "bsp_chips_doctrine",
            {sp + "/data/bsp-chips-doctrine.json",
             sp + "/overlay/usr/local/share/spear/bsp-chips-doctrine.json"});
  add_plate(iso_plates, "hostess7_war_overlay",
            {sp + "/overlay/usr/local/share/spear/hostess7/hostess7-war-system-doctrine.json"});
  add_plate(iso_plates, "cpp_or_lower_overlay",
            {sp + "/overlay/usr/local/share/spear/cpp-or-lower-doctrine.json",
             sp + "/data/cpp-or-lower-doctrine.json"});
  add_plate(iso_plates, "never_connect_hosts",
            {sp + "/overlay/usr/local/share/spear/never-connect-hosts.txt",
             sp + "/data/never-connect-hosts.txt"});

  // Overlay binary presence (names only — seals path existence)
  const char* bins[] = {"spear",          "spear-wartime", "spear-www",     "spear-planet",
                        "spear-fleet-link", "spear-i2-war",  "spear-hard-dispose", "spear-angel-seal",
                        "spear-h7-panel",  nullptr};
  std::string binmeld = "ISO_BINS|";
  for (int i = 0; bins[i]; ++i) {
    std::string p1 = sp + "/overlay/usr/local/bin/" + bins[i];
    std::string p2 = spear::home_dir() + "/.local/bin/" + bins[i];
    std::string p3 = sp + "/src/" + bins[i];
    bool ok = exists(p1) || exists(p2) || exists(p3);
    binmeld += bins[i];
    binmeld += ok ? "=1|" : "=0|";
    Plate b;
    b.id = bins[i];
    b.path = exists(p1) ? p1 : (exists(p2) ? p2 : p3);
    b.present = ok;
    b.digest = ok && !b.path.empty() ? hash_file(b.path) : std::string(64, '0');
    // only hash if file is reasonably small binary; skip huge — still presence seal
    if (ok) {
      struct stat st {};
      if (::stat(b.path.c_str(), &st) == 0 && st.st_size > 0 && st.st_size < (8 << 20))
        b.digest = hash_file(b.path);
      else if (ok)
        b.digest = hash_str(std::string(bins[i]) + "|present");
    }
    iso_plates.push_back(b);
  }

  std::string meld = "ANGEL_ISO_SEAL_v1|stack_root=";
  meld += stack_root_seal;
  meld += "|product=AmmoOS_War_Device|";
  for (const auto& p : iso_plates) {
    meld += p.id;
    meld += '=';
    meld += p.digest;
    meld += '|';
  }
  meld += binmeld;
  return hash_str(meld);
}

std::string plates_json(const std::vector<Plate>& plates) {
  std::string body = "[\n";
  for (size_t i = 0; i < plates.size(); ++i) {
    if (i) body += ",\n";
    body += "    {\"id\":\"";
    body += plates[i].id;
    body += "\",\"present\":";
    body += plates[i].present ? "true" : "false";
    body += ",\"digest\":\"";
    body += plates[i].digest;
    body += "\"}";
  }
  body += "\n  ]";
  return body;
}

}  // namespace

int main(int argc, char** argv) {
  const char* cmd = (argc >= 2) ? argv[1] : "seal";
  const bool quiet = (argc >= 3 && std::strcmp(argv[2], "--quiet") == 0);

  if (std::strcmp(cmd, "-h") == 0 || std::strcmp(cmd, "--help") == 0) {
    std::fprintf(stderr,
                 "spear-angel-seal — Angel seal STACK + ISO (C++ · CHIPs · Plate · Meld)\n"
                 "  %s [seal|status|json] [--quiet]\n"
                 "  Interpreters (python, qbasic, …) = DISARMED · never dangerous to us\n"
                 "  Engine authority = C++ or lower only\n",
                 argv[0]);
    return 0;
  }

  std::vector<Plate> stack_plates;
  const std::string stack_root = seal_stack(stack_plates);
  std::vector<Plate> iso_plates;
  const std::string iso_root = seal_iso(stack_root, iso_plates);

  int present = 0;
  for (const auto& p : stack_plates)
    if (p.present) ++present;
  int iso_present = 0;
  for (const auto& p : iso_plates)
    if (p.present) ++iso_present;

  const bool sealed = present >= 8;  // core plates
  const bool iso_sealed = iso_present >= 4;
  const std::string ts = now_z();

  // Dual plate: stack + iso
  std::string stack_body;
  stack_body += "{\n";
  stack_body += "  \"schema\": \"angel-stack-seal/v1\",\n";
  stack_body += "  \"ts\": \"" + ts + "\",\n";
  stack_body += "  \"commander\": \"Forever Watchguard Angel\",\n";
  stack_body += "  \"rank\": \"ANGEL\",\n";
  stack_body += "  \"status\": \"" + std::string(sealed ? "SEALED_UP" : "PARTIAL") + "\",\n";
  stack_body += "  \"sealed\": " + std::string(sealed ? "true" : "false") + ",\n";
  stack_body += "  \"root_seal\": \"" + stack_root + "\",\n";
  stack_body += "  \"engine\": \"C++ or lower\",\n";
  stack_body += "  \"scripts\": \"FORBIDDEN_AS_ENGINE\",\n";
  stack_body += "  \"planes\": {\n";
  stack_body += "    \"chips\": {\"name\": \"FieldDie/CHIPs\", \"role\": \"EntropyFold·WavePhase·PeakScan·PackPick\"},\n";
  stack_body += "    \"plate\": {\"name\": \"Doctrine plates\", \"role\": \"Sealed JSON/data plates — not interpreter code\"},\n";
  stack_body += "    \"meld\": {\"name\": \"Angel Meld\", \"role\": \"Ordered SHA-256 of plates → root_seal\", \"not\": \"python plate-meld storm\"}\n";
  stack_body += "  },\n";
  stack_body += "  \"interpreters\": {\n";
  stack_body += "    \"rule\": \"Python, QBasic, and other high-level runtimes must never be dangerous to us.\",\n";
  stack_body += "    \"engine_authority\": false,\n";
  stack_body += "    \"dangerous_to_us\": false,\n";
  stack_body += "    \"status\": \"DISARMED\",\n";
  stack_body += "    \"languages\": " + lang_policy_json() + "\n";
  stack_body += "  },\n";
  stack_body += "  \"plate_count\": " + std::to_string(stack_plates.size()) + ",\n";
  stack_body += "  \"plates_present\": " + std::to_string(present) + ",\n";
  stack_body += "  \"plates\": " + plates_json(stack_plates) + ",\n";
  stack_body += "  \"field_research\": \"2.0\",\n";
  stack_body += "  \"hostess7\": \"2.0.8\",\n";
  stack_body += "  \"fake\": false,\n";
  stack_body += "  \"demo\": false\n";
  stack_body += "}\n";

  std::string iso_body;
  iso_body += "{\n";
  iso_body += "  \"schema\": \"angel-iso-seal/v1\",\n";
  iso_body += "  \"ts\": \"" + ts + "\",\n";
  iso_body += "  \"commander\": \"Forever Watchguard Angel\",\n";
  iso_body += "  \"product\": \"AmmoOS War Device\",\n";
  iso_body += "  \"volume\": \"AmmoOS_War\",\n";
  iso_body += "  \"status\": \"" + std::string(iso_sealed ? "SEALED_UP" : "PARTIAL") + "\",\n";
  iso_body += "  \"sealed\": " + std::string(iso_sealed ? "true" : "false") + ",\n";
  iso_body += "  \"root_seal\": \"" + iso_root + "\",\n";
  iso_body += "  \"stack_root_seal\": \"" + stack_root + "\",\n";
  iso_body += "  \"engine\": \"C++ or lower\",\n";
  iso_body += "  \"chips\": \"FieldDie/CHIPs\",\n";
  iso_body += "  \"plate_meld\": \"Angel Meld ordered SHA-256\",\n";
  iso_body += "  \"interpreters_on_iso\": \"DISARMED_non_authority\",\n";
  iso_body += "  \"plates_present\": " + std::to_string(iso_present) + ",\n";
  iso_body += "  \"plates\": " + plates_json(iso_plates) + ",\n";
  iso_body += "  \"boot_cmdline_war\": \"field=1 i2=1 secure_layer=1 c2=9477 always_war=1 spear_mode=war spear_harden=1 angel_seal=1\",\n";
  iso_body += "  \"fake\": false\n";
  iso_body += "}\n";

  // Combined angel seal status (extends v2)
  std::string angel;
  angel += "{\n";
  angel += "  \"schema\": \"angel-seal-status/v3\",\n";
  angel += "  \"ts\": \"" + ts + "\",\n";
  angel += "  \"sealed\": " + std::string(sealed && iso_sealed ? "true" : "false") + ",\n";
  angel += "  \"stack_sealed\": " + std::string(sealed ? "true" : "false") + ",\n";
  angel += "  \"iso_sealed\": " + std::string(iso_sealed ? "true" : "false") + ",\n";
  angel += "  \"final_eye_sealed\": " +
           std::string(exists(home_sg() + "/zpics/final-eye-seal.json") ? "true" : "false") + ",\n";
  angel += "  \"commander\": \"Forever Watchguard Angel\",\n";
  angel += "  \"hostess7_commander\": \"hostess7\",\n";
  angel += "  \"rank\": \"ANGEL\",\n";
  angel += "  \"status\": \"" +
           std::string(sealed && iso_sealed ? "SEALED_UP" : (sealed ? "STACK_ONLY" : "UNSEALED")) +
           "\",\n";
  angel += "  \"stack\": \"C++\",\n";
  angel += "  \"planes\": [\"CHIPs\", \"Plate\", \"Meld\"],\n";
  angel += "  \"root_seal\": \"" + stack_root + "\",\n";
  angel += "  \"iso_root_seal\": \"" + iso_root + "\",\n";
  angel += "  \"interpreters\": \"DISARMED\",\n";
  angel += "  \"dangerous_languages\": false,\n";
  angel += "  \"rule\": \"Python, QBasic, and other high-level runtimes never dangerous to us; engine is C++ or lower.\",\n";
  angel += "  \"stack_plate\": \"angel-stack-seal.json\",\n";
  angel += "  \"iso_plate\": \"angel-iso-seal.json\"\n";
  angel += "}\n";

  if (std::strcmp(cmd, "status") != 0 || true) {
    write_all(stack_body, "angel-stack-seal.json");
    write_all(iso_body, "angel-iso-seal.json");
    write_all(angel, "angel-seal-status.json");
    // also doctrine companion
    const std::string doc =
        "{\n"
        "  \"schema\": \"spear-disarmed-interpreters/v1\",\n"
        "  \"updated\": \"" +
        ts +
        "\",\n"
        "  \"rule\": \"High-level languages may exist on disk. They are never war engine, never elevated "
        "authority, never served as product scripts, and must never be dangerous to us.\",\n"
        "  \"engine\": \"C++ or lower\",\n"
        "  \"chips\": \"FieldDie/CHIPs\",\n"
        "  \"plate\": true,\n"
        "  \"meld\": \"angel-sha256\",\n"
        "  \"languages\": " +
        lang_policy_json() +
        ",\n"
        "  \"angel_seal\": true\n"
        "}\n";
    write_all(doc, "disarmed-interpreters.json");
  }

  if (!quiet) {
    if (std::strcmp(cmd, "json") == 0 || std::strcmp(cmd, "status") == 0)
      std::fputs(angel.c_str(), stdout);
    else {
      std::printf("angel-seal stack=%s iso=%s status=%s\n", stack_root.c_str(), iso_root.c_str(),
                  (sealed && iso_sealed) ? "SEALED_UP" : (sealed ? "STACK_ONLY" : "PARTIAL"));
      std::printf("  plates_present=%d/%zu iso_present=%d/%zu interpreters=DISARMED engine=C++\n", present,
                  stack_plates.size(), iso_present, iso_plates.size());
    }
  }

  return (sealed && iso_sealed) ? 0 : 1;
}
