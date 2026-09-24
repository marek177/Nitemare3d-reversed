# Win16 MFC and memory reconstruction — 2026-09-25

This note records the direct-binary findings recovered from the audited NITE3W Win16 NE executable (SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`).

## Handle maps

Four MFC handle maps are statically recovered:

- `0x4250` — CWnd / HWND
- `0x44F2` — CDC / HDC, two handle fields
- `0x451C` — CGdiObject / HGDIOBJ
- `0x4548` — CMenu / HMENU

The common HandleMap layout is 0x26 bytes: two 0x10-byte hash maps followed by runtime-class, handle-offset and handle-count fields. Hash buckets use `(handle >> 4) % bucketCount`, separate chaining and 8-byte nodes.

## Temporary wrappers

`FromHandle` first checks the permanent map, then the temporary map, then creates a wrapper through the map's runtime class. Temporary wrappers are destroyed when the MFC temporary-map nesting count reaches zero. Handles are cleared before the virtual deleting destructor runs so borrowed Win16 handles are not destroyed by the wrapper destructor.

## CRuntimeClass16

Relocation-aware parsing of NE segment 10 recovers a 16-byte runtime-class record:

```cpp
struct CRuntimeClass16 {
    uint32_t classNameFar;
    uint16_t objectSize;
    uint16_t schema;
    uint32_t createObjectFar;
    uint16_t baseClassOffset;
    uint16_t nextClassOffset;
};
```

Important descriptors include CObject `04EE`, CWnd `0594`, CFrameWnd `05AC`, CView `05BC`, CControlBar `05CC`, CDC `0696`, CGdiObject `06D6`, CMenu `0746`, CCmdTarget `0756`, CDocument `076E`, CDocTemplate `0784` and CWinApp `07EC`.

## CWnd

The CWnd descriptor reports an object size of 0x1A bytes. The constructor at `1:114A` initializes the CWnd vtable and clears fields at +0x14, +0x16 and +0x18.

Recovered field semantics:

- +0x14: primary HWND
- +0x16: secondary HWND-like context/override; callers fall back to GetParent(+0x14) when zero
- +0x18: associated polymorphic MFC object/reference, cleared during teardown

The CWnd vtable begins at `4:49A4`. The deleting destructor points to `1:281E`; the teardown path uses `1:1666` and normal HWND destruction uses `1:171C`.

Four global CWnd sentinels are constructed with pseudo handles 0, 1, -1 and -2 at object offsets `41D6`, `41F0`, `420A`, `4224`, matching the MFC z-order sentinels wndTop, wndBottom, wndTopMost and wndNoTopMost. They are excluded from normal DestroyWindow ownership.

## Far heap and caches

The Win16 CRT far allocator uses 2-byte block headers: bit 0 is the free flag and the remaining bits hold the even payload size. It performs block splitting, adjacent free-block coalescing and arena growth through GlobalReAlloc. End-of-arena sentinel is 0xFFFE.

Recovered resource memory domains include:

- wall texture cache: 20 slots, 0x2000-byte payloads
- sprite/image cache: dynamic 1..128 slots
- audio sample cache: 20 slots, 0x4000-byte payloads plus 6-byte metadata
- oversized audio resources: dedicated HGLOBAL path

These are historical Win16 implementation details. A modern port should preserve observable cache/resource behavior rather than reproduce segmented allocation literally.


## CWnd constructor, create thunk and vtable anchors

The CWnd runtime descriptor at segment-10 offset `0594` reports a 0x1A-byte object and its create callback resolves to `1:1AEC`. That thunk invokes the constructor at `1:114A`. The alternate constructor at `1:1172` accepts the initial/pseudo HWND used by the four global z-order sentinels.

The recovered lifecycle anchors are:

- `1:068A` — runtime-class base traversal / IsKindOf-like helper
- `1:06C0` — generic runtime object allocation/create path
- `1:0730` — create-callback dispatcher
- `1:114A` — CWnd default constructor
- `1:1172` — CWnd constructor with initial HWND/pseudo-HWND
- `1:1AEC` — CWnd CRuntimeClass create thunk
- `1:1666` — CWnd teardown/destructor body
- `1:171C` — normal DestroyWindow + detach path
- `1:281E` — CWnd deleting destructor

The CWnd vtable starts at `4:49A4`. Relocation-aware decoding confirms at least the first 20 slots through byte offset `+4C`; notably `+00 -> 1:1B0C`, `+04 -> 1:281E`, `+18 -> 1:16FA`, and `+34 -> 1:171C`. The `+34` target independently closes the lifecycle dispatch observed in `1:16FA`.
