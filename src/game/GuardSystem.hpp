#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

namespace nitemare3d::game {

inline constexpr std::size_t kGuardCapacity = 100;
inline constexpr std::size_t kGuardRecordSize = 0x1A;
inline constexpr std::size_t kGuardSaveOffset = 0xB43B;
inline constexpr std::size_t kGuardSaveSize = 0x0A28;
inline constexpr std::uint8_t kFreshGuardStrength = 0xFF;

// Clean-room runtime layout recovered from NITE3W.EXE V1.10.
// Names below are promoted only where direct executable evidence exists.
#pragma pack(push, 1)
struct GuardRuntimeRecord {
    std::uint8_t unknown00_01[0x02];
    std::uint32_t timeStamp;          // +02 VERIFIED_EXE
    std::uint16_t stateTimer;         // +06 VERIFIED_EXE; debug label "timer"
    std::uint16_t objectSlot;         // +08 VERIFIED_EXE; index * 0x1C -> OBJECT
    std::uint8_t strategy;            // +0A VERIFIED_EXE; debug label "strategy"
    std::uint8_t state;               // +0B VERIFIED_EXE
    std::uint8_t nextState;           // +0C VERIFIED_EXE
    std::uint8_t savedMapObjectByte; // +0D: displaced map-cell object byte used on movement/death
    std::uint8_t definitionId;        // +0E PARTIAL: lookup-derived
    std::uint8_t syncFlag;            // +0F PARTIAL: derived boolean
    std::uint8_t strength;            // +10 VERIFIED_EXE: strength / HP
    std::uint8_t octant;              // +11 VERIFIED_EXE; debug label "octant"
    std::uint8_t resultOctant;        // +12 VERIFIED_EXE; debug label "resoct"
    std::int8_t moveX;                 // +13 VERIFIED_EXE in state 0x13
    std::int8_t moveY;                 // +14 VERIFIED_EXE in state 0x13
    std::uint8_t unknown15;            // +15 semantic TODO
    std::uint8_t transitionFlag;       // +16 PARTIAL control flag
    std::uint8_t unknown17_19[0x03];
};
#pragma pack(pop)

static_assert(sizeof(GuardRuntimeRecord) == kGuardRecordSize);
static_assert(offsetof(GuardRuntimeRecord, timeStamp) == 0x02);
static_assert(offsetof(GuardRuntimeRecord, stateTimer) == 0x06);
static_assert(offsetof(GuardRuntimeRecord, objectSlot) == 0x08);
static_assert(offsetof(GuardRuntimeRecord, strategy) == 0x0A);
static_assert(offsetof(GuardRuntimeRecord, state) == 0x0B);
static_assert(offsetof(GuardRuntimeRecord, nextState) == 0x0C);
static_assert(offsetof(GuardRuntimeRecord, savedMapObjectByte) == 0x0D);
static_assert(offsetof(GuardRuntimeRecord, definitionId) == 0x0E);
static_assert(offsetof(GuardRuntimeRecord, syncFlag) == 0x0F);
static_assert(offsetof(GuardRuntimeRecord, strength) == 0x10);
static_assert(offsetof(GuardRuntimeRecord, octant) == 0x11);
static_assert(offsetof(GuardRuntimeRecord, resultOctant) == 0x12);
static_assert(offsetof(GuardRuntimeRecord, moveX) == 0x13);
static_assert(offsetof(GuardRuntimeRecord, moveY) == 0x14);
static_assert(offsetof(GuardRuntimeRecord, unknown15) == 0x15);
static_assert(offsetof(GuardRuntimeRecord, transitionFlag) == 0x16);
static_assert(kGuardCapacity * sizeof(GuardRuntimeRecord) == kGuardSaveSize);

// The dispatcher accepts exactly 0x00..0x15. Only state 0x15 has a final
// high-level name established strongly enough to encode here. The other names
// remain numeric until their animation/sound/movement semantics are complete.
enum class GuardState : std::uint8_t {
    State00 = 0x00,
    State01 = 0x01,
    AlertSequence = 0x02,
    State02 = AlertSequence,
    AttackOpportunityCheck = 0x03,
    State03 = AttackOpportunityCheck,
    AttackExecution = 0x04,
    State04 = AttackExecution,
    MovementReplan = 0x05,
    State05 = MovementReplan,
    TimedMovement = 0x06,
    State06 = TimedMovement,
    StationaryAcquire = 0x07,
    PerceptionDecision = StationaryAcquire,
    State07 = StationaryAcquire,
    MovingAcquire = 0x08,
    State08 = MovingAcquire,
    DeathFinalize = 0x09,
    State09 = DeathFinalize,
    DeadTerminal = 0x0A,
    State0A = DeadTerminal,
    LethalPlayerContact = 0x0B,
    State0B = LethalPlayerContact,
    DormantUseMessage = 0x0C,
    State0C = DormantUseMessage,
    DormantSharedPose = 0x0D,
    State0D = DormantSharedPose,
    State0E = 0x0E,
    State0F = 0x0F,
    State10 = 0x10,
    DoorManeuver = 0x11,
    State11 = DoorManeuver,
    DeathWait = 0x12,
    State12 = DeathWait,
    TimedDirectionalMove = 0x13,
    State13 = TimedDirectionalMove,
    RadioDanceScript = 0x14,
    State14 = RadioDanceScript,
    PainReaction = 0x15,
};

inline constexpr std::size_t kGuardStateCount = 0x16;

inline constexpr std::size_t kGuardStrategyCount = 5;

inline constexpr std::uint8_t kGuardAcquireMaxTileDelta = 8;
inline constexpr std::uint16_t kGuardCloseAttackAxisDistance = 64;

enum class GuardEngagementMode : std::uint8_t {
    CloseProximity = 0,
    LineOfSight = 1,
    LegacyLineOfSight = 2,
};

constexpr bool engagementModeUsesCloseProximity(std::uint8_t mode) noexcept {
    return mode == static_cast<std::uint8_t>(GuardEngagementMode::CloseProximity);
}

constexpr bool engagementModeUsesLineOfSight(std::uint8_t mode) noexcept {
    return mode == static_cast<std::uint8_t>(GuardEngagementMode::LineOfSight) ||
           mode == static_cast<std::uint8_t>(GuardEngagementMode::LegacyLineOfSight);
}

constexpr bool engagementModeHasRecoveredNormalWriter(std::uint8_t mode) noexcept {
    return mode == static_cast<std::uint8_t>(GuardEngagementMode::CloseProximity) ||
           mode == static_cast<std::uint8_t>(GuardEngagementMode::LineOfSight);
}

// B02C initializes engagement mode to LOS (1) and overrides the listed
// close-range classes to mode 0. Mode 2 is accepted by 7594 as LOS-equivalent
// but has no recovered normal writer in Win16 1.3/1.6/1.8/1.10.
constexpr GuardEngagementMode guardInitialEngagementMode(std::uint8_t objectClass) noexcept {
    switch (objectClass) {
    case 0x08: // Bat
    case 0x09: // Frankenstein
    case 0x0A: // Mummy
    case 0x11: // Dracula
    case 0x12: // Cemetery Gargoyle
    case 0x13: // Garden Gargoyle
    case 0x14: // Dracula-Bat
    case 0x1A: // Ghost
        return GuardEngagementMode::CloseProximity;
    default:
        return GuardEngagementMode::LineOfSight;
    }
}

enum class GuardStrategy : std::uint8_t {
    DefaultMovement = 0,
    WoundedDoorSeek = 1,
    RouteMarkerMovement = 2,
    GargoyleOneShot = 3,
    Cannon = 4,
};

constexpr bool isRecoveredGuardStrategy(std::uint8_t strategy) noexcept {
    return strategy < kGuardStrategyCount;
}

constexpr bool strategyUsesAlternateMoveSequence(std::uint8_t strategy) noexcept {
    return strategy == static_cast<std::uint8_t>(GuardStrategy::RouteMarkerMovement);
}

constexpr bool strategySuppressesOrdinaryHitReaction(std::uint8_t strategy) noexcept {
    return strategy == static_cast<std::uint8_t>(GuardStrategy::Cannon);
}

constexpr bool strategyCanEnterTimedOneShotMove(std::uint8_t strategy) noexcept {
    return strategy == static_cast<std::uint8_t>(GuardStrategy::GargoyleOneShot);
}

// State reachability audit:
// - 0x0B is written on lethal guard-to-player contact and has no dispatcher case.
// - 0x0C/0x0D share a static sequence-refresh handler but no normal retail writer
//   was recovered in Win16 1.3/1.6/1.8/1.10 or DOS 1.0/1.7/1.8(=1.9)/2.0.
//   A crafted/restored state can still enter them; 0x0C retains the USE message
//   "I've nothing left!".
// - 0x13 is the strategy-3 timed movement path.
inline constexpr std::uint8_t kGuardStateLethalPlayerContact = 0x0B;
inline constexpr std::uint8_t kGuardStateDormantUseMessage = 0x0C;
inline constexpr std::uint8_t kGuardStateDormantSharedPose = 0x0D;
inline constexpr std::uint8_t kGuardStateStrategy3Movement = 0x13;

constexpr bool isRecoveredRetailDormantGuardState(std::uint8_t state) noexcept {
    return state == kGuardStateDormantUseMessage ||
           state == kGuardStateDormantSharedPose;
}

enum class GuardStateReachability : std::uint8_t {
    NormalRuntime,
    ConditionalRuntime,
    ClassSpecificRuntime,
    ScriptedRuntime,
    Terminal,
    Dormant,
};

// Win16 1.10 producer/reachability closure, cross-checked against the available
// 1.3/1.6/1.8 state-machine exports. Every numeric state has a recovered
// producer category except 0x0C/0x0D, whose handlers survive without a normal
// retail writer.
inline constexpr std::array<GuardStateReachability, kGuardStateCount>
kGuardStateReachability = {
    GuardStateReachability::NormalRuntime,       // 00 sequence wrapper / class-0x21 init
    GuardStateReachability::ConditionalRuntime,  // 01 accepted-fire wake cache
    GuardStateReachability::NormalRuntime,       // 02 wake/detection/strategy return
    GuardStateReachability::NormalRuntime,       // 03 sequence transition
    GuardStateReachability::NormalRuntime,       // 04 sequence transition
    GuardStateReachability::NormalRuntime,       // 05 sequence transition
    GuardStateReachability::NormalRuntime,       // 06 movement planner
    GuardStateReachability::NormalRuntime,       // 07 default init / state-11 return
    GuardStateReachability::NormalRuntime,       // 08 moving init / Dracula transform
    GuardStateReachability::ConditionalRuntime,  // 09 lethal-death finalization
    GuardStateReachability::Terminal,            // 0A ordinary finalized death
    GuardStateReachability::Terminal,            // 0B guard that caused player death
    GuardStateReachability::Dormant,             // 0C no recovered retail writer
    GuardStateReachability::Dormant,             // 0D no recovered retail writer
    GuardStateReachability::ClassSpecificRuntime,// 0E cannon-family initial state
    GuardStateReachability::ClassSpecificRuntime,// 0F cannon-family enabled/wait cycle
    GuardStateReachability::ClassSpecificRuntime,// 10 cannon-family attack cycle
    GuardStateReachability::ConditionalRuntime,  // 11 strategy-1 door maneuver
    GuardStateReachability::ConditionalRuntime,  // 12 lethal wait while OBJECT+1A > 0
    GuardStateReachability::ConditionalRuntime,  // 13 strategy-3 timed movement
    GuardStateReachability::ScriptedRuntime,     // 14 E1M9 Radio/Dancers script
    GuardStateReachability::ConditionalRuntime,  // 15 ordinary non-lethal pain reaction
};

constexpr bool guardStateHasRecoveredRetailProducer(std::uint8_t state) noexcept {
    return state < kGuardStateCount &&
           kGuardStateReachability[state] != GuardStateReachability::Dormant;
}

constexpr bool isGuardTerminalState(std::uint8_t state) noexcept {
    return state < kGuardStateCount &&
           kGuardStateReachability[state] == GuardStateReachability::Terminal;
}

constexpr std::size_t recoveredRetailProducedGuardStateCount() noexcept {
    std::size_t count = 0;
    for (std::size_t i = 0; i < kGuardStateReachability.size(); ++i) {
        if (kGuardStateReachability[i] != GuardStateReachability::Dormant) {
            ++count;
        }
    }
    return count;
}

static_assert(recoveredRetailProducedGuardStateCount() == 20);

inline constexpr std::uint16_t kGuardState13TimerRandomRange = 0x50;
inline constexpr std::uint16_t kGuardState13TimerMinimum = 8;

struct GuardMoveVector {
    std::int8_t dx;
    std::int8_t dy;
};

// FUN_1010_6F2A: facing 0..7 is cardinalized in pairs.
// RouteMarkerMovement (strategy 2) uses 16 world units; other strategies use 8.
constexpr GuardMoveVector guardDirectionalStep(std::uint8_t facing,
                                               std::uint8_t strategy) noexcept {
    constexpr std::array<std::int8_t, 8> dx = {0, 1, 1, 0, 0, -1, -1, 0};
    constexpr std::array<std::int8_t, 8> dy = {-1, 0, 0, 1, 1, 0, 0, -1};
    const auto i = static_cast<std::size_t>(facing & 7u);
    const std::int8_t scale =
        strategy == static_cast<std::uint8_t>(GuardStrategy::RouteMarkerMovement) ? 16 : 8;
    return {
        static_cast<std::int8_t>(dx[i] * scale),
        static_cast<std::int8_t>(dy[i] * scale)
    };
}

struct GuardInitialProfile {
    std::uint8_t strategy;
    std::uint8_t state;
    std::uint8_t nextState;
    std::uint8_t perceptionMode;
};

// FUN_1010_AF7E class-specific initialization. This captures only assignments
// backed by the 2026-09-26 static audit; later movement may promote state to 8.
constexpr GuardInitialProfile guardInitialProfile(std::uint8_t objectClass) noexcept {
    GuardInitialProfile p{
        static_cast<std::uint8_t>(GuardStrategy::DefaultMovement),
        static_cast<std::uint8_t>(GuardState::StationaryAcquire),
        static_cast<std::uint8_t>(GuardState::AlertSequence),
        static_cast<std::uint8_t>(guardInitialEngagementMode(objectClass))};

    switch (objectClass) {
    case 0x12:
    case 0x13:
        p.strategy = static_cast<std::uint8_t>(GuardStrategy::GargoyleOneShot);
        break;
    case 0x15:
    case 0x16:
        p.nextState = 0;
        break;
    case 0x19:
        p.strategy = static_cast<std::uint8_t>(GuardStrategy::Cannon);
        p.state = 0x0E;
        break;
    case 0x21:
        p.state = 0;
        p.nextState = 0;
        break;
    default:
        break;
    }
    return p;
}


struct GuardStrategyInitEvidence {
    std::uint8_t objectClass{};
    std::uint8_t strategy{};
};

// Class-defined strategy writers. Strategies 1/2 are additionally selected from
// the current wall marker class during B02C initialization.
inline constexpr std::array<GuardStrategyInitEvidence, 3> kClassStrategyWriters = {{
    {0x12, static_cast<std::uint8_t>(GuardStrategy::GargoyleOneShot)},
    {0x13, static_cast<std::uint8_t>(GuardStrategy::GargoyleOneShot)},
    {0x19, static_cast<std::uint8_t>(GuardStrategy::Cannon)},
}};

// B02C marker-derived strategy rules.
// 0x42 is RETREAT in the supplied class tables; 0x46 is ACTIONSPOT.
// 0x43 is the third TURN/RETREAT/FLEE-family class in older audited notes, but
// its single supplied tile is unused and its editor label is not independently
// present in the current class CSV, so the code-facing name remains door-seek.
constexpr std::uint8_t strategyForSpawnWallClass(std::uint8_t wallClass) noexcept {
    if (wallClass == 0x43) {
        return static_cast<std::uint8_t>(GuardStrategy::WoundedDoorSeek);
    }
    if (wallClass == 0x42 || wallClass == 0x46) {
        return static_cast<std::uint8_t>(GuardStrategy::RouteMarkerMovement);
    }
    return static_cast<std::uint8_t>(GuardStrategy::DefaultMovement);
}

constexpr bool strategyOneExistsOnlyAsDormantMarkerInSuppliedMaps() noexcept {
    return true; // supplied class inventory reports zero used cells for class 0x43
}

constexpr std::uint16_t guardState13InitialTimer(std::uint16_t randomValue) noexcept {
    return static_cast<std::uint16_t>(
        randomValue % kGuardState13TimerRandomRange + kGuardState13TimerMinimum);
}

// Control-flow summary recovered from the state dispatcher. These are handler
// offsets inside the original segment-3 code, useful for cross-checking IDA /
// Ghidra without pretending that all state names are already known.
inline constexpr std::array<std::uint16_t, kGuardStateCount> kGuardStateHandlerOffsets = {
    0x7BA2, // 00 animation/timer -> nextState
    0x7BE0, // 01 timer -> 02
    0x7BFA, // 02 alert/activation sound+sequence -> 03
    0x7C3C, // 03 attack opportunity/perception check -> 04 or 05
    0x7C86, // 04 attack execution -> 05
    0x7CE4, // 05 movement replanning -> 06
    0x7CEC, // 06 timed movement; timeout -> 03
    0x7D2A, // 07 stationary acquisition; strategy 3 -> 13, else -> 02
    0x7D7E, // 08 moving/marker acquisition; may -> 02
    0x7DEC, // 09 lethal death/special finalization
    0x80A4, // 0A terminal finalized-death state; no local handler
    0x80A4, // 0B terminal killer state after player death; no local handler
    0x7E54, // 0C dormant in recovered retail graph; USE has "I've nothing left!"
    0x7E54, // 0D dormant sibling; same sequence-refresh handler
    0x7E6C, // 0E conditional -> 0F
    0x7E9E, // 0F timer/action -> 10 or 0E
    0x7F26, // 10 timer -> 0F
    0x7F8E, // 11 strategy-1 door maneuver -> strategy=0,state=07
    0x7FEE, // 12 lethal wait/animation -> nextState 09
    0x8038, // 13 strategy-3 timed directional movement
    0x804A, // 14 E1M9 Radio/Dancers scripted movement
    0x807E, // 15 confirmed pain/hit -> nextState
};

// State 0x13 countdown from the 2026-09-24 Win16 audit. The timer always
// decreases, including when the attempted map step is blocked. A step commits
// coordinates/cell occupancy only when targetCellAllowsMove is true.
struct GuardState13StepResult {
    std::uint16_t nextTimer{};
    bool playMovementSound{};
    bool attemptMovement{};
    bool commitMovement{};
    bool clearStrategyAndEnterState2{};
};

constexpr GuardState13StepResult stepGuardState13(
    std::uint16_t currentTimer,
    bool targetCellAllowsMove) noexcept {
    if (currentTimer == 0) {
        return {0, false, false, false, true};
    }

    const std::uint16_t nextTimer =
        static_cast<std::uint16_t>(currentTimer - std::uint16_t{1});
    if (nextTimer == 8) {
        return {nextTimer, true, false, false, false};
    }
    if (nextTimer < 8) {
        return {nextTimer, false, true, targetCellAllowsMove, false};
    }
    return {nextTimer, false, false, false, false};
}

// Original score dispatcher: OBJECT+06 class values 0x08..0x20 map to
// GUARD1..GUARD25. Classes outside that switch return zero. GUARD26/Dancers is
// therefore on the default zero-score path rather than having an entry here.
inline constexpr std::uint8_t kFirstScoredGuardObjectClass = 0x08;
inline constexpr std::uint8_t kLastScoredGuardObjectClass = 0x20;
inline constexpr std::uint8_t kDraculaBatInternalClass = 0x14;
inline constexpr std::uint8_t kGuard25ExecutableOnlyClass = 0x20;
inline constexpr std::uint8_t kGuard26DancersClass = 0x21;
inline constexpr std::uint8_t kGuard26DancersObjectIdEpisode1 = 0x8C;

enum class GuardClassPresence : std::uint8_t {
    NotGuard,
    RetailPlaced,
    InternalTransformOnly,
    ExecutableOnlyFallback,
    RetailScripted,
};

// Shipped class-table audit across the supplied MAP.1-3 families:
// 0x08..0x1F are retail-mapped except 0x14 (Dracula-Bat transform only);
// 0x20 has executable support but no MAP class-table assignment or recovered
// OBJECT+06 writer; 0x21 is GUARD26/Dancers and is retail-placed/scripted.
constexpr GuardClassPresence guardClassPresence(std::uint8_t objectClass) noexcept {
    if (objectClass == kDraculaBatInternalClass) {
        return GuardClassPresence::InternalTransformOnly;
    }
    if (objectClass == kGuard25ExecutableOnlyClass) {
        return GuardClassPresence::ExecutableOnlyFallback;
    }
    if (objectClass == kGuard26DancersClass) {
        return GuardClassPresence::RetailScripted;
    }
    if (objectClass >= 0x08 && objectClass <= 0x1F) {
        return GuardClassPresence::RetailPlaced;
    }
    return GuardClassPresence::NotGuard;
}

constexpr bool hasShippedRetailGuardPlacement(std::uint8_t objectClass) noexcept {
    const auto p = guardClassPresence(objectClass);
    return p == GuardClassPresence::RetailPlaced ||
           p == GuardClassPresence::RetailScripted;
}
inline constexpr std::array<int, 25> kGuardScoreByObjectClass = {
    25,    // 0x08 GUARD1  Bat
    75,    // 0x09 GUARD2  Frankenstein
    50,    // 0x0A GUARD3  Mummy
    100,   // 0x0B GUARD4  Skeleton
    250,   // 0x0C GUARD5  Mrs H.
    150,   // 0x0D GUARD6  Zelda
    200,   // 0x0E GUARD7  Vampira
    100,   // 0x0F GUARD8  Baddie #1
    100,   // 0x10 GUARD9  Baddie #2
    0,     // 0x11 GUARD10 Dracula -- scripted behavior handled separately
    150,   // 0x12 GUARD11 Cemetery Gargoyle
    150,   // 0x13 GUARD12 Garden Gargoyle
    200,   // 0x14 GUARD13 Dracula-Bat internal transform
    -1000, // 0x15 GUARD14 Penelope
    1000,  // 0x16 GUARD15 Dr. Hamerstein
    100,   // 0x17 GUARD16 Tall slim robot
    200,   // 0x18 GUARD17 Trashcan robot
    0,     // 0x19 GUARD18 Cannon
    25,    // 0x1A GUARD19 Ghost
    100,   // 0x1B GUARD20 Goldie
    100,   // 0x1C GUARD21 Greenie
    250,   // 0x1D GUARD22 Demon
    250,   // 0x1E GUARD23 Alien #1
    200,   // 0x1F GUARD24 Alien #2
    50,    // 0x20 GUARD25 executable-only fallback/cut slot
};

constexpr int guardScoreForObjectClass(std::uint8_t objectClass) noexcept {
    if (objectClass < kFirstScoredGuardObjectClass ||
        objectClass > kLastScoredGuardObjectClass) {
        return 0;
    }
    return kGuardScoreByObjectClass[
        static_cast<std::size_t>(objectClass - kFirstScoredGuardObjectClass)];
}

static_assert(guardScoreForObjectClass(0x11) == 0);   // Dracula
static_assert(guardScoreForObjectClass(0x16) == 1000); // Dr. Hamerstein
static_assert(guardScoreForObjectClass(0x1D) == 250);  // Demon
static_assert(guardScoreForObjectClass(0x00) == 0);    // default path



enum class GuardHitDisposition : std::uint8_t {
    Ignored,
    Pain,
    Lethal,
};

struct GuardHitOutcome {
    std::uint8_t strength;
    std::uint8_t resultOctant;
    GuardHitDisposition disposition;
};

// Verified receiver contract from seg3:80F7/811C..81EF.
// Positive non-lethal hits subtract HP and write resoct=8.
// Lethal hits clear HP and branch to death/special handling.
// This helper intentionally does not guess the class-specific death handler.
constexpr GuardHitOutcome receiveGuardDamage(std::uint8_t strength,
                                             int damage,
                                             std::uint8_t currentResultOctant) noexcept {
    if (damage <= 0)
        return {strength, currentResultOctant, GuardHitDisposition::Ignored};
    if (damage >= strength)
        return {0, currentResultOctant, GuardHitDisposition::Lethal};
    return {
        static_cast<std::uint8_t>(strength - damage),
        8,
        GuardHitDisposition::Pain
    };
}

struct DraculaPhase2Reset {
    std::uint8_t objectClass;
    std::uint8_t strength;
    std::uint8_t state;
    std::uint8_t nextState;
    std::uint16_t timer;
    std::uint8_t sequenceValue;
    std::uint8_t eventId;
};

inline constexpr DraculaPhase2Reset kDraculaPhase2Reset{
    0x14, 0xFF, 0x08, 0x02, 1, 0x23, 0x22
};

// Damage receiver is structurally verified: a computed damage value is
// compared with strength. Lethal damage clears strength to zero and enters the
// death path. Positive non-lethal damage is subtracted, resultOctant is set to
// 8, and ordinary pain handling temporarily enters state 0x15 before restoring
// nextState. Player-weapon/class damage transforms are documented in
// docs/COMBAT_DAMAGE_RE.md; they are no longer an unknown producer.

} // namespace nitemare3d::game
