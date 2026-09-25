#include "game/InventoryRuntime.hpp"
#include "game/ProjectileRuntime.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <limits>
#include <string_view>

namespace {

// Deliberately independent of assert(): checks must also execute with NDEBUG.
struct Checks {
    std::size_t count{};
    std::size_t failures{};

    void require(bool condition, const char* message) {
        ++count;
        if (!condition) {
            if (failures < 8) std::cerr << "FAIL: " << message << '\n';
            ++failures;
        }
    }
};

void checkInventory(Checks& checks) {
    using namespace nitemare3d::game;
    // Exhaust all uint8_t masks and indices, including invalid indices 8..255.
    for (unsigned maskValue = 0; maskValue < 256; ++maskValue) {
        for (unsigned bitValue = 0; bitValue < 256; ++bitValue) {
            const auto mask = static_cast<InventoryMask>(maskValue);
            const auto bit = static_cast<std::uint8_t>(bitValue);
            const unsigned expectedBit = bitValue < 8 ? (1u << bitValue) : 0u;
            checks.require(hasInventoryBit(mask, bit) == ((maskValue & expectedBit) != 0),
                           "inventory membership / invalid index");
            auto granted = mask;
            grantInventoryBit(granted, bit);
            checks.require(granted == static_cast<InventoryMask>(maskValue | expectedBit),
                           "inventory grant preserves unrelated bits / invalid index is no-op");
        }
    }
    checks.require(!hasIdCard(0xFF, static_cast<IdCardBit>(255)),
                   "invalid ID-card enum value");
    checks.require(!hasPentagram(0xFF, static_cast<PentagramBit>(255)),
                   "invalid pentagram enum value");
    checks.require(hasAllPentagrams(0xFF) && !hasAllPentagrams(0x07),
                   "pentagram mask semantics unchanged");
}

void checkProjectiles(Checks& checks) {
    using namespace nitemare3d::game;
    constexpr auto low = std::numeric_limits<std::int32_t>::min();
    constexpr auto high = std::numeric_limits<std::int32_t>::max();
    constexpr std::array<std::int32_t, 17> coordinates{
        low, low + 9, low + 20, -21, -20, -10, -9, -1, 0,
        1, 9, 10, 20, 21, high - 20, high - 9, high
    };
    // Both axes, both argument orders, zero distances and INT32 extremes.
    // Literal thresholds intentionally make this oracle independent of constants.
    for (const auto px : coordinates) {
        for (const auto py : coordinates) {
            for (const auto tx : coordinates) {
                for (const auto ty : coordinates) {
                    const auto dx = static_cast<std::int64_t>(px) - tx;
                    const auto dy = static_cast<std::int64_t>(py) - ty;
                    const bool hit = dx >= -9 && dx <= 9 && dy >= -9 && dy <= 9;
                    const bool project = dx < -20 || dx > 20 || dy < -20 || dy > 20;
                    checks.require(projectileHitsGuard(px, py, tx, ty) == hit,
                                   "square hit tolerance / coordinate overflow");
                    checks.require(projectileNeedsProjection(px, py, tx, ty) == project,
                                   "projection threshold / coordinate overflow");
                }
            }
        }
    }
    // Corners distinguish axis-aligned squares from circular distance tests.
    checks.require(projectileHitsGuard(9, 9, 0, 0), "hit-square corner is included");
    checks.require(!projectileHitsGuard(10, 0, 0, 0), "hit threshold is inclusive at 9 only");
    checks.require(!projectileNeedsProjection(20, 20, 0, 0), "projection-square corner excluded");
    checks.require(projectileNeedsProjection(21, 0, 0, 0), "projection starts beyond 20");
}

} // namespace

int main(int argc, char** argv) {
    const std::string_view mode = argc > 1 ? argv[1] : "all";
    if (argc > 2 || (mode != "all" && mode != "inventory" && mode != "projectile")) {
        std::cerr << "Usage: runtime_safety_test [all|inventory|projectile]\n";
        return 2;
    }
    Checks checks;
    if (mode != "projectile") checkInventory(checks);
    if (mode != "inventory") checkProjectiles(checks);
    std::cout << "runtime_safety_test: " << checks.count << " checks, "
              << checks.failures << " failures\n";
    return checks.failures == 0 ? 0 : 1;
}
