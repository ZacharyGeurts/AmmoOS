#include "FieldQueenShell.hpp"

#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <string>
#include <vector>

namespace {

std::filesystem::path queenRoot() noexcept {
    const char* env = std::getenv("QUEEN_ROOT");
    if (env && env[0]) return std::filesystem::path(env);
    return std::filesystem::current_path();
}

bool existsBin(const std::string& name) noexcept {
    for (const auto& dir : {"/usr/local/bin", "/usr/bin"}) {
        const auto p = std::filesystem::path(dir) / name;
        if (std::filesystem::exists(p)) return true;
    }
    return false;
}

} // namespace

namespace FieldQueenShell {

bool init(SDL_Window** outWindow, SDL_Renderer** outRenderer) noexcept {
    if (!SDL_Init(SDL_INIT_VIDEO | SDL_INIT_EVENTS)) {
        std::fprintf(stderr, "[Queen] SDL_Init: %s\n", SDL_GetError());
        return false;
    }
    SDL_Window* win = SDL_CreateWindow("Queen Browser", 1440, 900, SDL_WINDOW_RESIZABLE);
    if (!win) {
        std::fprintf(stderr, "[Queen] SDL_CreateWindow: %s\n", SDL_GetError());
        return false;
    }
    SDL_Renderer* ren = SDL_CreateRenderer(win, nullptr);
    if (!ren) {
        std::fprintf(stderr, "[Queen] SDL_CreateRenderer: %s\n", SDL_GetError());
        SDL_DestroyWindow(win);
        return false;
    }
    *outWindow = win;
    *outRenderer = ren;
    return true;
}

void shutdown(SDL_Window* window, SDL_Renderer* renderer) noexcept {
    if (renderer) SDL_DestroyRenderer(renderer);
    if (window) SDL_DestroyWindow(window);
    SDL_Quit();
}

void renderBootFrame(SDL_Renderer* renderer, const BootState& boot, const Theme& theme,
                     int w, int h) noexcept {
    const float t = boot.sealed_time.load();
    const float load = boot.load_progress.load();
    const float pulse = 0.5f + 0.5f * std::sin(t * 6.28318f);

    const Uint8 br = static_cast<Uint8>(theme.void_r * 255);
    const Uint8 bg = static_cast<Uint8>(theme.void_g * 255);
    const Uint8 bb = static_cast<Uint8>(theme.void_b * 255);
    SDL_SetRenderDrawColor(renderer, br, bg, bb, 255);
    SDL_RenderClear(renderer);

    const int cx = w / 2;
    const int cy = h / 2 - h / 12;
    const int r0 = static_cast<int>(std::min(w, h) * (0.14f + pulse * 0.02f));
    const int r1 = static_cast<int>(std::min(w, h) * (0.22f + load * 0.06f));

    SDL_SetRenderDrawColor(renderer,
        static_cast<Uint8>(theme.aqua_r * 255),
        static_cast<Uint8>(theme.aqua_g * 255),
        static_cast<Uint8>(theme.aqua_b * 255), 200);
    for (int a = 0; a < 360; a += 4) {
        const float rad = static_cast<float>(a) * 3.14159f / 180.f;
        SDL_RenderLine(renderer,
            cx + static_cast<int>(std::cos(rad) * r0),
            cy + static_cast<int>(std::sin(rad) * r0),
            cx + static_cast<int>(std::cos(rad) * (r0 + 3)),
            cy + static_cast<int>(std::sin(rad) * (r0 + 3)));
    }

    SDL_SetRenderDrawColor(renderer,
        static_cast<Uint8>(theme.rose_r * 255),
        static_cast<Uint8>(theme.rose_g * 255),
        static_cast<Uint8>(theme.rose_b * 255), 180);
    for (int a = 0; a < 360; a += 6) {
        const float rad = static_cast<float>(a) * 3.14159f / 180.f;
        SDL_RenderLine(renderer,
            cx + static_cast<int>(std::cos(rad) * r1),
            cy + static_cast<int>(std::sin(rad) * r1),
            cx + static_cast<int>(std::cos(rad) * (r1 + 2)),
            cy + static_cast<int>(std::sin(rad) * (r1 + 2)));
    }

    const int barW = w * 2 / 5;
    const int barH = 12;
    const int barX = (w - barW) / 2;
    const int barY = cy + h / 8;
    SDL_SetRenderDrawColor(renderer, 26, 34, 48, 255);
    SDL_FRect track{static_cast<float>(barX), static_cast<float>(barY),
                    static_cast<float>(barW), static_cast<float>(barH)};
    SDL_RenderFillRect(renderer, &track);
    SDL_FRect fill{static_cast<float>(barX), static_cast<float>(barY),
                   static_cast<float>(barW) * load, static_cast<float>(barH)};
    SDL_SetRenderDrawColor(renderer,
        static_cast<Uint8>(theme.aqua_r * 255),
        static_cast<Uint8>(theme.aqua_g * 255),
        static_cast<Uint8>(theme.aqua_b * 255), 255);
    SDL_RenderFillRect(renderer, &fill);

    SDL_RenderPresent(renderer);
}

bool pickEngine(std::string& binary, std::string& engine_id) noexcept {
    const auto root = queenRoot();
    const std::vector<std::pair<std::string, std::string>> candidates = {
        {root.string() + "/vendor/ladybird/Build/release/bin/Ladybird", "ladybird"},
        {root.string() + "/vendor/ladybird/build/bin/Ladybird", "ladybird"},
        {root.string() + "/build/servo/servo", "servo"},
        {"fieldfox", "fieldfox"},
        {"field-queen", "field-queen"},
        {"queen-browser", "queen-shell"},
        {"firefox", "gecko"},
        {"librewolf", "gecko"},
        {"floorp", "gecko"},
    };
    for (const auto& [path, id] : candidates) {
        if (path.find('/') != std::string::npos) {
            if (std::filesystem::exists(path)) {
                binary = path;
                engine_id = id;
                return true;
            }
        } else if (existsBin(path)) {
            binary = path;
            engine_id = id;
            return true;
        }
    }
    return false;
}

bool launchEngine(const std::string& binary, const char* url) noexcept {
    if (binary.empty() || !url) return false;
    std::string cmd;
    if (binary.find('/') != std::string::npos) {
        cmd = "\"" + binary + "\" \"" + url + "\" &";
    } else {
        const char* launch = std::getenv("NEXUS_INSTALL_ROOT");
        std::string ff;
        if (launch) {
            ff = std::string(launch) + "/lib/fieldfox-launch.sh";
            if (std::filesystem::exists(ff)) {
                cmd = "NEXUS_INSTALL_ROOT=\"" + std::string(launch) + "\" \"" + ff + "\" \"" +
                      url + "\" &";
                return std::system(cmd.c_str()) == 0;
            }
        }
        cmd = binary + " --new-window \"" + url + "\" &";
    }
    std::fprintf(stderr, "[Queen] launch: %s\n", cmd.c_str());
    return std::system(cmd.c_str()) == 0;
}

void pumpBoot(SDL_Renderer* renderer, BootState& boot, const Theme& theme,
              int w, int h, float dt) noexcept {
    boot.sealed_time.store(boot.sealed_time.load() + dt);
    float p = boot.load_progress.load();
    p = std::min(1.f, p + dt * 0.55f);
    boot.load_progress.store(p);
    renderBootFrame(renderer, boot, theme, w, h);
    if (p >= 1.f) boot.boot_done.store(true);
}

} // namespace FieldQueenShell