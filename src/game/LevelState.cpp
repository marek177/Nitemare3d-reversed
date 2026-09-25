#include "game/LevelState.hpp"

#include <algorithm>
#include <cmath>
#include <stdexcept>
#include <string_view>

namespace n3d {
namespace {
bool classStartsWith(std::string_view value, std::string_view prefix) {
    return value.size() >= prefix.size() && value.substr(0, prefix.size()) == prefix;
}
bool nonBlockingObjectClass(std::string_view cls) {
    return cls == "NULL" || cls == "START" || cls == "KEY" || cls == "IDCARD" ||
           cls == "FOOD" || cls == "MAGICEYE" || cls == "CRYSTALB" ||
           cls == "PENTAGRAM" || cls == "WEAPON" || cls == "AMMO" ||
           cls == "SCROLL" || cls == "PERMEABLE" || cls == "IMPACT" ||
           cls == "UIFOBJ";
}
} // namespace

LevelState LevelState::create(const LevelMap& source,
                              const DefinitionTable& objectDefs,
                              const DefinitionTable& wallDefs) {
    LevelState out;
    out.cells_ = source.cells;
    out.objectDefs_ = objectDefs;
    out.wallDefs_ = wallDefs;
    out.discoverPlayerStart();
    out.discoverPushables();
    return out;
}

std::size_t LevelState::indexOf(int x, int y) const {
    if (!inBounds(x, y)) throw std::out_of_range("LevelState coordinate outside 64x64 map");
    return static_cast<std::size_t>(y) * LevelMap::Width + static_cast<std::size_t>(x);
}
bool LevelState::inBounds(int x, int y) const {
    return x >= 0 && y >= 0 && x < static_cast<int>(LevelMap::Width) && y < static_cast<int>(LevelMap::Height);
}
const MapCell& LevelState::at(int x, int y) const { return cells_.at(indexOf(x, y)); }
MapCell& LevelState::at(int x, int y) { return cells_.at(indexOf(x, y)); }

void LevelState::discoverPlayerStart() {
    for (int y = 0; y < static_cast<int>(LevelMap::Height); ++y) {
        for (int x = 0; x < static_cast<int>(LevelMap::Width); ++x) {
            auto& cell = at(x, y);
            if (cell.object < 1 || cell.object > 4) continue;
            player_.x = static_cast<double>(x) + 0.5;
            player_.y = static_cast<double>(y) + 0.5;
            switch (cell.object) {
            case 1: player_.angleRadians = -1.5707963267948966; break;
            case 2: player_.angleRadians = 0.0; break;
            case 3: player_.angleRadians = 1.5707963267948966; break;
            case 4: player_.angleRadians = 3.1415926535897932; break;
            default: break;
            }
            cell.object = 0;
            return;
        }
    }
    throw std::runtime_error("Level has no START object (IDs 0001-0004)");
}

void LevelState::discoverPushables() {
    pushables_.clear();
    for (int y = 0; y < static_cast<int>(LevelMap::Height); ++y) {
        for (int x = 0; x < static_cast<int>(LevelMap::Width); ++x) {
            const auto objectId = at(x, y).object;
            if (objectId == 0 || !objectDefs_.isClass(objectId, "PUSH")) continue;
            if (pushables_.size() >= MaxPushables) throw std::runtime_error("MAXPUSHES exceeded (12), matching NITE3W.EXE");
            PushableObject p;
            p.objectId = objectId;
            p.fixedX = x * FixedUnitsPerTile + FixedUnitsPerTile / 2;
            p.fixedY = y * FixedUnitsPerTile + FixedUnitsPerTile / 2;
            pushables_.push_back(p);
        }
    }
}

bool LevelState::wallAllowsMovement(std::uint8_t wallId) const {
    const auto* def = wallDefs_.find(wallId);
    if (!def) return false;
    const std::string_view cls = def->className;
    return cls == "FLOOR" || cls == "ACTIONSPOT" || classStartsWith(cls, "TRIGGER");
}

bool LevelState::objectBlocksMovement(std::uint8_t objectId) const {
    if (objectId == 0) return false;
    const auto* def = objectDefs_.find(objectId);
    if (!def) return true;
    if (def->className == "PUSH") return true;
    return !nonBlockingObjectClass(def->className);
}

bool LevelState::cellAllowsPlayer(int x, int y) const {
    if (!inBounds(x, y)) return false;
    const auto& cell = at(x, y);
    return wallAllowsMovement(cell.wall) && !objectBlocksMovement(cell.object);
}

bool LevelState::cellAllowsPushTarget(int x, int y) const {
    if (!inBounds(x, y)) return false;
    const auto& cell = at(x, y);
    return wallAllowsMovement(cell.wall) && cell.object == 0;
}

PushableObject* LevelState::pushableAtTile(int x, int y) {
    for (auto& p : pushables_) if (p.tileX() == x && p.tileY() == y) return &p;
    return nullptr;
}
const PushableObject* LevelState::pushableAtTile(int x, int y) const {
    for (const auto& p : pushables_) if (p.tileX() == x && p.tileY() == y) return &p;
    return nullptr;
}

bool LevelState::pushableOccupiesOrTargetsTile(int x, int y, const PushableObject* ignore) const {
    for (const auto& p : pushables_) {
        if (&p == ignore) continue;
        if (p.tileX() == x && p.tileY() == y) return true;
        if (!p.moving()) continue;

        // fixedX/fixedY are tile-center world coordinates. step*ticksRemaining
        // is the exact remaining displacement to the reserved destination.
        const int finalX = p.fixedX + static_cast<int>(p.stepX) * p.ticksRemaining;
        const int finalY = p.fixedY + static_cast<int>(p.stepY) * p.ticksRemaining;
        if (finalX / FixedUnitsPerTile == x && finalY / FixedUnitsPerTile == y) return true;
    }
    return false;
}

bool LevelState::beginPush(int x, int y, int dirX, int dirY) {
    if ((std::abs(dirX) + std::abs(dirY)) != 1) return false;
    auto* push = pushableAtTile(x, y);
    if (!push || push->moving()) return false;
    const int targetX = x + dirX;
    const int targetY = y + dirY;
    if (!cellAllowsPushTarget(targetX, targetY)) return false;
    if (pushableOccupiesOrTargetsTile(targetX, targetY, push)) return false;
    push->stepX = static_cast<std::int8_t>(dirX * PushStepUnits);
    push->stepY = static_cast<std::int8_t>(dirY * PushStepUnits);
    push->ticksRemaining = PushTicks;
    return true;
}

void LevelState::tickPushables() {
    for (auto& push : pushables_) {
        if (!push.moving()) continue;
        const int oldTileX = push.tileX();
        const int oldTileY = push.tileY();
        push.fixedX += push.stepX;
        push.fixedY += push.stepY;
        const int newTileX = push.tileX();
        const int newTileY = push.tileY();
        if ((newTileX != oldTileX || newTileY != oldTileY) && inBounds(oldTileX, oldTileY) && inBounds(newTileX, newTileY)) {
            auto& oldCell = at(oldTileX, oldTileY);
            auto& newCell = at(newTileX, newTileY);
            if (oldCell.object == push.objectId) {
                newCell.object = oldCell.object;
                oldCell.object = 0;
            }
        }
        --push.ticksRemaining;
        if (!push.moving()) { push.stepX = 0; push.stepY = 0; }
    }
}

bool LevelState::positionBlockedByPushable(double x, double y) const {
    constexpr double radius = 0.30;
    for (const auto& p : pushables_) {
        const double px = static_cast<double>(p.fixedX) / FixedUnitsPerTile;
        const double py = static_cast<double>(p.fixedY) / FixedUnitsPerTile;
        const double dx = x - px;
        const double dy = y - py;
        if (dx * dx + dy * dy < radius * radius) return true;
    }
    return false;
}

bool LevelState::tryMovePlayer(double dx, double dy, bool allowAutoPush) {
    const double nx = player_.x + dx;
    const double ny = player_.y + dy;
    const int tx = static_cast<int>(std::floor(nx));
    const int ty = static_cast<int>(std::floor(ny));
    if (inBounds(tx, ty)) {
        const auto& cell = at(tx, ty);
        if (objectDefs_.isClass(cell.object, "PUSH") && allowAutoPush) {
            int dirX = 0, dirY = 0;
            if (std::abs(dx) >= std::abs(dy) && std::abs(dx) > 1e-9) dirX = dx > 0.0 ? 1 : -1;
            else if (std::abs(dy) > 1e-9) dirY = dy > 0.0 ? 1 : -1;
            beginPush(tx, ty, dirX, dirY);
            return false;
        }
    }
    if (!cellAllowsPlayer(tx, ty) || positionBlockedByPushable(nx, ny)) return false;
    player_.x = nx;
    player_.y = ny;
    return true;
}

} // namespace n3d
