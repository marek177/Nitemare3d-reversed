#include "renderer/Win16WallRasterCore.hpp"

#include <array>
#include <cassert>
#include <cstdint>
#include <vector>

using nitemare3d::re::win16::VecRecord;

static VecRecord makeVec(std::uint8_t orientation,
                         std::int16_t x1, std::int16_t y1,
                         std::int16_t x2, std::int16_t y2) {
    VecRecord vec{};
    vec.orientation = orientation;
    vec.x1 = x1;
    vec.y1 = y1;
    vec.x2 = x2;
    vec.y2 = y2;
    return vec;
}

int main() {
    using namespace nitemare3d::re::win16;

    static_assert(sizeof(VecRecord) == 28);
    static_assert(offsetof(VecRecord, x1) == 0x0C);

    const auto tables = makeWallSamplingTables(200);
    assert(tables.step16_16[1] == 0x400000U);
    assert(tables.step16_16[2] == 0x200000U);
    assert(tables.step16_16[64] == 0x10000U);
    assert(tables.step16_16[512] == 0);
    assert(clippedStart16_16(tables, 200) == 0);
    assert(clippedStart16_16(tables, 400) == (16U << 16U));
    assert(clippedStart16_16(tables, 201) == 10433U);

    const auto old0 = makeVec(0, 10, 10, 20, 20);
    assert(ownerConflictReplaces(old0, makeVec(2, 11, 9, 21, 19)));
    assert(!ownerConflictReplaces(old0, makeVec(2, 10, 9, 21, 19)));
    assert(ownerConflictReplaces(old0, makeVec(3, 9, 9, 19, 19)));

    const auto old1 = makeVec(1, 10, 10, 20, 20);
    assert(ownerConflictReplaces(old1, makeVec(2, 11, 11, 21, 21)));
    assert(ownerConflictReplaces(old1, makeVec(3, 9, 11, 19, 21)));

    const auto old2 = makeVec(2, 10, 10, 20, 20);
    assert(ownerConflictReplaces(old2, makeVec(0, 9, 9, 21, 19)));
    assert(ownerConflictReplaces(old2, makeVec(1, 9, 21, 21, 21)));

    const auto old3 = makeVec(3, 10, 10, 20, 20);
    assert(ownerConflictReplaces(old3, makeVec(0, 9, 9, 19, 19)));
    assert(ownerConflictReplaces(old3, makeVec(1, 9, 11, 19, 21)));
    assert(!ownerConflictReplaces(old3, makeVec(3, 9, 11, 19, 21)));

    auto texVec = makeVec(0, 100, 100, 164, 100);
    texVec.screenX1 = 8;
    texVec.screenX2 = 31;
    assert(selectTextureU(texVec, 20, 67, 64) == 3); // ordinary masked coordinate
    texVec.flags = 0x08;
    assert(selectTextureU(texVec, 8, 67, 64) == 3);  // flag bypasses edge correction
    texVec.flags = 0;
    assert(selectTextureU(texVec, 30, 3, 64) == 63); // orientation 0 far-end sentinel
    assert(selectTextureU(texVec, 8, -100, 64) == 0); // orientation 0 start correction

    texVec.orientation = 1;
    assert(selectTextureU(texVec, 8, -1, 64) == 0);  // orientation 1 near-start clip
    assert(selectTextureU(texVec, 30, 64, 64) == 63); // orientation 1 far-end clip

    texVec.orientation = 2;
    texVec.y1 = 100;
    texVec.y2 = 164;
    assert(selectTextureU(texVec, 30, 3, 64) == 63); // orientation 2 far-end sentinel

    texVec.orientation = 3;
    texVec.renderClass = 2;
    assert(selectTextureU(texVec, 8, 0, 64) == 63);  // class 2 start sentinel
    assert(selectTextureU(texVec, 30, -100, 64) == 0); // class 2 negative-end correction

    texVec.orientation = 0;
    assert(selectTextureU(texVec, 8, 64, 64) == 63); // class 2 horizontal special case

    std::array<std::uint8_t, 64> textureColumn{};
    for (std::size_t i = 0; i < textureColumn.size(); ++i) {
        textureColumn[i] = static_cast<std::uint8_t>(i);
    }
    std::vector<std::uint8_t> framebuffer(320U * 200U, 0xEE);
    assert(drawWinGIndexedColumn(framebuffer, 320, 8, 4, 4,
                                 textureColumn, 0, 0x10000U));
    assert(framebuffer[4U * 320U + 8U] == 0);
    assert(framebuffer[5U * 320U + 8U] == 1);
    assert(framebuffer[6U * 320U + 8U] == 2);
    assert(framebuffer[7U * 320U + 8U] == 3);

    std::array<std::uint8_t, 256> remap{};
    for (std::size_t i = 0; i < remap.size(); ++i) {
        remap[i] = static_cast<std::uint8_t>(255U - i);
    }
    assert(drawWinGIndexedColumn(framebuffer, 320, 9, 4, 2,
                                 textureColumn, 0, 0x10000U, &remap));
    assert(framebuffer[4U * 320U + 9U] == 255);
    assert(framebuffer[5U * 320U + 9U] == 254);

    const auto beforeInvalid = framebuffer;
    assert(!drawWinGIndexedColumn(framebuffer, 320, 10, 4, 2,
                                  textureColumn, 63U << 16U, 0x10000U));
    assert(framebuffer == beforeInvalid);
    assert(!drawWinGIndexedColumn(framebuffer, 320, 320, 4, 1,
                                  textureColumn, 0, 0x10000U));
}
