#include "renderer/Framebuffer.hpp"

#include <algorithm>
#include <stdexcept>

namespace n3d {

Framebuffer::Framebuffer(int width, int height)
    : width_(width), height_(height), indices_(static_cast<std::size_t>(width) * height) {
    if (width <= 0 || height <= 0) {
        throw std::runtime_error("Framebuffer dimensions must be positive");
    }
}

void Framebuffer::clear(std::uint8_t colorIndex) {
    std::fill(indices_.begin(), indices_.end(), colorIndex);
}

void Framebuffer::setPixel(int x, int y, std::uint8_t colorIndex) {
    if (x < 0 || y < 0 || x >= width_ || y >= height_) {
        return;
    }
    indices_[static_cast<std::size_t>(y) * width_ + x] = colorIndex;
}

void Framebuffer::fillRect(int x, int y, int w, int h, std::uint8_t colorIndex) {
    for (int yy = 0; yy < h; ++yy) {
        for (int xx = 0; xx < w; ++xx) {
            setPixel(x + xx, y + yy, colorIndex);
        }
    }
}

std::vector<std::uint32_t> Framebuffer::toArgb8888(const std::array<Rgb8, 256>& palette) const {
    std::vector<std::uint32_t> out(indices_.size());
    for (std::size_t i = 0; i < indices_.size(); ++i) {
        const auto c = palette[indices_[i]];
        out[i] = 0xFF000000u |
                 (static_cast<std::uint32_t>(c.r) << 16u) |
                 (static_cast<std::uint32_t>(c.g) << 8u) |
                 static_cast<std::uint32_t>(c.b);
    }
    return out;
}

} // namespace n3d
