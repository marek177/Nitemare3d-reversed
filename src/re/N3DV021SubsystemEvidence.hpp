#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

namespace n3d::re::v021 {

enum class Confidence : std::uint8_t {
    Confirmed,
    Strong,
    Open
};

enum class Subsystem : std::uint8_t {
    Guard,
    Player,
    Projectile,
    InputAction,
    SecretPanel,
    Renderer,
    ObjectCandidate,
    Unknown
};

struct SubsystemAnchor {
    std::uint16_t offset;
    Subsystem subsystem;
    Confidence confidence;
};

inline constexpr std::array<SubsystemAnchor, 12> kDos20SubsystemAnchors = {{
    {0x5F26, Subsystem::Guard, Confidence::Strong},
    {0x59F0, Subsystem::Guard, Confidence::Confirmed},
    {0x6914, Subsystem::Player, Confidence::Confirmed},
    {0x6378, Subsystem::Player, Confidence::Confirmed},
    {0x6488, Subsystem::Player, Confidence::Confirmed},
    {0x8230, Subsystem::Projectile, Confidence::Confirmed},
    {0x8142, Subsystem::Projectile, Confidence::Confirmed},
    {0x89A2, Subsystem::InputAction, Confidence::Confirmed},
    {0x8F12, Subsystem::InputAction, Confidence::Confirmed},
    {0x0AEA, Subsystem::SecretPanel, Confidence::Confirmed},
    {0xB2D4, Subsystem::Renderer, Confidence::Confirmed},
    {0x0E50, Subsystem::ObjectCandidate, Confidence::Open}
}};

constexpr Subsystem classifySubsystemAddress(std::uint16_t offset) noexcept {
    for (const auto& anchor : kDos20SubsystemAnchors) {
        if (anchor.offset == offset) {
            return anchor.subsystem;
        }
    }
    return Subsystem::Unknown;
}

constexpr Confidence confidenceForAddress(std::uint16_t offset) noexcept {
    for (const auto& anchor : kDos20SubsystemAnchors) {
        if (anchor.offset == offset) {
            return anchor.confidence;
        }
    }
    return Confidence::Open;
}

struct TraceOrderCheck {
    bool firstSeen;
    bool secondSeen;
    bool orderSatisfied;

    constexpr bool decisive() const noexcept {
        return firstSeen && secondSeen;
    }
};

TraceOrderCheck verifyRelativeOrder(const std::uint16_t* trace,
                                    std::size_t count,
                                    std::uint16_t first,
                                    std::uint16_t second) noexcept;

struct RuntimeRegion {
    std::uint16_t base;
    std::uint16_t size;
    Confidence confidence;
};

inline constexpr RuntimeRegion kProjectilePool{
    0x41B6, 0x0150, Confidence::Confirmed
};

inline constexpr RuntimeRegion kGuardPoolBase{
    0x264E, 0x001A, Confidence::Strong
};

inline constexpr RuntimeRegion kSecretPanelRecord{
    0x34F6, 0x000E, Confidence::Confirmed
};

inline constexpr RuntimeRegion kSpanPool{
    0x4D6E, 0x038E, Confidence::Confirmed
};

struct EvidenceInvariant {
    const char* name;
    Confidence confidence;
};

inline constexpr EvidenceInvariant kProjectileBeforeFire{
    "projectile scheduler precedes action/FIRE path in the audited order",
    Confidence::Strong
};

inline constexpr EvidenceInvariant kObjectMutationOrder{
    "exact OBJECT iteration/mutation/deactivation order",
    Confidence::Open
};

inline constexpr EvidenceInvariant kExactFastMainOrder{
    "exact FAST/MAIN subsystem interleaving",
    Confidence::Open
};

}  // namespace n3d::re::v021
