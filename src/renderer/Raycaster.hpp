#pragma once

#include "game/LevelState.hpp"
#include "renderer/Framebuffer.hpp"

#include <vector>

namespace n3d {

// Playable verification renderer. The grid traversal and projection are a
// temporary reference implementation while the exact NITE3W.EXE ray-column
// routine is being reconstructed. It intentionally consumes the real MAP data
// and LevelState so gameplay systems can be tested now.
class Raycaster {
public:
    void render(Framebuffer& fb, const LevelState& level);

private:
    std::vector<double> depthBuffer_;
    void renderPushables(Framebuffer& fb, const LevelState& level,
                         double dirX, double dirY, double planeX, double planeY);
};

} // namespace n3d
