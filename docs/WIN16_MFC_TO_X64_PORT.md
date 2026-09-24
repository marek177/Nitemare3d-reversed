# Win16 MFC memory model -> modern x64 port

The recovered NITE3W MFC/Win16 structures are evidence about original behavior, not a requirement to reproduce Win16 implementation details literally.

## Preserve semantically

A modern port should preserve:

- one logical wrapper per permanently attached native/resource handle;
- temporary wrapper identity for the duration of a temporary-map scope when observable;
- explicit borrowed-versus-owned handle semantics;
- destruction ordering that prevents borrowed handles from being destroyed;
- runtime class/inheritance information where game/framework behavior depends on it;
- resource-cache limits and eviction/lifetime behavior when they affect observable game behavior.

## Replace on Windows 11 x64

Do not reproduce these implementation details in native x64 code:

- 16:16 far pointers/selectors;
- NE relocation chains;
- Win16 Local/Global heap segmented allocation;
- 16-bit HWND/HDC/HGDIOBJ/HMENU storage;
- raw MFC 2.5 vtable addresses;
- the 0x1A-byte binary CWnd object layout;
- Win16 CRuntimeClass pointer representation.

Use native pointer-width types, RAII and explicit ownership. The original offsets remain in `Win16MfcMemory.hpp` only as reverse-engineering evidence.

## Suggested compatibility model

A portable reconstruction can model a wrapper registry as:

```cpp
template<class NativeHandle, class Wrapper>
class HandleRegistry {
public:
    Wrapper* findPermanent(NativeHandle);
    Wrapper* findTemporary(NativeHandle);
    Wrapper& attachPermanent(NativeHandle);
    Wrapper& fromHandle(NativeHandle); // permanent -> temporary -> create borrowed wrapper
    void clearTemporaryScope();
};
```

Temporary wrappers should be marked borrowed. Permanent attachment should make ownership policy explicit instead of inferring it from a Win16 field offset.

## CWnd sentinel translation

The original static CWnd objects with pseudo-HWND values 0, 1, -1 and -2 correspond to z-order roles. In modern code represent these as an enum/value abstraction rather than constructing fake CWnd objects.

```cpp
enum class ZOrderTarget {
    Top,
    Bottom,
    TopMost,
    NoTopMost,
};
```

Translate to the platform API only at the Win32 boundary.

## Runtime classes

The recovered 16-byte `CRuntimeClass16` table is useful for validating original inheritance and object sizes. A modern reconstruction should use normal C++ type information or a small explicit metadata table rather than emulating MFC 2.5's linked runtime-class records.

## Validation rule

Keep two layers separate:

1. **original facts** — exact Win16 addresses, offsets, record sizes and lifecycle evidence;
2. **modern implementation** — safe native-width code that reproduces observable behavior.

This avoids accidentally treating historical ABI details as gameplay requirements.
