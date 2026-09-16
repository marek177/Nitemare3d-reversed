#pragma once

#include <array>
#include <cstdint>
#include <filesystem>
#include <vector>

namespace n3d {

struct DemoRecord {
    std::uint32_t rawInputState{}; // interpretation/bit mapping still under RE
    std::uint32_t tick{};          // monotonic in the supplied DEMO.1-.3
};

class DemoFile {
public:
    static DemoFile load(const std::filesystem::path& path);

    const std::array<std::uint16_t, 3>& rawHeaderWords() const { return rawHeaderWords_; }
    const std::vector<DemoRecord>& records() const { return records_; }
    bool ticksAreMonotonic() const { return ticksAreMonotonic_; }

private:
    std::array<std::uint16_t, 3> rawHeaderWords_{};
    std::vector<DemoRecord> records_;
    bool ticksAreMonotonic_{true};
};

} // namespace n3d
