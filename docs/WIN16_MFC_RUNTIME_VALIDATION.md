# Win16 MFC runtime validation checklist

Static analysis of the MFC/memory layer is now substantially closed. These debugger observations are the remaining high-value checks against a real Windows 3.1 NITE3W run.

## Test 1 — temporary CWnd FromHandle lifecycle

1. Break on the generic HandleMap FromHandle path for the CWnd map rooted at data offset `0x4250`.
2. Choose an HWND that is not permanently attached.
3. Record permanent-map lookup result.
4. Record temporary-map lookup result.
5. On miss, verify allocation size `0x1A` and the CWnd runtime descriptor `0x0594`.
6. Verify create thunk `1:1AEC` reaches constructor `1:114A`.
7. Verify the HWND is written at wrapper offset `+0x14`.
8. Call FromHandle again in the same temporary scope and verify wrapper identity is reused.
9. At temporary-map cleanup/nesting zero, verify `+0x14` is cleared before the deleting destructor.
10. Verify the borrowed HWND itself survives wrapper destruction.

Expected result: permanent -> temporary -> allocate-on-miss, stable temporary identity within the scope, no DestroyWindow for the borrowed handle.

## Test 2 — permanent CWnd ownership

1. Break on CWnd attach/detach.
2. Attach a real HWND and verify insertion in the permanent half of HandleMap `0x4250`.
3. Verify later FromHandle returns the permanent wrapper before consulting/creating a temporary wrapper.
4. Detach and verify map removal and `m_hWnd (+0x14) = 0`.

## Test 3 — CWnd destruction

Break at:

- `1:1666` — teardown body
- `1:171C` — DestroyWindow/detach path
- `1:281E` — deleting destructor

For an owned normal window, verify the path reaches `1:171C`. For a borrowed temporary wrapper, verify handle clearing prevents the same ownership path.

## Test 4 — z-order sentinels

Inspect the four static objects:

| object | expected pseudo HWND |
|---|---:|
| `1048:41D6` | 0 |
| `1048:41F0` | 1 |
| `1048:420A` | -1 / FFFF |
| `1048:4224` | -2 / FFFE |

Verify their use as insert-after/z-order arguments and verify teardown does not call DestroyWindow on these pseudo handles.

## Test 5 — CDC two-handle wrapper

Use HandleMap root `0x44F2`. Verify a temporary CDC wrapper maintains the recovered two-handle relationship and that temporary cleanup clears borrowed HDC state before deletion.

## Test 6 — CGdiObject and CMenu

Repeat temporary/permanent lookup checks for:

- CGdiObject map `0x451C`, runtime class `0x06D6`
- CMenu map `0x4548`, runtime class `0x0746`

Confirm wrapper handle field `+0x04` and borrowed-handle cleanup.

## Test 7 — CRuntimeClass ancestry

Break at the IsKindOf-like traversal `1:068A` and test objects from at least:

- CFrameWnd -> CWnd -> CCmdTarget -> CObject
- CPreviewView -> CScrollView -> CView -> CWnd
- CPen -> CGdiObject -> CObject
- CMenu -> CObject

Record each descriptor offset followed through the `+0x0C` base-class field.

## Evidence promotion rule

Only after these observations should `full runtime lifecycle validation` move from `RuntimePending` to a verified runtime evidence state. Do not promote a semantic field name solely because the trace is compatible with it; record the exact reads/writes and API arguments.
