#pragma once

#include <algorithm>
#include <cstddef>
#include <cstdint>

namespace nitemare3d::re::win16_20260925 {

// Evidence-backed NITE3W 1.10 facts recovered on 2026-09-25.
// This header intentionally keeps uncertain semantic interpretations out of
// executable logic. Segment:offset labels are preserved in comments where the
// original Win16 address is more meaningful than a flat address.

// -----------------------------------------------------------------------------
// Player / HUD
// -----------------------------------------------------------------------------
inline constexpr std::uint16_t kHudDispatcherSegment = 0x0003;
inline constexpr std::uint16_t kHudDispatcherOffset  = 0xA3B6;
inline constexpr std::uint16_t kAutomapDispatcherSegment = 0x0003;
inline constexpr std::uint16_t kAutomapDispatcherOffset  = 0xB1A4;

inline constexpr std::uint16_t kPlayerTileXGlobal = 0x4BF2;
inline constexpr std::uint16_t kPlayerTileYGlobal = 0x4BF4;
inline constexpr std::uint16_t kPlayerWorldXGlobal = 0x4BF6;
inline constexpr std::uint16_t kPlayerWorldYGlobal = 0x4BF8;
inline constexpr std::uint16_t kPlayerHealthGlobal = 0x4C1D;
inline constexpr std::uint16_t kEnemyLocatorEnergyGlobal = 0x4C42;
inline constexpr std::uint16_t kMapClarityEnergyGlobal = 0x4C43;

enum class HudRequest : std::uint8_t {
    FullRefresh = 0,
    NoOp1 = 1,
    WeaponBranch = 2,
    EpisodeLevel = 3,
    Score = 4,
    HealthPortrait = 5,
    NoOp6 = 6,
    SilverAmmo = 7,
    LaserAmmo = 8,
    WandAmmo = 9,
    NoOp10 = 10,
    NoOp11 = 11,
    WeaponIcon = 12,
    KeyIcon = 13,
    CardIcon = 14,
    NoOp15 = 15,
    NoOp16 = 16,
    NoOp17 = 17,
    Decoration = 18,
    EnemyLocatorGauge = 19,
    MapClarityGauge = 20,
    Status = 21,
    Coordinates = 22,
    RestoreOverlay = 23,
    InputOverlay = 24,
    DosCursor = 25,
};

inline constexpr int kHudPortraitX = 3;
inline constexpr int kHudPortraitY = 162;
inline constexpr int kHudPortraitFirstFrame = 13;
inline constexpr int kHudPortraitLastFrame = 23;

constexpr std::uint8_t clampHudHealth(std::uint8_t health) noexcept {
    return health > 100 ? 100 : health;
}

// Exact Win16 selection rule. HP 0 -> frame 13, 1..10 -> 14, ...,
// 91..100 -> 23. The HUD path writes the clamped HP value back to 0x4C1D.
constexpr int hudPortraitFrame(std::uint8_t health) noexcept {
    const auto hp = clampHudHealth(health);
    return kHudPortraitFirstFrame + (static_cast<int>(hp) + 9) / 10;
}

// Text destinations recovered from Hud_Dispatch.
struct HudTextField { int x; int y; int width; };
inline constexpr HudTextField kEpisodeLevelField{50, 171, 31};
inline constexpr HudTextField kScoreField{50, 191, 31};
inline constexpr HudTextField kHealthField{7, 192, 10};
inline constexpr HudTextField kSilverAmmoField{109, 164, 20};
inline constexpr HudTextField kLaserAmmoField{109, 177, 20};
inline constexpr HudTextField kWandAmmoField{109, 190, 20};
inline constexpr HudTextField kCoordinatesField{140, 192, 19};

// -----------------------------------------------------------------------------
// Automap / right HUD panel
// -----------------------------------------------------------------------------
enum class AutomapRequest : std::uint8_t {
    Request0 = 0,          // semantics still partial
    Request1 = 1,          // semantics still partial
    ClearBuffer = 2,
    RedrawWindow = 3,
    Request4 = 4,          // semantics still partial
    UpdatePlayerAndDraw = 5,
    DrawEligibleGuards = 6,
    LowEnergyNoise = 7,
    ClearOldPlayerCell = 8,
    DrawMarkerRectangle = 9,
};

inline constexpr int kAutomapWidth = 64;
inline constexpr int kAutomapHeight = 64;
inline constexpr int kAutomapBytes = 4096;
inline constexpr int kAutomapViewportWidth = 62;
inline constexpr int kAutomapViewportHeight = 36;
inline constexpr int kAutomapScreenX = 256;
inline constexpr int kAutomapScreenY = 162;

// Buffer 6:0000 is column-major, unlike the main MAP payload.
constexpr std::size_t automapIndex(int cellX, int cellY) noexcept {
    return static_cast<std::size_t>(cellX) * kAutomapHeight +
           static_cast<std::size_t>(cellY);
}

constexpr int automapOriginX(int playerCellX) noexcept {
    return std::clamp(playerCellX - 31, 0, 2);
}
constexpr int automapOriginY(int playerCellY) noexcept {
    return std::clamp(playerCellY - 18, 0, 28);
}

// For clarity energy <= 15 the original noise branch uses 500/(power^3).
// Power 0 does not execute the division.
constexpr int automapNoisePointCount(std::uint8_t power) noexcept {
    if (power == 0 || power > 15) return 0;
    const int p = power;
    return 500 / (p * p * p);
}

// Guard locator behavior observed for 0..15. Values >=16 remain continuously
// enabled; 1..15 blink on odd values.
constexpr bool enemyLocatorVisible(std::uint8_t power) noexcept {
    if (power == 0) return false;
    if (power <= 15) return (power & 1u) != 0;
    return true;
}

constexpr bool automapGuardClassExcluded(std::uint8_t objectClass) noexcept {
    return objectClass == 0x15 || objectClass == 0x16 ||
           objectClass == 0x19 || objectClass == 0x21;
}
inline constexpr std::uint8_t kAutomapGuardExcludedState = 0x0A;

// -----------------------------------------------------------------------------
// Renderer runtime globals and capacities
// -----------------------------------------------------------------------------
inline constexpr int kFramebufferWidth = 320;
inline constexpr int kFramebufferHeight = 200;
inline constexpr int kViewportX = 8;
inline constexpr int kViewportY = 4;
inline constexpr int kViewportWidth = 304;
inline constexpr int kViewportHeight = 152;
inline constexpr int kProjectionCenterY = 80;
inline constexpr double kRecoveredHorizontalFovDegrees = 80.99; // ~80.99 deg

inline constexpr std::uint16_t kWallOwnerTable = 0x53FE;       // 320 far ptrs
inline constexpr std::uint16_t kWallOcclusionTable = 0x58FE;   // 320 uint16
inline constexpr std::uint16_t kRgbPaletteTable = 0x5B7E;      // 256 * 3
inline constexpr std::uint16_t kVisibleSpanCount = 0x5E7E;
inline constexpr std::uint16_t kVisibilityBoundsBegin = 0x5E80; // through 5E86
inline constexpr std::uint16_t kVisibleSpanArray = 0x5E88;     // 50 * 20 B
inline constexpr std::uint16_t kProjectedSpriteArray = 0x6270; // 100 * 18 B
inline constexpr std::uint16_t kWinGBitmapHandle = 0x6978;
inline constexpr std::uint16_t kVecCountGlobal = 0x7E56;
inline constexpr std::uint16_t kObjectCountGlobal = 0x7E58;
inline constexpr std::uint16_t kWallResourceDescriptorCount = 0x7E5A;
inline constexpr std::uint16_t kObjectResourceDescriptorCount = 0x7E5C;
inline constexpr std::uint16_t kGuardCountGlobal = 0x7E5E;

inline constexpr int kWallOwnerColumns = 320;
inline constexpr int kWallOcclusionColumns = 320;
inline constexpr int kVisibleSpanCapacity = 50;
inline constexpr int kVisibleSpanStride = 20;
inline constexpr int kProjectedSpriteCapacity = 100;
inline constexpr int kProjectedSpriteStride = 18;
inline constexpr int kVecListCapacity = 333;
inline constexpr int kVecListCount = 4;

// -----------------------------------------------------------------------------
// GUARD record: exact offsets, with semantics limited to instruction-backed use.
// -----------------------------------------------------------------------------
inline constexpr std::size_t kGuardStride = 0x1A;
inline constexpr std::size_t kGuardTimestamp = 0x02; // dword, +02..+05
inline constexpr std::size_t kGuardStateTimer = 0x06;
inline constexpr std::size_t kGuardObjectSlot = 0x08;
inline constexpr std::size_t kGuardStrategy = 0x0A;
inline constexpr std::size_t kGuardState = 0x0B;
inline constexpr std::size_t kGuardNextOrReturnState = 0x0C;
inline constexpr std::size_t kGuardStrength = 0x10;
inline constexpr std::size_t kGuardOctant = 0x11;
inline constexpr std::size_t kGuardResultOctant = 0x12;
inline constexpr std::size_t kGuardState13MoveX = 0x13; // signed byte
inline constexpr std::size_t kGuardState13MoveY = 0x14; // signed byte

enum class GuardState : std::uint8_t {
    PerceptionDecision = 0x07,
    LethalContactTerminal = 0x0B,
    TimedDirectionalMove = 0x13,
    PainReturn = 0x15,
};

struct GuardMoveStep { std::int8_t dx; std::int8_t dy; };
constexpr GuardMoveStep guardState13Step(std::uint8_t octant) noexcept {
    switch (octant & 7u) {
    case 0: return { 0, -8};
    case 1: return {+8,  0};
    case 2: return {+8,  0};
    case 3: return { 0, +8};
    case 4: return { 0, +8};
    case 5: return {-8,  0};
    case 6: return {-8,  0};
    default:return { 0, -8};
    }
}

// State 13 runs one 8-unit update after the initial timer=8 entry and then
// seven further directional updates: 7*8 = 56 world units after the entry tick.
inline constexpr int kGuardState13StepUnits = 8;

// -----------------------------------------------------------------------------
// IMG/UIF facts used by HUD/resource reconstruction.
// -----------------------------------------------------------------------------
inline constexpr std::size_t kImgWallDirectoryOffset = 0x0000;
inline constexpr std::size_t kImgObjectDirectoryOffset = 0x0400;
inline constexpr std::size_t kImgDirectoryEntries = 256;
inline constexpr std::size_t kImgDirectoryEntryBytes = 4;
inline constexpr std::size_t kImgFrameHeaderBytes = 10;
inline constexpr std::size_t kImgFirstFrameStreamOffset = 0xBC00;

// IMG pixels are stored x-major: pixels[x * height + y].
constexpr std::size_t imgColumnMajorPixelIndex(std::size_t x,
                                                std::size_t y,
                                                std::size_t height) noexcept {
    return x * height + y;
}

// Object image 0xFF is the dynamic HUD bank in the audited Episode-1 data.
inline constexpr std::uint8_t kHudImageObjectId = 0xFF;
inline constexpr int kHudWeaponFrameFirst = 0;
inline constexpr int kHudWeaponFrameLast = 3;
inline constexpr int kHudKeyFrameFirst = 4;
inline constexpr int kHudKeyFrameLast = 7;
inline constexpr int kHudCardFrameFirst = 8;
inline constexpr int kHudCardFrameLast = 9;
inline constexpr int kHudPortraitFrameFirst = 13;
inline constexpr int kHudPortraitFrameLast = 23;
inline constexpr int kHudBankFrameCount = 29; // frames 0..28

inline constexpr int kUifDirectorySlots = 32;
inline constexpr int kUifDirectoryEntryBytes = 6;
inline constexpr int kUifKnownPopulatedFirst = 0;
inline constexpr int kUifKnownPopulatedLast = 16;
inline constexpr int kUifFontSlotFirst = 0;
inline constexpr int kUifFontSlotLast = 2;
inline constexpr int kUifPcxSlotFirst = 3;
inline constexpr int kUifPcxSlotLast = 16;

// -----------------------------------------------------------------------------
// Menu/save dispatcher facts.
// -----------------------------------------------------------------------------
inline constexpr std::uint16_t kMenuDispatcherSegment = 0x0004;
inline constexpr std::uint16_t kMenuDispatcherOffset = 0x27DE;
inline constexpr int kMenuActionFirst = 1;
inline constexpr int kMenuActionLast = 40;
inline constexpr int kMenuTableCount = 14;
inline constexpr int kMenuItemCount = 80;
inline constexpr int kSaveSlotCount = 10;
inline constexpr int kSaveNameMaxChars = 40;
inline constexpr int kSaveNameMaxPixels = 179;

// Some semantic mappings remain deliberately absent here:
// - Automap requests 0,1,4 and exact cell color/value meanings.
// - Exact HUD asset descriptor binding for every request.
// - GUARD +15/+16/+17..+19 meanings.
// - Complete menu action 1..40 symbolic names.
// Those still require stronger evidence before becoming runtime behavior.

} // namespace nitemare3d::re::win16_20260925
