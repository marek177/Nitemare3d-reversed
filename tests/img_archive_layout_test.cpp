#include "formats/ImgArchive.hpp"

#include <array>
#include <cassert>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <vector>

namespace {

void writeU32(std::vector<std::uint8_t>& bytes, std::size_t offset, std::uint32_t value) {
    bytes[offset + 0] = static_cast<std::uint8_t>(value);
    bytes[offset + 1] = static_cast<std::uint8_t>(value >> 8u);
    bytes[offset + 2] = static_cast<std::uint8_t>(value >> 16u);
    bytes[offset + 3] = static_cast<std::uint8_t>(value >> 24u);
}

void writeSequence(std::vector<std::uint8_t>& bytes,
                   std::size_t offset,
                   std::uint16_t interval,
                   std::uint8_t frameCount,
                   std::uint8_t altFlag) {
    bytes[offset + 0] = static_cast<std::uint8_t>(interval);
    bytes[offset + 1] = static_cast<std::uint8_t>(interval >> 8u);
    bytes[offset + 2] = frameCount;
    bytes[offset + 3] = altFlag;
}

} // namespace

int main() {
    using namespace n3d::img;

    static_assert(sequenceDefinitionOffset(SequenceBank::LowSelector, 1) == 0x0062);
    static_assert(sequenceDefinitionOffset(SequenceBank::LowSelector, 22) == 0x07C4);
    static_assert(sequenceDefinitionOffset(SequenceBank::LowSelector, 23) == 0x081E);
    static_assert(sequenceDefinitionOffset(SequenceBank::HighSelector, 0) == 0x5A08);
    static_assert(sequenceDefinitionOffset(SequenceBank::HighSelector, 255) == 0xB3AE);
    static_assert(sequenceDefinitionOverlapsImageDirectories(SequenceBank::LowSelector, 22));
    static_assert(!sequenceDefinitionOverlapsImageDirectories(SequenceBank::LowSelector, 23));
    static_assert(!sequenceDefinitionOverlapsImageDirectories(SequenceBank::HighSelector, 0));

    constexpr std::size_t imageOffset = 0xBC00;
    std::vector<std::uint8_t> bytes(imageOffset + 11, 0);
    writeU32(bytes, 4, static_cast<std::uint32_t>(imageOffset));
    writeU32(bytes, kObjectImageDirectoryOffset + 5 * 4,
             static_cast<std::uint32_t>(imageOffset));

    // A 1x1 frame: 10-byte header followed by one pixel.
    bytes[imageOffset] = 1;
    bytes[imageOffset + 1] = 1;
    bytes[imageOffset + 10] = 0x7F;

    writeSequence(bytes, sequenceDefinitionOffset(SequenceBank::LowSelector, 23), 300, 2, 1);
    writeSequence(bytes, sequenceDefinitionOffset(SequenceBank::HighSelector, 0), 100, 3, 0);

    const auto path = std::filesystem::temp_directory_path() / "n3d_img_archive_layout_test.img";
    {
        std::ofstream out(path, std::ios::binary);
        out.write(reinterpret_cast<const char*>(bytes.data()),
                  static_cast<std::streamsize>(bytes.size()));
        assert(out.good());
    }

    const auto archive = n3d::ImgArchive::load(path);
    std::filesystem::remove(path);

    assert(archive.wallSlotOffsets().size() == kImageIndexEntries);
    assert(archive.objectSlotOffsets().size() == kImageIndexEntries);
    assert(archive.slotOffsets().size() == kImageIndexEntries);
    assert(archive.wallSlotOffsets()[1] == imageOffset);
    assert(archive.objectSlotOffsets()[5] == imageOffset);
    assert(archive.frames().size() == 1);
    assert(archive.frameAtExactOffset(static_cast<std::uint32_t>(imageOffset)) == 0);

    assert(archive.hasSequenceDefinitions());
    const auto* low = archive.sequenceDefinition(SequenceBank::LowSelector, 23);
    const auto* high = archive.sequenceDefinition(SequenceBank::HighSelector, 0);
    assert(low && low->intervalMs() == 300 && low->frameCount() == 2 &&
           low->alternateTableFlag() == 1);
    assert(high && high->intervalMs() == 100 && high->frameCount() == 3 &&
           high->alternateTableFlag() == 0);
}
