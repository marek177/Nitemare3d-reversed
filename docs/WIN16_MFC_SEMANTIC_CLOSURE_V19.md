# Nitemare 3D Win16 1.10 — MFC semantic indirect-call closure v19

## Result

- Total indirect call sites: **212**
- Exact/function-level machine targets: **80**
- New exact closures since v18: **2**
- Framework/class-semantic closures with runtime-dynamic concrete target: **12**
- Generic `VIRTUAL_DYNAMIC_RECEIVER` backlog: **67** (v18: 81)
- Generic virtual backlog reduction in this pass: **14 calls** total:
  - 2 promoted to exact target
  - 12 promoted to named framework/interface semantics

## New exact closures

| Caller | Site | Slot | Concrete live vtable | Target | Function |
|---|---|---|---|---|---|
| FUN_1008_2162 | 0x216E | 0x30 | 0x5240 | 1008:225E | FUN_1008_2242 |
| FUN_1008_2162 | 0x217E | 0x34 | 0x5240 | 1008:2270 | FUN_1008_2242 |

Evidence: `FUN_1008_1DF4` installs base vptr `0x51DC`; its observed concrete
constructor caller `FUN_1008_2214` immediately overwrites the live instance with
vptr `0x5240`.  The two slots in the concrete table point to the entries above.
The base vptr is therefore treated as a constructor/destructor transitional vptr
for the currently observed Win16 1.10 construction chain.

## MFC/OLE notify-hook semantics

The following calls are no longer generic virtual calls:

| Caller/site | Receiver relation | Semantic target |
|---|---|---|
| FUN_1000_66DC @ 0x670C | CFrameWnd +0x32 | COleFrameHook::OnPreTranslateMessage |
| FUN_1000_6EF4 @ 0x6F0C | CFrameWnd +0x32 | COleFrameHook::OnActivate |
| FUN_1000_799E @ 0x79B7 | CFrameWnd +0x32 | COleFrameHook::OnPaletteChanged |
| FUN_1000_A20E @ 0xA23F | frame +0x32 | COleFrameHook slot 0x44 (method name still open) |

This closes the **receiver class and framework purpose** while intentionally
leaving the concrete hook implementation dynamic.

## CFrameWnd/CView structure closure

- `CFrameWnd +0x3A` = active-view pointer.
- `FUN_1000_7198` is the GetActiveView-like accessor.
- `FUN_1000_71A6` is the SetActiveView-like mutator.
- CView-family slot `0x90` is semantically `CView::OnActivateView`.
- Four calls formerly marked generic dynamic are therefore now named
  `CView::OnActivateView`; the concrete machine target stays dynamic because
  `CPreviewView` has a distinct override.

## CArchive/CFile structure closure

`FUN_1000_467E` has the CArchive-like layout and stores the attached file object
at offset `+0x0A`.  Four remaining calls in `FUN_1000_4882/FUN_1000_48FA` are
therefore reclassified from unknown virtual dispatch to **CArchive -> CFile-family
virtual I/O**.  Exact method/subclass resolution is deliberately deferred.

## Next target

The generic virtual backlog is now **67**.  Highest-value next work:

1. resolve remaining CFrameWnd/CView family calls using active-frame/view provenance;
2. recover the concrete CFile-derived vtables behind archive objects;
3. classify the remaining self-dispatch methods by exact vtable-entry ownership;
4. then attack struct-field callbacks and register/slot-0 calls.