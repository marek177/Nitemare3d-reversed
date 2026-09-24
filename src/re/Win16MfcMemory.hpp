#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

namespace nitemare3d::re::win16 {

struct CRuntimeClass16 {
    std::uint32_t classNameFar;
    std::uint16_t objectSize;
    std::uint16_t schema;
    std::uint32_t createObjectFar;
    std::uint16_t baseClassOffset;
    std::uint16_t nextClassOffset;
};
static_assert(sizeof(CRuntimeClass16) == 0x10);

struct HandleMapNode16 {
    std::uint16_t next;
    std::uint16_t bucketIndex;
    std::uint16_t key;
    std::uint16_t value;
};
static_assert(sizeof(HandleMapNode16) == 8);

struct MfcMap16 {
    std::uint32_t vtableFar;
    std::uint16_t buckets;
    std::uint16_t bucketCount;
    std::uint16_t entryCount;
    std::uint16_t freeList;
    std::uint16_t blockChain;
    std::uint16_t nodesPerBlock;
};
static_assert(sizeof(MfcMap16) == 0x10);

struct HandleMap16 {
    MfcMap16 permanent;
    MfcMap16 temporary;
    std::uint16_t tempRuntimeClassOffset;
    std::uint16_t handleFieldOffset;
    std::uint16_t handleCount;
};
static_assert(sizeof(HandleMap16) == 0x26);

inline constexpr std::uint16_t kCWndHandleMapRoot = 0x4250;
inline constexpr std::uint16_t kCDcHandleMapRoot = 0x44F2;
inline constexpr std::uint16_t kCGdiObjectHandleMapRoot = 0x451C;
inline constexpr std::uint16_t kCMenuHandleMapRoot = 0x4548;

inline constexpr std::uint16_t kCObjectRuntimeClass = 0x04EE;
inline constexpr std::uint16_t kCWndRuntimeClass = 0x0594;
inline constexpr std::uint16_t kCFrameWndRuntimeClass = 0x05AC;
inline constexpr std::uint16_t kCViewRuntimeClass = 0x05BC;
inline constexpr std::uint16_t kCControlBarRuntimeClass = 0x05CC;
inline constexpr std::uint16_t kCStatusBarRuntimeClass = 0x05E8;
inline constexpr std::uint16_t kCToolBarRuntimeClass = 0x0604;
inline constexpr std::uint16_t kCDialogBarRuntimeClass = 0x061A;
inline constexpr std::uint16_t kCDialogRuntimeClass = 0x063A;
inline constexpr std::uint16_t kCFileDialogRuntimeClass = 0x0650;
inline constexpr std::uint16_t kCPrintDialogRuntimeClass = 0x0660;
inline constexpr std::uint16_t kCDcRuntimeClass = 0x0696;
inline constexpr std::uint16_t kCClientDcRuntimeClass = 0x06A6;
inline constexpr std::uint16_t kCWindowDcRuntimeClass = 0x06B6;
inline constexpr std::uint16_t kCPaintDcRuntimeClass = 0x06C6;
inline constexpr std::uint16_t kCGdiObjectRuntimeClass = 0x06D6;
inline constexpr std::uint16_t kCPenRuntimeClass = 0x06E6;
inline constexpr std::uint16_t kCBrushRuntimeClass = 0x06F6;
inline constexpr std::uint16_t kCFontRuntimeClass = 0x0706;
inline constexpr std::uint16_t kCBitmapRuntimeClass = 0x0716;
inline constexpr std::uint16_t kCPaletteRuntimeClass = 0x0726;
inline constexpr std::uint16_t kCRgnRuntimeClass = 0x0736;
inline constexpr std::uint16_t kCMenuRuntimeClass = 0x0746;
inline constexpr std::uint16_t kCCmdTargetRuntimeClass = 0x0756;
inline constexpr std::uint16_t kCDocumentRuntimeClass = 0x076E;
inline constexpr std::uint16_t kCDocTemplateRuntimeClass = 0x0784;
inline constexpr std::uint16_t kCSingleDocTemplateRuntimeClass = 0x0794;
inline constexpr std::uint16_t kCSplitterWndRuntimeClass = 0x07AA;
inline constexpr std::uint16_t kCScrollViewRuntimeClass = 0x07BC;
inline constexpr std::uint16_t kCPreviewViewRuntimeClass = 0x07D6;
inline constexpr std::uint16_t kCWinAppRuntimeClass = 0x07EC;

inline constexpr std::uint16_t kCWndVtable = 0x49A4;
inline constexpr std::uint16_t kCWndObjectSize = 0x1A;
inline constexpr std::uint16_t kCWndHwndOffset = 0x14;
inline constexpr std::uint16_t kCWndSecondaryHwndOffset = 0x16;
inline constexpr std::uint16_t kCWndAssociatedObjectOffset = 0x18;

struct FarAddress16 {
    std::uint16_t segment;
    std::uint16_t offset;
};

inline constexpr FarAddress16 kCWndConstructor{1, 0x114A};
inline constexpr FarAddress16 kCWndHandleConstructor{1, 0x1172};
inline constexpr FarAddress16 kCWndCreateObjectThunk{1, 0x1AEC};
inline constexpr FarAddress16 kCWndTeardown{1, 0x1666};
inline constexpr FarAddress16 kCWndDestroyWindowPath{1, 0x171C};
inline constexpr FarAddress16 kCWndDeletingDestructor{1, 0x281E};
inline constexpr FarAddress16 kRuntimeCreateObject{1, 0x06C0};
inline constexpr FarAddress16 kRuntimeIsKindOf{1, 0x068A};
inline constexpr FarAddress16 kRuntimeCreateCallbackDispatch{1, 0x0730};

struct VtableSlot16 {
    std::uint16_t byteOffset;
    FarAddress16 target;
    const char* role;
};

inline constexpr std::array<VtableSlot16, 20> kCWndVtableSlots = {{
    {0x00, {1, 0x1B0C}, "runtime-class getter"},
    {0x04, {1, 0x281E}, "deleting destructor"},
    {0x08, {3, 0x0464}, "inherited virtual"},
    {0x0C, {1, 0x06B8}, "inherited virtual"},
    {0x10, {1, 0x06BC}, "inherited virtual"},
    {0x14, {1, 0x35C8}, "inherited virtual"},
    {0x18, {1, 0x16FA}, "window lifecycle dispatch"},
    {0x1C, {1, 0x1B12}, "runtime/class helper"},
    {0x20, {1, 0x36D4}, "inherited virtual"},
    {0x24, {1, 0x36CA}, "inherited virtual"},
    {0x28, {1, 0x36FA}, "inherited virtual"},
    {0x2C, {1, 0x3700}, "inherited virtual"},
    {0x30, {1, 0x1606}, "window virtual"},
    {0x34, {1, 0x171C}, "DestroyWindow/detach path"},
    {0x38, {1, 0x15E6}, "window virtual"},
    {0x3C, {1, 0x2448}, "window virtual"},
    {0x40, {1, 0x2116}, "window virtual"},
    {0x44, {1, 0x1A1A}, "window virtual"},
    {0x48, {1, 0x1E9C}, "window virtual"},
    {0x4C, {1, 0x17B2}, "window virtual"},
}};

struct SentinelWnd {
    std::uint16_t objectOffset;
    std::int16_t pseudoHwnd;
    const char* role;
};

inline constexpr std::array<SentinelWnd, 4> kCWndSentinels = {{
    {0x41D6, 0, "wndTop"},
    {0x41F0, 1, "wndBottom"},
    {0x420A, -1, "wndTopMost"},
    {0x4224, -2, "wndNoTopMost"},
}};

struct RuntimeClassFact {
    std::uint16_t offset;
    const char* name;
    std::uint16_t objectSize;
    std::uint16_t base;
};

inline constexpr std::array<RuntimeClassFact, 31> kRuntimeClasses = {{
    {kCObjectRuntimeClass, "CObject", 0x04, 0},
    {kCWndRuntimeClass, "CWnd", 0x1A, kCCmdTargetRuntimeClass},
    {kCFrameWndRuntimeClass, "CFrameWnd", 0x4E, kCWndRuntimeClass},
    {kCViewRuntimeClass, "CView", 0x1C, kCWndRuntimeClass},
    {kCControlBarRuntimeClass, "CControlBar", 0x2E, kCWndRuntimeClass},
    {kCStatusBarRuntimeClass, "CStatusBar", 0x32, kCControlBarRuntimeClass},
    {kCToolBarRuntimeClass, "CToolBar", 0x3E, kCControlBarRuntimeClass},
    {kCDialogBarRuntimeClass, "CDialogBar", 0x2E, kCControlBarRuntimeClass},
    {kCDialogRuntimeClass, "CDialog", 0x24, kCWndRuntimeClass},
    {kCFileDialogRuntimeClass, "CFileDialog", 0x1B8, kCDialogRuntimeClass},
    {kCPrintDialogRuntimeClass, "CPrintDialog", 0x5C, kCDialogRuntimeClass},
    {kCDcRuntimeClass, "CDC", 0x0A, kCObjectRuntimeClass},
    {kCClientDcRuntimeClass, "CClientDC", 0x0C, kCDcRuntimeClass},
    {kCWindowDcRuntimeClass, "CWindowDC", 0x0C, kCDcRuntimeClass},
    {kCPaintDcRuntimeClass, "CPaintDC", 0x2C, kCDcRuntimeClass},
    {kCGdiObjectRuntimeClass, "CGdiObject", 0x06, kCObjectRuntimeClass},
    {kCPenRuntimeClass, "CPen", 0x06, kCGdiObjectRuntimeClass},
    {kCBrushRuntimeClass, "CBrush", 0x06, kCGdiObjectRuntimeClass},
    {kCFontRuntimeClass, "CFont", 0x06, kCGdiObjectRuntimeClass},
    {kCBitmapRuntimeClass, "CBitmap", 0x06, kCGdiObjectRuntimeClass},
    {kCPaletteRuntimeClass, "CPalette", 0x06, kCGdiObjectRuntimeClass},
    {kCRgnRuntimeClass, "CRgn", 0x06, kCGdiObjectRuntimeClass},
    {kCMenuRuntimeClass, "CMenu", 0x06, kCObjectRuntimeClass},
    {kCCmdTargetRuntimeClass, "CCmdTarget", 0x14, kCObjectRuntimeClass},
    {kCDocumentRuntimeClass, "CDocument", 0x36, kCCmdTargetRuntimeClass},
    {kCDocTemplateRuntimeClass, "CDocTemplate", 0x36, kCCmdTargetRuntimeClass},
    {kCSingleDocTemplateRuntimeClass, "CSingleDocTemplate", 0x38, kCDocTemplateRuntimeClass},
    {kCSplitterWndRuntimeClass, "CSplitterWnd", 0x52, kCWndRuntimeClass},
    {kCScrollViewRuntimeClass, "CScrollView", 0x32, kCViewRuntimeClass},
    {kCPreviewViewRuntimeClass, "CPreviewView", 0x8A, kCScrollViewRuntimeClass},
    {kCWinAppRuntimeClass, "CWinApp", 0x8E, kCCmdTargetRuntimeClass},
}};

} // namespace nitemare3d::re::win16
