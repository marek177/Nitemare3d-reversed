#include "re/n3d_v018_facts.h"

#include <array>
#include <cstdint>

namespace n3d::re::v018 {

struct SecretPanelRecordLayout {
    static constexpr std::size_t kRecordSize = N3D_V018_SECRET_PANEL_RECORD_SIZE;
    static constexpr std::size_t kVec0 = 0x00;
    static constexpr std::size_t kVec1 = 0x02;
    static constexpr std::size_t kVec2 = 0x04;
    static constexpr std::size_t kVec3 = 0x06;
    static constexpr std::size_t kMapOffset = 0x08;
    static constexpr std::size_t kMapSegment = 0x0A;
    static constexpr std::size_t kState = 0x0C;
};

struct ProjectilePoolLayout {
    static constexpr std::size_t kSlotCount = N3D_V018_PROJECTILE_SLOT_COUNT;
    static constexpr std::size_t kSlotStride = N3D_V018_PROJECTILE_SLOT_STRIDE;
    static constexpr std::size_t kEmbeddedObject = 0x0E;
    static constexpr std::size_t kWorldX = 0x1E;
    static constexpr std::size_t kWorldY = 0x20;
};

constexpr std::array<std::uint8_t, 4> kWeaponCadence = {2, 1, 3, 1};

static_assert(SecretPanelRecordLayout::kRecordSize == 14);
static_assert(ProjectilePoolLayout::kSlotCount == 8);
static_assert(ProjectilePoolLayout::kSlotStride == 42);
static_assert(kWeaponCadence[0] == 2 && kWeaponCadence[2] == 3);

}  // namespace n3d::re::v018
