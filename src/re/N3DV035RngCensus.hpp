#pragma once

#include "re/N3DV020VerificationHarness.hpp"
#include "re/N3DV026GuardRngCoupling.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>

namespace n3d::re::v035 {

// DOS v2.0 canonical UNPACKED MZ load-image only:
// length=171360, SHA256=e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297
// 22 literal opcode 9A A0 01 BA 0F occurrences in the complete load image.
// At 8860/886C/887C, original 87D8 dispatcher uses CS jump-table 882E,
// proving those bytes are instruction entry points, not embedded data.
inline constexpr std::uint16_t kDamageDispatcher = 0x87D8;
inline constexpr std::uint16_t kDamageJumpInstruction = 0x8829;
inline constexpr std::uint16_t kDamageJumpTable = 0x882E;
inline constexpr std::uint16_t kDamageCodeSegmentImageBase = 0x83D0;
inline constexpr std::uint8_t kFirstDamageClass = 0x08;
inline constexpr std::uint8_t kLastDamageClass = 0x1E;

inline constexpr std::array<std::uint16_t, 23> kDamageClassBranchTargets = {{
    0x8860, // class 08: RNG&7
    0x886C, // class 09: RNG&15
    0x886C, // class 0A: RNG&15
    0x8876, // class 0B: base>>2
    0x889D, // class 0C: base
    0x885C, // class 0D: default
    0x885C, // class 0E
    0x885C, // class 0F
    0x885C, // class 10
    0x887C, // class 11: RNG&31
    0x887C, // class 12: RNG&31
    0x887C, // class 13: RNG&31
    0x887C, // class 14: RNG&31
    0x885C, // class 15
    0x8886, // class 16: special fixed damage
    0x885C, // class 17
    0x885C, // class 18
    0x889A, // class 19: 100
    0x885C, // class 1A
    0x885C, // class 1B
    0x885C, // class 1C
    0x889D, // class 1D
    0x889D, // class 1E
}};

constexpr std::optional<std::uint16_t>
damageClassTarget(std::uint8_t cls) noexcept {
    if (cls < kFirstDamageClass || cls > kLastDamageClass)
        return std::nullopt;
    return kDamageClassBranchTargets[cls - kFirstDamageClass];
}

constexpr std::optional<std::uint16_t>
damageRngCallsite(std::uint8_t cls) noexcept {
    const auto target = damageClassTarget(cls);
    if (!target) return std::nullopt;
    const auto offset = *target;
    if (offset == 0x8860 || offset == 0x886C || offset == 0x887C)
        return offset;
    return std::nullopt;
}

constexpr std::optional<std::uint16_t>
damageRngMask(std::uint8_t cls) noexcept {
    switch (cls) {
    case 0x08: return 0x0007;
    case 0x09:
    case 0x0A: return 0x000F;
    case 0x11:
    case 0x12:
    case 0x13:
    case 0x14: return 0x001F;
    default: return std::nullopt;
    }
}

// Arithmetic of the immediate incoming-damage RNG consumer ONLY; incoming
// distance/class/difficulty/death state effects still belong to other code.
constexpr std::optional<std::uint16_t>
maskedIncomingDamage(std::uint8_t cls, std::uint16_t rngResult) noexcept {
    const auto mask = damageRngMask(cls);
    return mask ? std::optional<std::uint16_t>(rngResult & *mask) : std::nullopt;
}

inline constexpr std::uint16_t kGuardActivationDraw = 0x5582;
inline constexpr std::uint16_t kProjectedAnimationDraw = 0xB276;
inline constexpr std::uint16_t kProjectedAnimationRejectionJump = 0xB297;

// GUARD scan 5510: after strategy==0, subtype match and state 7/8, the
// RNG%8 draw at 5582 writes GUARD+06 timer, then GUARD+0B state=1.
// Call it a static writer contract, not guaranteed live AI reachability.
constexpr bool guardCanEnterState1(std::uint8_t strategy,
                                  bool subtypeMatches,
                                  std::uint8_t state) noexcept {
    return strategy == 0 && subtypeMatches && (state == 7 || state == 8);
}
constexpr std::uint16_t guardActivationTimer(std::uint16_t rngResult) noexcept {
    return static_cast<std::uint16_t>(rngResult % 8u);
}

// B22C projection animation selects OBJECT variant with RNG&7, then rejects
// empty descriptor entries (high byte of 16-bit variant token ==0).
// Every rejection consumes ANOTHER RNG draw. An eligible scene may therefore
// have multiple RNG draws in one call. Does not model clipping/callback order.
constexpr std::uint8_t projectedVariantIndex(std::uint16_t rngResult) noexcept {
    return static_cast<std::uint8_t>(rngResult & 7u);
}
constexpr bool projectedVariantRejected(std::uint16_t descriptorWord) noexcept {
    return (descriptorWord & 0xFF00u) == 0u;
}

// Resource selectors 9FE3/A047 use signed 16-bit IDIV by +7 on a nonnegative
// 15-bit RNG output. The 'cmp SI,CX; je retry' test compares 0..6 against 7,
// hence this particular comparison is provably dead for this RNG domain.
// A SEPARATE table-byte==0 check still legitimately retries RNG.
constexpr std::uint16_t resourceSelectorModulo7(std::uint16_t rngResult) noexcept {
    return static_cast<std::uint16_t>((rngResult & 0x7FFFu) % 7u);
}
constexpr bool selectorEqualToRejectedSeven(std::uint16_t rngResult) noexcept {
    return resourceSelectorModulo7(rngResult) == 7u;
}
constexpr bool resourceVariantNeedsRedraw(std::uint8_t candidateTableByte) noexcept {
    return candidateTableByte == 0u;
}

// Cross-check the two independent build-scoped tables at compile-time.
// No runtime event counting is implied.
constexpr bool censusAndConsumersAgree() noexcept {
    if (v020::kDos20DirectRngCallsites.size() !=
        v026::kDos20RngCoupling.size()) return false;
    for (std::size_t i = 0; i < v020::kDos20DirectRngCallsites.size(); ++i) {
        if (v020::kDos20DirectRngCallsites[i] !=
            v026::kDos20RngCoupling[i].callsite) return false;
    }
    return true;
}

inline constexpr bool kOriginalRuntimeVerified = false;
inline constexpr bool kIndirectRngCensusClosed = false;
inline constexpr bool kDemoSeed1FullCallOrderClosed = false;

} // namespace n3d::re::v035
