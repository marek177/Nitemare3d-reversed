# Win16 indirect/vtable closure v17

## Results
- Indirect call sites: **212**
- Target-resolved sites: **74** (v16: 46; **+28**)
- Remaining VIRTUAL_DYNAMIC_RECEIVER: **85** (v16: 113; **-28**)
- Newly promoted dynamic virtual calls: **28**
- Confirmed vtable starts: **39** (v11b: 37; added secondary starts **0x497C** and **0x4CB8**)
- Vtable catalog rows after correct splitting/rebasing: **963**

## Strong new provenance chains
1. Runtime class DS:0030 = `CMainFrame` -> create entry `1010:0644` -> ctor `FUN_1010_0670` -> vptr `0x0792`.
2. Runtime class DS:0046 = `CNite3wDoc` -> create entry `1010:0832` -> ctor `FUN_1010_085e` -> vptr `0x08DC`.
3. Runtime class DS:005C = `CNite3wView` -> create entry `1010:0950` -> ctor `FUN_1010_097c` -> vptr `0x0BA0`.
4. Runtime class DS:05BC is `CView`; this proves `FUN_1000_068A(obj,0x5BC)` is a CView-family type test.
5. `FUN_1000_AD7E` writes vptr `0x4CB8`; this is a real secondary vtable embedded in the old 0x4C38 range.
6. `FUN_1000_4080` writes vptr `0x497C`; this is a second real secondary vtable embedded in the old 0x4934 range.

## Newly exact/function-level calls
- CDC-family invariant: 2
- CDocTemplate-family invariant: 2
- exact CMainFrame/CNite3wDoc runtime-class flow through template: 11
- CDocument-family invariant: 1
- secondary/embedded vtables in FUN_1000_C85E: 5
- interprocedural CMainFrame propagation into FUN_1008_2066: 2
- CView-family invariant: 2
- CFrameWnd-family invariant: 3

## Remaining main bottleneck
The unresolved virtual group is now **85** calls. Most are no longer unknown call mechanisms: they are calls with known receiver expression and slot, but the concrete runtime subclass is not yet singleton. The next best target is CFrameWnd/CView field provenance (+0x32, active-view +0x3A) and CDocument/View parent relations.