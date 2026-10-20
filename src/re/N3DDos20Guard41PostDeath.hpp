#pragma once
// Bounded report-derived DOS2 capture contract; not an N3DTRC01 parser.
// Provenance and unavailable raw-trace validation: docs/DOS20_GUARD41_POSTDEATH.md.
#include <cstdint>
namespace n3d::re::dos20::guard41 {
struct CaptureGate {
    std::uint16_t cs{}, ip{}, es{}, si{};
    std::uint8_t al{}, oldState{}, newState{};
    std::uint32_t writeLinear{};
};
// Full observed state-write identity: the same writer/actor also emitted 00->05.
// Caller must obtain all values from an authenticated, correlated CPU/W pair.
constexpr bool isObservedPostDeathWriter(const CaptureGate& g) noexcept {
    return g.cs==0x0CEB && g.ip==0x0E03 && g.es==0x2A21 && g.si==0x2A78 &&
           g.al==0x09 && g.oldState==0x00 && g.newState==0x09 &&
           g.writeLinear==0x2CC93;
}
inline constexpr CaptureGate kState0To9{0x0CEB,0x0E03,0x2A21,0x2A78,9,0,9,0x2CC93};
inline constexpr CaptureGate kPreDeathControl{0x0CEB,0x0E03,0x2A21,0x2A78,5,0,5,0x2CC93};
struct TraceBoundary {
    std::uint32_t cpu{}, reads{}, writes{};
    bool epilogueEntered{};
    const char* sha256{};
};
inline constexpr TraceBoundary kState0To9Trace{15000,42387,3318,false,
    "fc18b45497dcf52961e3840c7d62c6f0ffd438471763d4a2a10db3928997dc5f"};
inline constexpr TraceBoundary kState9TraceA{12000,39615,14453,true,
    "89a7ef6bb783cabaaa23a7e00ac7218aac167259b58d35765df251470d7b80b7"};
inline constexpr TraceBoundary kState9TraceB{4600,18692,12771,true,
    "52ac2aec7500e350b5c4368a38197e1025a42788641f454d81aa146d87fe9e05"};
inline constexpr TraceBoundary kDos12Reference{4235,17665,12675,false,
    "84cd4bf0c69b9a18f0d304499dc9e430bb90555df0e377728ca3a1e61c72bb6e"};
inline constexpr std::uint32_t kRngBefore=0xAEA69ED3, kRngAfter=0x12DBCE4A;
inline constexpr std::uint16_t kRngResult=4827;
inline constexpr unsigned kWorldFlagWriteCpu=15, kState9WriteCpu=17;
inline constexpr unsigned kRngLowWriteCpu=81, kRngHighWriteCpu=82;
inline constexpr std::uint8_t kWallId=0xBB, kWallProperty=0;
// Evidence status of this specific reported route, not global parity flags.
inline constexpr bool kDos20NaturalState09Reported=true;
inline constexpr bool kContinuousFatalToState0AProven=false;
inline constexpr bool kAllDropAndCleanupPathsClosed=false;
inline constexpr bool kRawTracesReverifiedInThisIntegration=false;
} // namespace n3d::re::dos20::guard41
