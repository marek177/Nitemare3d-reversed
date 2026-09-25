#pragma once

#include <array>
#include <cstdint>

namespace nitemare3d::re::win16 {

enum class MfcAddressKind16 : std::uint8_t {
    Code,
    Vtable,
    RuntimeClass,
    HandleMap,
    StaticObject,
};

struct MfcAddressFact16 {
    MfcAddressKind16 kind;
    std::uint16_t segment;
    std::uint16_t offset;
    const char* name;
};

inline constexpr std::array<MfcAddressFact16, 33> kMfcAddressCatalog = {{
    {MfcAddressKind16::Code, 1, 0x068A, "runtime IsKindOf/base traversal"},
    {MfcAddressKind16::Code, 1, 0x06C0, "generic runtime CreateObject"},
    {MfcAddressKind16::Code, 1, 0x0730, "runtime create callback dispatch"},
    {MfcAddressKind16::Code, 1, 0x02E2, "CDC Attach"},
    {MfcAddressKind16::Code, 1, 0x0316, "CDC Detach"},
    {MfcAddressKind16::Code, 1, 0x0342, "CDC base cleanup"},
    {MfcAddressKind16::Code, 1, 0x0D0A, "CPaintDC destructor"},
    {MfcAddressKind16::Code, 1, 0x104E, "CDC deleting destructor"},
    {MfcAddressKind16::Code, 1, 0x1070, "CClientDC deleting destructor"},
    {MfcAddressKind16::Code, 1, 0x1092, "CWindowDC deleting destructor"},
    {MfcAddressKind16::Code, 1, 0x10B4, "CPaintDC deleting destructor"},
    {MfcAddressKind16::Code, 1, 0x114A, "CWnd constructor"},
    {MfcAddressKind16::Code, 1, 0x1172, "CWnd constructor(initial HWND)"},
    {MfcAddressKind16::Code, 1, 0x1666, "CWnd teardown"},
    {MfcAddressKind16::Code, 1, 0x171C, "CWnd DestroyWindow/detach"},
    {MfcAddressKind16::Code, 1, 0x1AEC, "CWnd runtime create thunk"},
    {MfcAddressKind16::Code, 1, 0x281E, "CWnd deleting destructor"},
    {MfcAddressKind16::Vtable, 4, 0x49A4, "CWnd vtable"},
    {MfcAddressKind16::RuntimeClass, 10, 0x04EE, "CObject runtime class"},
    {MfcAddressKind16::RuntimeClass, 10, 0x0594, "CWnd runtime class"},
    {MfcAddressKind16::RuntimeClass, 10, 0x0696, "CDC runtime class"},
    {MfcAddressKind16::RuntimeClass, 10, 0x06D6, "CGdiObject runtime class"},
    {MfcAddressKind16::RuntimeClass, 10, 0x0746, "CMenu runtime class"},
    {MfcAddressKind16::RuntimeClass, 10, 0x0756, "CCmdTarget runtime class"},
    {MfcAddressKind16::HandleMap, 10, 0x4250, "CWnd HWND HandleMap"},
    {MfcAddressKind16::HandleMap, 10, 0x44F2, "CDC HDC HandleMap"},
    {MfcAddressKind16::HandleMap, 10, 0x451C, "CGdiObject HGDIOBJ HandleMap"},
    {MfcAddressKind16::HandleMap, 10, 0x4548, "CMenu HMENU HandleMap"},
    {MfcAddressKind16::StaticObject, 10, 0x41D6, "wndTop sentinel"},
    {MfcAddressKind16::StaticObject, 10, 0x41F0, "wndBottom sentinel"},
    {MfcAddressKind16::StaticObject, 10, 0x420A, "wndTopMost sentinel"},
    {MfcAddressKind16::StaticObject, 10, 0x4224, "wndNoTopMost sentinel"},
    {MfcAddressKind16::RuntimeClass, 10, 0x07EC, "CWinApp runtime class"},
}};

constexpr const MfcAddressFact16* findMfcAddress(
    MfcAddressKind16 kind, std::uint16_t segment, std::uint16_t offset) noexcept {
    for (const auto& fact : kMfcAddressCatalog)
        if (fact.kind == kind && fact.segment == segment && fact.offset == offset)
            return &fact;
    return nullptr;
}

} // namespace nitemare3d::re::win16
