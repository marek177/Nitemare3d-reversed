#pragma once

#include "formats/Pcx8.hpp"

#include <array>
#include <cstdint>
#include <vector>

namespace n3d {

class Framebuffer {
public:
    Framebuffer(int width, int height);

    int width() const { return width_; }
    int height() const { return height_; }
    std::vector<std::uint8_t>& indices() { return indices_; }
    const std::vector<std::uint8_t>& indices() const { return indices_; }

    void clear(std::uint8_t colorIndex);
    void setPixel(int x, int y, std::uint8_t colorIndex);
    void fillRect(int x, int y, int w, int h, std::uint8_t colorIndex);
    std::vector<std::uint32_t> toArgb8888(const std::array<Rgb8, 256>& palette) const;

private:
    int width_{};
    int height_{};
    std::vector<std::uint8_t> indices_;
};

} // namespace n3d
