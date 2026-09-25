#pragma once
#include <array>
#include <cstdint>
#include <string_view>

namespace n3d::re20260925 {

enum class CoverageState : std::uint8_t { Confirmed, StronglyInferred, Partial, Open };

struct CoverageEntry {
    std::string_view subsystem;
    std::uint8_t minPercent;
    std::uint8_t maxPercent;
    CoverageState state;
};

inline constexpr std::array<CoverageEntry, 10> Coverage{{
    {"renderer-static",80,85,CoverageState::Partial},
    {"player-movement-collision",80,90,CoverageState::Partial},
    {"use-interactions",75,90,CoverageState::Partial},
    {"guard-runtime-ai",75,90,CoverageState::Partial},
    {"object-runtime",70,85,CoverageState::Partial},
    {"hud-uif-menu",60,80,CoverageState::Partial},
    {"img-seqdef-animation",65,80,CoverageState::Partial},
    {"sound-event-mapping",65,85,CoverageState::Partial},
    {"mfc-runtime-init-memory",45,65,CoverageState::Partial},
    {"bsf-registration-integrity",35,50,CoverageState::Open}
}};

} // namespace n3d::re20260925
