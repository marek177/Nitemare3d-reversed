#pragma once

#include "game/LevelState.hpp"
#include "formats/ImgArchive.hpp"
#include "renderer/Framebuffer.hpp"

#include <vector>

namespace n3d {

// Playable verification renderer. This grid-DDA implementation intentionally
// consumes the real MAP data and LevelState so gameplay systems can be tested
// now, but it is not the recovered NITE3W.EXE renderer. The original traverses
// sorted wall-vector lists, assigns projected spans to screen columns, and then
// rasterizes those spans. See analysis/nite3w_renderer.md and
// OriginalRendererFacts.hpp.
class Raycaster {
public:
    explicit Raycaster(const ImgArchive* imageBank = nullptr) : imageBank_(imageBank) {}
    void render(Framebuffer& fb, const LevelState& level);

private:
    const ImgArchive* imageBank_{};
    std::vector<double> depthBuffer_;
    void renderPushables(Framebuffer& fb, const LevelState& level,
                         double dirX, double dirY, double planeX, double planeY);
};

} // namespace n3d
