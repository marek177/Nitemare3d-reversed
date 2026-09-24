#include "formats/DemoFile.hpp"

#include <cassert>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <string>
#include <vector>

namespace {

std::filesystem::path writeFixture(const std::vector<std::uint8_t>& bytes) {
    const auto stamp = std::to_string(
        std::filesystem::file_time_type::clock::now().time_since_epoch().count());
    const auto path = std::filesystem::temp_directory_path() /
                      ("nitemare3d_demo_file_test_" + stamp + ".demo");
    std::ofstream out(path, std::ios::binary);
    assert(out.good());
    out.write(reinterpret_cast<const char*>(bytes.data()),
              static_cast<std::streamsize>(bytes.size()));
    assert(out.good());
    return path;
}

} // namespace

int main() {
    // Header (10,5,20), then three 8-byte records:
    // event, 16-bit input mask, padding byte, render-generation index.
    const std::vector<std::uint8_t> bytes = {
        0x0A, 0x00, 0x05, 0x00, 0x14, 0x00,
        0x1B, 0x02, 0x00, 0x00, 0x13, 0x00, 0x00, 0x00,
        0x20, 0x00, 0x02, 0xA5, 0x13, 0x00, 0x00, 0x00,
        0x0D, 0x80, 0x00, 0x00, 0x14, 0x00, 0x00, 0x00,
    };
    const auto path = writeFixture(bytes);

    const auto demo = n3d::DemoFile::load(path);
    std::filesystem::remove(path);

    assert(demo.rawHeaderWords()[0] == 10);
    assert(demo.rawHeaderWords()[1] == 5);
    assert(demo.rawHeaderWords()[2] == 20);
    assert(demo.records().size() == 3);
    assert(demo.renderGenerationsAreMonotonic());

    const auto& first = demo.records()[0];
    assert(first.eventByte == 0x1B);
    assert(first.inputMask == 0x0002);
    assert(first.paddingByte == 0x00);
    assert(first.renderGeneration == 19);

    const auto& second = demo.records()[1];
    assert(second.eventByte == 0x20);
    assert(second.inputMask == 0x0200);
    assert(second.paddingByte == 0xA5);
    assert(second.renderGeneration == 19);

    const auto& third = demo.records()[2];
    assert(third.eventByte == 0x0D);
    assert(third.inputMask == 0x0080);
    assert(third.renderGeneration == 20);

    std::size_t cursor = 0;
    assert(demo.dispatchOneDueRecordAtGeneration(18, cursor) == nullptr);
    assert(cursor == 0);

    // A call consumes no more than one record, even when multiple records
    // share the same due generation.
    assert(demo.dispatchOneDueRecordAtGeneration(19, cursor) == &first);
    assert(cursor == 1);
    assert(demo.dispatchOneDueRecordAtGeneration(19, cursor) == &second);
    assert(cursor == 2);
    assert(demo.dispatchOneDueRecordAtGeneration(19, cursor) == nullptr);
    assert(cursor == 2);

    assert(demo.dispatchOneDueRecordAtGeneration(20, cursor) == &third);
    assert(cursor == 3);
    assert(demo.dispatchOneDueRecordAtGeneration(20, cursor) == nullptr);
    assert(cursor == 3);
}
