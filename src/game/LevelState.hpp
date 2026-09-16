#pragma once

#include "formats/DefinitionTable.hpp"
#include "formats/MapArchive.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <vector>

namespace n3d {

struct PlayerState {
    double x{1.5};
    double y{1.5};
    double angleRadians{0.0};
};

struct PushableObject {
    std::uint8_t objectId{};
    int fixedX{};
    int fixedY{};
    std::int8_t stepX{};
    std::int8_t stepY{};
    std::uint8_t ticksRemaining{};
    int tileX() const { return fixedX / 64; }
    int tileY() const { return fixedY / 64; }
    bool moving() const { return ticksRemaining != 0; }
};

class LevelState {
public:
    static constexpr int FixedUnitsPerTile = 64;
    static constexpr int PushStepUnits = 8;
    static constexpr std::uint8_t PushTicks = 8;
    static constexpr std::size_t MaxPushables = 12;
    static LevelState create(const LevelMap& source,
                             const DefinitionTable& objectDefs,
                             const DefinitionTable& wallDefs);
    const MapCell& at(int x, int y) const;
    MapCell& at(int x, int y);
    bool inBounds(int x, int y) const;
    const PlayerState& player() const { return player_; }
    PlayerState& player() { return player_; }
    const std::vector<PushableObject>& pushables() const { return pushables_; }
    bool wallAllowsMovement(std::uint8_t wallId) const;
    bool objectBlocksMovement(std::uint8_t objectId) const;
    bool cellAllowsPlayer(int x, int y) const;
    bool cellAllowsPushTarget(int x, int y) const;
    PushableObject* pushableAtTile(int x, int y);
    const PushableObject* pushableAtTile(int x, int y) const;
    bool beginPush(int x, int y, int dirX, int dirY);
    void tickPushables();
    bool tryMovePlayer(double dx, double dy, bool allowAutoPush = true);
private:
    std::array<MapCell, LevelMap::Width * LevelMap::Height> cells_{};
    const DefinitionTable* objectDefs_{};
    const DefinitionTable* wallDefs_{};
    PlayerState player_{};
    std::vector<PushableObject> pushables_;
    std::size_t indexOf(int x, int y) const;
    void discoverPlayerStart();
    void discoverPushables();
    bool positionBlockedByPushable(double x, double y) const;
};

} // namespace n3d
