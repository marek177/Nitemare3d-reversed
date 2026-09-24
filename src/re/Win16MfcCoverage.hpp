#pragma once

#include <array>
#include <cstdint>

namespace nitemare3d::re::win16 {

enum class MfcCoverageState16 : std::uint8_t {
    StaticClosed,
    StaticStrong,
    RuntimePending,
};

struct MfcCoverageArea16 {
    const char* area;
    MfcCoverageState16 state;
    const char* remaining;
};

inline constexpr std::array<MfcCoverageArea16, 9> kMfcCoverage = {{
    {"CRuntimeClass binary layout", MfcCoverageState16::StaticClosed, "runtime trace not required for layout"},
    {"MFC class hierarchy", MfcCoverageState16::StaticClosed, "only additional unused classes if discovered"},
    {"HandleMap structure/hash", MfcCoverageState16::StaticClosed, "runtime trace for behavioral confirmation"},
    {"CWnd object size/HWND field", MfcCoverageState16::StaticClosed, "none statically significant"},
    {"CWnd constructors/destructors/vtable anchors", MfcCoverageState16::StaticClosed, "runtime call-order confirmation"},
    {"CWnd +0x16 semantic name", MfcCoverageState16::StaticStrong, "observe exact runtime callers/values"},
    {"CWnd +0x18 semantic name", MfcCoverageState16::StaticStrong, "identify concrete associated object type"},
    {"temporary/permanent wrapper lifecycle", MfcCoverageState16::RuntimePending, "Win3.1 identity/cleanup trace"},
    {"CDC/GDI/Menu runtime ownership", MfcCoverageState16::RuntimePending, "Win3.1 handle-lifetime trace"},
}};

constexpr std::size_t countCoverage(MfcCoverageState16 state) noexcept {
    std::size_t count = 0;
    for (const auto& area : kMfcCoverage)
        if (area.state == state) ++count;
    return count;
}

} // namespace nitemare3d::re::win16
