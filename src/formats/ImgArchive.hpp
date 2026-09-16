#pragma once

#include <array>
#include <cstdint>
#include <filesystem>
#include <optional>
#include <unordered_map>
#include <vector>

namespace n3d {

struct ImgFrame {
    std::uint32_t fileOffset{};
    std::uint8_t width{};
    std::uint8_t height{};
    std::array<std::uint8_t, 8> metadata{};
    std::vector<std::uint8_t> pixels;
};

class ImgArchive {
public:
    static ImgArchive load(const std::filesystem::path& path);

    std::uint32_t reservedDword() const { return reservedDword_; }
    std::uint32_t firstDataOffset() const { return firstDataOffset_; }
    const std::vector<std::uint32_t>& slotOffsets() const { return slotOffsets_; }
    const std::vector<ImgFrame>& frames() const { return frames_; }

    std::optional<std::size_t> frameAtExactOffset(std::uint32_t offset) const;

private:
    std::uint32_t reservedDword_{};
    std::uint32_t firstDataOffset_{};
    std::vector<std::uint32_t> slotOffsets_;
    std::vector<ImgFrame> frames_;
    std::unordered_map<std::uint32_t, std::size_t> exactOffsetToFrame_;
};

} // namespace n3d
