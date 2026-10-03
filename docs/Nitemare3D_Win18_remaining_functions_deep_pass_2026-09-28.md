# Nitemare 3D Win16 v1.8 — remaining-functions deep pass

Date: 2026-09-28

## Executive result

- Exact Ghidra-export inventory for Win16 v1.8: **965 `FUN_*` blocks**.
- Exact reference inventory for Win16 v1.10: **967 `FUN_*` blocks**.
- This pass assigns and concrete v1.10 counterpart to **965/965 v1.8 functions (100.00%)**.
- The +2 functions in v1.10 are `FUN_1010_0af8` (small vtable/virtual-dispatch thunk) and `FUN_1010_3100` (palette BeginPaint/SelectPalette/RealizePalette/redraw fallback).
- Two v1.8 text helpers did not disappear: `FUN_1010_ef0e` and `FUN_1010_ef56` moved from segment 1010 to v1.10 `FUN_1018_0000` and `FUN_1018_0048`.
- Therefore the remaining problem is **not function identity**. The remaining work is precision of semantics, ABI/prototype repair, global-field meaning, and runtime edge cases.

## Correction to the earlier conversational count

The earlier estimate of about 1,070 total functions / 706 analyzed was not supported by the exact v1.8 export. The exact structural inventory is 965. To not use 706/1,070 as the Win16 v1.8 function count.

## Segment inventory

| Segment | v1.8 | v1.10 |
|---|---:|---:|
| `1000` | 328 | 328 |
| `1008` | 221 | 221 |
| `1010` | 320 | 320 |
| `1018` | 96 | 98 |

## Structural similarity of the 965 resolved pairs

| Similarity bin | Count |
|---|---:|
| >=0.99 | 842 |
| 0.98-0.99 | 71 |
| 0.95-0.98 | 37 |
| 0.90-0.95 | 8 |
| 0.80-0.90 | 3 |
| <0.80 | 4 |

The low textual-similarity pairs were manually inspected. They are explained by real version changes (palette handling, warning/fatal wrappers), relocated data/vtable addresses, or known resource-loader changes; none is an unresolved missing counterpart.

## Inherited semantic-confidence distribution

This uses the existing v1.10 semantic register only as and confidence inheritance aid, not as proof that every routine is behaviorally closed:

| Confidence | v1.8 counterparts |
|---|---:|
| high | 144 |
| medium | 710 |
| low | 111 |

## Important functions refined in this pass

| v1.8 function | v1.10 counterpart | Refined meaning |
|---|---|---|
| `FUN_1010_ef0e` | `FUN_1018_0000` | **MeasureBitmapTextWidth** — Exact semantic; iterates glyphs and sums width+1. Moved to 1018:0000 in 1.10. |
| `FUN_1010_ef56` | `FUN_1018_0048` | **ComputeCenteredTextX320** — Exact semantic; computes horizontal centered X from 320px width. Moved to 1018:0048 in 1.10. |
| `FUN_1010_3136` | `FUN_1010_31aa` | **SetupOrAnimateWin16Palette** — Palette setup/animation controller; 1.10 adds RC_PALETTE-dependent repaint/realize fallback. |
| `FUN_1010_3a90` | `FUN_1010_3b16` | **SetPaletteEntry** — Updates one palette index; direct VGA DAC path or WinG helper. 1.10 also updates software RGB shadow table. |
| `FUN_1010_47c4` | `FUN_1010_4868` | **LoadCurrentMapBlock8192** — Seeks to 0x202 + currentMapIndex*0x2000 and reads one 8192-byte map block. |
| `FUN_1010_48e6` | `FUN_1010_498a` | **BuildEpisodePathsAndLoadMapHeader** — Builds map.N/img.N/demo.N paths and loads 0x202-byte MAP header/directory. |
| `FUN_1010_508e` | `FUN_1010_5132` | **LoadSndEventDirectory32To110** — Reads SND.DAT directory entries 32..110: skips 0xC0 and reads 0x1DA = 79*6 bytes. |
| `FUN_1010_50ee` | `FUN_1010_5192` | **LoadSndDirectoryWithProgress79** — Loads SFX directory then advances the loading/progress path across 79 entries. |
| `FUN_1010_5c58` | `FUN_1010_5cfc` | **LazyLoadUifDirectoryAndGetEntryOffset** — Loads UIF.DAT 0xC0-byte directory once and returns slot*6. |
| `FUN_1010_5cce` | `FUN_1010_5d72` | **DecodeDisplayUifPcxSlot** — Uses UIF 6-byte descriptor, validates PCX-like header, decodes 320x200 RLE and draws scanlines. |
| `FUN_1010_5e6e` | `FUN_1010_5f12` | **LoadUifRawSlot** — Uses UIF 6-byte descriptor to seek and read an arbitrary slot payload. |
| `FUN_1010_9014` | `FUN_1010_90c2` | **ResetTwoTransientGlobals** — Writes zero to DS:0108 and DS:3752; exact gameplay meaning of both globals remains open. |
| `FUN_1018_3034` | `FUN_1018_308e` | **ShowWarningDialog** — Formats warning, beeps, MessageBox title Warning, temporarily changes multimedia state, then restores it. |
| `FUN_1018_30f0` | `FUN_1018_3118` | **FatalErrorDialogAndTerminate** — Formats fatal error, beeps, MessageBox title Fatal Error, invokes cleanup and termination. |
| `FUN_1018_1e78` | `FUN_1018_1ee0` | **ShowConditionalCompletionNarrative** — Patches/chooses conditional completion narrative strings and triggers display/event path. |
| `FUN_1018_24a0` | `FUN_1018_2508` | **ShowWeaponJammedMessage** — Displays the literal weapon-jammed gameplay message. |
| `FUN_1008_2ac2` | `FUN_1008_2ac2` | **FrameworkObjectInitWrapper_1008_2AC2** — Constructor/vtable-style wrapper; behavior equivalent, only relocated data addresses differ. |
| `FUN_1000_9ea8` | `FUN_1000_9ebc` | **FrameworkObjectInitWrapper_1000_9EA8** — Constructor/vtable-style wrapper; behavior equivalent, only relocated data/base target differs. |

## Concrete version differences found

### Palette path
- v1.8 `FUN_1010_3a90` sets one palette color either through the WinG helper or direct VGA DAC writes (`0x3C8/0x3C9`).
- v1.10 counterpart `FUN_1010_3b16` additionally writes the software RGB shadow table before the same device-dependent path.
- v1.10 adds `FUN_1010_3100`, and BeginPaint → SelectPalette → RealizePalette → redraw → EndPaint fallback. There is no v1.8 counterpart.

### SND.DAT
- v1.8 `FUN_1010_508e` seeks past `0xC0` bytes (32 × 6-byte entries) and reads `0x1DA` bytes (79 × 6-byte entries). This is the SFX event directory for physical SND records 32..110.
- v1.8 `FUN_1010_50ee` wraps that load and advances and 79-step progress path.

### UIF.DAT
- v1.8 `FUN_1010_5c58` lazily reads the fixed `0xC0`-byte UIF directory (32 × 6-byte entries) and returns `slot*6`.
- `FUN_1010_5cce` is the PCX-screen decoder/display path.
- `FUN_1010_5e6e` is the generic raw-slot payload loader; this is the path used by the bitmap-font loader.

### MAP/IMG/DEMO episode paths
- `FUN_1010_48e6` builds the episode paths `map.N`, `img.N`, `demo.N`, opens `map.N`, and reads the 0x202-byte map header/directory.
- `FUN_1010_47c4` reads one current map block at `0x202 + mapIndex*0x2000`, exactly 8192 bytes.

## What 100% means here

**100% = function inventory/counterpart identity for Win16 v1.8.** It does **not** mean 100% runtime equivalence or 100% exact semantic naming. Remaining uncertainties are concentrated in:
- some MFC/framework vtable and callback ownership;
- exact meanings of low-confidence globals/fields and decompiler-damaged Win16 far-pointer prototypes;
- complete GUARD state × strategy × class × timer/perception graph;
- collision/sliding/cache-freshness edge cases;
- save/load during moving doors/projectiles and other event-boundary cases;
- focus/pause/device failure paths and exact historical Win3.x runtime behavior.

## Bottom line

For **Win16 v1.8**, there is no longer and block of “unmatched remaining functions”: **965/965 are structurally accounted for**. The next useful stage is semantic closure of the remaining low-confidence routines and runtime verification, not discovering more ordinary `FUN_*` blocks in this export.

## Appendix: all 965 v1.8 → v1.10 mappings

