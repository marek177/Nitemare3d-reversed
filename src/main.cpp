#include "app/GameData.hpp"
#include "game/LevelState.hpp"
#include "platform/sdl/SDLVideo.hpp"
#include "renderer/Framebuffer.hpp"
#include "renderer/Raycaster.hpp"
#include "re/N3DPreviewFrameTrace.hpp"

#include <chrono>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>

namespace {
void cardinalFromAngle(double angle, int& dx, int& dy) {
    const double x = std::cos(angle), y = std::sin(angle);
    if (std::abs(x) >= std::abs(y)) { dx = x >= 0.0 ? 1 : -1; dy = 0; }
    else { dx = 0; dy = y >= 0.0 ? 1 : -1; }
}
}

int main(int argc, char** argv) {
    try {
        std::filesystem::path dataRoot = "data/original";
        int episode = 1, level = 1;
        std::filesystem::path previewTrace;
        for (int i = 1; i < argc; ++i) {
            const std::string arg = argv[i];
            if (arg == "--data" && i + 1 < argc) dataRoot = argv[++i];
            else if (arg == "--episode" && i + 1 < argc) episode = std::stoi(argv[++i]);
            else if (arg == "--level" && i + 1 < argc) level = std::stoi(argv[++i]);
            else if (arg == "--preview-trace" && i + 1 < argc) previewTrace = argv[++i];
            else if (arg == "--preview-trace") throw std::runtime_error("Missing --preview-trace path");
        }
        auto data = n3d::GameData::loadEpisode(dataRoot, episode);
        if (level < 1 || static_cast<std::size_t>(level) > data.episode().maps.levels().size()) throw std::runtime_error("Requested level is outside this episode");
        auto world = n3d::LevelState::create(data.episode().maps.levels().at(static_cast<std::size_t>(level - 1)), data.episode().objects, data.episode().walls);
        std::cout << "Episode " << episode << ", level " << level << ": pushables=" << world.pushables().size() << '\n';
        n3d::Framebuffer fb(320, 200);
        std::cerr << "RENDERER: diagnostic DDA preview ONLY; NOT original N3D pixel parity.\n";
        n3d::Raycaster raycaster(&data.episode().images);
        std::ofstream trace;
        if (!previewTrace.empty()) {
            trace.open(previewTrace);
            if (!trace) throw std::runtime_error("Cannot open preview trace");
            n3d::re::preview::header(trace);
            std::cerr << "PREVIEW: frame-based trace; not DOS tick parity.\n";
        }
        std::uint64_t frameNumber = 0, pushTick = 0;
        n3d::SDLVideo video(320, 200, 3);
        auto previous = std::chrono::steady_clock::now();
        double pushAccumulator = 0.0;
        constexpr double pushTickSeconds = 1.0 / 35.0;
        for (;;) {
            const auto input = video.pollInput();
            if (input.quit) break;
            const auto now = std::chrono::steady_clock::now();
            double dt = std::chrono::duration<double>(now - previous).count();
            previous = now;
            if (dt > 0.05) dt = 0.05;
            auto& player = world.player();
            constexpr double turnSpeed = 2.2, moveSpeed = 2.1;
            if (input.turnLeft) player.angleRadians -= turnSpeed * dt;
            if (input.turnRight) player.angleRadians += turnSpeed * dt;
            const double dirX = std::cos(player.angleRadians), dirY = std::sin(player.angleRadians);
            const double rightX = -dirY, rightY = dirX;
            double moveX = 0.0, moveY = 0.0;
            if (input.forward) { moveX += dirX; moveY += dirY; }
            if (input.backward) { moveX -= dirX; moveY -= dirY; }
            if (input.strafeRight) { moveX += rightX; moveY += rightY; }
            if (input.strafeLeft) { moveX -= rightX; moveY -= rightY; }
            const double len = std::hypot(moveX, moveY);
            if (len > 0.0) {
                moveX = moveX / len * moveSpeed * dt; moveY = moveY / len * moveSpeed * dt;
                world.tryMovePlayer(moveX, 0.0, true); world.tryMovePlayer(0.0, moveY, true);
            }
            if (input.actionPressed) {
                int dx = 0, dy = 0; cardinalFromAngle(player.angleRadians, dx, dy);
                world.beginPush(static_cast<int>(std::floor(player.x)) + dx, static_cast<int>(std::floor(player.y)) + dy, dx, dy);
            }
            pushAccumulator += dt;
            while (pushAccumulator >= pushTickSeconds) { world.tickPushables(); ++pushTick; pushAccumulator -= pushTickSeconds; }
            if (trace) {
                unsigned moving = 0;
                for (const auto& p : world.pushables()) if (p.moving()) ++moving;
                const std::uint16_t keys = (input.forward ? 1 : 0) | (input.backward ? 2 : 0) |
                    (input.turnLeft ? 4 : 0) | (input.turnRight ? 8 : 0) |
                    (input.strafeLeft ? 16 : 0) | (input.strafeRight ? 32 : 0) |
                    (input.actionPressed ? 64 : 0);
                if (!n3d::re::preview::record(trace, {frameNumber, pushTick, player.x,
                      player.y, player.angleRadians, keys,
                      static_cast<unsigned>(world.pushables().size()), moving}))
                    throw std::runtime_error("Failed to record preview frame");
            }
            ++frameNumber;
            raycaster.render(fb, world); video.present(fb, data.palette()); SDL_Delay(1);
        }
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "nitemare3d: " << e.what() << '\n';
        return 1;
    }
}
