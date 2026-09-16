#pragma once

#include <cstdint>
#include <filesystem>

namespace n3d {

struct FliHeader {
    std::uint32_t fileSize{};
    std::uint16_t magic{};
    std::uint16_t frames{};
    std::uint16_t width{};
    std::uint16_t height{};
    std::uint16_t depth{};
    std::uint16_t flags{};
    std::uint32_t speedRaw{};
};

class FliFile {
public:
    static FliHeader readHeader(const std::filesystem::path& path);
};

} // namespace n3d
