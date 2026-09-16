#include "formats/DemoFile.hpp"
#include "formats/BinaryIO.hpp"

#include <stdexcept>

namespace n3d {

DemoFile DemoFile::load(const std::filesystem::path& path) {
    const auto bytes = io::readFile(path);
    if (bytes.size() < 6 || (bytes.size() - 6) % 8 != 0) {
        throw std::runtime_error("Unexpected DEMO file size/layout: " + path.string());
    }

    DemoFile out;
    for (std::size_t i = 0; i < 3; ++i) {
        out.rawHeaderWords_[i] = io::readU16LE(bytes, i * 2);
    }

    std::uint32_t previousTick = 0;
    bool first = true;
    for (std::size_t pos = 6; pos < bytes.size(); pos += 8) {
        DemoRecord rec;
        rec.rawInputState = io::readU32LE(bytes, pos);
        rec.tick = io::readU32LE(bytes, pos + 4);
        if (!first && rec.tick < previousTick) {
            out.ticksAreMonotonic_ = false;
        }
        previousTick = rec.tick;
        first = false;
        out.records_.push_back(rec);
    }
    return out;
}

} // namespace n3d
