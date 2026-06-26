// Queen Browser — single RTX executable entry (AMOURANTHRTX navigator_main)
#include "Navigator.hpp"
#include "engine/FieldQueenBrowser.hpp"

#include <cstdlib>
#include <filesystem>
#include <string>

namespace {

void setDefaultEnv(const char* key, const std::string& value) {
    if (!std::getenv(key) || !std::getenv(key)[0])
        setenv(key, value.c_str(), 1);
}

std::string detectSgRoot() {
    if (const char* v = std::getenv("SG_ROOT"); v && v[0]) return v;
    // Queen/engine/queen-main.cpp → Queen → NewLatest → SG
    std::error_code ec;
    auto queen = std::filesystem::path(__FILE__).parent_path().parent_path();
    auto sg = queen.parent_path().parent_path();
    if (std::filesystem::exists(sg / "KILROY", ec))
        return sg.string();
    return "/home/default/Desktop/SG";
}

} // namespace

int main(int argc, char* argv[]) {
    FieldQueenBrowser::enableSovereignMode();
    FieldQueenSovereign::enableFieldRtxSovereign();
    setenv("NEXUS_PANEL_AUTO_OPEN", "1", 1);
    setenv("QUEEN_FIELD_GPU", "1", 1);
    setenv("QUEEN_AUTO_BOOT", "1", 1);
    setenv("QUEEN_WORLD_AUTO_BOOT", "1", 1);
    setenv("QUEEN_INSTANT_BROWSER", "1", 1);
    setenv("NEXUS_FIELD_BROWSER_QUEEN", "0", 1);
    setDefaultEnv("QUEEN_DISPLAY_REFRESH", "120");

    const std::string sg = detectSgRoot();
    const std::string queen = sg + "/NewLatest/Queen";
    const std::string kilroy = sg + "/KILROY";
    const std::string rtx = sg + "/AMOURANTHRTX";
    const std::string g16 = sg + "/Grok16";

    setDefaultEnv("SG_ROOT", sg);
    setDefaultEnv("NEXUS_INSTALL_ROOT", queen);
    setDefaultEnv("QUEEN_ROOT", queen);
    setDefaultEnv("GROK16_ROOT", g16);
    setDefaultEnv("KILROY_ROOT", kilroy);
    setDefaultEnv("AMOURANTHRTX_ROOT", rtx);
    setDefaultEnv("HOSTESS7_ROOT", sg + "/Hostess7");

    FieldQueenBrowser::parseArgvQueen(argc, argv);
    return navigator_main(argc, argv);
}