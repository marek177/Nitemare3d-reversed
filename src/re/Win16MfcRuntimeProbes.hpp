#pragma once

#include <array>
#include <cstdint>

namespace nitemare3d::re::win16 {

enum class RuntimeProbeKind16 : std::uint8_t {
    Breakpoint,
    WatchWrite,
    InspectData,
};

struct RuntimeProbe16 {
    RuntimeProbeKind16 kind;
    std::uint16_t segment;
    std::uint16_t offset;
    const char* label;
};

inline constexpr std::array<RuntimeProbe16, 13> kMfcRuntimeProbes = {{
    {RuntimeProbeKind16::Breakpoint, 1, 0x068A, "CRuntimeClass IsKindOf/base traversal"},
    {RuntimeProbeKind16::Breakpoint, 1, 0x06C0, "generic runtime CreateObject"},
    {RuntimeProbeKind16::Breakpoint, 1, 0x114A, "CWnd default constructor"},
    {RuntimeProbeKind16::Breakpoint, 1, 0x1172, "CWnd pseudo/initial HWND constructor"},
    {RuntimeProbeKind16::Breakpoint, 1, 0x1AEC, "CWnd runtime create thunk"},
    {RuntimeProbeKind16::Breakpoint, 1, 0x1666, "CWnd teardown"},
    {RuntimeProbeKind16::Breakpoint, 1, 0x171C, "CWnd DestroyWindow/detach path"},
    {RuntimeProbeKind16::Breakpoint, 1, 0x281E, "CWnd deleting destructor"},
    {RuntimeProbeKind16::InspectData, 10, 0x4250, "CWnd HWND HandleMap"},
    {RuntimeProbeKind16::InspectData, 10, 0x44F2, "CDC HDC HandleMap"},
    {RuntimeProbeKind16::InspectData, 10, 0x451C, "CGdiObject HGDIOBJ HandleMap"},
    {RuntimeProbeKind16::InspectData, 10, 0x4548, "CMenu HMENU HandleMap"},
    {RuntimeProbeKind16::InspectData, 10, 0x41D6, "first CWnd z-order sentinel"},
}};

struct RuntimeCapture16 {
    std::uint16_t cs;
    std::uint16_t ip;
    std::uint16_t ds;
    std::uint16_t objectOffset;
    std::uint16_t handle;
    std::uint16_t runtimeClassOffset;
    const char* observation;
};

} // namespace nitemare3d::re::win16
