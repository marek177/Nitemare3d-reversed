#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

namespace nitemare3d::re {

// Cross-thread reconstruction anchors from the original NITE3W.EXE V1.10 and
// original data files. Only values with direct EXE/DATA/SAVE evidence belong
// here. PARTIAL semantics are explicitly marked and must not be treated as final.

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

// Structural runtime/save evidence also exposes a 4096-byte 64x64-sized
// cell-state/visibility-like block. Exact bit semantics remain PARTIAL.
inline constexpr std::size_t kRuntimeCellStateBytes = 4096;

// Important distinction: 11/10/10 are the supplied archive payload counts, not
// a proven universal MAP-format ceiling. Historical MapEdit sources support a
// larger editor MAX_LEVELS; the original game executable's absolute archive
// ceiling is still tracked separately as an open question.

// Player movement/collision --------------------------------------------------
inline constexpr int kPlayerCollisionHalfExtent = 27;        // AABB, VERIFIED_EXE
inline constexpr int kPlayerProximityThreshold = 42;         // VERIFIED_EXE; purpose PARTIAL
inline constexpr std::uint16_t kInputForward = 0x0002;
inline constexpr std::uint16_t kInputBackward = 0x0004;
inline constexpr std::uint16_t kInputTurnA = 0x0008;          // direction label PARTIAL
inline constexpr std::uint16_t kInputTurnB = 0x0010;          // direction label PARTIAL
inline constexpr std::uint16_t kInputFastModifier = 0x0020;
inline constexpr std::uint16_t kInputIncrementReset = 0x0040;// exact high-level label PARTIAL
inline constexpr std::uint16_t kInputFire = 0x0080;
inline constexpr std::uint16_t kInputStrafeModifier = 0x0100;
inline constexpr std::uint16_t kInputUse = 0x0200;            // rising-edge USE/ACTION

// Original gameplay globals --------------------------------------------------
inline constexpr std::uint16_t kDifficultyGlobal = 0x4C14;
inline constexpr std::uint16_t kScoreLowGlobal = 0x4C16;
inline constexpr std::uint16_t kPlayerHealthGlobal = 0x4C1D;
inline constexpr std::uint16_t kSilverAmmoGlobal = 0x4C1F;
inline constexpr std::uint16_t kLaserAmmoGlobal = 0x4C20;
inline constexpr std::uint16_t kActiveWeaponGlobal = 0x4C23;
inline constexpr std::uint16_t kWeaponJamGlobal = 0x4C2E;
inline constexpr std::uint16_t kWandAmmoGlobal = 0x4C44;
inline constexpr std::uint16_t kOmnipotentGlobal = 0x4BE5;
inline constexpr std::uint16_t kPlayerWorldXGlobal = 0x4BF6;
inline constexpr std::uint16_t kPlayerWorldYGlobal = 0x4BF8;
inline constexpr std::uint16_t kEpisodeBossGateGlobal = 0x7E52; // semantic PARTIAL; Hamerstein checks value 3

// Difficulty value ordering is supported independently by player->guard
// damage, guard->player damage and GUARD timer scaling.
inline constexpr std::uint16_t kDifficultyEasier = 0;
inline constexpr std::uint16_t kDifficultyBaseline = 1;
inline constexpr std::uint16_t kDifficultyHarder = 2;

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

// Original runtime capacities/strides/bases --------------------------------
inline constexpr std::size_t kMaxDoors = 64;
inline constexpr std::size_t kDoorRuntimeStride = 22;
inline constexpr std::uint16_t kDoorRuntimeBase = 0x9DD6;
inline constexpr std::size_t kMaxPanels = 32;
inline constexpr std::size_t kPanelRuntimeStride = 22;
inline constexpr std::uint16_t kPanelRuntimeBase = 0xA356;
inline constexpr std::size_t kMaxPushables = 12;
inline constexpr std::size_t kPushRuntimeStride = 6;
inline constexpr std::uint16_t kPushRuntimeBase = 0xA616;
inline constexpr std::size_t kMaxObjects = 350;
inline constexpr std::size_t kObjectRuntimeStride = 28;
inline constexpr std::uint16_t kObjectRuntimeBase = 0x6D66;
inline constexpr std::uint16_t kObjectCountGlobal = 0x7E58;
inline constexpr std::size_t kMaxGuards = 100;
inline constexpr std::size_t kGuardRuntimeStride = 26;
inline constexpr std::uint16_t kGuardRuntimeBase = 0x93AE;
inline constexpr std::uint16_t kGuardCountGlobal = 0x7E5E;
inline constexpr std::size_t kMaxVectors = 1000;
inline constexpr std::size_t kVectorRuntimeStride = 28;
inline constexpr std::uint16_t kVectorCountGlobal = 0x7E56;
inline constexpr std::size_t kMaxSegments = 50;
inline constexpr std::size_t kWallSpanRuntimeStride = 20;
inline constexpr std::size_t kMaxImages = 70;
inline constexpr std::size_t kOrientationListCapacity = 333;
inline constexpr std::size_t kMaxProjectedSprites = 100;
inline constexpr std::size_t kProjectedSpriteStride = 18;

// Correction retained explicitly for audit history: older arithmetic guesses
// of OBJECT=80 B and GUARD=98 B were wrong. Direct indexing and USER.SAV block
// sizes prove OBJECT=28 B and GUARD=26 B.

// 28-byte OBJECT anchors -----------------------------------------------------
inline constexpr std::size_t kObjectClassOffset = 0x06;
inline constexpr std::size_t kObjectGuardIndexOffset = 0x07;
inline constexpr std::size_t kObjectMapBindingOffset = 0x0C;
inline constexpr std::size_t kObjectWorldXOffset = 0x10;
inline constexpr std::size_t kObjectWorldYOffset = 0x12;
inline constexpr std::size_t kObjectRenderSortAOffset = 0x14; // semantic PARTIAL
inline constexpr std::size_t kObjectRenderSortBOffset = 0x16; // semantic PARTIAL
// Read by damage producer as projected/view-space vertical baseline; writer
// semantics still PARTIAL. Explicitly not world Y.
inline constexpr std::size_t kObjectProjectedDamageBaselineOffset = 0x18;

// Renderer / viewport --------------------------------------------------------
inline constexpr int kFramebufferWidth = 320;
inline constexpr int kFramebufferHeight = 200;
inline constexpr std::size_t kFramebufferBytes = 64000;
inline constexpr int kViewportXMin = 8;
inline constexpr int kViewportXMax = 311;
inline constexpr int kViewportYMin = 4;
inline constexpr int kViewportYMax = 155;
inline constexpr int kViewportWidth = 304;
inline constexpr int kViewportHeight = 152;
inline constexpr int kViewportCenterX = 160;
inline constexpr int kViewportCenterY = 80;
inline constexpr int kViewportCenterYQ4 = 1280;
inline constexpr std::uint8_t kDefaultFloorPaletteIndex = 0x0C;
inline constexpr std::uint8_t kDefaultCeilingPaletteIndex = 0x11;
inline constexpr std::uint8_t kSpriteTransparentPaletteIndex = 0x29;

// Per-column owner table: 320 far pointers, exactly 4 bytes each.
inline constexpr std::uint16_t kColumnOwnerBase = 0x53FE;
inline constexpr std::size_t kColumnOwnerEntries = 320;
inline constexpr std::size_t kColumnOwnerEntryBytes = 4;

// Per-column wall silhouette/occlusion table. This is NOT documented as a
// conventional metric Z-buffer; wall and sprite code use its projected value.
inline constexpr std::uint16_t kWallOcclusionBase = 0x58FE;
inline constexpr std::size_t kWallOcclusionEntries = 320;
inline constexpr std::size_t kWallOcclusionEntryBytes = 2;

inline constexpr std::uint16_t kWallSpanCountGlobal = 0x5E7E;
inline constexpr std::uint16_t kWallSpanBase = 0x5E88;
inline constexpr std::uint16_t kProjectedSpriteQueueBase = 0x6270;

// Four orientation-specific VECLIST arrays. Each entry is a 4-byte far pointer
// to a 28-byte VEC record; 0x534 bytes = 333 * 4 separates adjacent lists.
inline constexpr std::array<std::uint16_t, 4> kVectorListCountGlobals = {
    0x697A, 0x697C, 0x697E, 0x6980
};
inline constexpr std::array<std::uint16_t, 4> kVectorListBases = {
    0x6982, 0x6EB6, 0x73EA, 0x791E
};

// 28-byte VEC record offsets. Exact endpoint/orientation offsets are confirmed;
// names of several resource/animation bytes remain PARTIAL.
inline constexpr std::size_t kVecWallIdOffset = 0x00;
inline constexpr std::size_t kVecTextureOffsetOffset = 0x01; // PARTIAL semantic
inline constexpr std::size_t kVecAnimAuxOffset = 0x02;       // PARTIAL semantic
inline constexpr std::size_t kVecAnimFrameOffset = 0x03;     // STRONG
inline constexpr std::size_t kVecTextureSetOffset = 0x04;    // STRONG
inline constexpr std::size_t kVecFlagsOffset = 0x05;
inline constexpr std::size_t kVecRenderClassOffset = 0x06;
inline constexpr std::size_t kVecOrientationOffset = 0x07;   // 0..3 CONFIRMED
inline constexpr std::size_t kVecTimerOffset = 0x08;         // PARTIAL semantic
inline constexpr std::size_t kVecX1Offset = 0x0C;
inline constexpr std::size_t kVecY1Offset = 0x0E;
inline constexpr std::size_t kVecX2Offset = 0x10;
inline constexpr std::size_t kVecY2Offset = 0x12;
inline constexpr std::size_t kVecScreenX1Offset = 0x14;
inline constexpr std::size_t kVecProjectedY1Q4Offset = 0x16;
inline constexpr std::size_t kVecScreenX2Offset = 0x18;
inline constexpr std::size_t kVecProjectedY2Q4Offset = 0x1A;

inline constexpr std::uint8_t kVecFlagActive = 0x01;         // high-confidence renderer use
inline constexpr std::uint8_t kVecFlagSpecial04 = 0x04;      // semantic TODO
inline constexpr std::uint8_t kVecFlagSpecial08 = 0x08;      // semantic TODO
inline constexpr std::uint8_t kVecFlagMaskedLike = 0x10;     // PARTIAL
inline constexpr std::uint8_t kVecFlagTextureUFlip = 0x20;   // high confidence

// Orientation construction from MAP boundary extraction.
// 0: (x,y)->(x+64,y)        top/horizontal
// 1: (x,y+64)->(x+64,y+64) bottom/horizontal
// 2: (x+64,y)->(x+64,y+64) right/vertical
// 3: (x,y)->(x,y+64)        left/vertical
inline constexpr std::uint8_t kVecTop = 0;
inline constexpr std::uint8_t kVecBottom = 1;
inline constexpr std::uint8_t kVecRight = 2;
inline constexpr std::uint8_t kVecLeft = 3;

// Pushable movement ---------------------------------------------------------
inline constexpr std::uint8_t kPushableRuntimeClass = 0x28;  // VERIFIED_EXE/DATA
inline constexpr int kPushSteps = 8;
inline constexpr int kPushUnitsPerStep = 8;                  // 8*8 == one 64-unit tile

// GUARD ---------------------------------------------------------------------
inline constexpr std::uint8_t kGuardInitialStrength = 0xFF;
inline constexpr std::uint8_t kGuardPainState = 0x15;
inline constexpr std::size_t kGuardStateCount = 0x16;        // states 00..15

// Recovered runtime classes used by combat/death dispatch.
inline constexpr std::uint8_t kGuardClassBat = 0x08;
inline constexpr std::uint8_t kGuardClassDracula = 0x11;
inline constexpr std::uint8_t kGuardClassDraculaBat = 0x14;  // transformed second phase
inline constexpr std::uint8_t kGuardClassPenelope = 0x15;
inline constexpr std::uint8_t kGuardClassHamerstein = 0x16;
inline constexpr std::uint8_t kGuardClassCannon = 0x19;
inline constexpr std::uint8_t kGuardClassGhost = 0x1A;
inline constexpr std::uint8_t kGuardClassAlien1 = 0x1E;
inline constexpr std::uint8_t kGuardClassAlien2 = 0x1F;
inline constexpr std::uint8_t kGuardClass25 = 0x20;           // identity/reachability PARTIAL

// Dracula lethal phase-1 transition anchors.
inline constexpr std::uint8_t kDraculaMorphStrength = 0xFF;
inline constexpr std::uint8_t kDraculaMorphState = 0x08;
inline constexpr std::uint8_t kDraculaMorphNextState = 0x02;
inline constexpr std::uint16_t kDraculaMorphTimer = 1;
inline constexpr std::uint8_t kDraculaMorphSequenceValue = 0x23;
inline constexpr std::uint8_t kDraculaMorphEventSoundRequest = 0x22;

// Hamerstein combat special branch.
inline constexpr std::uint16_t kHamersteinGateValue = 3;
inline constexpr int kHamersteinBaseDamageWhenVulnerable = 3;

// Per-kill score switch covers GUARD1..25. GUARD13 is the transformed
// Dracula-Bat second phase. GUARD25 remains unidentified; GUARD26/Dancers is
// outside the switch and falls back to 0.
inline constexpr std::array<int, 26> kGuardScorePoints = {
    25,    // GUARD1  Bat
    75,    // GUARD2  Frankenstein
    50,    // GUARD3  Mummy
    100,   // GUARD4  Skeleton
    250,   // GUARD5  Mrs H.
    150,   // GUARD6  Zelda
    200,   // GUARD7  Vampira
    100,   // GUARD8  Baddie #1
    100,   // GUARD9  Baddie #2
    0,     // GUARD10 Dracula phase 1
    150,   // GUARD11 Cemetery Gargoyle
    150,   // GUARD12 Garden Gargoyle
    200,   // GUARD13 Dracula-Bat internal second form
    -1000, // GUARD14 Penelope
    1000,  // GUARD15 Dr. Hamerstein
    100,   // GUARD16 Tall slim robot
    200,   // GUARD17 Trashcan robot
    0,     // GUARD18 Cannon
    25,    // GUARD19 Ghost
    100,   // GUARD20 Goldie
    100,   // GUARD21 Greenie
    250,   // GUARD22 Demon
    250,   // GUARD23 Alien #1
    200,   // GUARD24 Alien #2
    50,    // GUARD25 unresolved/cut/fallback identity
    0      // GUARD26 Dancers / default score path
};

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
inline constexpr std::uint8_t kEventEnteredTile = 0x16;      // tile-change/walk-over path, distinct from USE
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
inline constexpr std::size_t kSaveVectorBlockOffset = 0x2093;
inline constexpr std::size_t kSaveVectorBlockBytes = 28000;  // 1000*28
inline constexpr std::size_t kSaveObjectBlockOffset = 0x8DF3;
inline constexpr std::size_t kSaveObjectBlockBytes = 9800;   // 350*28
inline constexpr std::size_t kSaveGuardBlockOffset = 0xB43B;
inline constexpr std::size_t kSaveGuardBlockBytes = 0x0A28;  // 100*26
inline constexpr std::size_t kSaveDoorBlockOffset = 0xBE63;
inline constexpr std::size_t kSaveDoorBlockBytes = 1408;     // 64*22
inline constexpr std::size_t kSaveUnknown336Offset = 0xC403;// semantic TODO
inline constexpr std::size_t kSaveUnknown336Bytes = 336;
inline constexpr std::size_t kSavePushBlockOffset = 0xC55B;
inline constexpr std::size_t kSavePushBlockBytes = 72;       // 12*6
inline constexpr std::size_t kSaveFloorPaletteOffset = 0xD6E3;
inline constexpr std::size_t kSaveCeilingPaletteOffset = 0xD6E4;
inline constexpr std::size_t kSaveEnvironmentWordOffset = 0xD6E5; // mirrors 0x7E60, exact semantic TODO

// CONFIG.SAV ---------------------------------------------------------------
inline constexpr std::size_t kConfigSaveBytes = 20;

// Original NITE3W.EXE identity ---------------------------------------------
inline constexpr std::size_t kOriginalExeBytes = 230400;
// SHA-256: 12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481

} // namespace nitemare3d::re