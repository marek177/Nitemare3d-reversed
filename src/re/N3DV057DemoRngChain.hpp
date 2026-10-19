#pragma once
#include <array>
#include <cstdint>

namespace n3d::re::v057 {

struct RngEntry {
    std::uint8_t ordinal;
    std::uint32_t callsite;
    std::uint32_t stateAfter;
    std::uint16_t result;
};

inline constexpr std::array<RngEntry,18> kDos20DemoRngPrefix{{
    {1,0x56A6,0x0029E2C0u,41},
    {2,0x85AD,0xC823F683u,18467},
    {3,0xA047,0x18BE873Au,6334},
    {4,0xA047,0xE7847115u,26500},
    {5,0xA047,0xCAE1DF84u,19169},
    {6,0xA047,0x3D6C1037u,15724},
    {7,0xA047,0x2CD60A1Eu,11478},
    {8,0xA047,0x72AE7869u,29358},
    {9,0x5582,0x69521988u,26962},
    {10,0x5582,0xDF90722Bu,24464},
    {11,0x56A6,0x1649B442u,5705},
    {12,0x573F,0x6DF109FDu,28145},
    {13,0x56A6,0xDAF1B4CCu,23281},
    {14,0x56A6,0xC1BBB05Fu,16827},
    {15,0x85AD,0xA6E9C9A6u,9961},
    {16,0x9FE3,0x81EB59D1u,491},
    {17,0x9FE3,0x0BB31550u,2995},
    {18,0x9FE3,0xAEA69ED3u,11942},
}};

constexpr std::uint32_t nextState(std::uint32_t s) noexcept {
    return s * 214013u + 2531011u;
}
constexpr std::uint16_t result15(std::uint32_t s) noexcept {
    return static_cast<std::uint16_t>((s >> 16u) & 0x7FFFu);
}

constexpr bool validatesChain() noexcept {
    std::uint32_t before = 1u;
    for (const auto& e : kDos20DemoRngPrefix) {
        const auto after = nextState(before);
        if (after != e.stateAfter || result15(after) != e.result) return false;
        before = after;
    }
    return true;
}

inline constexpr std::uint8_t kIndependentlyReproducedPrefixLength = 8;
inline constexpr std::uint8_t kIndependentOriginalRuns = 2;
inline constexpr bool kEntries9To18IndependentlyReproduced = false;
inline constexpr bool kCompleteDemoRngLedgerClosed = false;

static_assert(validatesChain());

} // namespace n3d::re::v057
