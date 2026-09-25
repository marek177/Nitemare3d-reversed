#pragma once
#include <array>
#include <cstdint>
#include <optional>
#include <string_view>
#include <vector>

namespace n3d::re {

enum class Evidence : uint8_t { Confirmed, Inferred, Unknown };

inline constexpr std::size_t kMaxVec = 1000;
inline constexpr std::size_t kMaxObjects = 350;
inline constexpr std::size_t kMaxGuards = 100;
inline constexpr std::size_t kMaxDoorControllers = 64;
inline constexpr std::size_t kMaxSecretPanels = 32;
inline constexpr std::size_t kMaxPushObjects = 12;
inline constexpr std::size_t kMaxProjectiles = 8;
inline constexpr std::size_t kMaxVisibleSpans = 50;
inline constexpr std::size_t kMapWidth = 64;
inline constexpr std::size_t kMapHeight = 64;

inline constexpr std::size_t kVecStride = 28;
inline constexpr std::size_t kObjectStride = 28;
inline constexpr std::size_t kGuardStride = 26;
inline constexpr std::size_t kDoorStride = 22;
inline constexpr std::size_t kPushStride = 6;
inline constexpr std::size_t kProjectileStride = 42;
inline constexpr std::size_t kVisibleSpanStride = 20;

enum InputMask : uint16_t {
    InputEscape = 0x0001, InputForward = 0x0002, InputBackward = 0x0004,
    InputTurnLeft = 0x0008, InputTurnRight = 0x0010, InputUse = 0x0200,
};

enum class ObjectClass : uint8_t {
    Fire=7, Bat=8, Frankenstein=9, Mummy=10, Skeleton=11, MrsHamerstein=12,
    Zelda=13, Vampira=14, Baddie1=15, Baddie2=16, Dracula=17,
    CemeteryGargoyle=18, GardenGargoyle=19, Unknown20=20, Penelope=21,
    DrHamerstein=22, TallSlimRobot=23, TrashcanRobot=24, Cannon=25,
    Ghost=26, Goldie=27, Greenie=28, Demon=29, Alien1=30, Alien2=31, Unknown32=32
};

enum class GuardState : uint8_t {
    AnimateLoop=0x00, Delay=0x01, Wake=0x02, Acquire=0x03, Attack=0x04,
    Plan=0x05, Move=0x06, WaitForLos=0x07, WallMove=0x08, Interact=0x09,
    NoDirectBranch0A=0x0A, Disabled=0x0B, Directional0C=0x0C,
    Directional0D=0x0D, CannonIdle=0x0E, CannonCycle=0x0F,
    CannonAttack=0x10, RecoverMove=0x11, SequenceOffset=0x12,
    Strategy3=0x13, GlobalTimed=0x14, HitReaction=0x15,
};

enum class GuardStrategy : uint8_t {
    Generic=0, LowHpTargetSearch=1, AlternateMove=2, SpecialWall=3, HitReactionSuppressed=4,
};

#pragma pack(push,1)
struct GuardRecord {
    uint8_t unk00[2];
    uint32_t renderStamp;
    int16_t timer;
    uint16_t linkedObjectIndex;
    uint8_t strategy;
    uint8_t state;
    uint8_t nextState;
    uint8_t underlyingMapObject;
    uint8_t areaSelector;
    uint8_t directionMode;
    uint8_t hp;
    uint8_t facing;
    uint8_t sequenceDirectionKey;
    int8_t moveX;
    int8_t moveY;
    uint8_t unk15;
    uint8_t perceptionMode;
    uint8_t losResult;
    uint8_t proximityResult;
    uint8_t unk19;
};
static_assert(sizeof(GuardRecord)==kGuardStride);

struct ObjectRecord {
    uint8_t unk00[3];
    uint8_t frame;
    uint8_t sequenceSelector;
    uint8_t flags;
    uint8_t objectClass;
    uint8_t unk07;
    uint32_t animationDeadline;
    uint8_t unk0C[4];
    int16_t worldX;
    int16_t worldY;
    uint8_t type;
    uint8_t unk15[3];
    int16_t projectedBaseRow;
    int16_t verticalOffset;
};
static_assert(sizeof(ObjectRecord)==kObjectStride);

struct DemoEventWin16 {
    uint8_t keyEvent;
    uint16_t inputMask;
    uint8_t unused;
    uint32_t generation;
};
static_assert(sizeof(DemoEventWin16)==8);
#pragma pack(pop)

struct ProjectileSlot { std::array<uint8_t,14> motion{}; ObjectRecord object{}; };
static_assert(sizeof(ProjectileSlot)==kProjectileStride);

struct GameEventFlags {
    uint8_t secretPanelMask=0, cannonEnabled=1, storyLatch=0, oneShotH=0,
            eventG=0, eventA9=0, eventAA=0, darkEvent=0;
};

class N3dRng {
public:
    explicit N3dRng(uint32_t seed=1):state_(seed){}
    uint16_t next();
    uint32_t state() const { return state_; }
    void seed(uint32_t s){state_=s;}
private: uint32_t state_;
};

int16_t scoreForClass(uint8_t objectClass);

struct DamageInput {
    int16_t projectedBaseRow;
    int16_t viewportCenterY;
    uint8_t objectClass;
    uint8_t weaponSelector;
    uint8_t difficulty;
    uint8_t episode;
    uint16_t rngValue;
};
struct DamageResult {
    int rawSeed;
    int transformed;
    int afterDifficulty;
    uint8_t storedByte;
    Evidence confidence;
};
DamageResult computeDamage(const DamageInput&);
std::optional<uint8_t> fireDamagePerSlowUpdate(uint8_t mapObjectId);
std::array<int8_t,8> guardMoveX();
std::array<int8_t,8> guardMoveY();

struct GuardTickInput {
    bool globalBlock4BE7=false, los=false, perception7594=false,
         cannonGate51A5=true, globalGameStateIs2=false;
};
struct GuardTickResult {
    GuardState state;
    int16_t timer;
    bool needsStrategyPlan=false, shouldAttackPlayer=false,
         shouldRefreshDirectionSequence=false, unresolvedSideEffect=false;
};
GuardTickResult tickGuardCore(GuardState,int16_t,GuardState,GuardStrategy,const GuardTickInput&);

struct Placement {
    uint8_t episode, level, guard;
    std::string_view name;
    uint16_t count;
    bool playable;
};
const std::vector<Placement>& placements();
uint32_t guardCountForLevel(uint8_t,uint8_t);
uint32_t guardCountForEpisode(uint8_t);
uint32_t totalPlayableGuardPlacements();
int64_t oneAwardPerPlacementBaseline(bool excludePenelopePenalty=false);
int32_t inferredLevelCompletionBonus(uint16_t enemiesRemaining,uint16_t panelsMissing);

enum class GuardCategory : uint8_t { Combat, WallEnemy, NPC, PuzzleActor, BossOrScripted, Hazard, Unknown };
GuardCategory categoryForGuard(uint8_t guard);

} // namespace n3d::re
