#include "formats/FliFile.hpp"
#include "formats/BinaryIO.hpp"

#include <stdexcept>

namespace n3d {

FliHeader FliFile::readHeader(const std::filesystem::path& path) {
    const auto bytes = io::readFile(path);
    if (bytes.size() < 128) {
        throw std::runtime_error("FLI/FLC file too small: " + path.string());
    }

    FliHeader h;
    h.fileSize = io::readU32LE(bytes, 0);
    h.magic = io::readU16LE(bytes, 4);
    h.frames = io::readU16LE(bytes, 6);
    h.width = io::readU16LE(bytes, 8);
    h.height = io::readU16LE(bytes, 10);
    h.depth = io::readU16LE(bytes, 12);
    h.flags = io::readU16LE(bytes, 14);
    h.speedRaw = io::readU32LE(bytes, 16);
    return h;
}

} // namespace n3d
