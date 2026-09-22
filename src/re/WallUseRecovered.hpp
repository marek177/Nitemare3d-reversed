#pragma once

#include <cstdint>

// Consolidated wall/USE reconstruction from NITE3W.EXE and MAP/WALLS data.
// Keep VERIFIED facts separate from partial semantic labels.
namespace nitemare3d::re {

// Runtime wall-property bits built by the original wall-class preprocessing.
inline constexpr std::uint8_t kWallPropWorldGeometry = 0x01; // VERIFIED_EXE; exact high-level label partial
inline constexpr std::uint8_t kWallPropCollision     = 0x02; // VERIFIED_EXE
inline constexpr std::uint8_t kWallPropHardBlock     = 0x04; // VERIFIED_EXE
inline constexpr std::uint8_t kWallPropDoor          = 0x08; // VERIFIED_EXE, classes 0x31..0x40
inline constexpr std::uint8_t kWallPropExplodable    = 0x10; // VERIFIED_EXE, classes 0x2E..0x2F
inline constexpr std::uint8_t kWallPropTrigger       = 0x40; // VERIFIED_EXE, classes 0x47..0x48

// Recovered wall classes whose semantics are directly supported by EXE/data.
inline constexpr std::uint8_t kWallClassLevelUp      = 0x09;
inline constexpr std::uint8_t kWallClassLevelUp2     = 0x0A;
inline constexpr std::uint8_t kWallClassWarpS1       = 0x15;
inline constexpr std::uint8_t kWallClassWarpS2       = 0x16;
inline constexpr std::uint8_t kWallClassExplode1     = 0x2E;
inline constexpr std::uint8_t kWallClassExplode2     = 0x2F;
inline constexpr std::uint8_t kWallClassDoorVC       = 0x3F; // curtain, vertical
inline constexpr std::uint8_t kWallClassDoorHC       = 0x40; // curtain, horizontal
inline constexpr std::uint8_t kWallClassTrigger1     = 0x47;
inline constexpr std::uint8_t kWallClassTrigger2     = 0x48;

// USE/ACTION bit recovered from the input mask.
inline constexpr std::uint16_t kUseActionMask = 0x0200;

// The original USE dispatcher first tests the derived door property; non-door
// paths then handle level exits, WARP families, panels and special wall/object
// classes. These values are retained as reconstruction anchors, not as a claim
// that every class in the range has identical high-level behavior.
inline constexpr std::uint8_t kWarpDispatchFirstClass = 0x0D;
inline constexpr std::uint8_t kWarpDispatchLastClass  = 0x2C;

// WARP_S1 requires four pentagram bits; WARP_S2 is the broken-mirror endpoint.
inline constexpr std::uint8_t kAllPentagramsMask = 0x0F;

// Runtime families recovered from fixed-capacity arrays.
inline constexpr std::uint8_t kDoorStateCount = 4; // states 0..3 are directly observed
inline constexpr int kDoorMotionStep = 2;
inline constexpr int kPushMotionSteps = 8;
inline constexpr int kPushMotionUnitsPerStep = 8;

struct WallUseAuditStatus {
    bool wallPropertyTableVerified = true;
    bool curtainDoorClassesVerified = true;
    bool levelExitClassesVerified = true;
    bool warpSpecialPairVerified = true;
    bool triggerClassesVerified = true;
    bool completeControlCommandMapping = false;
    bool oneShotActivationClosed = false;
    bool special1DispatchClosed = false;
};

inline constexpr WallUseAuditStatus kWallUseAuditStatus{};

} // namespace nitemare3d::re
