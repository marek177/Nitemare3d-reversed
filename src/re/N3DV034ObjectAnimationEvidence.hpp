#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <string_view>

namespace n3d::re::v034 {

// All offsets are into the SHA-256-identified DOS v2.0 UNPACKED MZ LOAD IMAGE,
// not a packed EXE file, current CPU CS:IP, or Win16 NE segment offset.
// Direct machine-code edges are statically proven. No original runtime trace
// or exhaustive indirect-call census is claimed.
enum class Confidence : std::uint8_t {
    VerifiedOriginalStatic,
    RuntimeOpen
};

enum class CallEncoding : std::uint8_t { Near16, Far16 };

enum class Role : std::uint8_t {
    Fast,
    EmptyFastHook,
    OuterScheduler,
    RenderFrame,
    BuildSpans,
    RenderSpans,
    ProjectSortedObject,
    SpriteProjection,
    SpanFrameAnimation,
    ProjectedObjectAnimation,
    ProjectedDirectionalAnimation,
    PushUpdate,
    PanelUpdate,
    ProjectileUpdate,
};

struct DirectCall {
    std::uint16_t site;              // original IMAGE-relative call opcode
    std::uint32_t targetImageOffset; // far seg*16+off or near + signed displacement
    CallEncoding encoding;
    Role role;
    std::string_view evidence;
};

inline constexpr std::array<DirectCall, 16> kOriginalDirectCalls = {{
    {0xC153, 0xC51A, CallEncoding::Far16, Role::EmptyFastHook,
     "C51A consists of RETF; not an all-object scheduler"},
    {0xC172, 0x0E50, CallEncoding::Far16, Role::PushUpdate,
     "FAST calls six-byte PUSH updater, v0.33"},
    {0xC1EA, 0xC150, CallEncoding::Near16, Role::Fast,
     "normal FAST call from outer time bucket"},
    {0xC22E, 0xC150, CallEncoding::Near16, Role::Fast,
     "DEMO odd-frame conditional FAST call"},
    {0xC239, 0xBF36, CallEncoding::Near16, Role::RenderFrame,
     "frame-update branch calls renderer"},
    {0xBF40, 0x213E, CallEncoding::Far16, Role::BuildSpans,
     "build/reset span list"},
    {0xBF5A, 0x2500, CallEncoding::Far16, Role::RenderSpans,
     "iterate wall/span rasterization and optional 241E frame updates"},
    {0xBF5F, 0x21F0, CallEncoding::Far16, Role::ProjectSortedObject,
     "iterate sorted scene object pointers"},
    {0x2721, 0x241E, CallEncoding::Near16, Role::SpanFrameAnimation,
     "descriptor interval nonzero gate at 2716"},
    {0x2225, 0xB2D4, CallEncoding::Far16, Role::SpriteProjection,
     "selected object projection via sorted scene path"},
    {0x8307, 0xB2D4, CallEncoding::Far16, Role::SpriteProjection,
     "projectile update also submits projection"},
    {0xB521, 0xB22C, CallEncoding::Near16, Role::ProjectedObjectAnimation,
     "after projection/clipping: normal eligible object animation"},
    {0xB532, 0xB17E, CallEncoding::Near16, Role::ProjectedDirectionalAnimation,
     "after projection/clipping: alternate class-specific animation"},
    {0xC246, 0x0AEA, CallEncoding::Far16, Role::PanelUpdate,
     "frame branch moves secret-panel VEC geometry"},
    {0xC24B, 0x8230, CallEncoding::Far16, Role::ProjectileUpdate,
     "frame branch updates projectile pool"},
    {0xBF64, 0x273C, CallEncoding::Far16, Role::RenderFrame,
     "renderer overlay/other display pass; semantics not fully named"},
}};

constexpr const DirectCall* callAt(std::uint16_t site) noexcept {
    for (const auto& call : kOriginalDirectCalls)
        if (call.site == site) return &call;
    return nullptr;
}

constexpr bool isDirectTarget(std::uint16_t callSite,
                              std::uint32_t target) noexcept {
    const auto* edge = callAt(callSite);
    return edge != nullptr && edge->targetImageOffset == target;
}

// In the frame bucket C21A tests DEMO mode, then C221 tests the *existing*
// render-generation DS:4540 bit0. If set, C22E calls FAST, BEFORE the
// frame renderer BF36 increments DS:4540 at BF36. This narrow branch rule
// does NOT assert how many frame buckets the outer loop executes or what
// reentrant callbacks do.
constexpr bool demoFrameBranchCallsFast(bool frameBucketDue,
                                        bool demoModeNonzero,
                                        std::uint32_t renderGenerationBefore) noexcept {
    return frameBucketDue && demoModeNonzero &&
           (renderGenerationBefore & 1u) != 0u;
}

inline constexpr std::uint16_t kSpanAnimator = 0x241E;
inline constexpr std::uint16_t kSpanAnimatorCaller = 0x2721;
inline constexpr std::uint16_t kSpanFrameIncrement = 0x2433;
inline constexpr std::uint16_t kSpanRngDrawSite = 0x2478;
inline constexpr std::uint16_t kProjectedAnimator = 0xB22C;
inline constexpr std::uint16_t kProjectedFrameIncrement = 0xB242;
inline constexpr std::uint16_t kDirectionalAnimator = 0xB17E;
inline constexpr std::uint16_t kDirectionalFrameIncrement = 0xB1B9;
inline constexpr std::uint16_t kCurrentClockLowWord = 0x081E;
inline constexpr std::uint8_t kObjectFrameField = 0x03;
inline constexpr std::uint8_t kObjectSequenceSelectorField = 0x04;
inline constexpr std::uint8_t kObjectProjectionFlagField = 0x05;
inline constexpr std::uint8_t kObjectAnimationDeadlineOffset = 0x08;
inline constexpr std::uint16_t kSpanPoolCount = 0x4D64;
inline constexpr std::uint16_t kSpanPoolBase = 0x4D6E;

// Underlying code uses 32-bit unsigned JA after comparing deadline with
// current DS:081E clock. Equal deadline is due; a future deadline skips.
// This models the local comparison only, not IRQ wraparound/clock catch-up.
constexpr bool animationDeadlineDue(std::uint32_t deadline,
                                    std::uint32_t observedCurrentTime) noexcept {
    return deadline <= observedCurrentTime;
}

// The source has no "advance all objects" call at these sites:
// 2500 -> 241E requires span processing AND descriptor interval != 0.
// B2D4 -> B22C/B17E requires projection to pass geometry/clipping gates.
// Other GUARD, projectile and special animation writers also exist.
constexpr bool spanAnimationCanRun(bool spanProcessed,
                                   std::uint16_t descriptorInterval,
                                   std::uint32_t deadline,
                                   std::uint32_t now) noexcept {
    return spanProcessed && descriptorInterval != 0 &&
           animationDeadlineDue(deadline, now);
}

// B2D4 chooses regular B22C for non-directional classes only when the
// descriptor interval (+2) is nonzero. Class 0x05 is skipped entirely.
constexpr bool projectedRegularAnimationCanRun(bool projectionAccepted,
                                               std::uint8_t objectFlags,
                                               std::uint8_t objectClass,
                                               std::uint16_t descriptorInterval,
                                               std::uint32_t deadline,
                                               std::uint32_t now) noexcept {
    return projectionAccepted && (objectFlags & 0x01u) != 0 &&
           objectClass != 0x05 &&
           objectClass != 0x2C && objectClass != 0x2D &&
           descriptorInterval != 0 && animationDeadlineDue(deadline, now);
}

// Class 0x2C/0x2D goes to B17E without the descriptor +2 interval gate.
// Its own deadline is checked inside B17E. Do not reuse the regular gate.
constexpr bool projectedDirectionalAnimationCanRun(bool projectionAccepted,
                                                   std::uint8_t objectFlags,
                                                   std::uint8_t objectClass,
                                                   std::uint32_t deadline,
                                                   std::uint32_t now) noexcept {
    return projectionAccepted && (objectFlags & 0x01u) != 0 &&
           (objectClass == 0x2C || objectClass == 0x2D) &&
           animationDeadlineDue(deadline, now);
}

inline constexpr Confidence kThreeAnimatorSitesConfidence =
    Confidence::VerifiedOriginalStatic;
inline constexpr Confidence kCompleteObjectWriterCensusConfidence =
    Confidence::RuntimeOpen;
inline constexpr Confidence kExactFastFrameRngChronologyConfidence =
    Confidence::RuntimeOpen;
inline constexpr bool kMonolithicObjectSchedulerIdentified = false;

} // namespace n3d::re::v034
