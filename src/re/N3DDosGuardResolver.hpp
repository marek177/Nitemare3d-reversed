#pragma once
// Bounded semantic model of NEXT16's seven-DOS-build lookup contract.
// Source: docs/NEXT16_DOS_GUARD_RESOLVER.md. Not a runtime-reachability proof.
#include <cstddef>
#include <cstdint>
#include <span>

namespace n3d::re::dos::guardresolver {
struct FarPointer {
    std::uint16_t offset{}, segment{};
    friend constexpr bool operator==(FarPointer, FarPointer) = default;
};
struct Guard {
    std::uint16_t objectIndex{}; // raw +08 word
    std::uint8_t field0B{}, field0C{}, field0D{};
};
enum class Outcome { Accepted, RejectedMatchExit1, MissingMatchExit1, IncompleteSnapshot };
struct Result {
    Outcome outcome{Outcome::IncompleteSnapshot};
    std::size_t guardIndex{}; // meaningful only for Accepted / RejectedMatchExit1
    std::uint8_t diagnostic0D{}, diagnostic0C{}, diagnostic0B{};
};
// Read WORD with 16-bit effective-address wrapping, without host signed overflow.
inline std::uint16_t word(std::span<const std::uint8_t> bank, std::uint16_t at) noexcept {
    return std::uint16_t(bank[at] | (unsigned(bank[std::uint16_t(at+1u)])<<8u));
}
inline FarPointer mapPointer(std::span<const std::uint8_t> bank, const Guard& g) noexcept {
    // WORLD slot starts at +6; WORLD +12/+14 are OBJECT +0C/+0E.
    const auto at=std::uint16_t(std::uint32_t(g.objectIndex)*28u+0x12u);
    return {word(bank,at),word(bank,std::uint16_t(at+2u))};
}
// Caller supplies semantic GUARD records and both complete segment snapshots.
// This is not the raw GUARD FAR-pointer ABI or a host process termination API.
inline Result resolve(std::span<const Guard> guards, std::int16_t count,
                      std::span<const std::uint8_t> world,
                      std::span<const std::uint8_t> area,
                      FarPointer cell) noexcept {
    if(count<=0) return {Outcome::MissingMatchExit1};
    const auto n=static_cast<std::size_t>(count);
    if(guards.size()<n || world.size()!=65536) return {};
    for(std::size_t i=0;i<n;++i) {
        const auto& g=guards[i];
        if(g.field0B==0x0A || g.field0C==0x09) continue;
        if(mapPointer(world,g)==cell) return {Outcome::Accepted,i};
    }
    if(area.size()!=65536) return {};
    for(std::size_t i=0;i<n;++i) {
        const auto& g=guards[i];
        if(mapPointer(area,g)==cell)
            return {Outcome::RejectedMatchExit1,i,g.field0D,g.field0C,g.field0B};
    }
    return {Outcome::MissingMatchExit1};
}
} // namespace n3d::re::dos::guardresolver