| v1.8 | v1.10 | similarity | inherited label | confidence |
|---|---|---:|---|---|
| `FUN_1000_0356` | `FUN_1000_036a` | 0.9737 | BaseExceptionCtor | medium |
| `FUN_1000_0374` | `FUN_1000_0388` | 1.0000 | PtVisibleThunk | high |
| `FUN_1000_038c` | `FUN_1000_03a0` | 1.0000 | RectVisibleThunk | high |
| `FUN_1000_03a4` | `FUN_1000_03b8` | 1.0000 | ExtTextOutThunk | high |
| `FUN_1000_046c` | `FUN_1000_0480` | 1.0000 | GrayStringThunk | high |
| `FUN_1000_04ac` | `FUN_1000_04c0` | 1.0000 | EscapeThunk | high |
| `FUN_1000_0676` | `FUN_1000_068a` | 1.0000 | IsKindOfOrInClassChain | high |
| `FUN_1000_06ac` | `FUN_1000_06c0` | 1.0000 | CheckedDynamicCast | medium |
| `FUN_1000_071c` | `FUN_1000_0730` | 1.0000 | InvokeOptionalDestructor | high |
| `FUN_1000_078c` | `FUN_1000_07a0` | 1.0000 | DosCallWithLongResult | high |
| `FUN_1000_07f0` | `FUN_1000_0804` | 1.0000 | DosCallErrorWrapperA | high |
| `FUN_1000_0812` | `FUN_1000_0826` | 1.0000 | DosCallErrorWrapperB | high |
| `FUN_1000_0854` | `FUN_1000_0868` | 0.9783 | FileObjectDefaultCtor | high |
| `FUN_1000_087c` | `FUN_1000_0890` | 0.9802 | FileObjectCtor | high |
| `FUN_1000_08a6` | `FUN_1000_08ba` | 0.9789 | FileObjectDtor | high |
| `FUN_1000_08d6` | `FUN_1000_08ea` | 0.9921 | CloneFileObject | medium |
| `FUN_1000_09d6` | `FUN_1000_09ea` | 1.0000 | ReportIoErrorA | medium |
| `FUN_1000_0a10` | `FUN_1000_0a24` | 1.0000 | ReportIoErrorB | medium |
| `FUN_1000_0a5e` | `FUN_1000_0a72` | 1.0000 | FileSeekOrPosition | medium |
| `FUN_1000_0a94` | `FUN_1000_0aa8` | 1.0000 | GetFilePosition | medium |
| `FUN_1000_0ac8` | `FUN_1000_0adc` | 1.0000 | FlushFile | high |
| `FUN_1000_0af2` | `FUN_1000_0b06` | 1.0000 | CloseFile | high |
| `FUN_1000_0b4a` | `FUN_1000_0b5e` | 1.0000 | LockFileRange | medium |
| `FUN_1000_0b7a` | `FUN_1000_0b8e` | 1.0000 | UnlockFileRange | medium |
| `FUN_1000_0baa` | `FUN_1000_0bbe` | 1.0000 | FlushViaVirtualAndReport | medium |
| `FUN_1000_0c40` | `FUN_1000_0c54` | 1.0000 | ResolvePathOrTempName | medium |
| `FUN_1000_0c9c` | `FUN_1000_0cb0` | 1.0000 | DeleteFileObject | medium |
| `FUN_1000_0cc8` | `FUN_1000_0cdc` | 1.0000 | StringInitEmpty | high |
| `FUN_1000_0cde` | `FUN_1000_0cf2` | 1.0000 | StringFreeBuffer | high |
| `FUN_1000_0cf4` | `FUN_1000_0d08` | 1.0000 | StringCtorEmpty | high |
| `FUN_1000_0d08` | `FUN_1000_0d1c` | 1.0000 | StringMoveOrCopyCtor | medium |
| `FUN_1000_0d2a` | `FUN_1000_0d3e` | 1.0000 | StringAllocate | high |
| `FUN_1000_0d60` | `FUN_1000_0d74` | 1.0000 | StringDestroyAndReset | high |
| `FUN_1000_0d7a` | `FUN_1000_0d8e` | 1.0000 | StringDestroy | high |
| `FUN_1000_0d8c` | `FUN_1000_0da0` | 1.0000 | StringSubstringCopy | high |
| `FUN_1000_0dca` | `FUN_1000_0dde` | 1.0000 | StringFromCStr | high |
| `FUN_1000_0e12` | `FUN_1000_0e26` | 1.0000 | StringAssignBuffer | high |
| `FUN_1000_0e56` | `FUN_1000_0e6a` | 1.0000 | StringAssignString | high |
| `FUN_1000_0e74` | `FUN_1000_0e88` | 1.0000 | StringAssignCStr | high |
| `FUN_1000_0ea6` | `FUN_1000_0eba` | 1.0000 | StringConcatBuffers | high |
| `FUN_1000_0ee4` | `FUN_1000_0ef8` | 1.0000 | StringConcat | high |
| `FUN_1000_0f38` | `FUN_1000_0f4c` | 1.0000 | StringReserve | high |
| `FUN_1000_0f82` | `FUN_1000_0f96` | 1.0000 | StringSetLength | high |
| `FUN_1000_0fac` | `FUN_1000_0fc0` | 1.0000 | StringGetBufferSetLength | high |
| `FUN_1000_0fce` | `FUN_1000_0fe2` | 1.0000 | StringFindAny | high |
| `FUN_1000_1046` | `FUN_1000_105a` | 0.9920 | StringFromFarText | high |
| `FUN_1000_1094` | `FUN_1000_10a8` | 1.0000 | AnsiStrChr | high |
| `FUN_1000_1136` | `FUN_1000_114a` | 0.9879 | WindowObjectCtor | medium |
| `FUN_1000_115e` | `FUN_1000_1172` | 0.9894 | WindowObjectCtorWithId | medium |
| `FUN_1000_118a` | `FUN_1000_119e` | 1.0000 | CopyTenByteId | low |
| `FUN_1000_11ae` | `FUN_1000_11c2` | 1.0000 | WindowMapLookup | low |
| `FUN_1000_128e` | `FUN_1000_12a2` | 1.0000 | AllocateWindowMapNode | medium |
| `FUN_1000_12aa` | `FUN_1000_12be` | 1.0000 | InitWindowMapNode | low |
| `FUN_1000_12de` | `FUN_1000_12f2` | 1.0000 | GetPermanentWindowMap | medium |
| `FUN_1000_12e8` | `FUN_1000_12fc` | 1.0000 | LookupWindowHandle | medium |
| `FUN_1000_12fa` | `FUN_1000_130e` | 1.0000 | AttachWindowHandle | medium |
| `FUN_1000_1318` | `FUN_1000_132c` | 1.0000 | IsWindowHandleMapped | medium |
| `FUN_1000_1342` | `FUN_1000_1356` | 1.0000 | DetachWindowHandle | medium |
| `FUN_1000_136a` | `FUN_1000_137e` | 1.0000 | CreateTempWindowWrapper | low |
| `FUN_1000_146e` | `FUN_1000_1482` | 0.9963 | WindowBaseCtor | medium |
| `FUN_1000_14b8` | `FUN_1000_14cc` | 0.9944 | WindowBaseDtor | medium |
| `FUN_1000_14ec` | `FUN_1000_1500` | 1.0000 | WindowDelete | medium |
| `FUN_1000_15f2` | `FUN_1000_1606` | 0.9946 | GetWindowRuntimeClass | low |
| `FUN_1000_1652` | `FUN_1000_1666` | 0.9929 | WindowDerivedCtor | medium |
| `FUN_1000_1708` | `FUN_1000_171c` | 1.0000 | AttachOrCreateWindow | medium |
| `FUN_1000_1866` | `FUN_1000_187a` | 1.0000 | FindWindowByHandle | medium |
| `FUN_1000_18cc` | `FUN_1000_18e0` | 1.0000 | RouteWindowMessage | medium |
| `FUN_1000_1a06` | `FUN_1000_1a1a` | 0.9967 | DefaultWindowProcBridge | low |
| `FUN_1000_1b04` | `FUN_1000_1b18` | 1.0000 | FindMessageMapEntry | medium |
| `FUN_1000_1b3e` | `FUN_1000_1b52` | 0.9987 | DispatchMessageMapEntry | low |
| `FUN_1000_1ef0` | `FUN_1000_1f04` | 1.0000 | GetMenuOrWindowHandle | medium |
| `FUN_1000_1f1a` | `FUN_1000_1f2e` | 1.0000 | CreateGuiObject | medium |
| `FUN_1000_1f7a` | `FUN_1000_1f8e` | 1.0000 | DestroyGuiObject | medium |
| `FUN_1000_1fb0` | `FUN_1000_1fc4` | 1.0000 | CloneOrCreateGuiObject | medium |
| `FUN_1000_1ffc` | `FUN_1000_2010` | 1.0000 | AttachGuiResource | medium |
| `FUN_1000_207c` | `FUN_1000_2090` | 1.0000 | RemoveGuiResource | medium |
| `FUN_1000_2108` | `FUN_1000_211c` | 1.0000 | FindGuiResource | medium |
| `FUN_1000_213e` | `FUN_1000_2152` | 1.0000 | RectNormalizeOrCopy | medium |
| `FUN_1000_216e` | `FUN_1000_2182` | 1.0000 | RectOffset | medium |
| `FUN_1000_21aa` | `FUN_1000_21be` | 1.0000 | RectInflate | medium |
| `FUN_1000_21e8` | `FUN_1000_21fc` | 1.0000 | RectIntersect | medium |
| `FUN_1000_2242` | `FUN_1000_2256` | 0.9986 | RectUnionOrSubtract | medium |
| `FUN_1000_237c` | `FUN_1000_2390` | 1.0000 | CreateDeviceContextWrapper | low |
| `FUN_1000_2482` | `FUN_1000_2496` | 1.0000 | ReleaseGuiHandle | medium |
| `FUN_1000_24e6` | `FUN_1000_24fa` | 1.0000 | SelectGdiObject | medium |
| `FUN_1000_2508` | `FUN_1000_251c` | 1.0000 | RestoreGdiObject | medium |
| `FUN_1000_252a` | `FUN_1000_253e` | 1.0000 | DeleteGdiObjectWrapper | medium |
| `FUN_1000_2550` | `FUN_1000_2564` | 1.0000 | CreateCompatibleDcObject | medium |
| `FUN_1000_25dc` | `FUN_1000_25f0` | 1.0000 | InitDcState | medium |
| `FUN_1000_25f8` | `FUN_1000_260c` | 1.0000 | MapLogicalPoint | medium |
| `FUN_1000_26d4` | `FUN_1000_26e8` | 1.0000 | PrepareTextOrFontMetrics | medium |
| `FUN_1000_278e` | `FUN_1000_27a2` | 1.0000 | ClampCoordinate | medium |
| `FUN_1000_282c` | `FUN_1000_2840` | 1.0000 | InitGuiFramework | medium |
| `FUN_1000_295c` | `FUN_1000_2970` | 0.9942 | LookupOrCreateGdiWrapper | medium |
| `FUN_1000_2a00` | `FUN_1000_2a14` | 1.0000 | RemoveGdiWrapper | medium |
| `FUN_1000_2a12` | `FUN_1000_2a26` | 1.0000 | DestroyGdiMap | medium |
| `FUN_1000_2a7a` | `FUN_1000_2a8e` | 1.0000 | GdiObjectDtor | medium |
| `FUN_1000_2bf6` | `FUN_1000_2c0a` | 0.9912 | CreatePenOrBrushWrapper | medium |
| `FUN_1000_2c3c` | `FUN_1000_2c50` | 1.0000 | CreateStockGdiWrapper | low |
| `FUN_1000_2cf8` | `FUN_1000_2d0c` | 0.9857 | GuiDerivedDtor | medium |
| `FUN_1000_2dbe` | `FUN_1000_2dd2` | 0.9922 | WindowObjectCopyCtor | medium |
| `FUN_1000_2e08` | `FUN_1000_2e1c` | 1.0000 | CreateOrAttachWindow | medium |
| `FUN_1000_2e34` | `FUN_1000_2e48` | 1.0000 | DestroyAttachedWindow | medium |
| `FUN_1000_2eb4` | `FUN_1000_2ec8` | 1.0000 | DefaultCreateStruct | medium |
| `FUN_1000_2f2a` | `FUN_1000_2f3e` | 1.0000 | CreateWindowObject | medium |
| `FUN_1000_2fb8` | `FUN_1000_2fcc` | 1.0000 | NoOpWindowHook | low |
| `FUN_1000_2fcc` | `FUN_1000_2fe0` | 1.0000 | SelectGdiObjectAndTrack | medium |
| `FUN_1000_3026` | `FUN_1000_303a` | 0.9963 | RestoreSelectedGdiObjects | medium |
| `FUN_1000_323c` | `FUN_1000_3250` | 1.0000 | StringCompareNoCase | medium |
| `FUN_1000_326e` | `FUN_1000_3282` | 0.9825 | AnsiUpperByte | high |
| `FUN_1000_3288` | `FUN_1000_329c` | 0.9958 | NormalizePathString | medium |
| `FUN_1000_330c` | `FUN_1000_3320` | 1.0000 | IsDbcsLeadByte | high |
| `FUN_1000_335c` | `FUN_1000_3370` | 1.0000 | ShutdownGlobalGdiMap | medium |
| `FUN_1000_3366` | `FUN_1000_337a` | 1.0000 | ShutdownGlobalWindowMap | medium |
| `FUN_1000_3378` | `FUN_1000_338c` | 0.9735 | RuntimeObjectCtor | medium |
| `FUN_1000_33b8` | `FUN_1000_33cc` | 1.0000 | RemoveHandleMapEntry | medium |
| `FUN_1000_33e0` | `FUN_1000_33f4` | 0.9735 | RuntimeObjectDtor | medium |
| `FUN_1000_3404` | `FUN_1000_3418` | 1.0000 | DeleteRuntimeObject | medium |
| `FUN_1000_3494` | `FUN_1000_34a8` | 0.9844 | CommandTargetCtor | medium |
| `FUN_1000_34d0` | `FUN_1000_34e4` | 0.9851 | CommandTargetDtor | medium |
| `FUN_1000_3504` | `FUN_1000_3518` | 1.0000 | FindMessageHandler | medium |
| `FUN_1000_35b4` | `FUN_1000_35c8` | 1.0000 | DispatchMessageHandler | medium |
| `FUN_1000_3690` | `FUN_1000_36a4` | 1.0000 | GetRuntimeClassDescriptorA | medium |
| `FUN_1000_36a0` | `FUN_1000_36b4` | 1.0000 | GetRuntimeClassDescriptorB | medium |
| `FUN_1000_36f2` | `FUN_1000_3706` | 1.0000 | GetMessageMap | medium |
| `FUN_1000_37b8` | `FUN_1000_37cc` | 1.0000 | RegisterWindowMessageHandler | medium |
| `FUN_1000_3870` | `FUN_1000_3884` | 1.0000 | DispatchCommandMessage | medium |
| `FUN_1000_38b6` | `FUN_1000_38ca` | 1.0000 | UpdateCommandUi | medium |
| `FUN_1000_3922` | `FUN_1000_3936` | 0.9944 | FormatFrameworkMessage | medium |
| `FUN_1000_39da` | `FUN_1000_39ee` | 0.9943 | MapWindowMessage | medium |
| `FUN_1000_3a8a` | `FUN_1000_3a9e` | 1.0000 | SerializePrimitiveBlock | medium |
| `FUN_1000_3ad4` | `FUN_1000_3ae8` | 1.0000 | AttachArchiveObject | medium |
| `FUN_1000_3cd6` | `FUN_1000_3cea` | 0.9984 | DynamicDowncast | medium |
| `FUN_1000_3d5e` | `FUN_1000_3d72` | 1.0000 | SerializeRuntimeObject | medium |
| `FUN_1000_3fac` | `FUN_1000_3fc0` | 0.9976 | ReportArchiveError | medium |
| `FUN_1000_406c` | `FUN_1000_4080` | 0.9421 | ArchiveExceptionCtor | medium |
| `FUN_1000_40ee` | `FUN_1000_4102` | 1.0000 | AllocateArchiveBuffer | medium |
| `FUN_1000_4160` | `FUN_1000_4174` | 1.0000 | CopyArchiveBytes | medium |
| `FUN_1000_417a` | `FUN_1000_418e` | 1.0000 | ArchiveReadBytes | medium |
| `FUN_1000_41b2` | `FUN_1000_41c6` | 1.0000 | ArchiveWriteBytes | medium |
| `FUN_1000_41e8` | `FUN_1000_41fc` | 1.0000 | ArchiveReadPrimitive | medium |
| `FUN_1000_4222` | `FUN_1000_4236` | 1.0000 | ArchiveWritePrimitive | medium |
| `FUN_1000_4262` | `FUN_1000_4276` | 1.0000 | ArchiveSeekOrFlush | medium |
| `FUN_1000_42bc` | `FUN_1000_42d0` | 1.0000 | FrameworkAlloc | high |
| `FUN_1000_42ee` | `FUN_1000_4302` | 1.0000 | FrameworkFree | high |
| `FUN_1000_440e` | `FUN_1000_4422` | 1.0000 | PushExceptionFrame | high |
| `FUN_1000_4432` | `FUN_1000_4446` | 1.0000 | PopExceptionFrame | high |
| `FUN_1000_445e` | `FUN_1000_4472` | 1.0000 | IsExceptionType | medium |
| `FUN_1000_447e` | `FUN_1000_4492` | 1.0000 | ThrowFrameworkException | medium |
| `FUN_1000_4516` | `FUN_1000_452a` | 1.0000 | RethrowFrameworkException | medium |
| `FUN_1000_4550` | `FUN_1000_4564` | 1.0000 | ThrowMemoryException | medium |
| `FUN_1000_45fe` | `FUN_1000_4612` | 0.9869 | DeleteExceptionObjectA | medium |
| `FUN_1000_4622` | `FUN_1000_4636` | 0.9869 | DeleteExceptionObjectB | medium |
| `FUN_1000_4646` | `FUN_1000_465a` | 0.9869 | DeleteExceptionObjectC | medium |
| `FUN_1000_466a` | `FUN_1000_467e` | 1.0000 | MapDosErrorToException | medium |
| `FUN_1000_4700` | `FUN_1000_4714` | 0.9954 | FormatExceptionText | medium |
| `FUN_1000_4752` | `FUN_1000_4766` | 1.0000 | GetErrorMessageText | medium |
| `FUN_1000_486e` | `FUN_1000_4882` | 0.9971 | CopyExceptionState | medium |
| `FUN_1000_48e6` | `FUN_1000_48fa` | 1.0000 | LookupErrorMessage | medium |
| `FUN_1000_49ee` | `FUN_1000_4a02` | 0.9811 | NewGenericException | medium |
| `FUN_1000_4a5e` | `FUN_1000_4a72` | 1.0000 | GetLastFrameworkError | medium |
| `FUN_1000_4aac` | `FUN_1000_4ac0` | 1.0000 | ThrowIoException | medium |
| `FUN_1000_4ad2` | `FUN_1000_4ae6` | 0.9844 | ThrowFileException | medium |
| `FUN_1000_4b80` | `FUN_1000_4b94` | 1.0000 | MapFileError | medium |
| `FUN_1000_4c24` | `FUN_1000_4c38` | 1.0000 | ConcatStringRanges | high |
| `FUN_1000_4c7a` | `FUN_1000_4c8e` | 1.0000 | ConcatCString | high |
| `FUN_1000_4cac` | `FUN_1000_4cc0` | 1.0000 | ConcatStringLeft | high |
| `FUN_1000_4cc6` | `FUN_1000_4cda` | 1.0000 | ConcatStringRight | high |
| `FUN_1000_4ce4` | `FUN_1000_4cf8` | 1.0000 | SubstringToResult | medium |
| `FUN_1000_4d8e` | `FUN_1000_4da2` | 1.0000 | CompareAnsiStrings | medium |
| `FUN_1000_4ef8` | `FUN_1000_4f0c` | 0.9903 | DocumentTemplateCtor | medium |
| `FUN_1000_5038` | `FUN_1000_504c` | 1.0000 | DocumentTemplateDtor | medium |
| `FUN_1000_50fa` | `FUN_1000_510e` | 0.9965 | DocumentTemplateInit | medium |
| `FUN_1000_5294` | `FUN_1000_52a8` | 1.0000 | DocumentTemplateMatch | medium |
| `FUN_1000_53c4` | `FUN_1000_53d8` | 0.9934 | FrameWindowCtor | medium |
| `FUN_1000_5416` | `FUN_1000_542a` | 1.0000 | LoadFrameResource | medium |
| `FUN_1000_5450` | `FUN_1000_5464` | 0.9877 | FrameWindowDtor | medium |
| `FUN_1000_54e0` | `FUN_1000_54f4` | 0.9897 | FrameWindowMessageMap | medium |
| `FUN_1000_5514` | `FUN_1000_5528` | 0.9934 | FramePreCreateWindow | medium |
| `FUN_1000_5566` | `FUN_1000_557a` | 0.9931 | CreateFrameWindow | medium |
| `FUN_1000_56b4` | `FUN_1000_56c8` | 1.0000 | FrameWindowProc | medium |
| `FUN_1000_570c` | `FUN_1000_5720` | 0.9941 | ViewWindowCtor | medium |
| `FUN_1000_576a` | `FUN_1000_577e` | 0.9861 | ViewMessageMap | medium |
| `FUN_1000_57f8` | `FUN_1000_580c` | 1.0000 | SetWindowPlacement | medium |
| `FUN_1000_5a0e` | `FUN_1000_5a22` | 1.0000 | ApplicationStateInit | medium |
| `FUN_1000_5cb0` | `FUN_1000_5cc4` | 1.0000 | GetApplicationObject | medium |
| `FUN_1000_5cc6` | `FUN_1000_5cda` | 1.0000 | CommandLineInfoInit | medium |
| `FUN_1000_5d10` | `FUN_1000_5d24` | 0.9941 | ParseCommandLine | medium |
| `FUN_1000_5e80` | `FUN_1000_5e94` | 0.9933 | ParseCommandLineToken | medium |
| `FUN_1000_5fd4` | `FUN_1000_5fe8` | 1.0000 | RunApplicationLoop | medium |
| `FUN_1000_6070` | `FUN_1000_6084` | 0.9900 | ApplicationInitInstance | medium |
| `FUN_1000_6104` | `FUN_1000_6118` | 0.9844 | ApplicationExceptionCtor | medium |
| `FUN_1000_613e` | `FUN_1000_6152` | 1.0000 | CopyRuntimeBuffer | medium |
| `FUN_1000_6182` | `FUN_1000_6196` | 1.0000 | FreeRuntimeBuffer | medium |
| `FUN_1000_61d8` | `FUN_1000_61ec` | 1.0000 | AllocateRuntimeArray | medium |
| `FUN_1000_6252` | `FUN_1000_6266` | 1.0000 | GetThreadState | high |
| `FUN_1000_626c` | `FUN_1000_6280` | 1.0000 | HandleMapLookup | high |
| `FUN_1000_62b4` | `FUN_1000_62c8` | 1.0000 | HandleMapFind | high |
| `FUN_1000_62e0` | `FUN_1000_62f4` | 1.0000 | HandleMapCreateTemporary | medium |
| `FUN_1000_6342` | `FUN_1000_6356` | 1.0000 | HandleMapRemove | medium |
| `FUN_1000_639a` | `FUN_1000_63ae` | 1.0000 | DocumentViewApplicationFramework_1000_63AE | medium |
| `FUN_1000_660a` | `FUN_1000_661e` | 0.9909 | Win16FrameworkContinuation_1000_661E | medium |
| `FUN_1000_6680` | `FUN_1000_6694` | 0.9840 | Win16FrameworkContinuation_1000_6694 | medium |
| `FUN_1000_66a4` | `FUN_1000_66b8` | 1.0000 | Win16FrameworkContinuation_1000_66B8 | low |
| `FUN_1000_66c8` | `FUN_1000_66dc` | 0.9945 | Win16FrameworkContinuation_1000_66DC | medium |
| `FUN_1000_6760` | `FUN_1000_6774` | 1.0000 | Win16FrameworkContinuation_1000_6774 | low |
| `FUN_1000_67ca` | `FUN_1000_67de` | 1.0000 | Win16FrameworkContinuation_1000_67DE | medium |
| `FUN_1000_685a` | `FUN_1000_686e` | 1.0000 | Win16FrameworkContinuation_1000_686E | medium |
| `FUN_1000_68b0` | `FUN_1000_68c4` | 1.0000 | Win16FrameworkContinuation_1000_68C4 | low |
| `FUN_1000_6a34` | `FUN_1000_6a48` | 1.0000 | Win16FrameworkContinuation_1000_6AND48 | medium |
| `FUN_1000_6a8e` | `FUN_1000_6aa2` | 1.0000 | Win16FrameworkContinuation_1000_6AA2 | medium |
| `FUN_1000_6aac` | `FUN_1000_6ac0` | 1.0000 | Win16WindowMessage_1000_6AC0 | high |
| `FUN_1000_6d36` | `FUN_1000_6d4a` | 1.0000 | Win16FrameworkContinuation_1000_6D4AND | medium |
| `FUN_1000_6e18` | `FUN_1000_6e2c` | 1.0000 | Win16WindowMessage_1000_6E2C | high |
| `FUN_1000_6e4c` | `FUN_1000_6e60` | 1.0000 | Win16WindowMessage_1000_6E60 | high |
| `FUN_1000_6e80` | `FUN_1000_6e94` | 1.0000 | Win16FrameworkContinuation_1000_6E94 | medium |
| `FUN_1000_6ee0` | `FUN_1000_6ef4` | 1.0000 | Win16FrameworkContinuation_1000_6EF4 | medium |
| `FUN_1000_7046` | `FUN_1000_705a` | 1.0000 | Win16FrameworkContinuation_1000_705AND | low |
| `FUN_1000_7162` | `FUN_1000_7176` | 1.0000 | Win16WindowMessage_1000_7176 | high |
| `FUN_1000_7184` | `FUN_1000_7198` | 1.0000 | Win16FrameworkContinuation_1000_7198 | low |
| `FUN_1000_7192` | `FUN_1000_71a6` | 1.0000 | Win16FrameworkContinuation_1000_71AND6 | medium |
| `FUN_1000_7234` | `FUN_1000_7248` | 0.9984 | Win16FrameworkContinuation_1000_7248 | medium |
| `FUN_1000_7486` | `FUN_1000_749a` | 1.0000 | Win16FrameworkContinuation_1000_749AND | medium |
| `FUN_1000_74ca` | `FUN_1000_74de` | 1.0000 | Win16WindowMessage_1000_74DE | high |
| `FUN_1000_7502` | `FUN_1000_7516` | 1.0000 | Win16WindowMessage_1000_7516 | high |
| `FUN_1000_75a2` | `FUN_1000_75b6` | 1.0000 | TimerInput_1000_75B6 | high |
| `FUN_1000_7902` | `FUN_1000_7916` | 1.0000 | Win16FrameworkContinuation_1000_7916 | low |
| `FUN_1000_7916` | `FUN_1000_792a` | 1.0000 | Win16WindowMessage_1000_792AND | high |
| `FUN_1000_798a` | `FUN_1000_799e` | 0.9910 | Win16FrameworkContinuation_1000_799E | medium |
| `FUN_1000_79c4` | `FUN_1000_79d8` | 1.0000 | Win16FrameworkContinuation_1000_79D8 | medium |
| `FUN_1000_7ad8` | `FUN_1000_7aec` | 1.0000 | Win16FrameworkContinuation_1000_7AEC | medium |
| `FUN_1000_7e24` | `FUN_1000_7e38` | 1.0000 | Win16FrameworkContinuation_1000_7E38 | medium |
| `FUN_1000_7ff6` | `FUN_1000_800a` | 1.0000 | Win16WindowMessage_1000_800AND | high |
| `FUN_1000_8118` | `FUN_1000_812c` | 1.0000 | Win16WindowMessage_1000_812C | high |
| `FUN_1000_8188` | `FUN_1000_819c` | 1.0000 | Win16FrameworkContinuation_1000_819C | low |
| `FUN_1000_81aa` | `FUN_1000_81be` | 0.9936 | Win16WindowMessage_1000_81BE | high |
| `FUN_1000_837e` | `FUN_1000_8392` | 0.9876 | Win16FrameworkContinuation_1000_8392 | medium |
| `FUN_1000_83ae` | `FUN_1000_83c2` | 1.0000 | Win16FrameworkContinuation_1000_83C2 | low |
| `FUN_1000_8472` | `FUN_1000_8486` | 1.0000 | Win16WindowMessage_1000_8486 | high |
| `FUN_1000_84e2` | `FUN_1000_84f6` | 1.0000 | Win16FrameworkContinuation_1000_84F6 | low |
| `FUN_1000_87b8` | `FUN_1000_87cc` | 1.0000 | Win16WindowMessage_1000_87CC | high |
| `FUN_1000_87dc` | `FUN_1000_87f0` | 1.0000 | Win16WindowMessage_1000_87F0 | high |
| `FUN_1000_880c` | `FUN_1000_8820` | 1.0000 | Win16DrawingGdi_1000_8820 | high |
| `FUN_1000_890e` | `FUN_1000_8922` | 1.0000 | Win16WindowMessage_1000_8922 | high |
| `FUN_1000_8976` | `FUN_1000_898a` | 1.0000 | Win16FrameworkContinuation_1000_898AND | medium |
| `FUN_1000_8a64` | `FUN_1000_8a78` | 1.0000 | StringText_1000_8AND78 | high |
| `FUN_1000_8b28` | `FUN_1000_8b3c` | 1.0000 | Win16DrawingGdi_1000_8B3C | high |
| `FUN_1000_8c38` | `FUN_1000_8c4c` | 1.0000 | Win16DrawingGdi_1000_8C4C | high |
| `FUN_1000_8dc2` | `FUN_1000_8dd6` | 1.0000 | Win16FrameworkContinuation_1000_8DD6 | low |
| `FUN_1000_8dda` | `FUN_1000_8dee` | 0.9891 | Win16DrawingGdi_1000_8DEE | high |
| `FUN_1000_8e64` | `FUN_1000_8e78` | 1.0000 | Win16FrameworkContinuation_1000_8E78 | low |
| `FUN_1000_8f0e` | `FUN_1000_8f22` | 1.0000 | StringText_1000_8F22 | high |
| `FUN_1000_8fc6` | `FUN_1000_8fda` | 1.0000 | Win16FrameworkContinuation_1000_8FDA | medium |
| `FUN_1000_9090` | `FUN_1000_90a4` | 1.0000 | Win16DrawingGdi_1000_90AND4 | high |
| `FUN_1000_90de` | `FUN_1000_90f2` | 0.9981 | Win16DrawingGdi_1000_90F2 | high |
| `FUN_1000_91c0` | `FUN_1000_91d4` | 1.0000 | Win16DrawingGdi_1000_91D4 | high |
| `FUN_1000_9294` | `FUN_1000_92a8` | 1.0000 | Win16DrawingGdi_1000_92AND8 | high |
| `FUN_1000_95e2` | `FUN_1000_95f6` | 1.0000 | Win16DrawingGdi_1000_95F6 | high |
| `FUN_1000_964c` | `FUN_1000_9660` | 1.0000 | Win16DrawingGdi_1000_9660 | high |
| `FUN_1000_9678` | `FUN_1000_968c` | 0.9975 | Win16DrawingGdi_1000_968C | high |
| `FUN_1000_9820` | `FUN_1000_9834` | 1.0000 | Win16FrameworkContinuation_1000_9834 | medium |
| `FUN_1000_98a2` | `FUN_1000_98b6` | 1.0000 | Win16FrameworkContinuation_1000_98B6 | medium |
| `FUN_1000_98ce` | `FUN_1000_98e2` | 1.0000 | Win16FrameworkContinuation_1000_98E2 | medium |
| `FUN_1000_9984` | `FUN_1000_9998` | 1.0000 | Win16FrameworkContinuation_1000_9998 | low |
| `FUN_1000_99b0` | `FUN_1000_99c4` | 1.0000 | Win16FrameworkContinuation_1000_99C4 | medium |
| `FUN_1000_9a2c` | `FUN_1000_9a40` | 1.0000 | Win16WindowMessage_1000_9AND40 | high |
| `FUN_1000_9ab6` | `FUN_1000_9aca` | 1.0000 | Win16FrameworkContinuation_1000_9ACA | medium |
| `FUN_1000_9af8` | `FUN_1000_9b0c` | 1.0000 | Win16WindowMessage_1000_9B0C | high |
| `FUN_1000_9b90` | `FUN_1000_9ba4` | 1.0000 | Win16WindowMessage_1000_9BA4 | high |
| `FUN_1000_9c82` | `FUN_1000_9c96` | 1.0000 | Win16WindowMessage_1000_9C96 | high |
| `FUN_1000_9ea8` | `FUN_1000_9ebc` | 0.8968 | FrameworkObjectInitWrapper_1000_9EA8 | medium |
| `FUN_1000_9fc4` | `FUN_1000_9fd8` | 1.0000 | Win16FrameworkContinuation_1000_9FD8 | medium |
| `FUN_1000_a08a` | `FUN_1000_a09e` | 1.0000 | Win16FrameworkContinuation_1000_AND09E | medium |
| `FUN_1000_a0a0` | `FUN_1000_a0b4` | 1.0000 | Win16FrameworkContinuation_1000_AND0B4 | medium |
| `FUN_1000_a0d6` | `FUN_1000_a0ea` | 1.0000 | Win16FrameworkContinuation_1000_AND0EA | low |
| `FUN_1000_a19e` | `FUN_1000_a1b2` | 1.0000 | Win16FrameworkContinuation_1000_AND1B2 | medium |
| `FUN_1000_a1fa` | `FUN_1000_a20e` | 1.0000 | Win16FrameworkContinuation_1000_AND20E | medium |
| `FUN_1000_a330` | `FUN_1000_a344` | 0.9924 | Win16FrameworkContinuation_1000_AND344 | medium |
| `FUN_1000_a59c` | `FUN_1000_a5b0` | 0.9915 | StringText_1000_AND5B0 | high |
| `FUN_1000_a62c` | `FUN_1000_a640` | 0.9957 | Win16WindowMessage_1000_AND640 | high |
| `FUN_1000_a830` | `FUN_1000_a844` | 0.9847 | Win16FrameworkContinuation_1000_AND844 | medium |
| `FUN_1000_a874` | `FUN_1000_a888` | 0.9976 | Win16FrameworkContinuation_1000_AND888 | medium |
| `FUN_1000_a952` | `FUN_1000_a966` | 0.9954 | Win16FrameworkContinuation_1000_AND966 | medium |
| `FUN_1000_ab04` | `FUN_1000_ab18` | 1.0000 | Win16FrameworkContinuation_1000_AB18 | medium |
| `FUN_1000_ab26` | `FUN_1000_ab3a` | 1.0000 | Win16FrameworkContinuation_1000_AB3AND | medium |
| `FUN_1000_ab56` | `FUN_1000_ab6a` | 0.9956 | StringText_1000_AB6AND | high |
| `FUN_1000_ac5c` | `FUN_1000_ac70` | 1.0000 | Win16FrameworkContinuation_1000_AC70 | medium |
| `FUN_1000_ad6a` | `FUN_1000_ad7e` | 0.9378 | Win16FrameworkContinuation_1000_AD7E | medium |
| `FUN_1000_adf0` | `FUN_1000_ae04` | 1.0000 | Win16FrameworkContinuation_1000_AE04 | medium |
| `FUN_1000_ae66` | `FUN_1000_ae7a` | 1.0000 | Win16FrameworkContinuation_1000_AE7AND | medium |
| `FUN_1000_ae92` | `FUN_1000_aea6` | 1.0000 | Win16DrawingGdi_1000_AEA6 | high |
| `FUN_1000_b07e` | `FUN_1000_b092` | 1.0000 | Win16DrawingGdi_1000_B092 | high |
| `FUN_1000_b1ee` | `FUN_1000_b202` | 1.0000 | Win16DrawingGdi_1000_B202 | high |
| `FUN_1000_b274` | `FUN_1000_b288` | 1.0000 | Win16FrameworkContinuation_1000_B288 | low |
| `FUN_1000_b2ac` | `FUN_1000_b2c0` | 1.0000 | Win16FrameworkContinuation_1000_B2C0 | medium |
| `FUN_1000_ba14` | `FUN_1000_ba28` | 1.0000 | Win16DrawingGdi_1000_BA28 | high |
| `FUN_1000_ba76` | `FUN_1000_ba8a` | 0.9980 | Win16FrameworkContinuation_1000_BA8AND | medium |
| `FUN_1000_bafa` | `FUN_1000_bb0e` | 1.0000 | Win16WindowMessage_1000_BB0E | high |
| `FUN_1000_bc46` | `FUN_1000_bc5a` | 1.0000 | Win16WindowMessage_1000_BC5AND | high |
| `FUN_1000_bcb2` | `FUN_1000_bcc6` | 1.0000 | Win16FrameworkContinuation_1000_BCC6 | medium |
| `FUN_1000_bcd0` | `FUN_1000_bce4` | 1.0000 | Win16WindowMessage_1000_BCE4 | high |
| `FUN_1000_bd4a` | `FUN_1000_bd5e` | 1.0000 | Win16WindowMessage_1000_BD5E | high |
| `FUN_1000_bdf4` | `FUN_1000_be08` | 1.0000 | Win16FrameworkContinuation_1000_BE08 | medium |
| `FUN_1000_bfc6` | `FUN_1000_bfda` | 1.0000 | Win16FrameworkContinuation_1000_BFDA | medium |
| `FUN_1000_c42e` | `FUN_1000_c442` | 1.0000 | Win16FrameworkContinuation_1000_C442 | medium |
| `FUN_1000_c494` | `FUN_1000_c4a8` | 1.0000 | Win16FrameworkContinuation_1000_C4AND8 | medium |
| `FUN_1000_c4ba` | `FUN_1000_c4ce` | 1.0000 | Win16FrameworkContinuation_1000_C4CE | medium |
| `FUN_1000_c74c` | `FUN_1000_c760` | 0.9958 | Win16FrameworkContinuation_1000_C760 | medium |
| `FUN_1000_c7b2` | `FUN_1000_c7c6` | 0.9846 | Win16FrameworkContinuation_1000_C7C6 | medium |
| `FUN_1000_c814` | `FUN_1000_c828` | 1.0000 | Win16FrameworkContinuation_1000_C828 | medium |
| `FUN_1000_c84a` | `FUN_1000_c85e` | 0.9962 | Win16DrawingGdi_1000_C85E | high |
| `FUN_1000_cb1c` | `FUN_1000_cb30` | 1.0000 | Win16FrameworkContinuation_1000_CB30 | low |
| `FUN_1000_cbf0` | `FUN_1000_cc04` | 1.0000 | Win16FrameworkContinuation_1000_CC04 | medium |
| `FUN_1000_cc76` | `FUN_1000_cc8a` | 1.0000 | Win16FrameworkContinuation_1000_CC8AND | medium |
| `FUN_1000_d464` | `FUN_1000_d478` | 0.9959 | Win16FrameworkContinuation_1000_D478 | medium |
| `FUN_1000_d5a0` | `FUN_1000_d5b4` | 1.0000 | Win16FrameworkContinuation_1000_D5B4 | medium |
| `FUN_1000_d5c4` | `FUN_1000_d5d8` | 1.0000 | Win16FrameworkContinuation_1000_D5D8 | medium |
| `FUN_1000_d5f2` | `FUN_1000_d606` | 1.0000 | Win16FrameworkContinuation_1000_D606 | medium |
| `FUN_1000_d620` | `FUN_1000_d634` | 1.0000 | Win16FrameworkContinuation_1000_D634 | medium |
| `FUN_1000_d770` | `FUN_1000_d784` | 1.0000 | Win16FrameworkContinuation_1000_D784 | medium |
| `FUN_1000_d878` | `FUN_1000_d88c` | 0.9949 | Win16FrameworkContinuation_1000_D88C | medium |
| `FUN_1000_d912` | `FUN_1000_d926` | 1.0000 | Win16FrameworkContinuation_1000_D926 | low |
| `FUN_1000_d942` | `FUN_1000_d956` | 1.0000 | Win16FrameworkContinuation_1000_D956 | low |
| `FUN_1000_d964` | `FUN_1000_d978` | 1.0000 | Win16FrameworkContinuation_1000_D978 | low |
| `FUN_1000_d980` | `FUN_1000_d994` | 1.0000 | Win16FrameworkContinuation_1000_D994 | medium |
| `FUN_1000_da24` | `FUN_1000_da38` | 1.0000 | Win16FrameworkContinuation_1000_DA38 | medium |
| `FUN_1000_da74` | `FUN_1000_da88` | 1.0000 | Win16FrameworkContinuation_1000_DA88 | low |
| `FUN_1000_dbd8` | `FUN_1000_dbec` | 0.9961 | Win16FrameworkContinuation_1000_DBEC | low |
| `FUN_1008_0226` | `FUN_1008_0226` | 1.0000 | GdiWindowControlFramework_1008_0226 | medium |
| `FUN_1008_028c` | `FUN_1008_028c` | 0.9791 | GdiWindowControlFramework_1008_028C | low |
| `FUN_1008_02c6` | `FUN_1008_02c6` | 1.0000 | GdiWindowControlFramework_1008_02C6 | medium |
| `FUN_1008_02d0` | `FUN_1008_02d0` | 1.0000 | GdiWindowControlFramework_1008_02D0 | medium |
| `FUN_1008_02e2` | `FUN_1008_02e2` | 1.0000 | GdiWindowControlFramework_1008_02E2 | medium |
| `FUN_1008_0316` | `FUN_1008_0316` | 1.0000 | GdiWindowControlFramework_1008_0316 | medium |
| `FUN_1008_0342` | `FUN_1008_0342` | 0.9708 | GdiWindowControlFramework_1008_0342 | medium |
| `FUN_1008_0372` | `FUN_1008_0372` | 1.0000 | GdiWindowControlFramework_1008_0372 | low |
| `FUN_1008_0382` | `FUN_1008_0382` | 1.0000 | GdiWindowControlFramework_1008_0382 | low |
| `FUN_1008_0392` | `FUN_1008_0392` | 1.0000 | GdiWindowControlFramework_1008_0392 | low |
| `FUN_1008_03a2` | `FUN_1008_03a2` | 1.0000 | GdiWindowControlFramework_1008_03AND2 | low |
| `FUN_1008_0406` | `FUN_1008_0406` | 1.0000 | GdiWindowControlFramework_1008_0406 | low |
| `FUN_1008_0424` | `FUN_1008_0424` | 1.0000 | GdiWindowControlFramework_1008_0424 | low |
| `FUN_1008_0490` | `FUN_1008_0490` | 1.0000 | GdiWindowControlFramework_1008_0490 | low |
| `FUN_1008_06ec` | `FUN_1008_06ec` | 1.0000 | GdiWindowControlFramework_1008_06EC | low |
| `FUN_1008_082e` | `FUN_1008_082e` | 1.0000 | GdiWindowControlFramework_1008_082E | low |
| `FUN_1008_08c0` | `FUN_1008_08c0` | 1.0000 | GdiWindowControlFramework_1008_08C0 | medium |
| `FUN_1008_0914` | `FUN_1008_0914` | 1.0000 | GdiWindowControlFramework_1008_0914 | medium |
| `FUN_1008_0968` | `FUN_1008_0968` | 1.0000 | GdiWindowControlFramework_1008_0968 | medium |
| `FUN_1008_09c8` | `FUN_1008_09c8` | 1.0000 | Win16WindowMessage_1008_09C8 | high |
| `FUN_1008_0a1c` | `FUN_1008_0a1c` | 1.0000 | GdiWindowControlFramework_1008_0AND1C | medium |
| `FUN_1008_0a7c` | `FUN_1008_0a7c` | 1.0000 | Win16WindowMessage_1008_0AND7C | high |
| `FUN_1008_0ad0` | `FUN_1008_0ad0` | 1.0000 | GdiWindowControlFramework_1008_0AD0 | low |
| `FUN_1008_0ae8` | `FUN_1008_0ae8` | 1.0000 | Win16DrawingGdi_1008_0AE8 | high |
| `FUN_1008_0b3c` | `FUN_1008_0b3c` | 1.0000 | Win16DrawingGdi_1008_0B3C | high |
| `FUN_1008_0be4` | `FUN_1008_0be4` | 0.9858 | Win16DrawingGdi_1008_0BE4 | high |
| `FUN_1008_0c2c` | `FUN_1008_0c2c` | 0.9741 | Win16DrawingGdi_1008_0C2C | high |
| `FUN_1008_0c56` | `FUN_1008_0c56` | 0.9861 | Win16WindowMessage_1008_0C56 | high |
| `FUN_1008_0c9e` | `FUN_1008_0c9e` | 0.9741 | Win16DrawingGdi_1008_0C9E | high |
| `FUN_1008_0cc8` | `FUN_1008_0cc8` | 0.9779 | GdiWindowControlFramework_1008_0CC8 | medium |
| `FUN_1008_0d38` | `FUN_1008_0d38` | 0.9735 | GdiWindowControlFramework_1008_0D38 | low |
| `FUN_1008_0d88` | `FUN_1008_0d88` | 1.0000 | GdiWindowControlFramework_1008_0D88 | medium |
| `FUN_1008_0d92` | `FUN_1008_0d92` | 1.0000 | GdiWindowControlFramework_1008_0D92 | medium |
| `FUN_1008_0da4` | `FUN_1008_0da4` | 1.0000 | GdiWindowControlFramework_1008_0DA4 | medium |
| `FUN_1008_0dce` | `FUN_1008_0dce` | 1.0000 | GdiWindowControlFramework_1008_0DCE | medium |
| `FUN_1008_0df6` | `FUN_1008_0df6` | 0.9853 | GdiWindowControlFramework_1008_0DF6 | medium |
| `FUN_1008_0e18` | `FUN_1008_0e18` | 0.9735 | GdiWindowControlFramework_1008_0E18 | medium |
| `FUN_1008_0ea8` | `FUN_1008_0ea8` | 0.9812 | GdiWindowControlFramework_1008_0EA8 | medium |
| `FUN_1008_0fc4` | `FUN_1008_0fc4` | 0.9869 | GdiWindowControlFramework_1008_0FC4 | medium |
| `FUN_1008_0fe8` | `FUN_1008_0fe8` | 1.0000 | GdiWindowControlFramework_1008_0FE8 | medium |
| `FUN_1008_1136` | `FUN_1008_1136` | 1.0000 | StringText_1008_1136 | high |
| `FUN_1008_1178` | `FUN_1008_1178` | 0.9926 | Win16WindowMessage_1008_1178 | high |
| `FUN_1008_11c2` | `FUN_1008_11c2` | 1.0000 | Win16WindowMessage_1008_11C2 | high |
| `FUN_1008_1214` | `FUN_1008_1214` | 1.0000 | GdiWindowControlFramework_1008_1214 | medium |
| `FUN_1008_125e` | `FUN_1008_125e` | 0.9872 | Win16WindowMessage_1008_125E | high |
| `FUN_1008_1352` | `FUN_1008_1352` | 0.9910 | GdiWindowControlFramework_1008_1352 | medium |
| `FUN_1008_13fe` | `FUN_1008_13fe` | 1.0000 | GdiWindowControlFramework_1008_13FE | medium |
| `FUN_1008_1422` | `FUN_1008_1422` | 1.0000 | GdiWindowControlFramework_1008_1422 | medium |
| `FUN_1008_146c` | `FUN_1008_146c` | 0.9956 | Win16WindowMessage_1008_146C | high |
| `FUN_1008_1642` | `FUN_1008_1642` | 1.0000 | GdiWindowControlFramework_1008_1642 | low |
| `FUN_1008_1660` | `FUN_1008_1660` | 1.0000 | GdiWindowControlFramework_1008_1660 | medium |
| `FUN_1008_168c` | `FUN_1008_168c` | 1.0000 | GdiWindowControlFramework_1008_168C | medium |
| `FUN_1008_16a0` | `FUN_1008_16a0` | 1.0000 | GdiWindowControlFramework_1008_16AND0 | medium |
| `FUN_1008_1ce8` | `FUN_1008_1ce8` | 1.0000 | GdiWindowControlFramework_1008_1CE8 | medium |
| `FUN_1008_1d0e` | `FUN_1008_1d0e` | 1.0000 | GdiWindowControlFramework_1008_1D0E | medium |
| `FUN_1008_1d44` | `FUN_1008_1d44` | 1.0000 | GdiWindowControlFramework_1008_1D44 | low |
| `FUN_1008_1d70` | `FUN_1008_1d70` | 1.0000 | GdiWindowControlFramework_1008_1D70 | medium |
| `FUN_1008_1df4` | `FUN_1008_1df4` | 0.9957 | GdiWindowControlFramework_1008_1DF4 | medium |
| `FUN_1008_1e5c` | `FUN_1008_1e5c` | 0.9969 | GdiWindowControlFramework_1008_1E5C | medium |
| `FUN_1008_1ed4` | `FUN_1008_1ed4` | 0.9828 | GdiWindowControlFramework_1008_1ED4 | medium |
| `FUN_1008_1f00` | `FUN_1008_1f00` | 1.0000 | GdiWindowControlFramework_1008_1F00 | low |
| `FUN_1008_1ffe` | `FUN_1008_1ffe` | 1.0000 | GdiWindowControlFramework_1008_1FFE | medium |
| `FUN_1008_2066` | `FUN_1008_2066` | 0.9976 | GdiWindowControlFramework_1008_2066 | medium |
| `FUN_1008_2162` | `FUN_1008_2162` | 0.9948 | GdiWindowControlFramework_1008_2162 | medium |
| `FUN_1008_2214` | `FUN_1008_2214` | 0.9917 | GdiWindowControlFramework_1008_2214 | medium |
| `FUN_1008_2242` | `FUN_1008_2242` | 0.9813 | GdiWindowControlFramework_1008_2242 | medium |
| `FUN_1008_22c6` | `FUN_1008_22c6` | 1.0000 | GdiWindowControlFramework_1008_22C6 | medium |
| `FUN_1008_24d8` | `FUN_1008_24d8` | 0.9853 | GdiWindowControlFramework_1008_24D8 | medium |
| `FUN_1008_24fa` | `FUN_1008_24fa` | 0.9870 | GdiWindowControlFramework_1008_24FA | medium |
| `FUN_1008_2524` | `FUN_1008_2524` | 0.9846 | GdiWindowControlFramework_1008_2524 | low |
| `FUN_1008_2544` | `FUN_1008_2544` | 1.0000 | GdiWindowControlFramework_1008_2544 | medium |
| `FUN_1008_25ac` | `FUN_1008_25ac` | 1.0000 | GdiWindowControlFramework_1008_25AC | low |
| `FUN_1008_262e` | `FUN_1008_262e` | 1.0000 | GdiWindowControlFramework_1008_262E | medium |
| `FUN_1008_26ea` | `FUN_1008_26ea` | 1.0000 | GdiWindowControlFramework_1008_26EA | low |
| `FUN_1008_2702` | `FUN_1008_2702` | 1.0000 | GdiWindowControlFramework_1008_2702 | low |
| `FUN_1008_27a2` | `FUN_1008_27a2` | 1.0000 | GdiWindowControlFramework_1008_27AND2 | medium |
| `FUN_1008_27fa` | `FUN_1008_27fa` | 0.9913 | Win16WindowMessage_1008_27FA | high |
| `FUN_1008_2892` | `FUN_1008_2892` | 0.9847 | GdiWindowControlFramework_1008_2892 | medium |
| `FUN_1008_292e` | `FUN_1008_292e` | 0.9912 | GdiWindowControlFramework_1008_292E | medium |
| `FUN_1008_2968` | `FUN_1008_2968` | 1.0000 | GdiWindowControlFramework_1008_2968 | low |
| `FUN_1008_2a8c` | `FUN_1008_2a8c` | 0.9212 | GdiWindowControlFramework_1008_2AND8C | medium |
| `FUN_1008_2ac2` | `FUN_1008_2ac2` | 0.8839 | FrameworkObjectInitWrapper_1008_2AC2 | medium |
| `FUN_1008_2ca2` | `FUN_1008_2ca2` | 0.9929 | GdiWindowControlFramework_1008_2CA2 | medium |
| `FUN_1008_2e14` | `FUN_1008_2e14` | 1.0000 | GdiWindowControlFramework_1008_2E14 | medium |
| `FUN_1008_2e96` | `FUN_1008_2e96` | 1.0000 | GdiWindowControlFramework_1008_2E96 | medium |
| `FUN_1008_2f08` | `FUN_1008_2f08` | 1.0000 | Win16WindowMessage_1008_2F08 | high |
| `FUN_1008_2fd0` | `FUN_1008_2fd0` | 1.0000 | Win16WindowMessage_1008_2FD0 | high |
| `FUN_1008_302e` | `FUN_1008_302e` | 1.0000 | Win16WindowMessage_1008_302E | high |
| `FUN_1008_30b0` | `FUN_1008_30b0` | 1.0000 | UiDialogMenuFramework_1008_30B0 | medium |
| `FUN_1008_319c` | `FUN_1008_319c` | 0.9976 | Win16WindowMessage_1008_319C | high |
| `FUN_1008_32a6` | `FUN_1008_32a6` | 1.0000 | Win16WindowMessage_1008_32AND6 | high |
| `FUN_1008_3338` | `FUN_1008_3338` | 1.0000 | UiDialogMenuFramework_1008_3338 | low |
| `FUN_1008_3354` | `FUN_1008_3354` | 1.0000 | UiDialogMenuFramework_1008_3354 | low |
| `FUN_1008_3370` | `FUN_1008_3370` | 0.9957 | UiDialogMenuFramework_1008_3370 | medium |
| `FUN_1008_360c` | `FUN_1008_360c` | 1.0000 | Win16WindowMessage_1008_360C | high |
| `FUN_1008_37c2` | `FUN_1008_37c2` | 1.0000 | UiDialogMenuFramework_1008_37C2 | medium |
| `FUN_1008_37ee` | `FUN_1008_37ee` | 0.9933 | UiDialogMenuFramework_1008_37EE | medium |
| `FUN_1008_38cd` | `FUN_1008_38cd` | 1.0000 | UiDialogMenuFramework_1008_38CD | medium |
| `FUN_1008_38db` | `FUN_1008_38db` | 1.0000 | UiDialogMenuFramework_1008_38DB | medium |
| `FUN_1008_390a` | `FUN_1008_390a` | 1.0000 | UiDialogMenuFramework_1008_390AND | medium |
| `FUN_1008_396b` | `FUN_1008_396b` | 1.0000 | UiDialogMenuFramework_1008_396B | low |
| `FUN_1008_3994` | `FUN_1008_3994` | 1.0000 | UiDialogMenuFramework_1008_3994 | low |
| `FUN_1008_39a8` | `FUN_1008_39a8` | 1.0000 | UiDialogMenuFramework_1008_39AND8 | medium |
| `FUN_1008_39cc` | `FUN_1008_39cc` | 1.0000 | UiDialogMenuFramework_1008_39CC | medium |
| `FUN_1008_39f2` | `FUN_1008_39f2` | 1.0000 | UiDialogMenuFramework_1008_39F2 | medium |
| `FUN_1008_3a26` | `FUN_1008_3a26` | 1.0000 | UiDialogMenuFramework_1008_3AND26 | medium |
| `FUN_1008_3ba8` | `FUN_1008_3ba8` | 1.0000 | UiDialogMenuFramework_1008_3BA8 | medium |
| `FUN_1008_3c3d` | `FUN_1008_3c3d` | 0.9972 | UiDialogMenuFramework_1008_3C3D | medium |
| `FUN_1008_3cb7` | `FUN_1008_3cb7` | 1.0000 | UiDialogMenuFramework_1008_3CB7 | medium |
| `FUN_1008_3cf4` | `FUN_1008_3cf4` | 1.0000 | UiDialogMenuFramework_1008_3CF4 | medium |
| `FUN_1008_3d22` | `FUN_1008_3d22` | 1.0000 | UiDialogMenuFramework_1008_3D22 | medium |
| `FUN_1008_3d2f` | `FUN_1008_3d2f` | 1.0000 | UiDialogMenuFramework_1008_3D2F | medium |
| `FUN_1008_3d41` | `FUN_1008_3d41` | 1.0000 | UiDialogMenuFramework_1008_3D41 | medium |
| `FUN_1008_3d59` | `FUN_1008_3d59` | 1.0000 | UiDialogMenuFramework_1008_3D59 | medium |
| `FUN_1008_3d80` | `FUN_1008_3d80` | 0.9918 | UiDialogMenuFramework_1008_3D80 | medium |
| `FUN_1008_3e74` | `FUN_1008_3e74` | 1.0000 | UiDialogMenuFramework_1008_3E74 | medium |
| `FUN_1008_3ea4` | `FUN_1008_3ea4` | 0.9801 | UiDialogMenuFramework_1008_3EA4 | medium |
| `FUN_1008_3ebe` | `FUN_1008_3ebe` | 1.0000 | UiDialogMenuFramework_1008_3EBE | medium |
| `FUN_1008_3fc4` | `FUN_1008_3fc4` | 1.0000 | UiDialogMenuFramework_1008_3FC4 | medium |
| `FUN_1008_4068` | `FUN_1008_4068` | 1.0000 | UiDialogMenuFramework_1008_4068 | medium |
| `FUN_1008_415a` | `FUN_1008_415a` | 1.0000 | UiDialogMenuFramework_1008_415AND | medium |
| `FUN_1008_4186` | `FUN_1008_4186` | 1.0000 | UiDialogMenuFramework_1008_4186 | medium |
| `FUN_1008_41ca` | `FUN_1008_41ca` | 1.0000 | UiDialogMenuFramework_1008_41CA | medium |
| `FUN_1008_42fc` | `FUN_1008_42fc` | 1.0000 | UiDialogMenuFramework_1008_42FC | medium |
| `FUN_1008_437a` | `FUN_1008_437a` | 1.0000 | UiDialogMenuFramework_1008_437AND | medium |
| `FUN_1008_43b8` | `FUN_1008_43b8` | 1.0000 | UiDialogMenuFramework_1008_43B8 | medium |
| `FUN_1008_440e` | `FUN_1008_440e` | 1.0000 | UiDialogMenuFramework_1008_440E | medium |
| `FUN_1008_449a` | `FUN_1008_449a` | 1.0000 | UiDialogMenuFramework_1008_449AND | medium |
| `FUN_1008_4504` | `FUN_1008_4504` | 0.9985 | UiDialogMenuFramework_1008_4504 | medium |
| `FUN_1008_4d8a` | `FUN_1008_4d8a` | 1.0000 | UiDialogMenuFramework_1008_4D8AND | low |
| `FUN_1008_4daa` | `FUN_1008_4daa` | 1.0000 | UiDialogMenuFramework_1008_4DAA | medium |
| `FUN_1008_4dd8` | `FUN_1008_4dd8` | 1.0000 | UiDialogMenuFramework_1008_4DD8 | medium |
| `FUN_1008_4df2` | `FUN_1008_4df2` | 1.0000 | UiDialogMenuFramework_1008_4DF2 | medium |
| `FUN_1008_4e24` | `FUN_1008_4e24` | 0.9936 | UiDialogMenuFramework_1008_4E24 | medium |
| `FUN_1008_530c` | `FUN_1008_530c` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_530C | medium |
| `FUN_1008_5348` | `FUN_1008_5348` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_5348 | medium |
| `FUN_1008_53b0` | `FUN_1008_53b0` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_53B0 | medium |
| `FUN_1008_53e8` | `FUN_1008_53e8` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_53E8 | medium |
| `FUN_1008_54bc` | `FUN_1008_54bc` | 0.9965 | CRuntimeMemoryStringAndImportThunks_1008_54BC | medium |
| `FUN_1008_54d4` | `FUN_1008_54d4` | 0.9965 | CRuntimeMemoryStringAndImportThunks_1008_54D4 | medium |
| `FUN_1008_5787` | `FUN_1008_5787` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_5787 | low |
| `FUN_1008_5798` | `FUN_1008_5798` | 0.9974 | CRuntimeMemoryStringAndImportThunks_1008_5798 | medium |
| `FUN_1008_5902` | `FUN_1008_5902` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_5902 | medium |
| `FUN_1008_59dc` | `FUN_1008_59dc` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_59DC | medium |
| `FUN_1008_5a40` | `FUN_1008_5a40` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_5AND40 | medium |
| `FUN_1008_5a4e` | `FUN_1008_5a4e` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_5AND4E | medium |
| `FUN_1008_5a9c` | `FUN_1008_5a9c` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_5AND9C | low |
| `FUN_1008_5ab0` | `FUN_1008_5ab0` | 0.9952 | MemoryRuntime_1008_5AB0 | high |
| `FUN_1008_5b0c` | `FUN_1008_5b0c` | 1.0000 | MemoryRuntime_1008_5B0C | high |
| `FUN_1008_5b26` | `FUN_1008_5b26` | 1.0000 | MemoryRuntime_1008_5B26 | high |
| `FUN_1008_5b94` | `FUN_1008_5b94` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_5B94 | medium |
| `FUN_1008_5bec` | `FUN_1008_5bec` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_5BEC | low |
| `FUN_1008_5c8e` | `FUN_1008_5c8e` | 0.9861 | CRuntimeMemoryStringAndImportThunks_1008_5C8E | low |
| `FUN_1008_5caf` | `FUN_1008_5caf` | 0.9958 | CRuntimeMemoryStringAndImportThunks_1008_5CAF | medium |
| `FUN_1008_5d56` | `FUN_1008_5d56` | 0.9923 | CRuntimeMemoryStringAndImportThunks_1008_5D56 | medium |
| `FUN_1008_5d8a` | `FUN_1008_5d8a` | 0.9801 | CRuntimeMemoryStringAndImportThunks_1008_5D8AND | medium |
| `FUN_1008_5dc0` | `FUN_1008_5dc0` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_5DC0 | medium |
| `FUN_1008_5e3c` | `FUN_1008_5e3c` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_5E3C | medium |
| `FUN_1008_5ec8` | `FUN_1008_5ec8` | 0.9935 | MemoryRuntime_1008_5EC8 | high |
| `FUN_1008_5f2e` | `FUN_1008_5f2e` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_5F2E | low |
| `FUN_1008_5f4e` | `FUN_1008_5f4e` | 0.9940 | MemoryRuntime_1008_5F4E | high |
| `FUN_1008_5fd0` | `FUN_1008_5fd0` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_5FD0 | medium |
| `FUN_1008_5fe0` | `FUN_1008_5fe0` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_5FE0 | medium |
| `FUN_1008_5ff0` | `FUN_1008_5ff0` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_5FF0 | low |
| `FUN_1008_601a` | `FUN_1008_601a` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_601AND | medium |
| `FUN_1008_602c` | `FUN_1008_602c` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_602C | medium |
| `FUN_1008_606c` | `FUN_1008_606c` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_606C | medium |
| `FUN_1008_609e` | `FUN_1008_609e` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_609E | low |
| `FUN_1008_60ba` | `FUN_1008_60ba` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_60BA | medium |
| `FUN_1008_60e2` | `FUN_1008_60e2` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_60E2 | medium |
| `FUN_1008_60fe` | `FUN_1008_60fe` | 0.9754 | CRuntimeMemoryStringAndImportThunks_1008_60FE | low |
| `FUN_1008_615e` | `FUN_1008_615e` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_615E | medium |
| `FUN_1008_61de` | `FUN_1008_61de` | 0.9959 | CRuntimeMemoryStringAndImportThunks_1008_61DE | medium |
| `FUN_1008_6260` | `FUN_1008_6260` | 0.9959 | CRuntimeMemoryStringAndImportThunks_1008_6260 | medium |
| `FUN_1008_63e4` | `FUN_1008_63e4` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_63E4 | medium |
| `FUN_1008_6442` | `FUN_1008_6442` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_6442 | medium |
| `FUN_1008_6486` | `FUN_1008_6486` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_6486 | medium |
| `FUN_1008_64c2` | `FUN_1008_64c2` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_64C2 | medium |
| `FUN_1008_651c` | `FUN_1008_651c` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_651C | medium |
| `FUN_1008_6538` | `FUN_1008_6538` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_6538 | medium |
| `FUN_1008_65a8` | `FUN_1008_65a8` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_65AND8 | medium |
| `FUN_1008_66fe` | `FUN_1008_66fe` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_66FE | medium |
| `FUN_1008_673a` | `FUN_1008_673a` | 0.9587 | MemoryRuntime_1008_673AND | high |
| `FUN_1008_676f` | `FUN_1008_676f` | 0.9983 | MemoryRuntime_1008_676F | high |
| `FUN_1008_68a0` | `FUN_1008_68a0` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_68AND0 | low |
| `FUN_1008_68de` | `FUN_1008_68de` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_68DE | medium |
| `FUN_1008_6972` | `FUN_1008_6972` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_6972 | medium |
| `FUN_1008_699c` | `FUN_1008_699c` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_699C | medium |
| `FUN_1008_69d2` | `FUN_1008_69d2` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_69D2 | medium |
| `FUN_1008_69fa` | `FUN_1008_69fa` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_69FA | medium |
| `FUN_1008_6a54` | `FUN_1008_6a54` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_6AND54 | medium |
| `FUN_1008_6aac` | `FUN_1008_6aac` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_6AAC | medium |
| `FUN_1008_6b06` | `FUN_1008_6b06` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_6B06 | medium |
| `FUN_1008_6b96` | `FUN_1008_6b96` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_6B96 | medium |
| `FUN_1008_6bf6` | `FUN_1008_6bf6` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_6BF6 | medium |
| `FUN_1008_6c80` | `FUN_1008_6c80` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_6C80 | medium |
| `FUN_1008_6cac` | `FUN_1008_6cac` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_6CAC | medium |
| `FUN_1008_6ce6` | `FUN_1008_6ce6` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_6CE6 | medium |
| `FUN_1008_6d4e` | `FUN_1008_6d4e` | 0.9964 | CRuntimeMemoryStringAndImportThunks_1008_6D4E | medium |
| `FUN_1008_6e92` | `FUN_1008_6e92` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_6E92 | medium |
| `FUN_1008_6eb0` | `FUN_1008_6eb0` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_6EB0 | low |
| `FUN_1008_6ec8` | `FUN_1008_6ec8` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_6EC8 | medium |
| `FUN_1008_6f02` | `FUN_1008_6f02` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_6F02 | medium |
| `FUN_1008_6f38` | `FUN_1008_6f38` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_6F38 | medium |
| `FUN_1008_6f5c` | `FUN_1008_6f5c` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_6F5C | medium |
| `FUN_1008_6f80` | `FUN_1008_6f80` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_6F80 | low |
| `FUN_1008_701a` | `FUN_1008_701a` | 0.9900 | CRuntimeMemoryStringAndImportThunks_1008_701AND | medium |
| `FUN_1008_7028` | `FUN_1008_7028` | 0.9900 | CRuntimeMemoryStringAndImportThunks_1008_7028 | medium |
| `FUN_1008_705c` | `FUN_1008_705c` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_705C | medium |
| `FUN_1008_707e` | `FUN_1008_707e` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_707E | medium |
| `FUN_1008_7118` | `FUN_1008_7118` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_7118 | low |
| `FUN_1008_7156` | `FUN_1008_7156` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_7156 | medium |
| `FUN_1008_7176` | `FUN_1008_7176` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_7176 | medium |
| `FUN_1008_7232` | `FUN_1008_7232` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_7232 | medium |
| `FUN_1008_7290` | `FUN_1008_7290` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_7290 | medium |
| `FUN_1008_72c2` | `FUN_1008_72c2` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_72C2 | medium |
| `FUN_1008_7344` | `FUN_1008_7344` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_7344 | medium |
| `FUN_1008_735e` | `FUN_1008_735e` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_735E | medium |
| `FUN_1008_739a` | `FUN_1008_739a` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_739AND | low |
| `FUN_1008_73c0` | `FUN_1008_73c0` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_73C0 | low |
| `FUN_1008_73c5` | `FUN_1008_73c5` | 1.0000 | CRuntimeMemoryStringAndImportThunks_1008_73C5 | medium |
| `FUN_1010_0006` | `FUN_1010_0006` | 0.9876 | GameApplicationDispatchAndUiGlue_1010_0006 | medium |
| `FUN_1010_01dc` | `FUN_1010_01dc` | 0.9878 | GameApplicationDispatchAndUiGlue_1010_01DC | medium |
| `FUN_1010_0210` | `FUN_1010_0210` | 0.9878 | GameApplicationDispatchAndUiGlue_1010_0210 | medium |
| `FUN_1010_0244` | `FUN_1010_0244` | 0.9915 | GameApplicationDispatchAndUiGlue_1010_0244 | medium |
| `FUN_1010_026a` | `FUN_1010_026a` | 0.9915 | GameApplicationDispatchAndUiGlue_1010_026AND | medium |
| `FUN_1010_0290` | `FUN_1010_0290` | 0.9906 | GameApplicationDispatchAndUiGlue_1010_0290 | medium |
| `FUN_1010_02c2` | `FUN_1010_02c2` | 0.9906 | GameApplicationDispatchAndUiGlue_1010_02C2 | medium |
| `FUN_1010_02f4` | `FUN_1010_02f4` | 0.9906 | GameApplicationDispatchAndUiGlue_1010_02F4 | medium |
| `FUN_1010_0326` | `FUN_1010_0326` | 0.9906 | GameApplicationDispatchAndUiGlue_1010_0326 | medium |
| `FUN_1010_0358` | `FUN_1010_0358` | 0.9917 | GameApplicationDispatchAndUiGlue_1010_0358 | medium |
| `FUN_1010_037c` | `FUN_1010_037c` | 0.9897 | GameApplicationDispatchAndUiGlue_1010_037C | medium |
| `FUN_1010_039c` | `FUN_1010_039c` | 0.9911 | GameApplicationDispatchAndUiGlue_1010_039C | medium |
| `FUN_1010_0424` | `FUN_1010_0424` | 0.9718 | GameApplicationDispatchAndUiGlue_1010_0424 | medium |
| `FUN_1010_0670` | `FUN_1010_0670` | 0.9903 | GameApplicationDispatchAndUiGlue_1010_0670 | medium |
| `FUN_1010_06a0` | `FUN_1010_06a0` | 0.9898 | GameApplicationDispatchAndUiGlue_1010_06AND0 | medium |
| `FUN_1010_0716` | `FUN_1010_0716` | 1.0000 | GameApplicationDispatchAndUiGlue_1010_0716 | medium |
| `FUN_1010_0730` | `FUN_1010_0730` | 1.0000 | GameApplicationDispatchAndUiGlue_1010_0730 | medium |
| `FUN_1010_0748` | `FUN_1010_0748` | 1.0000 | GameApplicationDispatchAndUiGlue_1010_0748 | medium |
| `FUN_1010_085e` | `FUN_1010_085e` | 0.9873 | GameApplicationDispatchAndUiGlue_1010_085E | medium |
| `FUN_1010_097c` | `FUN_1010_097c` | 0.9705 | GameApplicationDispatchAndUiGlue_1010_097C | medium |
| `FUN_1010_09be` | `FUN_1010_09be` | 1.0000 | GameApplicationDispatchAndUiGlue_1010_09BE | medium |
| `FUN_1010_09e8` | `FUN_1010_09e8` | 1.0000 | GameApplicationDispatchAndUiGlue_1010_09E8 | medium |
| `FUN_1010_09fa` | `FUN_1010_09fa` | 0.9928 | TimerInput_1010_09FA | high |
| `FUN_1010_0a2a` | `FUN_1010_0a2a` | 1.0000 | GameApplicationDispatchAndUiGlue_1010_0AND2AND | medium |
| `FUN_1010_0a3c` | `FUN_1010_0a3c` | 1.0000 | GameApplicationDispatchAndUiGlue_1010_0AND3C | medium |
| `FUN_1010_0ad6` | `FUN_1010_0b22` | 1.0000 | GameApplicationDispatchAndUiGlue_1010_0B22 | low |
| `FUN_1010_0b00` | `FUN_1010_0b4c` | 1.0000 | GameApplicationDispatchAndUiGlue_1010_0B4C | low |
| `FUN_1010_0cc2` | `FUN_1010_0d0e` | 1.0000 | GameApplicationDispatchAndUiGlue_1010_0D0E | medium |
| `FUN_1010_0d52` | `FUN_1010_0d9e` | 1.0000 | GameApplicationDispatchAndUiGlue_1010_0D9E | low |
| `FUN_1010_0d58` | `FUN_1010_0da4` | 1.0000 | GameApplicationDispatchAndUiGlue_1010_0DA4 | low |
| `FUN_1010_0d86` | `FUN_1010_0dd2` | 1.0000 | GameApplicationDispatchAndUiGlue_1010_0DD2 | low |
| `FUN_1010_0da2` | `FUN_1010_0dee` | 1.0000 | GameApplicationDispatchAndUiGlue_1010_0DEE | medium |
| `FUN_1010_0de0` | `FUN_1010_0e2c` | 1.0000 | GameApplicationDispatchAndUiGlue_1010_0E2C | medium |
| `FUN_1010_0e1e` | `FUN_1010_0e6a` | 1.0000 | GameApplicationDispatchAndUiGlue_1010_0E6AND | medium |
| `FUN_1010_0e52` | `FUN_1010_0e9e` | 1.0000 | GameApplicationDispatchAndUiGlue_1010_0E9E | medium |
| `FUN_1010_0eaa` | `FUN_1010_0ef6` | 1.0000 | GameApplicationDispatchAndUiGlue_1010_0EF6 | low |
| `FUN_1010_0f18` | `FUN_1010_0f64` | 1.0000 | GameApplicationDispatchAndUiGlue_1010_0F64 | medium |
| `FUN_1010_124a` | `FUN_1010_1296` | 0.9880 | GameApplicationDispatchAndUiGlue_1010_1296 | medium |
| `FUN_1010_129c` | `FUN_1010_12e8` | 0.9883 | GameApplicationDispatchAndUiGlue_1010_12E8 | medium |
| `FUN_1010_12ee` | `FUN_1010_133a` | 0.9898 | GameApplicationDispatchAndUiGlue_1010_133AND | medium |
| `FUN_1010_1348` | `FUN_1010_1394` | 1.0000 | GameApplicationDispatchAndUiGlue_1010_1394 | medium |
| `FUN_1010_142a` | `FUN_1010_1476` | 1.0000 | GameApplicationDispatchAndUiGlue_1010_1476 | low |
| `FUN_1010_1446` | `FUN_1010_1492` | 1.0000 | GameApplicationDispatchAndUiGlue_1010_1492 | low |
| `FUN_1010_145c` | `FUN_1010_14a8` | 0.9955 | GameApplicationDispatchAndUiGlue_1010_14AND8 | medium |
| `FUN_1010_168a` | `FUN_1010_16d6` | 0.9985 | GameApplicationDispatchAndUiGlue_1010_16D6 | medium |
| `FUN_1010_17d0` | `FUN_1010_181c` | 0.9969 | GameApplicationDispatchAndUiGlue_1010_181C | medium |
| `FUN_1010_183e` | `FUN_1010_188a` | 1.0000 | GameApplicationDispatchAndUiGlue_1010_188AND | medium |
| `FUN_1010_19d6` | `FUN_1010_1a22` | 1.0000 | GameApplicationDispatchAndUiGlue_1010_1AND22 | medium |
| `FUN_1010_1d02` | `FUN_1010_1d4e` | 1.0000 | GameApplicationDispatchAndUiGlue_1010_1D4E | medium |
| `FUN_1010_1db4` | `FUN_1010_1e00` | 1.0000 | GameApplicationDispatchAndUiGlue_1010_1E00 | medium |
| `FUN_1010_216a` | `FUN_1010_21b6` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_21B6 | medium |
| `FUN_1010_21c4` | `FUN_1010_2210` | 0.9972 | GameDataMapObjectOrRendererSupport_1010_2210 | medium |
| `FUN_1010_22e8` | `FUN_1010_2334` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_2334 | low |
| `FUN_1010_234c` | `FUN_1010_2398` | 0.9871 | GameDataMapObjectOrRendererSupport_1010_2398 | medium |
| `FUN_1010_2390` | `FUN_1010_23dc` | 0.9885 | GameDataMapObjectOrRendererSupport_1010_23DC | medium |
| `FUN_1010_23da` | `FUN_1010_2426` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_2426 | medium |
| `FUN_1010_242e` | `FUN_1010_247a` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_247AND | medium |
| `FUN_1010_2470` | `FUN_1010_24bc` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_24BC | medium |
| `FUN_1010_250a` | `FUN_1010_2556` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_2556 | medium |
| `FUN_1010_25ac` | `FUN_1010_25f8` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_25F8 | medium |
| `FUN_1010_25fe` | `FUN_1010_264a` | 0.9963 | GameDataMapObjectOrRendererSupport_1010_264AND | medium |
| `FUN_1010_272e` | `FUN_1010_277a` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_277AND | medium |
| `FUN_1010_27b4` | `FUN_1010_2800` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_2800 | medium |
| `FUN_1010_28e4` | `FUN_1010_2930` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_2930 | low |
| `FUN_1010_2972` | `FUN_1010_29be` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_29BE | medium |
| `FUN_1010_2a60` | `FUN_1010_2aac` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_2AAC | medium |
| `FUN_1010_2b88` | `FUN_1010_2bd4` | 1.0000 | Win16WindowMessage_1010_2BD4 | high |
| `FUN_1010_2b9a` | `FUN_1010_2be6` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_2BE6 | medium |
| `FUN_1010_2bb6` | `FUN_1010_2c02` | 0.9946 | GameDataMapObjectOrRendererSupport_1010_2C02 | medium |
| `FUN_1010_2c16` | `FUN_1010_2c62` | 1.0000 | Win16WindowMessage_1010_2C62 | high |
| `FUN_1010_2c7a` | `FUN_1010_2cc6` | 1.0000 | Win16DrawingGdi_1010_2CC6 | high |
| `FUN_1010_2d0c` | `FUN_1010_2d58` | 0.9915 | GameDataMapObjectOrRendererSupport_1010_2D58 | medium |
| `FUN_1010_2d50` | `FUN_1010_2d9c` | 0.9553 | Win16WindowMessage_1010_2D9C | high |
| `FUN_1010_2ec2` | `FUN_1010_2f36` | 0.9852 | Win16DrawingGdi_1010_2F36 | high |
| `FUN_1010_300c` | `FUN_1010_3080` | 1.0000 | Win16DrawingGdi_1010_3080 | high |
| `FUN_1010_307e` | `FUN_1010_30f2` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_30F2 | medium |
| `FUN_1010_30d6` | `FUN_1010_314a` | 0.9957 | Win16DrawingGdi_1010_314AND | high |
| `FUN_1010_3136` | `FUN_1010_31aa` | 0.4797 | SetupOrAnimateWin16Palette | high |
| `FUN_1010_32b2` | `FUN_1010_3360` | 0.9748 | GameDataMapObjectOrRendererSupport_1010_3360 | medium |
| `FUN_1010_3330` | `FUN_1010_33d6` | 0.9392 | GameDataMapObjectOrRendererSupport_1010_33D6 | medium |
| `FUN_1010_358c` | `FUN_1010_3612` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_3612 | medium |
| `FUN_1010_35e4` | `FUN_1010_366a` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_366AND | medium |
| `FUN_1010_36c8` | `FUN_1010_374e` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_374E | medium |
| `FUN_1010_389e` | `FUN_1010_3924` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_3924 | medium |
| `FUN_1010_391c` | `FUN_1010_39a2` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_39AND2 | low |
| `FUN_1010_3946` | `FUN_1010_39cc` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_39CC | medium |
| `FUN_1010_398e` | `FUN_1010_3a14` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_3AND14 | medium |
| `FUN_1010_39d8` | `FUN_1010_3a5e` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_3AND5E | low |
| `FUN_1010_39f4` | `FUN_1010_3a7a` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_3AND7AND | medium |
| `FUN_1010_3a32` | `FUN_1010_3ab8` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_3AB8 | medium |
| `FUN_1010_3a3c` | `FUN_1010_3ac2` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_3AC2 | low |
| `FUN_1010_3a46` | `FUN_1010_3acc` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_3ACC | low |
| `FUN_1010_3a6e` | `FUN_1010_3af4` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_3AF4 | medium |
| `FUN_1010_3a90` | `FUN_1010_3b16` | 0.7739 | SetPaletteEntry | medium |
| `FUN_1010_3ad8` | `FUN_1010_3b7c` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_3B7C | medium |
| `FUN_1010_3d14` | `FUN_1010_3db8` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_3DB8 | medium |
| `FUN_1010_3da0` | `FUN_1010_3e44` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_3E44 | medium |
| `FUN_1010_3edc` | `FUN_1010_3f80` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_3F80 | medium |
| `FUN_1010_40fe` | `FUN_1010_41a2` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_41AND2 | medium |
| `FUN_1010_41e0` | `FUN_1010_4284` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_4284 | medium |
| `FUN_1010_4252` | `FUN_1010_42f6` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_42F6 | medium |
| `FUN_1010_42c4` | `FUN_1010_4368` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_4368 | medium |
| `FUN_1010_4366` | `FUN_1010_440a` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_440AND | medium |
| `FUN_1010_44a8` | `FUN_1010_454c` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_454C | medium |
| `FUN_1010_454c` | `FUN_1010_45f0` | 0.9946 | GameDataMapObjectOrRendererSupport_1010_45F0 | medium |
| `FUN_1010_459c` | `FUN_1010_4640` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_4640 | medium |
| `FUN_1010_45f2` | `FUN_1010_4696` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_4696 | medium |
| `FUN_1010_4654` | `FUN_1010_46f8` | 1.0000 | GameDataMapObjectOrRendererSupport_1010_46F8 | medium |
| `FUN_1010_46da` | `FUN_1010_477e` | 0.9796 | GameDataMapObjectOrRendererSupport_1010_477E | medium |
| `FUN_1010_4762` | `FUN_1010_4806` | 0.9835 | GameDataMapObjectOrRendererSupport_1010_4806 | medium |
| `FUN_1010_47c4` | `FUN_1010_4868` | 0.9536 | LoadCurrentMapBlock8192 | medium |
| `FUN_1010_48e6` | `FUN_1010_498a` | 0.9404 | BuildEpisodePathsAndLoadMapHeader | medium |
| `FUN_1010_497a` | `FUN_1010_4a1e` | 0.9846 | GameDataMapObjectOrRendererSupport_1010_4AND1E | medium |
| `FUN_1010_4a0c` | `FUN_1010_4ab0` | 0.9784 | GameDataMapObjectOrRendererSupport_1010_4AB0 | medium |
| `FUN_1010_4ae2` | `FUN_1010_4b86` | 0.9732 | GameDataMapObjectOrRendererSupport_1010_4B86 | medium |
| `FUN_1010_4be6` | `FUN_1010_4c8a` | 0.9984 | GameDataMapObjectOrRendererSupport_1010_4C8AND | medium |
| `FUN_1010_508e` | `FUN_1010_5132` | 0.9205 | LoadSndEventDirectory32To110 | medium |
| `FUN_1010_50ee` | `FUN_1010_5192` | 1.0000 | LoadSndDirectoryWithProgress79 | medium |
| `FUN_1010_5110` | `FUN_1010_51b4` | 1.0000 | GameSimulationInputAndMultimedia_1010_51B4 | medium |
| `FUN_1010_51bc` | `FUN_1010_5260` | 1.0000 | GameSimulationInputAndMultimedia_1010_5260 | medium |
| `FUN_1010_52aa` | `FUN_1010_534e` | 0.9344 | GameSimulationInputAndMultimedia_1010_534E | medium |
| `FUN_1010_52e4` | `FUN_1010_5388` | 0.9787 | GameSimulationInputAndMultimedia_1010_5388 | medium |
| `FUN_1010_53c2` | `FUN_1010_5466` | 0.9764 | GameSimulationInputAndMultimedia_1010_5466 | medium |
| `FUN_1010_56a8` | `FUN_1010_574c` | 0.9859 | GameSimulationInputAndMultimedia_1010_574C | medium |
| `FUN_1010_5af2` | `FUN_1010_5b96` | 0.9753 | GameSimulationInputAndMultimedia_1010_5B96 | medium |
| `FUN_1010_5c58` | `FUN_1010_5cfc` | 0.8898 | LazyLoadUifDirectoryAndGetEntryOffset | medium |
| `FUN_1010_5cce` | `FUN_1010_5d72` | 0.9747 | DecodeDisplayUifPcxSlot | medium |
| `FUN_1010_5e6e` | `FUN_1010_5f12` | 0.9357 | LoadUifRawSlot | medium |
| `FUN_1010_5ef4` | `FUN_1010_5f98` | 0.9681 | GameSimulationInputAndMultimedia_1010_5F98 | medium |
| `FUN_1010_5fea` | `FUN_1010_608e` | 1.0000 | GameSimulationInputAndMultimedia_1010_608E | medium |
| `FUN_1010_6006` | `FUN_1010_60aa` | 0.9834 | GameSimulationInputAndMultimedia_1010_60AA | medium |
| `FUN_1010_609e` | `FUN_1010_6142` | 1.0000 | GameSimulationInputAndMultimedia_1010_6142 | low |
| `FUN_1010_60ae` | `FUN_1010_6152` | 1.0000 | GameSimulationInputAndMultimedia_1010_6152 | medium |
| `FUN_1010_61c2` | `FUN_1010_6266` | 0.9909 | GameSimulationInputAndMultimedia_1010_6266 | medium |
| `FUN_1010_62a4` | `FUN_1010_6348` | 1.0000 | GameSimulationInputAndMultimedia_1010_6348 | medium |
| `FUN_1010_637e` | `FUN_1010_6422` | 1.0000 | GameSimulationInputAndMultimedia_1010_6422 | medium |
| `FUN_1010_6502` | `FUN_1010_65a6` | 1.0000 | GameSimulationInputAndMultimedia_1010_65AND6 | medium |
| `FUN_1010_660c` | `FUN_1010_66b0` | 1.0000 | GameSimulationInputAndMultimedia_1010_66B0 | medium |
| `FUN_1010_6870` | `FUN_1010_6914` | 1.0000 | GameSimulationInputAndMultimedia_1010_6914 | medium |
| `FUN_1010_68a6` | `FUN_1010_694a` | 1.0000 | GameSimulationInputAndMultimedia_1010_694AND | medium |
| `FUN_1010_68e2` | `FUN_1010_6986` | 1.0000 | GameSimulationInputAndMultimedia_1010_6986 | medium |
| `FUN_1010_6a20` | `FUN_1010_6ac4` | 1.0000 | GameSimulationInputAndMultimedia_1010_6AC4 | medium |
| `FUN_1010_6adc` | `FUN_1010_6b80` | 1.0000 | GameSimulationInputAndMultimedia_1010_6B80 | medium |
| `FUN_1010_6b76` | `FUN_1010_6c1a` | 0.9775 | GameSimulationInputAndMultimedia_1010_6C1AND | medium |
| `FUN_1010_6bd4` | `FUN_1010_6c78` | 0.9817 | GameSimulationInputAndMultimedia_1010_6C78 | medium |
| `FUN_1010_6d18` | `FUN_1010_6dbc` | 1.0000 | GameSimulationInputAndMultimedia_1010_6DBC | medium |
| `FUN_1010_6d56` | `FUN_1010_6dfa` | 1.0000 | GameSimulationInputAndMultimedia_1010_6DFA | medium |
| `FUN_1010_6dc2` | `FUN_1010_6e66` | 1.0000 | GameSimulationInputAndMultimedia_1010_6E66 | medium |
| `FUN_1010_6e3c` | `FUN_1010_6ee0` | 1.0000 | GameSimulationInputAndMultimedia_1010_6EE0 | medium |
| `FUN_1010_6f2a` | `FUN_1010_6fce` | 1.0000 | GameSimulationInputAndMultimedia_1010_6FCE | low |
| `FUN_1010_6f66` | `FUN_1010_700a` | 1.0000 | GameSimulationInputAndMultimedia_1010_700AND | medium |
| `FUN_1010_7138` | `FUN_1010_71dc` | 0.9995 | GameSimulationInputAndMultimedia_1010_71DC | medium |
| `FUN_1010_73f0` | `FUN_1010_7494` | 1.0000 | GameSimulationInputAndMultimedia_1010_7494 | medium |
| `FUN_1010_74f0` | `FUN_1010_7594` | 1.0000 | GameSimulationInputAndMultimedia_1010_7594 | medium |
| `FUN_1010_7588` | `FUN_1010_762c` | 1.0000 | GameSimulationInputAndMultimedia_1010_762C | low |
| `FUN_1010_75c0` | `FUN_1010_7664` | 1.0000 | GameSimulationInputAndMultimedia_1010_7664 | medium |
| `FUN_1010_7658` | `FUN_1010_76fc` | 1.0000 | GameSimulationInputAndMultimedia_1010_76FC | medium |
| `FUN_1010_787c` | `FUN_1010_7920` | 1.0000 | GameSimulationInputAndMultimedia_1010_7920 | medium |
| `FUN_1010_7962` | `FUN_1010_7a06` | 1.0000 | GameSimulationInputAndMultimedia_1010_7AND06 | medium |
| `FUN_1010_79a0` | `FUN_1010_7a44` | 0.9968 | GameSimulationInputAndMultimedia_1010_7AND44 | medium |
| `FUN_1010_7ab2` | `FUN_1010_7b56` | 1.0000 | GameSimulationInputAndMultimedia_1010_7B56 | medium |
| `FUN_1010_8006` | `FUN_1010_80aa` | 0.9905 | GameRuntimeAndResourceProcessing_1010_80AA | medium |
| `FUN_1010_8046` | `FUN_1010_80ea` | 1.0000 | GameRuntimeAndResourceProcessing_1010_80EA | low |
| `FUN_1010_8054` | `FUN_1010_80f8` | 1.0000 | GameRuntimeAndResourceProcessing_1010_80F8 | medium |
| `FUN_1010_8264` | `FUN_1010_8308` | 0.9864 | GameRuntimeAndResourceProcessing_1010_8308 | medium |
| `FUN_1010_832e` | `FUN_1010_83d2` | 0.9945 | GameRuntimeAndResourceProcessing_1010_83D2 | medium |
| `FUN_1010_83a8` | `FUN_1010_844c` | 1.0000 | GameRuntimeAndResourceProcessing_1010_844C | low |
| `FUN_1010_83da` | `FUN_1010_847e` | 1.0000 | GameRuntimeAndResourceProcessing_1010_847E | medium |
| `FUN_1010_8450` | `FUN_1010_84f4` | 1.0000 | GameRuntimeAndResourceProcessing_1010_84F4 | medium |
| `FUN_1010_8560` | `FUN_1010_8604` | 0.9942 | GameRuntimeAndResourceProcessing_1010_8604 | medium |
| `FUN_1010_8712` | `FUN_1010_87b6` | 1.0000 | GameRuntimeAndResourceProcessing_1010_87B6 | medium |
| `FUN_1010_885e` | `FUN_1010_8902` | 1.0000 | GameRuntimeAndResourceProcessing_1010_8902 | medium |
| `FUN_1010_8914` | `FUN_1010_89b8` | 1.0000 | GameRuntimeAndResourceProcessing_1010_89B8 | low |
| `FUN_1010_897c` | `FUN_1010_8a20` | 0.9940 | GameRuntimeAndResourceProcessing_1010_8AND20 | medium |
| `FUN_1010_8a08` | `FUN_1010_8aac` | 1.0000 | GameRuntimeAndResourceProcessing_1010_8AAC | medium |
| `FUN_1010_8a38` | `FUN_1010_8adc` | 1.0000 | GameRuntimeAndResourceProcessing_1010_8ADC | medium |
| `FUN_1010_8a62` | `FUN_1010_8b06` | 0.9971 | GameRuntimeAndResourceProcessing_1010_8B06 | medium |
| `FUN_1010_8b66` | `FUN_1010_8c0a` | 1.0000 | GameRuntimeAndResourceProcessing_1010_8C0AND | medium |
| `FUN_1010_8bf6` | `FUN_1010_8c9a` | 1.0000 | GameRuntimeAndResourceProcessing_1010_8C9AND | low |
| `FUN_1010_8c2e` | `FUN_1010_8cd2` | 0.9971 | Win16WindowMessage_1010_8CD2 | high |
| `FUN_1010_8e26` | `FUN_1010_8eca` | 1.0000 | TimerInput_1010_8ECA | high |
| `FUN_1010_8e5e` | `FUN_1010_8f02` | 0.9669 | TimerInput_1010_8F02 | high |
| `FUN_1010_8ee2` | `FUN_1010_8f86` | 0.9890 | GameRuntimeAndResourceProcessing_1010_8F86 | medium |
| `FUN_1010_9014` | `FUN_1010_90c2` | 1.0000 | ResetTwoTransientGlobals | low |
| `FUN_1010_9020` | `FUN_1010_90ce` | 0.9719 | GameRuntimeAndResourceProcessing_1010_90CE | medium |
| `FUN_1010_91ba` | `FUN_1010_9268` | 1.0000 | GameRuntimeAndResourceProcessing_1010_9268 | medium |
| `FUN_1010_9238` | `FUN_1010_92e6` | 1.0000 | GameRuntimeAndResourceProcessing_1010_92E6 | medium |
| `FUN_1010_925c` | `FUN_1010_930a` | 1.0000 | Win16WindowMessage_1010_930AND | high |
| `FUN_1010_92e4` | `FUN_1010_9392` | 1.0000 | GameRuntimeAndResourceProcessing_1010_9392 | medium |
| `FUN_1010_9500` | `FUN_1010_95ae` | 1.0000 | TimerInput_1010_95AE | high |
| `FUN_1010_9590` | `FUN_1010_963e` | 1.0000 | GameRuntimeAndResourceProcessing_1010_963E | medium |
| `FUN_1010_9648` | `FUN_1010_96f6` | 1.0000 | GameRuntimeAndResourceProcessing_1010_96F6 | medium |
| `FUN_1010_9758` | `FUN_1010_9806` | 0.9881 | TimerInput_1010_9806 | medium |
| `FUN_1010_99fe` | `FUN_1010_9aac` | 1.0000 | GameRuntimeAndResourceProcessing_1010_9AAC | medium |
| `FUN_1010_9ab6` | `FUN_1010_9b64` | 0.9994 | GameRuntimeAndResourceProcessing_1010_9B64 | medium |
| `FUN_1010_9c82` | `FUN_1010_9d30` | 0.9989 | GameRuntimeAndResourceProcessing_1010_9D30 | medium |
| `FUN_1010_9d72` | `FUN_1010_9e20` | 0.9980 | GameRuntimeAndResourceProcessing_1010_9E20 | medium |
| `FUN_1010_9e62` | `FUN_1010_9f10` | 1.0000 | GameRuntimeAndResourceProcessing_1010_9F10 | medium |
| `FUN_1010_9ef4` | `FUN_1010_9fa2` | 1.0000 | GameRuntimeAndResourceProcessing_1010_9FA2 | medium |
| `FUN_1010_a018` | `FUN_1010_a0c6` | 1.0000 | GameRuntimeAndResourceProcessing_1010_AND0C6 | medium |
| `FUN_1010_a040` | `FUN_1010_a0ee` | 1.0000 | GameRuntimeAndResourceProcessing_1010_AND0EE | medium |
| `FUN_1010_a13c` | `FUN_1010_a1ea` | 1.0000 | GameRuntimeAndResourceProcessing_1010_AND1EA | medium |
| `FUN_1010_a220` | `FUN_1010_a2ce` | 1.0000 | GameRuntimeAndResourceProcessing_1010_AND2CE | medium |
| `FUN_1010_a308` | `FUN_1010_a3b6` | 0.9975 | GameRuntimeAndResourceProcessing_1010_AND3B6 | medium |
| `FUN_1010_a882` | `FUN_1010_a930` | 1.0000 | GameRuntimeAndResourceProcessing_1010_AND930 | low |
| `FUN_1010_a8a8` | `FUN_1010_a956` | 1.0000 | GameRuntimeAndResourceProcessing_1010_AND956 | low |
| `FUN_1010_a8ce` | `FUN_1010_a97c` | 1.0000 | GameRuntimeAndResourceProcessing_1010_AND97C | medium |
| `FUN_1010_a932` | `FUN_1010_a9e0` | 1.0000 | GameRuntimeAndResourceProcessing_1010_AND9E0 | medium |
| `FUN_1010_a9e2` | `FUN_1010_aa90` | 1.0000 | GameRuntimeAndResourceProcessing_1010_AA90 | medium |
| `FUN_1010_aa38` | `FUN_1010_aae6` | 1.0000 | GameRuntimeAndResourceProcessing_1010_AAE6 | medium |
| `FUN_1010_aa90` | `FUN_1010_ab3e` | 1.0000 | GameRuntimeAndResourceProcessing_1010_AB3E | medium |
| `FUN_1010_aab8` | `FUN_1010_ab66` | 1.0000 | GameRuntimeAndResourceProcessing_1010_AB66 | medium |
| `FUN_1010_ab4e` | `FUN_1010_abfc` | 1.0000 | GameRuntimeAndResourceProcessing_1010_ABFC | medium |
| `FUN_1010_ac0a` | `FUN_1010_acb8` | 1.0000 | GameRuntimeAndResourceProcessing_1010_ACB8 | medium |
| `FUN_1010_ac1c` | `FUN_1010_acca` | 1.0000 | GameRuntimeAndResourceProcessing_1010_ACCA | medium |
| `FUN_1010_ac2e` | `FUN_1010_acdc` | 1.0000 | GameRuntimeAndResourceProcessing_1010_ACDC | medium |
| `FUN_1010_ac40` | `FUN_1010_acee` | 1.0000 | GameRuntimeAndResourceProcessing_1010_ACEE | medium |
| `FUN_1010_ac52` | `FUN_1010_ad00` | 0.9951 | GameRuntimeAndResourceProcessing_1010_AD00 | medium |
| `FUN_1010_acf0` | `FUN_1010_ad9e` | 1.0000 | GameRuntimeAndResourceProcessing_1010_AD9E | medium |
| `FUN_1010_ada8` | `FUN_1010_ae56` | 1.0000 | GameRuntimeAndResourceProcessing_1010_AE56 | medium |
| `FUN_1010_af62` | `FUN_1010_b010` | 1.0000 | GameRuntimeAndResourceProcessing_1010_B010 | medium |
| `FUN_1010_af7e` | `FUN_1010_b02c` | 1.0000 | GameRuntimeAndResourceProcessing_1010_B02C | medium |
| `FUN_1010_b07a` | `FUN_1010_b128` | 1.0000 | GameRuntimeAndResourceProcessing_1010_B128 | medium |
| `FUN_1010_b0f6` | `FUN_1010_b1a4` | 0.9992 | GameRuntimeAndResourceProcessing_1010_B1AND4 | medium |
| `FUN_1010_b4e6` | `FUN_1010_b594` | 1.0000 | GameRuntimeAndResourceProcessing_1010_B594 | medium |
| `FUN_1010_b51a` | `FUN_1010_b5c8` | 1.0000 | GameRuntimeAndResourceProcessing_1010_B5C8 | medium |
| `FUN_1010_b536` | `FUN_1010_b5e4` | 1.0000 | GameRuntimeAndResourceProcessing_1010_B5E4 | medium |
| `FUN_1010_b5f2` | `FUN_1010_b6a0` | 1.0000 | GameRuntimeAndResourceProcessing_1010_B6AND0 | medium |
| `FUN_1010_b6b4` | `FUN_1010_b762` | 1.0000 | GameRuntimeAndResourceProcessing_1010_B762 | medium |
| `FUN_1010_b730` | `FUN_1010_b7de` | 1.0000 | GameRuntimeAndResourceProcessing_1010_B7DE | low |
| `FUN_1010_b74e` | `FUN_1010_b7fc` | 1.0000 | GameRuntimeAndResourceProcessing_1010_B7FC | medium |
| `FUN_1010_b7b4` | `FUN_1010_b862` | 1.0000 | GameRuntimeAndResourceProcessing_1010_B862 | medium |
| `FUN_1010_b8a0` | `FUN_1010_b94e` | 1.0000 | GameRuntimeAndResourceProcessing_1010_B94E | medium |
| `FUN_1010_b904` | `FUN_1010_b9b2` | 1.0000 | GameRuntimeAndResourceProcessing_1010_B9B2 | medium |
| `FUN_1010_b968` | `FUN_1010_ba16` | 1.0000 | GameRuntimeAndResourceProcessing_1010_BA16 | medium |
| `FUN_1010_b9a6` | `FUN_1010_ba54` | 1.0000 | GameRuntimeAndResourceProcessing_1010_BA54 | medium |
| `FUN_1010_b9c6` | `FUN_1010_ba74` | 1.0000 | GameRuntimeAndResourceProcessing_1010_BA74 | medium |
| `FUN_1010_ba78` | `FUN_1010_bb26` | 1.0000 | GameRuntimeAndResourceProcessing_1010_BB26 | medium |
| `FUN_1010_bb1c` | `FUN_1010_bbca` | 1.0000 | GameRuntimeAndResourceProcessing_1010_BBCA | medium |
| `FUN_1010_bbbc` | `FUN_1010_bc6a` | 1.0000 | GameRuntimeAndResourceProcessing_1010_BC6AND | medium |
| `FUN_1010_bbe2` | `FUN_1010_bc90` | 1.0000 | GameRuntimeAndResourceProcessing_1010_BC90 | medium |
| `FUN_1010_bc08` | `FUN_1010_bcb6` | 1.0000 | GameRuntimeAndResourceProcessing_1010_BCB6 | low |
| `FUN_1010_bc3c` | `FUN_1010_bcea` | 1.0000 | GameRuntimeAndResourceProcessing_1010_BCEA | medium |
| `FUN_1010_bc7c` | `FUN_1010_bd2a` | 1.0000 | GameRuntimeAndResourceProcessing_1010_BD2AND | medium |
| `FUN_1010_bd2a` | `FUN_1010_bdd8` | 1.0000 | GameRuntimeAndResourceProcessing_1010_BDD8 | medium |
| `FUN_1010_bda8` | `FUN_1010_be56` | 1.0000 | GameRuntimeAndResourceProcessing_1010_BE56 | medium |
| `FUN_1010_bdb4` | `FUN_1010_be62` | 1.0000 | GameRuntimeAndResourceProcessing_1010_BE62 | medium |
| `FUN_1010_be46` | `FUN_1010_bef4` | 1.0000 | GameRuntimeAndResourceProcessing_1010_BEF4 | medium |
| `FUN_1010_be72` | `FUN_1010_bf20` | 1.0000 | GameRuntimeAndResourceProcessing_1010_BF20 | medium |
| `FUN_1010_bec2` | `FUN_1010_bf70` | 1.0000 | GameRuntimeAndResourceProcessing_1010_BF70 | medium |
| `FUN_1010_bedc` | `FUN_1010_bf8a` | 1.0000 | GameRuntimeAndResourceProcessing_1010_BF8AND | medium |
| `FUN_1010_bef6` | `FUN_1010_bfa4` | 1.0000 | GameRuntimeAndResourceProcessing_1010_BFA4 | medium |
| `FUN_1010_bf10` | `FUN_1010_bfbe` | 1.0000 | GameRuntimeAndResourceProcessing_1010_BFBE | medium |
| `FUN_1010_bf2a` | `FUN_1010_bfd8` | 1.0000 | GameRuntimeAndResourceProcessing_1010_BFD8 | medium |
| `FUN_1010_bff4` | `FUN_1010_c0a2` | 1.0000 | GameRuntimeAndResourceProcessing_1010_C0AND2 | medium |
| `FUN_1010_c078` | `FUN_1010_c126` | 1.0000 | GameRuntimeAndResourceProcessing_1010_C126 | medium |
| `FUN_1010_c20a` | `FUN_1010_c2b8` | 1.0000 | GameRuntimeAndResourceProcessing_1010_C2B8 | medium |
| `FUN_1010_c2a8` | `FUN_1010_c356` | 1.0000 | GameRuntimeAndResourceProcessing_1010_C356 | low |
| `FUN_1010_c2ce` | `FUN_1010_c37c` | 1.0000 | GameRuntimeAndResourceProcessing_1010_C37C | medium |
| `FUN_1010_c2de` | `FUN_1010_c38c` | 1.0000 | GameRuntimeAndResourceProcessing_1010_C38C | medium |
| `FUN_1010_c44c` | `FUN_1010_c4fa` | 1.0000 | GameRuntimeAndResourceProcessing_1010_C4FA | medium |
| `FUN_1010_c4b4` | `FUN_1010_c562` | 1.0000 | GameRuntimeAndResourceProcessing_1010_C562 | medium |
| `FUN_1010_c508` | `FUN_1010_c5b6` | 1.0000 | GameRuntimeAndResourceProcessing_1010_C5B6 | medium |
| `FUN_1010_c534` | `FUN_1010_c5e2` | 1.0000 | GameRuntimeAndResourceProcessing_1010_C5E2 | medium |
| `FUN_1010_c590` | `FUN_1010_c63e` | 1.0000 | GameRuntimeAndResourceProcessing_1010_C63E | medium |
| `FUN_1010_c5e8` | `FUN_1010_c696` | 1.0000 | GameRuntimeAndResourceProcessing_1010_C696 | medium |
| `FUN_1010_c6c4` | `FUN_1010_c772` | 0.9957 | GameRuntimeAndResourceProcessing_1010_C772 | medium |
| `FUN_1010_c7ba` | `FUN_1010_c868` | 1.0000 | GameRuntimeAndResourceProcessing_1010_C868 | low |
| `FUN_1010_c7bc` | `FUN_1010_c86a` | 1.0000 | GameRuntimeAndResourceProcessing_1010_C86AND | low |
| `FUN_1010_c80a` | `FUN_1010_c8b8` | 1.0000 | GameRuntimeAndResourceProcessing_1010_C8B8 | low |
| `FUN_1010_c858` | `FUN_1010_c906` | 0.9930 | GameRuntimeAndResourceProcessing_1010_C906 | medium |
| `FUN_1010_c8f8` | `FUN_1010_c9a6` | 1.0000 | GameRuntimeAndResourceProcessing_1010_C9AND6 | medium |
| `FUN_1010_ca78` | `FUN_1010_cb26` | 1.0000 | GameRuntimeAndResourceProcessing_1010_CB26 | medium |
| `FUN_1010_cb26` | `FUN_1010_cbd4` | 1.0000 | GameRuntimeAndResourceProcessing_1010_CBD4 | medium |
| `FUN_1010_cbce` | `FUN_1010_cc7c` | 1.0000 | GameRuntimeAndResourceProcessing_1010_CC7C | medium |
| `FUN_1010_ce42` | `FUN_1010_cef0` | 1.0000 | GameRuntimeAndResourceProcessing_1010_CEF0 | low |
| `FUN_1010_ce9c` | `FUN_1010_cf4a` | 1.0000 | GameRuntimeAndResourceProcessing_1010_CF4AND | low |
| `FUN_1010_ceb2` | `FUN_1010_cf60` | 1.0000 | GameRuntimeAndResourceProcessing_1010_CF60 | medium |
| `FUN_1010_d0f4` | `FUN_1010_d1a2` | 0.9993 | GameRuntimeAndResourceProcessing_1010_D1AND2 | medium |
| `FUN_1010_d31c` | `FUN_1010_d3ca` | 0.9979 | GameRuntimeAndResourceProcessing_1010_D3CA | medium |
| `FUN_1010_d3a6` | `FUN_1010_d454` | 1.0000 | GameRuntimeAndResourceProcessing_1010_D454 | medium |
| `FUN_1010_d45c` | `FUN_1010_d50a` | 1.0000 | GameRuntimeAndResourceProcessing_1010_D50AND | low |
| `FUN_1010_d5be` | `FUN_1010_d66c` | 1.0000 | GameRuntimeAndResourceProcessing_1010_D66C | medium |
| `FUN_1010_d618` | `FUN_1010_d6c6` | 1.0000 | TimerInput_1010_D6C6 | high |
| `FUN_1010_d634` | `FUN_1010_d6e2` | 1.0000 | GameRuntimeAndResourceProcessing_1010_D6E2 | medium |
| `FUN_1010_d65c` | `FUN_1010_d70a` | 1.0000 | GameRuntimeAndResourceProcessing_1010_D70AND | low |
| `FUN_1010_d69c` | `FUN_1010_d74a` | 1.0000 | GameRuntimeAndResourceProcessing_1010_D74AND | low |
| `FUN_1010_d6de` | `FUN_1010_d78c` | 1.0000 | GameRuntimeAndResourceProcessing_1010_D78C | medium |
| `FUN_1010_d712` | `FUN_1010_d7c0` | 1.0000 | GameRuntimeAndResourceProcessing_1010_D7C0 | medium |
| `FUN_1010_d722` | `FUN_1010_d7d0` | 1.0000 | GameRuntimeAndResourceProcessing_1010_D7D0 | medium |
| `FUN_1010_d84e` | `FUN_1010_d8fc` | 1.0000 | GameRuntimeAndResourceProcessing_1010_D8FC | medium |
| `FUN_1010_d8c6` | `FUN_1010_d974` | 1.0000 | GameRuntimeAndResourceProcessing_1010_D974 | medium |
| `FUN_1010_d918` | `FUN_1010_d9c6` | 1.0000 | GameRuntimeAndResourceProcessing_1010_D9C6 | medium |
| `FUN_1010_d9d8` | `FUN_1010_da86` | 1.0000 | GameRuntimeAndResourceProcessing_1010_DA86 | medium |
| `FUN_1010_d9f2` | `FUN_1010_daa0` | 1.0000 | GameRuntimeAndResourceProcessing_1010_DAA0 | medium |
| `FUN_1010_dc34` | `FUN_1010_dce2` | 1.0000 | MultimediaAudio_1010_DCE2 | high |
| `FUN_1010_dc6a` | `FUN_1010_dd18` | 1.0000 | MultimediaAudio_1010_DD18 | high |
| `FUN_1010_dc9c` | `FUN_1010_dd4a` | 1.0000 | MultimediaAudio_1010_DD4AND | high |
| `FUN_1010_dcd2` | `FUN_1010_dd80` | 1.0000 | MultimediaAudio_1010_DD80 | high |
| `FUN_1010_dcec` | `FUN_1010_dd9a` | 1.0000 | MultimediaAudio_1010_DD9AND | high |
| `FUN_1010_dd04` | `FUN_1010_ddb2` | 0.9871 | GameRuntimeAndResourceProcessing_1010_DDB2 | medium |
| `FUN_1010_dd4e` | `FUN_1010_ddfc` | 0.9869 | GameRuntimeAndResourceProcessing_1010_DDFC | medium |
| `FUN_1010_ddd4` | `FUN_1010_de82` | 0.9805 | MultimediaAudio_1010_DE82 | medium |
| `FUN_1010_df4a` | `FUN_1010_dff8` | 1.0000 | MultimediaAudio_1010_DFF8 | high |
| `FUN_1010_e016` | `FUN_1010_e0c4` | 0.9865 | MultimediaAudio_1010_E0C4 | medium |
| `FUN_1010_e24c` | `FUN_1010_e2fa` | 1.0000 | GameRuntimeAndResourceProcessing_1010_E2FA | medium |
| `FUN_1010_e302` | `FUN_1010_e3b0` | 0.9968 | MultimediaAudio_1010_E3B0 | high |
| `FUN_1010_e468` | `FUN_1010_e516` | 1.0000 | GameRuntimeAndResourceProcessing_1010_E516 | medium |
| `FUN_1010_e52a` | `FUN_1010_e5d8` | 1.0000 | GameRuntimeAndResourceProcessing_1010_E5D8 | medium |
| `FUN_1010_e6ea` | `FUN_1010_e798` | 1.0000 | GameRuntimeAndResourceProcessing_1010_E798 | medium |
| `FUN_1010_eb28` | `FUN_1010_ebd6` | 1.0000 | GameRuntimeAndResourceProcessing_1010_EBD6 | medium |
| `FUN_1010_ebfe` | `FUN_1010_ecac` | 1.0000 | GameRuntimeAndResourceProcessing_1010_ECAC | medium |
| `FUN_1010_ec4a` | `FUN_1010_ecf8` | 1.0000 | GameRuntimeAndResourceProcessing_1010_ECF8 | medium |
| `FUN_1010_ec96` | `FUN_1010_ed44` | 1.0000 | GameRuntimeAndResourceProcessing_1010_ED44 | medium |
| `FUN_1010_ece2` | `FUN_1010_ed90` | 1.0000 | GameRuntimeAndResourceProcessing_1010_ED90 | medium |
| `FUN_1010_ed78` | `FUN_1010_ee26` | 1.0000 | GameRuntimeAndResourceProcessing_1010_EE26 | medium |
| `FUN_1010_eede` | `FUN_1010_ef8c` | 1.0000 | GameRuntimeAndResourceProcessing_1010_EF8C | low |
| `FUN_1010_eeec` | `FUN_1010_ef9a` | 1.0000 | GameRuntimeAndResourceProcessing_1010_EF9AND | low |
| `FUN_1010_ef0e` | `FUN_1018_0000` | 1.0000 | MeasureBitmapTextWidth | medium |
| `FUN_1010_ef56` | `FUN_1018_0048` | 1.0000 | ComputeCenteredTextX320 | medium |
| `FUN_1018_0000` | `FUN_1018_0068` | 1.0000 | HighLevelNite3WApplicationGameLogic_1018_0068 | medium |
| `FUN_1018_00ca` | `FUN_1018_0132` | 1.0000 | HighLevelNite3WApplicationGameLogic_1018_0132 | medium |
| `FUN_1018_0122` | `FUN_1018_018a` | 0.9944 | HighLevelNite3WApplicationGameLogic_1018_018AND | medium |
| `FUN_1018_0204` | `FUN_1018_026c` | 1.0000 | HighLevelNite3WApplicationGameLogic_1018_026C | medium |
| `FUN_1018_028e` | `FUN_1018_02f6` | 1.0000 | HighLevelNite3WApplicationGameLogic_1018_02F6 | medium |
| `FUN_1018_02c2` | `FUN_1018_032a` | 1.0000 | HighLevelNite3WApplicationGameLogic_1018_032AND | medium |
| `FUN_1018_030c` | `FUN_1018_0374` | 1.0000 | HighLevelNite3WApplicationGameLogic_1018_0374 | medium |
| `FUN_1018_037e` | `FUN_1018_03e6` | 1.0000 | HighLevelNite3WApplicationGameLogic_1018_03E6 | medium |
| `FUN_1018_03c0` | `FUN_1018_0428` | 1.0000 | HighLevelNite3WApplicationGameLogic_1018_0428 | medium |
| `FUN_1018_0424` | `FUN_1018_048c` | 1.0000 | HighLevelNite3WApplicationGameLogic_1018_048C | medium |
| `FUN_1018_049e` | `FUN_1018_0506` | 1.0000 | HighLevelNite3WApplicationGameLogic_1018_0506 | medium |
| `FUN_1018_04c0` | `FUN_1018_0528` | 1.0000 | HighLevelNite3WApplicationGameLogic_1018_0528 | medium |
| `FUN_1018_04e4` | `FUN_1018_054c` | 1.0000 | HighLevelNite3WApplicationGameLogic_1018_054C | medium |
| `FUN_1018_067e` | `FUN_1018_06e6` | 1.0000 | HighLevelNite3WApplicationGameLogic_1018_06E6 | medium |
| `FUN_1018_073a` | `FUN_1018_07a2` | 0.9677 | HighLevelNite3WApplicationGameLogic_1018_07AND2 | medium |
| `FUN_1018_07b0` | `FUN_1018_0818` | 1.0000 | HighLevelNite3WApplicationGameLogic_1018_0818 | medium |
| `FUN_1018_07d6` | `FUN_1018_083e` | 1.0000 | HighLevelNite3WApplicationGameLogic_1018_083E | medium |
| `FUN_1018_080e` | `FUN_1018_0876` | 1.0000 | HighLevelNite3WApplicationGameLogic_1018_0876 | medium |
| `FUN_1018_08da` | `FUN_1018_0942` | 1.0000 | HighLevelNite3WApplicationGameLogic_1018_0942 | medium |
| `FUN_1018_098a` | `FUN_1018_09f2` | 1.0000 | HighLevelNite3WApplicationGameLogic_1018_09F2 | medium |
| `FUN_1018_0a48` | `FUN_1018_0ab0` | 0.9770 | HighLevelNite3WApplicationGameLogic_1018_0AB0 | medium |