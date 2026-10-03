# Win16 indirect provenance v18

- Total indirect sites: **212**
- Target-resolved: **78** (v16 46 -> v17 74 -> **v18 78**)
- Remaining dynamic virtual receivers: **81** (v16 113 -> v17 85 -> **v18 81**)
- New v18 promotions: **4**

## v18 closures
- `FUN_1008_1D70 @ 1DAA`: document field `+0x20` is the owning `CDocTemplate`; slot `+0x14` -> `1000:35C8`.
- `FUN_1008_2162 @ 2193`: template document enumeration returns a `CDocument`; slot `+0x54` -> `1008:1C84`.
- `FUN_1000_66DC @ 6743`: hidden frame slot `+0x70` entry `1000:722A` returns active view's document (`view+0x1A`); document slot `+0x68` -> `1008:18AE`.
- `FUN_1000_A20E @ A226`: app slot `+0x6C` hidden entry `1000:3EA6` returns main-window/frame pointer; CFrameWnd/CMainFrame slot `+0x68` -> `1000:279C`.