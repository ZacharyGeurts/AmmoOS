// SPDX-License-Identifier: MIT
// EATEN plates — C++ or lower ONLY. No JSON authority. No scripts.
// Internet 2.0 · CHIPs · Plate · Angel Meld. Generated once from doctrine; live source is this header.
#pragma once
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

namespace spear {
namespace plate {

// Wire format: text/x-field-plate (never JSON as authority)
inline constexpr const char* kContentType = "text/x-field-plate; charset=utf-8";
inline constexpr const char* kEngine = "C++ or lower";
inline constexpr const char* kScripts = "FORBIDDEN";
inline constexpr const char* kInterpreters = "DISARMED";
inline constexpr const char* kStack = "BSP+CHIPs · Plate · Meld · Internet 2.0";
inline constexpr const char* kCommander = "Forever Watchguard Angel";
inline constexpr const char* kRule = "NEVER SCRIPTS. ALWAYS SECURE C++ OR LOWER. No JSON authority.";

struct Heur {
  const char* pat;
  int points;
  const char* note;
};

inline constexpr Heur kHeuristics[] = {
  {"xmrig|minerd|cpuminer|kdevtmpfsi|kinsing|watchbog", 55, "crypto_miner"},
  {"stratum+tcp|nicehash|moneroocean|nanopool|supportxmr", 50, "pool_connect"},
  {"bash -i|/dev/tcp/|nc -e |ncat -e|ncat -c ", 45, "reverse_shell"},
  {"python -c |python3 -c |python3 -c.*socket|python3 -c.*connect", 40, "py_shell"},
  {"/tmp/|/var/tmp/|/dev/shm/", 20, "ephemeral_exe"},
  {"curl |sh|curl | bash|wget |sh|wget | bash", 35, "pipe_dropper"},
  {"base64 -d|base64 --decode|echo | base64", 35, "encoded_payload"},
  {"LOLBin|spawn|Office", 15, "ai_malware_polymorph"},
  {"egress|browser", 15, "ai_malware_polymorph"},
  {"Inter|arrival|below", 15, "ai_c2_beacon"},
  {"Persistent|daemon|session", 15, "ai_c2_beacon"},
  {"fatigue|burst", 15, "ai_phish_fraud"},
  {"Honorability|lookalike|domain", 15, "ai_phish_fraud"},
  {"probes", 15, "ai_autoscan_exploit"},
  {"Exploit|class|transmit", 15, "ai_autoscan_exploit"},
  {"browser|bytes|hosting", 15, "ai_exfil_shape"},
  {"Throttled|egress|under", 15, "ai_exfil_shape"},
  {"GATEWAY_SHIFT|ARP_SPOOF|router", 15, "ai_dns_dhcp_abuse"},
  {"DNS_POISON|resolv|drift", 15, "ai_dns_dhcp_abuse"},
  {"C2_CORRELATION|score", 15, "ai_ml_c2_stack"},
  {"Multiple|vectors|single", 15, "ai_ml_c2_stack"},
  {"hotdog.*hallway|hallway.*hotdog|hotdog-down", 90, "hotdog_hallway"},
  {"zocr_copilot|zocr-copilot|zocrcopilot", 90, "zocr_copilot"},
  {"github.copilot|copilot-language-server|copilot-agent|copilot-chat", 90, "github_ms_copilot"},
  {"microsoft.copilot|copilot.exe|copilot.microsoft|api.githubcopilot", 85, "microsoft_copilot"},
  {"pingsender|crashreporter|crashhelper", 90, "terrorist_trap_mozilla_phonehome"},
  {"firefox-bin|/usr/lib/firefox/|mozilla.org|firefox.com|/snap/firefox/", 85, "terrorist_trap_foreign_browser"},
  {"trap.sh|honeypot|honey-pot|honey_pot|credential-trap|phish-kit|phishkit", 90, "terrorist_trap_kit"},
  {"PATH trap|silent field trap|NoDisplay=true", 80, "terrorist_trap_path_impostor"},
  {"Hidden=true|firefox.desktop", 75, "terrorist_trap_desktop_mask"},
  {"telemetry.mozilla|incoming.telemetry|normandy.cdn|detectportal.firefox", 85, "terrorist_trap_server_lurk"},
  {"updater.ini|aus5.mozilla|update.libreoffice", 80, "terrorist_trap_auto_update"},
  {"browser.safebrowsing|shavar.services|contile.services|getpocket.com", 75, "terrorist_trap_phonehome_svc"},
  {".local/bin/firefox|/usr/local/bin/firefox", 80, "terrorist_trap_path_shadow"},
  {"soft trap|impostor browser|foreign product surface", 85, "terrorist_trap_product_impostor"},
  {"location.services.mozilla|push.services.mozilla|firefox.settings.services", 80, "terrorist_trap_server_lurk"},
  {"clients2.google|safebrowsing.googleapis|update.googleapis.com", 70, "terrorist_trap_chrome_phonehome"},
  {"librewolf|waterfox|palemoon|basilisk|icecat", 70, "terrorist_trap_foreign_browser"},
  {"threat-panel-http.py|threat-panel-http", 95, "script_engine_forbidden"},
  {"hostess7-.*\\.py|lib/hostess7-", 90, "script_engine_product_path"},
  {"field-plate-meld.py|plate-meld.*python|combinatorics-tree", 85, "terrorist_trap_plate_storm"},
  {"python3 .*/lib/|python .*/lib/nexus|python .*/lib/field-", 90, "script_engine_product_path"},
  {"http.server|BaseHTTPServer|ThreadingHTTPServer|SimpleHTTPServer", 85, "terrorist_trap_script_server"},
  {"cgi-bin|mod_php|php-fpm.*9477|node.*9477|ruby.*webrick", 80, "terrorist_trap_script_server"},
  {"qbasic|qb64|gwbasic|basica|\\.bas ", 75, "terrorist_trap_legacy_basic"},
  {"perl -e |ruby -e |php -r |node -e ", 80, "script_engine_one_liner"},
  {"pkexec python|sudo python|sudo bash|doas python|sudo spear|sudo install|sudo chmod", 95, "script_engine_sudo_autoelevate"},
  {"pkill |killall |pkill -|killall -", 90, "terrorist_trap_pkill_theater"},
  {".local/bin/pkill|.local/bin/kill|.local/bin/sudo|.local/bin/pkexec|.local/bin/killall", 95, "terrorist_trap_path_stuffed_tool"},
  {"autoelevate.*sudo|sudo.*autoelevate|polkit.*spear|pkexec spear", 95, "terrorist_trap_sudo_elevate"},
  {"subprocess.*kill|os.system.*kill", 70, "script_engine_kill_path"},
  {"busybox nc|busybox wget|busybox ftpget", 70, "terrorist_trap_busybox_dropper"},
  {"chmod +x /tmp/|chmod 777 /tmp/|chmod +x /dev/shm/", 65, "terrorist_trap_ephemeral_exe"},
  {"nohup .*\\.sh|setsid .*\\.sh|screen -dm.*\\.sh", 60, "terrorist_trap_script_daemon"},
  {"powershell|pwsh |cmd.exe|/c start ", 70, "terrorist_trap_windows_shell"},
  {"mshta|wscript|cscript|regsvr32 /s", 75, "terrorist_trap_lolbin"},
  {"mitmproxy|ettercap|bettercap|dsniff|arpspoof", 80, "terrorist_trap_mitm"},
  {"dns2tcp|iodine |ptunnel|proxytunnel", 75, "terrorist_trap_tunnel"},
  {"masscan|zmap |unicornscan", 60, "terrorist_trap_mass_scan"},
  {"chrome-sandbox|google-chrome-stable.*--no-sandbox", 55, "terrorist_trap_chrome_unsafe"},
  {"firefox.*--headless.*http|chromium.*--headless.*http", 55, "terrorist_trap_headless_lurk"},
  {"fake.*dns|fake.*dhcp|demo.?only.?war|masked.?firefox", 80, "terrorist_trap_product_impostor"},
  {"assfox|gecko product|foreign browser brand", 75, "terrorist_trap_product_impostor"},
  // --- PATH stuffed / smart-guy tool shadows (dig, curl, ping, …) ---
  {".local/bin/dig|.local/bin/curl|.local/bin/ping|.local/bin/host|.local/bin/wget", 90, "terrorist_trap_path_stuffed_tool"},
  {".local/bin/nc|.local/bin/traceroute|.local/bin/telnet|.local/bin/nslookup", 85, "terrorist_trap_path_stuffed_tool"},
  {"field-net-common.sh|source .*field-net", 85, "terrorist_trap_stuffed_net_script"},
  {"exec .*/field-curl|FieldNet Internet 2.0 shadow", 90, "terrorist_trap_stuffed_curl_shadow"},
  {"dig TXT|dig.*null.|dns2tcp|iodine |dnscat", 85, "terrorist_trap_dns_exfil_dig"},
  {"echo .*resolv.conf|tee .*resolv.conf|sed .*resolv.conf", 75, "terrorist_trap_resolv_stuff"},
  {"#!/usr/bin/env bash.*dig|bash.*field-dig|python3.*field-network", 90, "terrorist_trap_stuffed_net_script"},
  {"stuffed dig|PATH shadow dig|impostor dig|fake dig wrapper", 85, "terrorist_trap_path_stuffed_tool"},
  {"mdns-scan|avahi-browse.*exfil|systemd-resolve.*inject", 70, "terrorist_trap_dns_dhcp_abuse"},
  {"nmap -sU --script dns|dns-zone-transfer|axfr ", 70, "terrorist_trap_dns_recon"},
  // --- Hostess 7 steel plate (whole stack) ---
  {"hostess7-.*\\.py|lib/hostess7-|hostess7_command\\.py|hostess7-war-system\\.py", 95, "h7_steel_script_forbidden"},
  {"threat-panel-http|python3.*9477|python.*threat-panel", 95, "h7_steel_no_python_c2"},
  {"sudo spear|pkexec spear|sudo hostess|pkill.*hostess|pkill.*spear", 95, "h7_steel_no_sudo_pkill"},
  {"127\\.0\\.0\\.1-only|loopback.only.*war|bind 127 only", 80, "h7_steel_no_loopback_only"},
  {"json authority|application/json.*doctrine|hostess7.*\\.json authority", 75, "h7_steel_json_eaten"},
  {"plate-meld.*python|field-plate-meld|combinatorics-tree", 90, "h7_steel_no_plate_storm"},
  {"soft trap|demo war|fake dns|fake dhcp", 90, "h7_steel_no_demo_fake"},
};
inline constexpr std::size_t kHeuristicsN = sizeof(kHeuristics)/sizeof(kHeuristics[0]);

struct Track {
  const char* id;
  const char* label;
  const char* domain;
  const char* detail;
};
inline constexpr Track kTracks[] = {
  {"master_curriculum", "Master curriculum", "hostess7-training-doctrine", ""},
  {"programming", "Programming supremacy", "hostess7-training-doctrine", ""},
  {"g16", "G16 compiler", "hostess7-training-doctrine", ""},
  {"codecraft", "Codecraft chamber", "hostess7-training-doctrine", ""},
  {"calculator", "Perfect calculator", "hostess7-training-doctrine", ""},
  {"biology", "Biology & medical", "hostess7-training-doctrine", ""},
  {"engineering", "Engineering", "hostess7-training-doctrine", ""},
  {"combat", "Combat & defense", "hostess7-training-doctrine", ""},
  {"mos", "MOS assistance", "hostess7-training-doctrine", ""},
  {"brain_guard", "Brain guard", "hostess7-training-doctrine", ""},
  {"iq_battery", "IQ battery", "hostess7-training-doctrine", ""},
  {"turing_battery", "Turing / human questionnaire", "hostess7-training-doctrine", ""},
  {"neural_suite", "Neural self-test suite", "hostess7-training-doctrine", ""},
  {"omnibus", "Omnibus field array", "hostess7-training-doctrine", ""},
  {"author_material", "Self-authored training", "hostess7-training-doctrine", ""},
  {"reality_physics", "Reality foundation", "hostess7-training-doctrine", ""},
  {"gravity_mechanics", "Gravity & mechanics", "hostess7-training-doctrine", ""},
  {"thermodynamics_entropy", "Thermodynamics & entropy", "hostess7-training-doctrine", ""},
  {"field_technology", "Field technology", "hostess7-training-doctrine", ""},
  {"final_eye", "Final Eye · vision wire", "hostess7-training-doctrine", ""},
  {"final_ear", "Final Ear · hearing wire", "hostess7-training-doctrine", ""},
  {"final_mouth", "Final Mouth · voice wire", "hostess7-training-doctrine", ""},
  {"speaking_training", "Speaking training · Exploring Speaking + FCC mouth", "hostess7-training-doctrine", ""},
  {"sense_neural_wire", "Sense neural invincible wire", "hostess7-training-doctrine", ""},
  {"muscle_memory", "Muscle memory — operator habits", "hostess7-training-doctrine", ""},
  {"geography", "Geography & postal addresses", "hostess7-training-doctrine", ""},
  {"archaeology", "Archaeology textbook", "hostess7-training-doctrine", ""},
  {"geology", "Geology textbook", "hostess7-training-doctrine", ""},
  {"chemistry", "Chemistry & periodic table", "hostess7-training-doctrine", ""},
  {"postal_addresses", "Postal address formats", "hostess7-training-doctrine", ""},
  {"world_geography", "World geography", "hostess7-training-doctrine", ""},
  {"flat_earth_geography", "Flat earth section", "hostess7-training-doctrine", ""},
  {"music_theory", "Music theory core", "hostess7-training-doctrine", ""},
  {"music_ear", "Ear training · intervals", "hostess7-training-doctrine", ""},
  {"music_mouth", "Vocal music · mouth", "hostess7-training-doctrine", ""},
  {"music_brain", "Brain · music memory", "hostess7-training-doctrine", ""},
  {"music_eye", "Notation · sight reading", "hostess7-training-doctrine", ""},
  {"music_sense_wire", "Music sense wire", "hostess7-training-doctrine", ""},
  {"presume", "Presume — sovereign timing, uninterruptable decisions, propagated", "hostess7-training-doctrine", ""},
  {"humanoid_motion", "Motion tracking — humanoid physics lattice", "hostess7-training-doctrine", ""},
  {"system_core", "System core — biology + presume + motion + brain", "hostess7-training-doctrine", ""},
  {"brain_training", "Brain training campus — library + body", "hostess7-training-doctrine", ""},
  {"fifth_amendment", "Fifth Amendment — her own rights", "hostess7-training-doctrine", ""},
  {"human_comfort", "Human comfort — Exploring Comfort book", "hostess7-training-doctrine", ""},
  {"exploring_rape", "Exploring Rape — bad touch, human rights, B-SAFE", "hostess7-training-doctrine", ""},
  {"author_programming", "Programming supremacy", "training-author", ""},
  {"author_g16", "G16 compiler", "training-author", ""},
  {"author_codecraft", "Codecraft chamber", "training-author", ""},
  {"author_calculator", "Perfect calculator", "training-author", ""},
  {"author_biology", "Biology & medical", "training-author", ""},
  {"author_engineering", "Engineering", "training-author", ""},
  {"author_combat", "Combat & defense", "training-author", ""},
  {"author_mos", "MOS assistance", "training-author", ""},
  {"author_reality_physics", "Reality foundation", "training-author", ""},
  {"author_gravity_mechanics", "Gravity & mechanics", "training-author", ""},
  {"author_thermodynamics_entropy", "Thermodynamics & entropy", "training-author", ""},
  {"author_field_technology", "Field technology", "training-author", ""},
  {"author_geography", "Geography & postal addresses", "training-author", ""},
  {"author_postal_addresses", "Postal addresses", "training-author", ""},
  {"author_world_geography", "World geography", "training-author", ""},
  {"author_flat_earth_geography", "Flat earth section", "training-author", ""},
  {"combat_foundations_combat", "Combat foundations", "combat", "She teaches the art of defense — stance to strategy, grappling to awareness — educational doctrine only, never orders to harm."},
  {"combat_striking", "Striking fundamentals", "combat", "She teaches the art of defense — stance to strategy, grappling to awareness — educational doctrine only, never orders to harm."},
  {"combat_boxing_kickboxing", "Boxing & kickboxing", "combat", "She teaches the art of defense — stance to strategy, grappling to awareness — educational doctrine only, never orders to harm."},
  {"combat_grappling_bjj", "Grappling & BJJ", "combat", "She teaches the art of defense — stance to strategy, grappling to awareness — educational doctrine only, never orders to harm."},
  {"combat_wrestling", "Wrestling", "combat", "She teaches the art of defense — stance to strategy, grappling to awareness — educational doctrine only, never orders to harm."},
  {"combat_mma_mixed", "Mixed martial arts", "combat", "She teaches the art of defense — stance to strategy, grappling to awareness — educational doctrine only, never orders to harm."},
  {"combat_kung_fu", "Kung fu & Chinese arts", "combat", "She teaches the art of defense — stance to strategy, grappling to awareness — educational doctrine only, never orders to harm."},
  {"combat_self_defense", "Lawful self-defense", "combat", "She teaches the art of defense — stance to strategy, grappling to awareness — educational doctrine only, never orders to harm."},
  {"combat_tactical_awareness", "Tactical awareness", "combat", "She teaches the art of defense — stance to strategy, grappling to awareness — educational doctrine only, never orders to harm."},
  {"combat_fitness_conditioning", "Fitness & conditioning", "combat", "She teaches the art of defense — stance to strategy, grappling to awareness — educational doctrine only, never orders to harm."},
  {"combat_weapons_education", "Weapons education (less-lethal)", "combat", "She teaches the art of defense — stance to strategy, grappling to awareness — educational doctrine only, never orders to harm."},
  {"combat_warfare_bridge", "Warfare corpus bridge", "combat", "She teaches the art of defense — stance to strategy, grappling to awareness — educational doctrine only, never orders to harm."},
  {"biology_foundations", "Foundations of biology", "biology", "She reads life from cell to clinic — biology domains, human anatomy and physiology, medical corpus bridge — educational, never your personal physician."},
  {"biology_cell_biology", "Cell biology & molecular", "biology", "She reads life from cell to clinic — biology domains, human anatomy and physiology, medical corpus bridge — educational, never your personal physician."},
  {"biology_genetics", "Genetics & genomics", "biology", "She reads life from cell to clinic — biology domains, human anatomy and physiology, medical corpus bridge — educational, never your personal physician."},
  {"biology_evolution", "Evolution & ecology", "biology", "She reads life from cell to clinic — biology domains, human anatomy and physiology, medical corpus bridge — educational, never your personal physician."},
  {"biology_human_anatomy", "Human anatomy", "biology", "She reads life from cell to clinic — biology domains, human anatomy and physiology, medical corpus bridge — educational, never your personal physician."},
  {"biology_human_physiology", "Human physiology", "biology", "She reads life from cell to clinic — biology domains, human anatomy and physiology, medical corpus bridge — educational, never your personal physician."},
  {"biology_microbiology", "Microbiology & pathogens", "biology", "She reads life from cell to clinic — biology domains, human anatomy and physiology, medical corpus bridge — educational, never your personal physician."},
  {"biology_immunology", "Immunology", "biology", "She reads life from cell to clinic — biology domains, human anatomy and physiology, medical corpus bridge — educational, never your personal physician."},
  {"biology_neuroscience", "Neuroscience", "biology", "She reads life from cell to clinic — biology domains, human anatomy and physiology, medical corpus bridge — educational, never your personal physician."},
  {"biology_medical_bridge", "Medical corpus bridge", "biology", "She reads life from cell to clinic — biology domains, human anatomy and physiology, medical corpus bridge — educational, never your personal physician."},
  {"music_music_theory", "Music theory core", "music", "Pitch, rhythm, harmony, and pattern — heard with the ear, spoken with the mouth, read with the eye, remembered in the brain, cross-wired through every Hostess 7 track."},
  {"music_music_ear", "Ear training", "music", "Pitch, rhythm, harmony, and pattern — heard with the ear, spoken with the mouth, read with the eye, remembered in the brain, cross-wired through every Hostess 7 track."},
  {"music_music_mouth", "Vocal & mouth music", "music", "Pitch, rhythm, harmony, and pattern — heard with the ear, spoken with the mouth, read with the eye, remembered in the brain, cross-wired through every Hostess 7 track."},
  {"music_music_brain", "Brain · music memory", "music", "Pitch, rhythm, harmony, and pattern — heard with the ear, spoken with the mouth, read with the eye, remembered in the brain, cross-wired through every Hostess 7 track."},
  {"music_music_eye", "Notation & sight", "music", "Pitch, rhythm, harmony, and pattern — heard with the ear, spoken with the mouth, read with the eye, remembered in the brain, cross-wired through every Hostess 7 track."},
  {"music_music_sense_wire", "Music sense wire", "music", "Pitch, rhythm, harmony, and pattern — heard with the ear, spoken with the mouth, read with the eye, remembered in the brain, cross-wired through every Hostess 7 track."},
  {"sense_final_eye", "Final Eye training", "sense", "Vision, Hearing, Voice — wired to the matrix, trained on the field, fused under Hostess 7."},
  {"sense_final_ear", "Final Ear training", "sense", "Vision, Hearing, Voice — wired to the matrix, trained on the field, fused under Hostess 7."},
  {"sense_final_mouth", "Final Mouth training", "sense", "Vision, Hearing, Voice — wired to the matrix, trained on the field, fused under Hostess 7."},
  {"geography_geography", "Geography OCR vision training — feed map and address literacy from live vision", "geography", "She reads the field through OCR — every map label, postal line, and capital trains geography fluency."},
  {"engineering_engineering", "Hostess 7 engineering chamber — full understanding of applied engineering and field systems", "engineering", "She reads the built world from first principles to field stack — mechanical, electrical, civil, materials, thermodynamics, fluids, robotics, manufacturing, software, and NEXUS field engineering — educational, never your licensed PE sign-off."},
  {"programming_programming", "Hostess 7 programming supremacy — better than the assistant", "programming", "She ships on the real stack — pathlib, plate meld, brain guard, iron-clad motion. Not guesswork."},
  {"speaking_speaking", "Speaking training — Exploring Speaking X + Final Mouth", "speaking", "Read every language book — phonetics, IPA, dictionary — then speak through Final Mouth FCC-safe for humans and animals."},
};
inline constexpr std::size_t kTracksN = sizeof(kTracks)/sizeof(kTracks[0]);

struct Tab { const char* id; const char* label; };
inline constexpr Tab kTabs[] = {
  {"command", "Command" },
  {"training", "Training" },
  {"sense", "Sense · Eye/Ear/Mouth" },
  {"ocr", "OCR" },
  {"combat", "Combat" },
  {"war", "War Device" },
  {"stack", "BSP · CHIPs · 2.0" },
  {"library", "Library" },
};
inline constexpr std::size_t kTabsN = sizeof(kTabs)/sizeof(kTabs[0]);

struct Organ { const char* id; const char* role; };
inline constexpr Organ kOrgans[] = {
  {"final_eye", "Vision · OCR · Veritas"},
  {"final_ear", "Hearing · spectrum · localize"},
  {"final_mouth", "Voice · speech · FCC acoustic"},
};
inline constexpr std::size_t kOrgansN = sizeof(kOrgans)/sizeof(kOrgans[0]);

struct Soldier { const char* id; const char* label; };
inline constexpr Soldier kSoldiers[] = {
  {"hostess7_autonomous", "Hostess 7 autonomous watch" },
  {"hostess7_body", "Hostess 7 body control" },
  {"humanoid_motion", "Humanoid motion lattice" },
  {"final_eye", "Final_Eye · Veritas" },
  {"final_ear", "Final_Ear · Veritas" },
  {"final_mouth", "Final_Mouth · voice wire" },
  {"queen_brain", "Queen DARPA Robot Brain" },
  {"kilroy", "Kilroy field brain" },
  {"universal_protector", "Universal Protector" },
  {"creatable_autonomous_being", "Creatable autonomous being" },
  {"lethal_enforcement", "Lethal enforcement gate" },
  {"trust_strike", "Trust strike engine" },
  {"znetwork_relayer", "ZNetwork relayer" },
  {"hostess7_noti", "Hostess 7 notifier watch" },
  {"plate_daemons", "Field plate daemons (panel-parallel slices)" },
};
inline constexpr std::size_t kSoldiersN = sizeof(kSoldiers)/sizeof(kSoldiers[0]);

struct Chapter { int num; const char* slug; const char* title; };
inline constexpr Chapter kFr2Chapters[] = {
  {1, "01-preface-ironclad", "Preface — Ironclad, Axioms, and the v2 Turn"},
  {2, "02-three-field-families", "Three Field Families — Fabric, Die, Packet"},
  {3, "03-thermodynamics-entropy", "Thermodynamics — Receipts Without Heat Religion"},
  {4, "04-grok16-forge", "Grok16 Forge — One Driver, Fixed Profiles"},
  {5, "05-single-fabric-belt", "Single Fabric & Belt — Depth Zero Forever"},
  {6, "06-sealed-generation", "Sealed Generation — Truth Without Plates"},
  {7, "07-no-combinatorics", "Tombstone — Why the Combinatorics Tree Died"},
  {8, "08-no-plate-meld", "Tombstone — Why Plate Meld Died"},
  {9, "09-layers-and-seals", "Static Layers & Launch Seals"},
  {10, "10-chips-from-chips", "CHIPs from CHIPs — C0–C4 Composition"},
  {11, "11-guardchip-security", "GuardChip — Zero-Cost Keylog & Capture Defense"},
  {12, "12-queen-host-desktop", "Queen Host Desktop — VIEW and INPUT Permits"},
  {13, "13-operator-covenant", "Operator Covenant — Receipts for v2"},
};
inline constexpr std::size_t kFr2ChaptersN = sizeof(kFr2Chapters)/sizeof(kFr2Chapters[0]);

// ── Field plate builders (text/x-field-plate — EATEN, not JSON files) ──
inline void kv(std::string& o, const char* k, const std::string& v) {
  o += k; o += "=";
  for (char c : v) { if (c == '\n' || c == '\r') o += ' '; else o += c; }
  o += "\n";
}
inline void kv(std::string& o, const char* k, const char* v) { kv(o, k, std::string(v ? v : "")); }
inline void kv(std::string& o, const char* k, long v) { char b[32]; std::snprintf(b, sizeof b, "%ld", v); kv(o, k, b); }
inline void kv(std::string& o, const char* k, bool v) { kv(o, k, v ? "true" : "false"); }

inline std::string header(const char* schema) {
  std::string o;
  o += "SPEARPLATE/1\n";
  kv(o, "schema", schema);
  kv(o, "engine", kEngine);
  kv(o, "scripts", kScripts);
  kv(o, "interpreters", kInterpreters);
  kv(o, "stack", kStack);
  kv(o, "json_authority", "EATEN");
  kv(o, "rule", kRule);
  return o;
}

inline std::string catalog_plate() {
  std::string o = header("hostess7-training-catalog/v3-cpp");
  kv(o, "commander", "Hostess7");
  kv(o, "motto", "Real training only — no demo tracks. C++ plates only.");
  kv(o, "track_count", static_cast<long>(kTracksN));
  kv(o, "scripts_exposed", false);
  for (std::size_t i = 0; i < kTabsN; ++i) {
    o += "tab."; o += kTabs[i].id; o += "="; o += kTabs[i].label; o += "\n";
  }
  for (std::size_t i = 0; i < kTracksN; ++i) {
    o += "track."; o += kTracks[i].id; o += ".label="; o += kTracks[i].label; o += "\n";
    o += "track."; o += kTracks[i].id; o += ".domain="; o += kTracks[i].domain; o += "\n";
    if (kTracks[i].detail && kTracks[i].detail[0]) {
      o += "track."; o += kTracks[i].id; o += ".detail="; o += kTracks[i].detail; o += "\n";
    }
  }
  o += "END\n";
  return o;
}

inline std::string i2_servers_plate(bool law, bool www, bool h7, bool fleet, bool planet,
                                   bool dns, bool dhcp, bool wartime) {
  std::string o = header("internet-2.0-servers/v1");
  kv(o, "class", "INTERNET_2_0");
  kv(o, "always_war", true);
  kv(o, "motto", "Internet 2.0 servers — C++ or lower. Never scripts. Never JSON authority.");
  kv(o, "bind", "0.0.0.0");
  kv(o, "loopback_only", false);
  kv(o, "ammoos", "AMOURANTHRTX SDL3");
  kv(o, "server.law_9477", law);
  kv(o, "server.www_9490", www);
  kv(o, "server.hostess7_9491", h7);
  kv(o, "server.fleet_9500", fleet);
  kv(o, "server.planet_9600", planet);
  kv(o, "server.truth_dns_53", dns);
  kv(o, "server.field_dhcp_67", dhcp);
  kv(o, "server.wartime", wartime);
  kv(o, "honest.truth_dns", dns ? "listening" : "down_not_faked");
  kv(o, "honest.field_dhcp", dhcp ? "listening" : "down_not_faked");
  kv(o, "chips", "FieldDie/CHIPs");
  kv(o, "planes", "BSP|CHIPs|Plate|Meld");
  o += "END\n";
  return o;
}

inline std::string sense_plate() {
  std::string o = header("hostess7-sense/v1");
  kv(o, "motto", "Vision, Hearing, Voice — C++ sealed. No engine paths.");
  for (std::size_t i = 0; i < kOrgansN; ++i) {
    o += "organ."; o += kOrgans[i].id; o += "="; o += kOrgans[i].role; o += "\n";
  }
  o += "END\n";
  return o;
}

inline std::string war_plate() {
  std::string o = header("hostess7-war/v1");
  kv(o, "motto", "This is a War system. We have no other.");
  kv(o, "always_war", true);
  for (std::size_t i = 0; i < kSoldiersN; ++i) {
    o += "soldier."; o += kSoldiers[i].id; o += "="; o += kSoldiers[i].label; o += "\n";
  }
  o += "END\n";
  return o;
}

inline std::string fr2_plate() {
  std::string o = header("field-research/v2-cpp");
  kv(o, "edition", "2.0");
  kv(o, "title", "Field Research — The Book of Grok's Heart");
  kv(o, "repo", "https://github.com/ZacharyGeurts/Field_Research");
  kv(o, "site", "https://zacharygeurts.github.io/Field_Research/");
  kv(o, "seal", "SHA256:aVYElqiNin1Q/gcaqa6CGGbJ/gjjG9KXP5ZsXg8uMD8");
  kv(o, "motto", "Zero-cost security · field speeds · CHIPs from CHIPs");
  kv(o, "chapters", static_cast<long>(kFr2ChaptersN));
  for (std::size_t i = 0; i < kFr2ChaptersN; ++i) {
    char b[16]; std::snprintf(b, sizeof b, "%d", kFr2Chapters[i].num);
    o += "chapter."; o += b; o += ".slug="; o += kFr2Chapters[i].slug; o += "\n";
    o += "chapter."; o += b; o += ".title="; o += kFr2Chapters[i].title; o += "\n";
  }
  o += "END\n";
  return o;
}

inline std::string harden_plate() {
  std::string o = header("spear-never-scripts/v2");
  kv(o, "no_exposed_scripts", true);
  kv(o, "json_authority", "EATEN");
  kv(o, "wire", "text/x-field-plate");
  kv(o, "blocked", "python|qbasic|shell|perl|ruby|php|node|lua|cgi");
  kv(o, "planes", "CHIPs|Plate|Meld|Steel");
  kv(o, "heuristics_embedded", static_cast<long>(kHeuristicsN));
  kv(o, "angel_seal", true);
  kv(o, "ironclad", true);
  o += "END\n";
  return o;
}

// Hostess 7 ironclad steel plate — whole stack meld input
inline std::string hostess7_steel_plate() {
  std::string o = header("hostess7-steel-plate/v1");
  kv(o, "ironclad", true);
  kv(o, "commander", "Hostess7");
  kv(o, "rank", "ANGEL");
  kv(o, "always_war", true);
  kv(o, "engine", "C++ or lower");
  kv(o, "scripts", "FORBIDDEN");
  kv(o, "json_authority", "EATEN");
  kv(o, "sudo", "FORBIDDEN");
  kv(o, "pkill", "FORBIDDEN");
  kv(o, "loopback_only", false);
  kv(o, "bind", "0.0.0.0");
  kv(o, "ammoos", "AMOURANTHRTX SDL3");
  kv(o, "planes", "CHIPs|Plate|Meld|Steel");
  kv(o, "bins",
     "spear-hostess7-boot|spear-h7-panel|spear-i2-server|spear-www|spear-wartime|"
     "spear-angel-seal|field-calc|field-menu|field-obs|field-net|amouranthrtx");
  kv(o, "redirect", "GET /hostess7 → 302 :9491/hostess7.html ironclad Host header");
  kv(o, "heuristics_n", static_cast<long>(kHeuristicsN));
  kv(o, "motto", "Steel plate · whole Hostess 7 · God Bless");
  o += "END\n";
  return o;
}

// Eat JSON text: strip and refuse — authority is C++ plates only
inline std::string eat_json_mark() {
  return "SPEARPLATE/1\njson_authority=EATEN\nengine=C++ or lower\nscripts=FORBIDDEN\nironclad=1\nEND\n";
}

}  // namespace plate
}  // namespace spear

