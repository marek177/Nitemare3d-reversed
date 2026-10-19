#include "formats/ImgArchive.hpp"
#include "renderer/ImgTextureSampler.hpp"
#include "renderer/Raycaster.hpp"

#include <array>
#include <cassert>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <vector>

namespace {
void putU32(std::vector<std::uint8_t>& v, unsigned offset, std::uint32_t value) {
    for (unsigned j = 0; j < 4; ++j) {
        v[offset + j] = static_cast<std::uint8_t>(value >> (j * 8));
    }
}
}

int main() {
    constexpr std::uint32_t base = 0xBC00u;
    // Synthetic archive with a 2x3 frame; pixels are COLUMN-major.
    std::vector<std::uint8_t> bytes(base + 10 + 6, 0);
    putU32(bytes, 4, base);
    putU32(bytes, 5 * 4, base); // WALL 5
    putU32(bytes, 0x400 + 24 * 4, base); // PUSH object 24
    bytes[base] = 2;
    bytes[base + 1] = 3;
    const std::array<std::uint8_t, 6> sample{41,42,43,51,52,0x1F};
    for (unsigned i = 0; i < sample.size(); ++i) bytes[base + 10 + i] = sample[i];

    const auto path = std::filesystem::temp_directory_path() / "n3d_img_texture_sampler_test.img";
    {
        std::ofstream file(path, std::ios::binary);
        file.write(reinterpret_cast<const char*>(bytes.data()),
                   static_cast<std::streamsize>(bytes.size()));
        assert(file.good());
    }
    const auto bank = n3d::ImgArchive::load(path);
    std::filesystem::remove(path);

    auto* wall = n3d::img::imageForSlot(bank, n3d::img::RenderSlot::Wall, 5);
    auto* sprite = n3d::img::imageForSlot(bank, n3d::img::RenderSlot::Object, 24);
    assert(wall && wall == sprite);
    assert(!n3d::img::imageForSlot(bank, n3d::img::RenderSlot::Wall, 0));
    assert(!n3d::img::imageForSlot(bank, n3d::img::RenderSlot::Object, 25));
    assert(n3d::img::pixelAtColumnMajor(*wall, 0, 0) == 41);
    assert(n3d::img::pixelAtColumnMajor(*wall, 0, 2) == 43);
    assert(n3d::img::pixelAtColumnMajor(*wall, 1, 0) == 51);
    assert(n3d::img::pixelAtColumnMajor(*wall, 1, 1) == 52);
    assert(n3d::img::pixelAtColumnMajor(*wall, 1, 2) == n3d::img::kSpriteTransparentIndex);
    assert(n3d::img::sampleImage(*wall, 0.0, 0.0) == 41);
    assert(n3d::img::sampleImage(*wall, 0.8, 0.5) == 52);
    assert(n3d::img::sampleImage(*wall, 1.0, 1.0) == n3d::img::kSpriteTransparentIndex);
    assert(n3d::img::sampleImage(*wall, -1.0, -0.5) == 41);

    // The screenshot must actually change when a valid IMG texture is supplied.
    // Use real definition-parser contracts but fully synthetic MAP/IMG assets.
    const auto defs = std::filesystem::temp_directory_path() / "n3d_img_texture_wall_test.def";
    {
        std::ofstream out(defs);
        out << "0000 0 floor FLOOR Empty\n0005 5 tex WALL Solid\n";
        assert(out.good());
    }
    const auto wallDefs = n3d::DefinitionTable::load(defs);
    std::filesystem::remove(defs);
    n3d::LevelMap map{};
    for (auto& c : map.cells) c.wall = 5;
    // LevelMap::at() is const; construct its editable cells through the array.
    for (unsigned y = 2; y <= 6; ++y)
        for (unsigned x = 2; x <= 5; ++x) map.cells[y * 64u + x].wall = 0;
    map.cells[4u * 64u + 4u].object = 2; // START facing east
    const auto state = n3d::LevelState::create(map, {}, wallDefs);
    n3d::Framebuffer plain(64,48), textured(64,48);
    n3d::Raycaster fallback;
    n3d::Raycaster fromImage(&bank);
    fallback.render(plain, state);
    fromImage.render(textured, state);
    assert(plain.indices() != textured.indices());
    // The wall straight ahead is WALL 5, and its center texel can never equal
    // the original placeholder 37/29 because we stored {41,42,43,51,52,31}.
    assert(plain.indices()[24 * 64 + 32] != textured.indices()[24 * 64 + 32]);
    return 0;
}
