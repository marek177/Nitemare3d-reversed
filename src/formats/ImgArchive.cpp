#include "formats/ImgArchive.hpp"
#include "formats/BinaryIO.hpp"

#include <algorithm>
#include <span>
#include <stdexcept>

namespace n3d {

ImgArchive ImgArchive::load(const std::filesystem::path& path) {
    const auto bytes = io::readFile(path);
    if (bytes.size() < 8) {
        throw std::runtime_error("IMG file too small: " + path.string());
    }

    ImgArchive out;
    out.reservedDword_ = io::readU32LE(bytes, 0);
    out.firstDataOffset_ = io::readU32LE(bytes, 4);
    if (out.firstDataOffset_ < 8 || out.firstDataOffset_ > bytes.size() ||
        (out.firstDataOffset_ - 4) % 4 != 0) {
        throw std::runtime_error("IMG first data offset is invalid: " + path.string());
    }

    const std::size_t slotCount = (out.firstDataOffset_ - 4) / 4;
    out.slotOffsets_.reserve(slotCount);
    for (std::size_t i = 0; i < slotCount; ++i) {
        out.slotOffsets_.push_back(io::readU32LE(bytes, 4 + i * 4));
    }

    std::size_t pos = out.firstDataOffset_;
    while (pos < bytes.size()) {
        if (pos + 10 > bytes.size()) {
            throw std::runtime_error("Truncated IMG frame header: " + path.string());
        }

        ImgFrame frame;
        frame.fileOffset = static_cast<std::uint32_t>(pos);
        frame.width = bytes[pos];
        frame.height = bytes[pos + 1];
        std::copy_n(bytes.begin() + static_cast<std::ptrdiff_t>(pos + 2), 8, frame.metadata.begin());

        const std::size_t pixelCount = static_cast<std::size_t>(frame.width) * frame.height;
        if (pos + 10 + pixelCount > bytes.size()) {
            throw std::runtime_error("IMG frame extends past EOF: " + path.string());
        }
        frame.pixels.assign(bytes.begin() + static_cast<std::ptrdiff_t>(pos + 10),
                            bytes.begin() + static_cast<std::ptrdiff_t>(pos + 10 + pixelCount));

        const std::size_t index = out.frames_.size();
        out.exactOffsetToFrame_.emplace(frame.fileOffset, index);
        out.frames_.push_back(std::move(frame));
        pos += 10 + pixelCount;
    }

    return out;
}

std::optional<std::size_t> ImgArchive::frameAtExactOffset(std::uint32_t offset) const {
    const auto it = exactOffsetToFrame_.find(offset);
    if (it == exactOffsetToFrame_.end()) {
        return std::nullopt;
    }
    return it->second;
}

} // namespace n3d
