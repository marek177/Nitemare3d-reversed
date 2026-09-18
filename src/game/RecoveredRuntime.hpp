#pragma once

#include <cstddef>
#include <cstdint>

namespace nitemare3d::re {

// Cross-thread reconstruction anchors from the original NITE3W.EXE V1.10 and
// original data files.  Only values with direct EXE/DATA evidence belong here.
// PARTIAL semantics are explicitly marked and must not be treated as final.

// MAP.1/.2/.3 ---------------------------------------------------------------
inline constexpr std::size_t kMapWidth = 64;                 // VERIFIED_DATA/EXE
inline constexpr std::size_t kMapHeight = 64;                // VERIFIED_DATA/EXE
inline constexpr std::size_t kMapCellBytes = 2;              // {wall, object}
inline constexpr std::size_t kMapLevelBytes = 8192;
inline constexpr std::size_t kMapHeaderBytes = 514;
inline constexpr std::size_t kEpisode1Levels = 11;           // E1M11 is internal/demo
inline constexpr std::size_t kEpisode2Levels = 10;
inline constexpr std::size_t kEpisode3Levels = 10;
inline constexpr int kWorldUnitsPerTile = 64;                // coord >> 6

// Player movement/collision --------------------------------------------------
inline constexpr int kPlayerCollisionHalfExtent = 27;        // AABB, VERIFIED_EXE
inline constexpr int kPlayerProximityThreshold = 42;         // VERIFIED_EXE; purpose PARTIAL
inline constexpr std::uint16_t kInputFire = 0x0080;
inline constexpr std::uint16_t kInputStrafeModifier = 0x0100;
inline constexpr std::uint16_t kInputUse = 0x0200;            // rising-edge USE/ACTION

// Runtime property tables ---------------------------------------------------
inline constexpr std::uint16_t kWallPropertyTable = 0x7E94;  // DS offset in original
inline constexpr std::uint16_t kObjectPropertyTable = 0x7F94;
inline constexpr std::uint8_t kWallHardBlock = 0x04;
inline constexpr std::uint8_t kWallDynamicDoor = 0x08;
inline constexpr std::uint8_t kWallScriptTouch = 0x40;
inline constexpr std::uint8_t kObjectRuntimePresent = 0x01;
inline constexpr std::uint8_t kObjectBlocksMovement = 0x02;
inline constexpr std::uint8_t kObjectSpecialTouch = 0x04;
inline constexpr std::uint8_t kObjectCreatesGuard = 0x08;

// Original runtime capacities/strides ---------------------------------------
inline constexpr std::size_t kMaxDoors = 64;
inline constexpr std::size_t kDoorRuntimeStride = 22;
inline constexpr std::size_t kMaxPanels = 32;
inline constexpr std::size_t kPanelRuntimeStride = 22;
inline constexpr std::size_t kMaxPushables = 12;
inline constexpr std::size_t kPushRuntimeStride = 6;
inline constexpr std::size_t kMaxObjects = 350;
inline constexpr std::size_t kObjectRuntimeStride = 28;
inline constexpr std::size_t kMaxGuards = 100;
inline constexpr std::size_t kGuardRuntimeStride = 26;
inline constexpr std::size_t kMaxVectors = 1000;
inline constexpr std::size_t kMaxSegments = 50;
inline constexpr std::size_t kMaxImages = 70;
inline constexpr std::size_t kOrientationListCapacity = 333;

// Pushable movement ---------------------------------------------------------
inline constexpr std::uint8_t kPushableRuntimeClass = 0x28;  // VERIFIED_EXE/DATA
inline constexpr int kPushSteps = 8;
inline constexpr int kPushUnitsPerStep = 8;                  // 8*8 == one 64-unit tile

// Weapons/ammo --------------------------------------------------------------
enum class Weapon : std::uint8_t {
    SingleShotLaser = 0,
    MagicWand = 1,
    SilverPistol = 2,
    ContinuousLaser = 3,
};
inline constexpr std::uint8_t kNoWeapon = 0xFF;
inline constexpr int kAmmoPickupIncrement = 20;
inline constexpr int kAmmoForcedValue = 50;
inline constexpr int kAmmoThreshold = 100;

// Known level/script event anchors ------------------------------------------
inline constexpr std::uint8_t kEventEnteredTile = 0x16;
inline constexpr std::uint8_t kEventSetWeaponJam = 0x47;
inline constexpr std::uint8_t kEventClearWeaponJam = 0x48;

// DEMO ----------------------------------------------------------------------
inline constexpr std::size_t kDemoHeaderBytes = 6;
inline constexpr std::size_t kDemoRecordBytes = 8;
#pragma pack(push, 1)
struct DemoRecord {
    std::uint8_t eventByte;
    std::uint16_t inputMask;
    std::uint8_t pad;
    std::uint32_t timestamp;
};
#pragma pack(pop)
static_assert(sizeof(DemoRecord) == kDemoRecordBytes);

// USER.SAV ------------------------------------------------------------------
inline constexpr std::size_t kUserSaveSlotBytes = 0xD6E7;    // 55,015
inline constexpr std::size_t kSaveDescriptionOffset = 0x0004;
inline constexpr std::size_t kSaveEpisodeOffset = 0x002D;
inline constexpr std::size_t kSaveLevelOffset = 0x002F;
inline constexpr std::size_t kSaveTickOffset = 0x0031;
inline constexpr std::size_t kSaveMapOffset = 0x0035;
inline constexpr std::size_t kSaveGlobalsOffset = 0x2035;
inline constexpr std::size_t kSaveGlobalsBytes = 0x005E;
inline constexpr std::size_t kSaveGuardBlockOffset = 0xB43B;
inline constexpr std::size_t kSaveGuardBlockBytes = 0x0A28;  // 100*26

// CONFIG.SAV ---------------------------------------------------------------
inline constexpr std::size_t kConfigSaveBytes = 20;

// Original NITE3W.EXE identity ---------------------------------------------
inline constexpr std::size_t kOriginalExeBytes = 230400;
// SHA-256: 12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481

} // namespace nitemare3d::re
