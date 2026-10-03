# Nitemare 3D: first 100 unnamed functions audit

Date: 2026-09-22. Inputs: Ghidra C exports `N3D-DOS-UNFULL-v20.exe.c` and `nite3w110.exe.c`. Functions are sorted numerically by segment:offset, not by export order. Proposed names are analytical labels, not original symbols.

## Method and confidence

Each function was extracted with brace-balanced boundaries, then checked for signature, body size, callees, constants, table strides, global accesses, port values, map dimensions and known Win16/DOS APIs. `high` means the operation is directly visible; `medium` means the subsystem and role are clear but exact semantics/prototype need raw assembly; `low` means only structural classification is currently defensible. Several Ghidra boundaries are demonstrably wrong because an apparent `void(void)` target is called with arguments or a later entry lands inside a preceding logical routine.

## DOS N3D v2.0 — first 100

| # | Address | Proposed name | Function and evidence | Confidence |
|---:|---|---|---|---|
| 1 | `FUN_1000_0052` | `FindSpecialWallAt` | lookup 14-byte special-wall record by X/Y. Evidence: 20 lines; calls `func_0x0000fbac`; constants `0x34f6`, `0xe`, `0x1000`, `0x52`. | high |
| 2 | `FUN_1000_00a2` | `FindMapObjectAt` | iterator/lookup for map objects on one tile; Ghidra boundary is wrong. Evidence: 5 lines; calls none visible; constants none. | low |
| 3 | `FUN_1000_00a4` | `FindObjectRefAt` | lookup 6-byte object reference by runtime-object X/Y. Evidence: 21 lines; calls `func_0x0000fbac`; constants `0x36b6`, `0x1c`, `0x12`, `0x14`, `0x1000`. | high |
| 4 | `FUN_1000_01e0` | `IsWallStateIdleOrTerminal` | tests wall state 0 or 4. Evidence: 11 lines; calls none visible; constants none. | high |
| 5 | `FUN_1000_01fc` | `IsWallStateOne` | tests wall state 1. Evidence: 8 lines; calls none visible; constants none. | high |
| 6 | `FUN_1000_020c` | `AcknowledgeSoundHandle` | probable audio-handle thunk; current empty body is unreliable. Evidence: 5 lines; calls none visible; constants none. | low |
| 7 | `FUN_1000_0212` | `BuildPairedWallRuntimeTable` | scans 64x64 map and builds max 64 paired-wall records. Evidence: 110 lines; calls `func_0x0000fbac`; constants `0x2556`, `0x10`, `0x0`, `0x373e`, `0x2558`. | high |
| 8 | `FUN_1000_03fe` | `BuildFourWaySpecialWallTable` | builds max 32 four-direction class-3 wall records. Evidence: 62 lines; calls `func_0x0000fbac`, `FUN_1000_00a2`; constants `0x1000`, `0x2556`, `0x2`, `0x373e`, `0x2558`. | high |
| 9 | `FUN_1000_04be` | `FinishExplodingWallAnimation` | completion path called when runtime class 0x2D reaches final frame. Evidence: 66 lines; calls `FUN_1000_00a2`, `func_0x0000fbac`; constants `0xe`, `0x10`, `0x3f`, `0x2558`, `0xc`. | low |
| 10 | `FUN_1000_0598` | `SetAndPropagatePairedWallState` | changes paired-wall state, collision flags and SFX 0x25/0x26. Evidence: 81 lines; calls `func_0x0000c686`, `switchD_1000:85d0::caseD_7`; constants `0x430e`, `0x10`, `0x1000`, `0x26`, `0x25`. | high |
| 11 | `FUN_1000_0704` | `HandlePlayerUse` | central USE dispatcher for doors, keys/cards, pickups and special wall classes. Evidence: 175 lines; calls `switchD_1000:85d0::caseD_7`, `func_0x0000a33a`, `FUN_1000_0598`, `func_0x00001262`; constants `0x4158`, `0x822`, `0x417c`, `0x417e`, `0xd30e`. | high |
| 12 | `FUN_1000_0a40` | `TickPairedWallAutoClose` | counts down open paired walls and closes unblocked ones. Evidence: 44 lines; calls `func_0x0000c686`; constants `0x1000`, `0x3076`, `0x3b`, `0x3c`, `0x417c`. | high |
| 13 | `FUN_1000_0c5f` | `TickMovingAndSpecialWalls` | moves paired walls by 2 units and completes four-way special walls. Evidence: 188 lines; calls `func_0x0000980c`; constants `0x1000`, `0x0`, `0x10`, `0x20`, `0xc`. | high |
| 14 | `FUN_1000_0df8` | `ActivateObjectOnTile` | activates an object reference using player direction/position. Evidence: 16 lines; calls `FUN_1000_00a4`, `func_0x0000925e`; constants `0xd00c`, `0x4158`, `0xca`, `0xd2`. | high |
| 15 | `FUN_1000_0e50` | `TickMovingMapObjects` | moves active 28-byte map objects and updates occupied tiles. Evidence: 52 lines; calls `func_0x0000affe`; constants `0x36b6`, `0x1000`, `0x1c`, `0x21fd`, `0x16`. | high |
| 16 | `FUN_1000_0f74` | `FindPrimaryWallClassIndex` | finds first primary-wall definition index, with wrap-around. Evidence: 25 lines; calls `func_0x0000fbac`; constants `0x100`, `0xd30e`, `0x1000`, `0xda`. | high |
| 17 | `FUN_1000_0fbe` | `FindSecondaryWallClassIndex` | finds secondary-wall definition index. Evidence: 18 lines; calls `func_0x0000fbac`; constants `0x100`, `0xd40e`, `0x1000`, `0xf2`. | high |
| 18 | `FUN_1000_0ff4` | `GuardClassToRuntimeType` | maps a guard class through 28-byte guard definition records. Evidence: 22 lines; calls `func_0x0000fbac`; constants `0x6270`, `0xc`, `0x1c`, `0x1000`, `0x109`. | high |
| 19 | `FUN_1000_103e` | `FindHighestPrimaryWallIndexInMap` | scans primary map plane for highest matching definition index. Evidence: 27 lines; calls none visible; constants `0x373e`, `0x40`, `0xd30e`, `0x80`, `0x37be`. | high |
| 20 | `FUN_1000_1092` | `FindHighestSecondaryWallIndexInMap` | scans secondary map plane for highest matching index. Evidence: 27 lines; calls none visible; constants `0x373f`, `0x40`, `0xd40e`, `0x80`, `0x37bf`. | high |
| 21 | `FUN_1000_10e6` | `DecodeDoorVariantIndex` | caches base class D index and returns door graphic variant. Evidence: 16 lines; calls `FUN_1000_0f74`; constants `0x12a`, `0x626a`, `0x44`, `0x2650`, `0xd30e`. | high |
| 22 | `FUN_1000_1126` | `BuildPrimaryWallPropertyFlags` | builds 256-entry bitmask table from primary wall classes. Evidence: 52 lines; calls none visible; constants `0x2cf2`, `0x30`, `0xfb`, `0x2e`, `0x2f`. | high |
| 23 | `FUN_1000_1187` | `BuildPrimaryWallFlagsTail` | compiler-split continuation of primary wall flag builder. Evidence: 60 lines; calls none visible; constants `0x41`, `0xfd`, `0x47`, `0x48`, `0xbf`. | medium |
| 24 | `FUN_1000_11c0` | `BuildSecondaryWallPropertyFlags` | builds secondary-wall class bitmasks. Evidence: 43 lines; calls none visible; constants `0x2bf2`, `0x3d`, `0xfe`, `0x2d`, `0xfd`. | high |
| 25 | `FUN_1000_11d2` | `BuildSecondaryWallFlagsPart2` | compiler-split continuation of secondary flag builder. Evidence: 51 lines; calls none visible; constants `0x3d`, `0x2d`, `0xfd`, `0x2f`, `0xfb`. | medium |
| 26 | `FUN_1000_1236` | `BuildSecondaryWallFlagsTail` | final compiler-split portion of secondary flag builder. Evidence: 49 lines; calls none visible; constants `0x40`, `0x2ef4`, `0xff`, `0x2bf1`, `0x3d`. | medium |
| 27 | `FUN_1000_1262` | `ResolveEpisodeOrLevelResource` | maps values 9/10/12 to episode/resource selection. Evidence: 25 lines; calls `func_0x0000924c`, `func_0x000017b4`, `func_0x0000eda2`; constants `0x626c`, `0xd`, `0x1000`, `0x83d`, `0xc`. | medium |
| 28 | `FUN_1000_129a` | `NoOpCallback129A` | empty callback or bad function boundary. Evidence: 5 lines; calls none visible; constants none. | low |
| 29 | `FUN_1000_12c4` | `ChooseFreeAdjacentTile` | tests four neighboring map tiles and returns direction 0..3/-1. Evidence: 44 lines; calls none visible; constants `0x40`, `0x373e`, `0x417c`, `0x417e`, `0x21fd`. | high |
| 30 | `FUN_1000_13f4` | `ResolveTeleportDestination` | dispatches warp classes, locates target tile and facing direction. Evidence: 90 lines; calls `func_0x0000ee64`, `func_0x0000f040`, `func_0x0000ef06`, `func_0x0000f0aa`; constants `0xc`, `0x2d`, `0x15`, `0x18`, `0x19`. | high |
| 31 | `FUN_1000_154b` | `TeleportResultSuccessTail` | compiler-split success return that writes centered coordinate. Evidence: 11 lines; calls none visible; constants `0xe`, `0x20`. | low |
| 32 | `FUN_1000_155a` | `ReturnFalse155A` | false/failure helper or split tail. Evidence: 5 lines; calls none visible; constants none. | low |
| 33 | `FUN_1000_1560` | `BuildReciprocalProjectionTable` | fills table with 0x400000 / distance values. Evidence: 16 lines; calls none visible; constants `0x2656`, `0x400000`, `0x2e52`. | high |
| 34 | `FUN_1000_1590` | `BuildViewAngleTables` | initializes angle/projection lookup tables. Evidence: 32 lines; calls none visible; constants `0x3054`, `0x4546`, `0xf`, `0x10`, `0x2e52`. | medium |
| 35 | `FUN_1000_15ee` | `ReadVideoStatusBits` | reads cached/display status fields. Evidence: 15 lines; calls none visible; constants `0x12e`, `0x12c`, `0xc`, `0x3d4`. | medium |
| 36 | `FUN_1000_1601` | `ReadVgaStatusPort` | small VGA status helper. Evidence: 8 lines; calls none visible; constants `0x3d4`. | medium |
| 37 | `FUN_1000_1608` | `WaitForVerticalRetrace` | polls VGA status and retrace-related state. Evidence: 21 lines; calls none visible; constants `0x12e`, `0x12c`, `0x3da`, `0x3d4`, `0xc`. | medium |
| 38 | `FUN_1000_1638` | `SetVideoModeOrPage` | validates and switches DOS video mode/page. Evidence: 31 lines; calls `FUN_1000_1fc6`, `func_0x0000fbac`, `FUN_1000_1560`; constants `0x10`, `0x3452`, `0x1000`. | medium |
| 39 | `FUN_1000_168a` | `WriteVgaDacColor` | writes RGB components through ports 0x3C8/0x3C9. Evidence: 15 lines; calls none visible; constants `0x3c8`, `0x300`, `0x3c9`. | high |
| 40 | `FUN_1000_16b0` | `WriteVgaPaletteRange` | programs a range of VGA DAC entries. Evidence: 9 lines; calls none visible; constants `0x3c8`, `0x3c9`. | medium |
| 41 | `FUN_1000_16f5` | `BuildShadeOrPaletteTable` | constructs palette/shading conversion table. Evidence: 70 lines; calls none visible; constants `0x16`, `0x1e`, `0x10`, `0x4a64`, `0x14`. | medium |
| 42 | `FUN_1000_1715` | `WaitDisplayStatus` | polls display-status bit. Evidence: 18 lines; calls none visible; constants `0x5ba`, `0x2b`. | medium |
| 43 | `FUN_1000_176a` | `ApplyPaletteTransform` | transforms/fades a palette block. Evidence: 68 lines; calls none visible; constants `0x20`, `0xf`, `0xe`, `0x10`, `0x2df4`. | medium |
| 44 | `FUN_1000_1921` | `FadePaletteIn` | iteratively updates VGA DAC toward target palette. Evidence: 29 lines; calls `FUN_1000_168a`, `FUN_1000_19b6`; constants `0x308`, `0x100`, `0x3f`, `0x3cd1`. | medium |
| 45 | `FUN_1000_1988` | `SetPaletteEntry` | sets one palette entry. Evidence: 17 lines; calls `FUN_1000_168a`; constants `0x3cd1`. | medium |
| 46 | `FUN_1000_19b6` | `ReadVgaInputStatus` | reads VGA input-status register. Evidence: 10 lines; calls none visible; constants `0x3da`. | high |
| 47 | `FUN_1000_19ba` | `WaitVgaRetraceEdge` | waits for VGA retrace transition. Evidence: 10 lines; calls none visible; constants `0x3da`. | high |
| 48 | `FUN_1000_19c6` | `ConfigureVgaRegisters` | writes sequencer/graphics controller registers. Evidence: 47 lines; calls none visible; constants `0x12e`, `0xff`, `0x50`, `0x3c4`, `0x3c5`. | medium |
| 49 | `FUN_1000_1a2e` | `VgaMaskedWrite` | low-level VGA plane/mask write helper. Evidence: 87 lines; calls none visible; constants `0xff00`, `0x4552`, `0x454e`, `0x454c`, `0x4546`. | medium |
| 50 | `FUN_1000_1ae1` | `CopyPlanarBlock` | copies planar video-memory block. Evidence: 57 lines; calls none visible; constants `0x10`, `0x50`, `0x3454`. | medium |
| 51 | `FUN_1000_1b10` | `SelectVgaPlane` | selects VGA plane/map mask. Evidence: 26 lines; calls none visible; constants `0x50`. | medium |
| 52 | `FUN_1000_1b71` | `DrawPlanarSpriteOrWall` | large planar blitter used by renderer. Evidence: 144 lines; calls none visible; constants `0x14`, `0xff`, `0xe`, `0x10`, `0x20`. | medium |
| 53 | `FUN_1000_1d3e` | `BlitMaskedColumn` | masked planar-column helper. Evidence: 78 lines; calls none visible; constants `0x12e`, `0x12c`, `0xff`, `0x50`, `0x3c4`. | medium |
| 54 | `FUN_1000_1dec` | `SetVgaWriteMode` | configures VGA write mode and masks. Evidence: 19 lines; calls none visible; constants `0x12e`, `0x12c`, `0x3c4`, `0x3c5`, `0x11`. | medium |
| 55 | `FUN_1000_1e34` | `CopyScreenRegion` | copies rectangular planar screen region. Evidence: 42 lines; calls none visible; constants `0x12e`, `0x12c`, `0xff`, `0x50`, `0x3c4`. | medium |
| 56 | `FUN_1000_1ea6` | `ClearScreenRegion` | clears/fills planar region. Evidence: 9 lines; calls `FUN_1000_1e34`; constants none. | medium |
| 57 | `FUN_1000_1edc` | `RestoreVgaState` | restores VGA registers after drawing. Evidence: 12 lines; calls `func_0x000028f8`, `FUN_1000_1e34`; constants `0x1000`, `0x10`. | medium |
| 58 | `FUN_1000_1f24` | `SetDisplayStart` | sets VGA display start/page offset. Evidence: 52 lines; calls none visible; constants `0x12e`, `0x12c`, `0xff`, `0x50`, `0x3c4`. | medium |
| 59 | `FUN_1000_1f9a` | `ProgramCrtcRegister` | writes selected CRTC register/value. Evidence: 22 lines; calls none visible; constants `0x3c4`, `0xf02`, `0x12e`, `0x12c`, `0x0`. | medium |
| 60 | `FUN_1000_1fc6` | `ConfigureDisplayPage` | programs CRTC/page state. Evidence: 32 lines; calls `FUN_1000_1f9a`; constants `0x10`, `0x3c4`, `0x3c5`, `0xf7`, `0x3ce`. | medium |
| 61 | `FUN_1000_202a` | `InitRuntimeActorRecord` | initializes fields of a runtime actor/vector record. Evidence: 50 lines; calls none visible; constants `0x10`, `0x4554`, `0xe`. | medium |
| 62 | `FUN_1000_213e` | `AllocateRuntimeActor` | allocates/links actor record with overflow checking. Evidence: 45 lines; calls `FUN_1000_202a`, `func_0x0000980c`, `func_0x0000fbac`; constants `0x4d64`, `0x4d6e`, `0x4548`, `0x4564`, `0x454a`. | medium |
| 63 | `FUN_1000_21a6` | `FreeRuntimeActor` | unlinks/frees an actor record. Evidence: 40 lines; calls `func_0x0000fbac`, `FUN_1000_202a`, `func_0x0000980c`; constants `0x4d64`, `0x31`, `0x454a`, `0x14`. | medium |
| 64 | `FUN_1000_22ca` | `ComputeActorVisibilityOrRange` | fixed-point geometry/range test for runtime actors. Evidence: 75 lines; calls none visible; constants `0x14`, `0x18`, `0x10`, `0xc`, `0x12`. | medium |
| 65 | `FUN_1000_241e` | `AdvanceActorAnimation` | advances frames; dispatches class 0x2D completion. Evidence: 68 lines; calls `FUN_1000_04be`, `func_0x0000fd40`; constants `0x81e`, `0x2f`, `0x30`, `0x2d`, `0x1000`. | high |
| 66 | `FUN_1000_25dc` | `TickActorList` | main update loop over runtime actors/objects. Evidence: 134 lines; calls `func_0x0000cedc`, `FUN_1000_22ca`, `func_0x00001a2e`, `FUN_1000_241e`; constants `0xe`, `0x4164`, `0x12`, `0x80`, `0xc`. | medium |
| 67 | `FUN_1000_26c0` | `RenderOrUpdateActorList` | second actor traversal with visibility and animation handling. Evidence: 141 lines; calls `FUN_1000_22ca`, `func_0x00001a2e`, `FUN_1000_241e`, `func_0x00007a82`; constants `0x1000`, `0x22`, `0x4554`, `0xe`, `0x10`. | medium |
| 68 | `FUN_1000_2772` | `OpenRequiredDataFile` | opens resource and aborts through shared fatal-error path. Evidence: 33 lines; calls `FUN_1000_3a96`, `func_0x00013b52`, `func_0x0000fbac`, `func_0x00013ab6`; constants `0x1000`, `0x17e`, `0x626a`, `0x17c`, `0x11ee`. | medium |
| 69 | `FUN_1000_27fa` | `ReadRequiredDataBlock` | reads exact data block with error checking. Evidence: 25 lines; calls `func_0x00013b52`, `func_0x0000fbac`, `func_0x00013ab6`, `func_0x0000fc3e`; constants `0x1000`, `0x1ac`, `0x11ee`, `0x1ae`, `0x8000`. | medium |
| 70 | `FUN_1000_28f8` | `DecodeResourceByte` | resource/decompression byte decoder. Evidence: 59 lines; calls `func_0x0000fcac`; constants `0x1000`, `0x244`, `0x2a`, `0x15`, `0xd6`. | low |
| 71 | `FUN_1000_28fe` | `DecodeResourceByteVariant` | alternate entry of same decoder; boundary needs correction. Evidence: 67 lines; calls `func_0x0000fcac`; constants `0x1000`, `0x244`, `0x2a`, `0x15`, `0xd6`. | low |
| 72 | `FUN_1000_2a16` | `SeekRequiredDataFile` | checked seek in resource file. Evidence: 31 lines; calls `func_0x00013b52`, `func_0x0000fbac`, `func_0x00013ab6`, `func_0x00013cf4`; constants `0x1000`, `0x245`, `0x8000`, `0x11ee`, `0x24e`. | medium |
| 73 | `FUN_1000_2aa6` | `LoadEpisodeResourceHeader` | opens/validates episode data and initializes offsets. Evidence: 24 lines; calls `FUN_1000_466c`, `func_0x00013b52`, `func_0x0000fbac`, `func_0x00013cf4`; constants `0x626a`, `0x627c`, `0x291`, `0x28c`, `0x628c`. | medium |
| 74 | `FUN_1000_2b3a` | `LoadResourceDirectory` | reads resource directory/table and prepares buffers. Evidence: 33 lines; calls `func_0x00013cf4`, `func_0x0000fbac`, `FUN_1000_4778`, `FUN_1000_3f45`; constants `0x1000`, `0x10`, `0x11ee`, `0x2d7`, `0x628c`. | medium |
| 75 | `FUN_1000_2ba4` | `CloseResourceFile` | checked close/cleanup path. Evidence: 17 lines; calls `func_0x0000fc3e`, `func_0x0000fbac`; constants `0x1000`, `0xfba`, `0x31d`, `0x628c`. | medium |
| 76 | `FUN_1000_2bcc` | `DecodeResourceBlock` | block decompressor/copy routine. Evidence: 81 lines; calls `func_0x00013cf4`, `func_0x0000fbac`, `FUN_1000_4778`, `func_0x00013ab6`; constants `0x3cce`, `0x1000`, `0x10`, `0x11ee`, `0x333`. | medium |
| 77 | `FUN_1000_2c16` | `LoadResourceEntry` | loads one indexed resource with bounds/error checks. Evidence: 50 lines; calls `FUN_1000_3f32`, `func_0x0000fbac`; constants `0x1000`, `0xe`, `0xc01`, `0xc`, `0xc00`. | medium |
| 78 | `FUN_1000_2cf4` | `LoadAndDecodeResourceEntry` | higher-level resource entry loader/decompressor. Evidence: 50 lines; calls `func_0x0000fbac`, `func_0x00013ab6`, `func_0x00013cf4`, `FUN_1000_5baf`; constants `0x3ee`, `0x3e9`, `0x1000`, `0x3f5`, `0x45`. | medium |
| 79 | `FUN_1000_3390` | `ParseNumericText` | parses signed/hex-like numeric text into an integer. Evidence: 71 lines; calls none visible; constants `0x3cdc`, `0xffff`, `0x3466`. | medium |
| 80 | `FUN_1000_34ae` | `ParseConfigValue` | reads and validates a numeric configuration value. Evidence: 42 lines; calls `FUN_1000_3390`, `func_0x00013b52`, `func_0x00013ab6`, `func_0x00013cf4`; constants `0xffff`, `0x8000`, `0x1000`, `0xd5e6`, `0x20`. | medium |
| 81 | `FUN_1000_3a00` | `LoadSavedGameOrLevelState` | large checked file-read path restoring wall/object tables. Evidence: 160 lines; calls `func_0x00013cf4`, `func_0x0000fc3e`, `func_0x0000980c`, `func_0x0000c838`; constants `0x1000`, `0x11ee`, `0xfba`, `0x3076`, `0x21fd`. | medium |
| 82 | `FUN_1000_3a96` | `SaveGameOrLevelState` | large checked file-write path serializing runtime tables. Evidence: 149 lines; calls `func_0x0000fc3e`, `func_0x00013cf4`, `func_0x0000980c`, `func_0x0000c838`; constants `0x1000`, `0xc`, `0xe`, `0xb`, `0xfba`. | medium |
| 83 | `FUN_1000_3dde` | `FatalInvalidState` | small fatal-error wrapper. Evidence: 6 lines; calls `func_0x0000fbac`; constants `0x1000`, `0x663`. | medium |
| 84 | `FUN_1000_3ed6` | `OpenSaveOrConfigFile` | checked file-open wrapper used by state/config paths. Evidence: 23 lines; calls `func_0x00013b52`, `func_0x0000fbac`, `func_0x0000fc3e`, `FUN_1000_3a96`; constants `0x678`, `0x1000`, `0x679`, `0x8000`, `0x11ee`. | medium |
| 85 | `FUN_1000_3f1e` | `CloseSaveOrConfigFile` | checked close wrapper. Evidence: 15 lines; calls `func_0x0000fbac`, `FUN_1000_3a96`; constants `0x1000`, `0x6a7`, `0x69f`. | medium |
| 86 | `FUN_1000_3f32` | `GetConfiguredPath` | returns configured path/drive fields. Evidence: 16 lines; calls none visible; constants `0x2c4`, `0x1bdb`. | medium |
| 87 | `FUN_1000_3f45` | `NoOpFileCallback` | empty callback or lost import thunk. Evidence: 5 lines; calls none visible; constants none. | low |
| 88 | `FUN_1000_40dc` | `ReadSaveHeader` | checked save/config header reader. Evidence: 22 lines; calls `func_0x00013b52`, `func_0x0000fbac`, `FUN_1000_3ed6`, `func_0x00013ab6`; constants `0x1000`, `0x6f2`, `0x8000`, `0x11ee`, `0x702`. | medium |
| 89 | `FUN_1000_4162` | `WriteSaveHeader` | checked header/block writer. Evidence: 48 lines; calls `func_0x00013b52`, `func_0x0000fbac`, `func_0x00013ab6`, `func_0x00013cf4`; constants `0x1000`, `0x628c`, `0x8000`, `0x11ee`, `0x736`. | medium |
| 90 | `FUN_1000_4206` | `FinalizeSaveWrite` | flushes/closes save data and handles failure. Evidence: 25 lines; calls `func_0x00013cf4`, `func_0x0000fbac`, `func_0x00013ab6`, `FUN_1000_2b3a`; constants `0x1000`, `0x11ee`. | medium |
| 91 | `FUN_1000_4246` | `AbortSaveOperation` | delegates to save/load cleanup. Evidence: 6 lines; calls `FUN_1000_3a96`; constants none. | medium |
| 92 | `FUN_1000_4256` | `WriteTypedSaveBlock` | writes a typed block through common writer. Evidence: 9 lines; calls `func_0x00000fbe`, `FUN_1000_4162`; constants `0x1000`, `0x3e`, `0xf7`. | medium |
| 93 | `FUN_1000_4272` | `ReadTypedBlock` | checked typed block reader. Evidence: 27 lines; calls `func_0x00013b52`, `func_0x0000fbac`, `FUN_1000_3f45`, `func_0x00013ab6`; constants `0x1000`, `0x8000`, `0x10`, `0x11ee`, `0x794`. | medium |
| 94 | `FUN_1000_4278` | `ReadTypedBlockVariant` | alternate checked reader; overlapping boundary suspected. Evidence: 33 lines; calls `func_0x00013b52`, `func_0x0000fbac`, `FUN_1000_3f45`, `func_0x00013ab6`; constants `0x1000`, `0x8000`, `0x10`, `0x11ee`, `0x794`. | medium |
| 95 | `FUN_1000_430a` | `ClearInputState` | clears 0x140-byte input/control state. Evidence: 21 lines; calls none visible; constants `0x140`. | medium |
| 96 | `FUN_1000_4346` | `PollKeyboardAndControls` | polls keyboard/control events and updates action state. Evidence: 68 lines; calls `func_0x000144ee`, `FUN_1000_25dc`, `FUN_1000_430a`; constants `0x10002`, `0x10001`. | medium |
| 97 | `FUN_1000_4484` | `PollJoystickOrMouse` | updates analog/digital controller state. Evidence: 53 lines; calls `FUN_1000_25dc`, `FUN_1000_430a`; constants `0x10001`, `0xf`, `0x140`. | medium |
| 98 | `FUN_1000_453e` | `TranslateControlInput` | maps raw input into game actions. Evidence: 35 lines; calls `FUN_1000_25dc`, `func_0x000016b0`; constants `0x10002`, `0x100`, `0x10003`, `0x11ee`. | medium |
| 99 | `FUN_1000_45ce` | `DispatchControlMode` | selects keyboard/joystick/mouse control handler. Evidence: 27 lines; calls `FUN_1000_25dc`, `FUN_1000_453e`, `FUN_1000_4484`, `func_0x0000fbac`; constants `0x10006`, `0xb`, `0xc`, `0xd`, `0xf`. | medium |
| 100 | `FUN_1000_462c` | `WaitForInputRelease` | waits for actions to clear and reports errors. Evidence: 26 lines; calls `FUN_1000_25dc`, `func_0x0000fbac`, `FUN_1000_45ce`; constants `0x10010`, `0xe06`. | medium |

## Windows NITE3W 1.10 — first 100

Important result: this address range is mainly Borland/Microsoft-style Win16 support/framework code—exception handling, DOS-file wrappers, dynamic strings, HWND/GDI maps and GUI message routing. It is not the first 100 gameplay functions. This distinction prevents framework helpers from being misidentified as enemy, renderer or map logic.

| # | Address | Proposed name | Function and evidence | Confidence |
|---:|---|---|---|---|
| 1 | `FUN_1000_036a` | `BaseExceptionCtor` | constructs compiler exception base/vtable. Evidence: 9 lines; calls none visible; constants `0x48b8`, `0x16`, `0x48bc`. | medium |
| 2 | `FUN_1000_0388` | `PtVisibleThunk` | GDI PtVisible import wrapper. Evidence: 8 lines; calls none visible; constants none. | high |
| 3 | `FUN_1000_03a0` | `RectVisibleThunk` | GDI RectVisible import wrapper. Evidence: 8 lines; calls none visible; constants none. | high |
| 4 | `FUN_1000_03b8` | `ExtTextOutThunk` | GDI ExtTextOut import wrapper. Evidence: 11 lines; calls none visible; constants none. | high |
| 5 | `FUN_1000_0480` | `GrayStringThunk` | GDI/User GrayString wrapper. Evidence: 18 lines; calls none visible; constants none. | high |
| 6 | `FUN_1000_04c0` | `EscapeThunk` | GDI Escape wrapper. Evidence: 9 lines; calls none visible; constants none. | high |
| 7 | `FUN_1000_068a` | `IsKindOfOrInClassChain` | walks runtime-class/base chain and tests class id. Evidence: 15 lines; calls none visible; constants `0xc`. | high |
| 8 | `FUN_1000_06c0` | `CheckedDynamicCast` | allocates/throws around a runtime class conversion. Evidence: 32 lines; calls `FUN_1000_4422`, `FUN_1008_5fe0`, `FUN_1000_0730`, `FUN_1000_4446`; constants `0x1000`. | medium |
| 9 | `FUN_1000_0730` | `InvokeOptionalDestructor` | calls optional cleanup/destructor callback. Evidence: 13 lines; calls none visible; constants none. | high |
| 10 | `FUN_1000_07a0` | `DosCallWithLongResult` | DOS3CALL wrapper returning error or 32-bit result. Evidence: 20 lines; calls none visible; constants `0x10`, `0xffff`. | high |
| 11 | `FUN_1000_0804` | `DosCallErrorWrapperA` | DOS3CALL wrapper normalized to zero/error. Evidence: 12 lines; calls none visible; constants none. | high |
| 12 | `FUN_1000_0826` | `DosCallErrorWrapperB` | second DOS3CALL normalized wrapper. Evidence: 12 lines; calls none visible; constants none. | high |
| 13 | `FUN_1000_0868` | `FileObjectDefaultCtor` | constructs file wrapper with invalid handle. Evidence: 11 lines; calls none visible; constants `0x48b8`, `0x16`, `0x4934`, `0xffff`. | high |
| 14 | `FUN_1000_0890` | `FileObjectCtor` | constructs file wrapper with supplied handle. Evidence: 11 lines; calls none visible; constants `0x48b8`, `0x16`, `0x4934`. | high |
| 15 | `FUN_1000_08ba` | `FileObjectDtor` | closes owned handle then restores base vtable. Evidence: 12 lines; calls `FUN_1000_0b06`; constants `0x4934`, `0x16`, `0x48bc`. | high |
| 16 | `FUN_1000_08ea` | `CloneFileObject` | allocates and duplicates file wrapper state. Evidence: 21 lines; calls `FUN_1008_5fe0`, `FUN_1000_0890`, `FUN_1008_65a8`; constants `0x1000`, `0xffff`. | medium |
| 17 | `FUN_1000_09ea` | `ReportIoErrorA` | converts runtime I/O error to framework exception. Evidence: 11 lines; calls `FUN_1008_701a`, `FUN_1000_4ac0`; constants none. | medium |
| 18 | `FUN_1000_0a24` | `ReportIoErrorB` | reports I/O error and optionally throws. Evidence: 16 lines; calls `FUN_1008_7028`, `FUN_1000_4ac0`, `FUN_1000_4ae6`; constants `0xffff`, `0xd`. | medium |
| 19 | `FUN_1000_0a72` | `FileSeekOrPosition` | DOS-call wrapper returning 32-bit file position. Evidence: 14 lines; calls `FUN_1000_07a0`, `FUN_1000_4ac0`; constants none. | medium |
| 20 | `FUN_1000_0aa8` | `GetFilePosition` | queries current file position. Evidence: 14 lines; calls `FUN_1000_07a0`, `FUN_1000_4ac0`; constants none. | medium |
| 21 | `FUN_1000_0adc` | `FlushFile` | flushes valid file handle and reports error. Evidence: 13 lines; calls `FUN_1008_6f80`, `FUN_1000_4ac0`; constants none. | high |
| 22 | `FUN_1000_0b06` | `CloseFile` | closes file handle and clears ownership fields. Evidence: 16 lines; calls `FUN_1008_6f5c`, `FUN_1000_4ac0`; constants `0xffff`. | high |
| 23 | `FUN_1000_0b5e` | `LockFileRange` | DOS lock-range wrapper. Evidence: 12 lines; calls `FUN_1000_0826`, `FUN_1000_4ac0`; constants none. | medium |
| 24 | `FUN_1000_0b8e` | `UnlockFileRange` | DOS unlock-range wrapper. Evidence: 12 lines; calls `FUN_1000_0826`, `FUN_1000_4ac0`; constants none. | medium |
| 25 | `FUN_1000_0bbe` | `FlushViaVirtualAndReport` | calls virtual flush then reports error. Evidence: 14 lines; calls `FUN_1008_7028`, `FUN_1000_4ac0`; constants `0x20`. | medium |
| 26 | `FUN_1000_0c54` | `ResolvePathOrTempName` | uses a 260-byte path buffer and DOS error conversion. Evidence: 14 lines; calls `FUN_1000_0804`, `FUN_1000_4ac0`; constants none. | medium |
| 27 | `FUN_1000_0cb0` | `DeleteFileObject` | destructor plus optional memory free. Evidence: 9 lines; calls `FUN_1000_08ba`, `FUN_1008_5fd0`; constants none. | medium |
| 28 | `FUN_1000_0cdc` | `StringInitEmpty` | initializes small dynamic-string structure. Evidence: 8 lines; calls none visible; constants `0x584`. | high |
| 29 | `FUN_1000_0cf2` | `StringFreeBuffer` | frees non-static string buffer. Evidence: 8 lines; calls `FUN_1008_5fd0`; constants `0x584`. | high |
| 30 | `FUN_1000_0d08` | `StringCtorEmpty` | empty string constructor. Evidence: 6 lines; calls `FUN_1000_0cdc`; constants none. | high |
| 31 | `FUN_1000_0d1c` | `StringMoveOrCopyCtor` | constructs from another dynamic string. Evidence: 6 lines; calls `FUN_1000_0da0`; constants none. | medium |
| 32 | `FUN_1000_0d3e` | `StringAllocate` | allocates length+1 and initializes length/capacity. Evidence: 17 lines; calls `FUN_1000_0cdc`, `FUN_1008_5fe0`; constants none. | high |
| 33 | `FUN_1000_0d74` | `StringDestroyAndReset` | frees buffer and resets to empty. Evidence: 7 lines; calls `FUN_1000_0cf2`, `FUN_1000_0cdc`; constants none. | high |
| 34 | `FUN_1000_0d8e` | `StringDestroy` | frees string buffer. Evidence: 6 lines; calls `FUN_1000_0cf2`; constants none. | high |
| 35 | `FUN_1000_0da0` | `StringSubstringCopy` | constructs substring from source buffer. Evidence: 12 lines; calls `FUN_1000_0cdc`, `FUN_1000_0d3e`, `FUN_1008_6c80`; constants none. | high |
| 36 | `FUN_1000_0dde` | `StringFromCStr` | constructs dynamic string from C string. Evidence: 20 lines; calls `FUN_1008_609e`, `FUN_1000_0cdc`, `FUN_1000_0d3e`, `FUN_1008_6c80`; constants none. | high |
| 37 | `FUN_1000_0e26` | `StringAssignBuffer` | resizes and assigns bytes with NUL termination. Evidence: 14 lines; calls `FUN_1000_0d74`, `FUN_1000_0d3e`, `FUN_1008_6c80`; constants none. | high |
| 38 | `FUN_1000_0e6a` | `StringAssignString` | assigns one dynamic string to another. Evidence: 6 lines; calls `FUN_1000_0e26`; constants none. | high |
| 39 | `FUN_1000_0e88` | `StringAssignCStr` | assigns C string. Evidence: 14 lines; calls `FUN_1008_609e`, `FUN_1000_0e26`; constants none. | high |
| 40 | `FUN_1000_0eba` | `StringConcatBuffers` | allocates and concatenates two byte ranges. Evidence: 8 lines; calls `FUN_1000_0d3e`, `FUN_1008_6c80`; constants none. | high |
| 41 | `FUN_1000_0ef8` | `StringConcat` | returns concatenation through temporary string. Evidence: 18 lines; calls `FUN_1000_0d08`, `FUN_1008_609e`, `FUN_1000_0eba`, `FUN_1000_0d1c`; constants none. | high |
| 42 | `FUN_1000_0f4c` | `StringReserve` | grows capacity while preserving contents. Evidence: 17 lines; calls `FUN_1000_0d3e`, `FUN_1008_6c80`, `FUN_1000_0cf2`; constants none. | high |
| 43 | `FUN_1000_0f96` | `StringSetLength` | sets length and NUL terminator. Evidence: 10 lines; calls `FUN_1008_609e`; constants none. | high |
| 44 | `FUN_1000_0fc0` | `StringGetBufferSetLength` | reserves and exposes mutable buffer. Evidence: 8 lines; calls `FUN_1000_0f4c`; constants none. | high |
| 45 | `FUN_1000_0fe2` | `StringFindAny` | finds any character, DBCS-aware when enabled. Evidence: 35 lines; calls `FUN_1008_6a54`, `FUN_1000_3320`; constants `0x1000`. | high |
| 46 | `FUN_1000_105a` | `StringFromFarText` | constructs from far/Win16 text pointer. Evidence: 17 lines; calls `FUN_1000_0d3e`, `FUN_1008_7232`, `FUN_1000_0cdc`; constants `0x1e`. | high |
| 47 | `FUN_1000_10a8` | `AnsiStrChr` | DBCS-aware character search. Evidence: 27 lines; calls none visible; constants `0x10`, `0x0`. | high |
| 48 | `FUN_1000_114a` | `WindowObjectCtor` | constructs GUI/window wrapper and clears handles. Evidence: 11 lines; calls `FUN_1000_34a8`; constants `0x49a4`, `0x16`, `0xb`, `0xc`. | medium |
| 49 | `FUN_1000_1172` | `WindowObjectCtorWithId` | GUI/window wrapper constructor with id/handle. Evidence: 11 lines; calls `FUN_1000_34a8`; constants `0x49a4`, `0x16`, `0xb`, `0xc`. | medium |
| 50 | `FUN_1000_119e` | `CopyTenByteId` | copies a fixed 10-byte identifier. Evidence: 11 lines; calls none visible; constants `0xa`. | low |
| 51 | `FUN_1000_11c2` | `WindowMapLookup` | looks up a window/object association. Evidence: 75 lines; calls `FUN_1000_4422`, `FUN_1000_119e`, `FUN_1000_4564`, `FUN_1000_4446`; constants `0x1000`, `0x3f`, `0x111`, `0x3e`, `0x58`. | low |
| 52 | `FUN_1000_12a2` | `AllocateWindowMapNode` | allocates a 16-byte association node. Evidence: 13 lines; calls none visible; constants `0x10`. | medium |
| 53 | `FUN_1000_12be` | `InitWindowMapNode` | initializes a 0x5C-byte GUI association structure. Evidence: 9 lines; calls none visible; constants `0x5c`. | low |
| 54 | `FUN_1000_12f2` | `GetPermanentWindowMap` | returns/initializes global permanent window map. Evidence: 6 lines; calls `FUN_1000_2a26`; constants `0x4250`. | medium |
| 55 | `FUN_1000_12fc` | `LookupWindowHandle` | looks up HWND in global map. Evidence: 6 lines; calls `FUN_1000_2970`; constants `0x4250`. | medium |
| 56 | `FUN_1000_130e` | `AttachWindowHandle` | attaches HWND to wrapper object. Evidence: 14 lines; calls `FUN_1000_62c8`; constants `0x4250`. | medium |
| 57 | `FUN_1000_132c` | `IsWindowHandleMapped` | tests whether HWND/object is in the handle map. Evidence: 12 lines; calls `FUN_1000_62f4`; constants `0x14`, `0x4250`. | medium |
| 58 | `FUN_1000_1356` | `DetachWindowHandle` | removes handle association. Evidence: 12 lines; calls `FUN_1000_2a14`; constants `0x14`, `0x4250`. | medium |
| 59 | `FUN_1000_137e` | `CreateTempWindowWrapper` | creates temporary wrapper for an HWND. Evidence: 10 lines; calls `FUN_1000_130e`, `FUN_1000_11c2`; constants none. | low |
| 60 | `FUN_1000_1482` | `WindowBaseCtor` | initializes base window object fields. Evidence: 31 lines; calls none visible; constants `0x4a`, `0x1000`, `0x10`. | medium |
| 61 | `FUN_1000_14cc` | `WindowBaseDtor` | destroys/detaches base window object. Evidence: 17 lines; calls none visible; constants `0x4a`, `0x1000`. | medium |
| 62 | `FUN_1000_1500` | `WindowDelete` | destructor plus optional free. Evidence: 73 lines; calls `FUN_1000_1482`, `FUN_1000_14cc`; constants `0x38`, `0x60`, `0x1000`. | medium |
| 63 | `FUN_1000_1606` | `GetWindowRuntimeClass` | returns runtime-class descriptor. Evidence: 18 lines; calls `FUN_1000_1500`; constants `0x14`, `0x1e`, `0x4000`. | low |
| 64 | `FUN_1000_1666` | `WindowDerivedCtor` | constructs derived GUI object and list links. Evidence: 13 lines; calls `FUN_1000_171c`, `FUN_1000_34e4`; constants `0x49a4`, `0x16`, `0x41d6`, `0x41f0`, `0x420a`. | medium |
| 65 | `FUN_1000_171c` | `AttachOrCreateWindow` | attaches or creates wrapper around HWND. Evidence: 19 lines; calls `FUN_1000_62c8`, `FUN_1000_1356`; constants `0x14`, `0x4250`, `0x1000`. | medium |
| 66 | `FUN_1000_187a` | `FindWindowByHandle` | searches window/object handle maps. Evidence: 39 lines; calls `FUN_1000_337a`; constants `0x1000`. | medium |
| 67 | `FUN_1000_18e0` | `RouteWindowMessage` | finds wrapper and routes a Windows message. Evidence: 34 lines; calls `FUN_1000_337a`, `FUN_1000_187a`, `FUN_1000_2010`, `FUN_1000_2496`; constants `0x10`, `0x14`, `0x0`, `0x18`, `0x1000`. | medium |
| 68 | `FUN_1000_1a1a` | `DefaultWindowProcBridge` | bridges message to default/previous procedure. Evidence: 33 lines; calls `FUN_1000_36a4`, `FUN_1000_2090`, `FUN_1000_1f8e`, `FUN_1000_a344`; constants `0x68`, `0x1000`, `0x9c`, `0x1f`, `0x14`. | low |
| 69 | `FUN_1000_1b18` | `FindMessageMapEntry` | searches message-map table by message/code/id. Evidence: 15 lines; calls none visible; constants `0x10`, `0x0`. | medium |
| 70 | `FUN_1000_1b52` | `DispatchMessageMapEntry` | dispatches resolved message-map callback. Evidence: 218 lines; calls `FUN_1000_1b18`, `FUN_1008_02d0`, `FUN_1000_12fc`, `FUN_1008_028c`; constants `0x111`, `0x48`, `0x5c`, `0x1c`, `0x3f`. | low |
| 71 | `FUN_1000_1f04` | `GetMenuOrWindowHandle` | small GUI handle accessor. Evidence: 11 lines; calls `FUN_1008_1214`; constants none. | medium |
| 72 | `FUN_1000_1f2e` | `CreateGuiObject` | allocates and initializes a GUI wrapper. Evidence: 37 lines; calls `FUN_1000_12fc`; constants `0x14`, `0x16`, `0x0`, `0x68`, `0x1000`. | medium |
| 73 | `FUN_1000_1f8e` | `DestroyGuiObject` | releases GUI wrapper/associated handle. Evidence: 20 lines; calls `FUN_1008_1214`, `FUN_1000_12fc`; constants `0x14`. | medium |
| 74 | `FUN_1000_1fc4` | `CloneOrCreateGuiObject` | creates a GUI object from descriptor. Evidence: 26 lines; calls `FUN_1000_1f2e`; constants `0x0`, `0x68`. | medium |
| 75 | `FUN_1000_2010` | `AttachGuiResource` | attaches a GUI resource/handle with validation. Evidence: 38 lines; calls `FUN_1000_12fc`, `FUN_1000_130e`; constants `0x1000`. | medium |
| 76 | `FUN_1000_2090` | `RemoveGuiResource` | detaches GUI resource from map. Evidence: 36 lines; calls `FUN_1000_130e`, `FUN_1000_11c2`; constants `0x1000`, `0x14`. | medium |
| 77 | `FUN_1000_211c` | `FindGuiResource` | looks up GUI resource wrapper. Evidence: 15 lines; calls none visible; constants `0x40`. | medium |
| 78 | `FUN_1000_2152` | `RectNormalizeOrCopy` | copies/normalizes a 4-word rectangle. Evidence: 15 lines; calls none visible; constants `0x40`. | medium |
| 79 | `FUN_1000_2182` | `RectOffset` | offsets rectangle coordinates. Evidence: 16 lines; calls none visible; constants `0x40`. | medium |
| 80 | `FUN_1000_21be` | `RectInflate` | inflates/deflates rectangle. Evidence: 16 lines; calls none visible; constants `0x40`. | medium |
| 81 | `FUN_1000_21fc` | `RectIntersect` | rectangle intersection/helper. Evidence: 23 lines; calls none visible; constants `0x40`. | medium |
| 82 | `FUN_1000_2256` | `RectUnionOrSubtract` | rectangle composition helper. Evidence: 93 lines; calls `FUN_1000_12fc`, `FUN_1000_2390`, `FUN_1000_130e`; constants `0x0`, `0x14`, `0x1e`, `0x10`, `0x3c`. | medium |
| 83 | `FUN_1000_2390` | `CreateDeviceContextWrapper` | constructs DC/GDI wrapper. Evidence: 28 lines; calls none visible; constants `0x0`, `0x14`. | low |
| 84 | `FUN_1000_2496` | `ReleaseGuiHandle` | generic GUI handle release callback. Evidence: 3 lines; calls none visible; constants none. | medium |
| 85 | `FUN_1000_24fa` | `SelectGdiObject` | selects GDI object through wrapper. Evidence: 11 lines; calls `FUN_1000_2496`, `FUN_1000_12be`; constants none. | medium |
| 86 | `FUN_1000_251c` | `RestoreGdiObject` | restores previous selected GDI object. Evidence: 11 lines; calls `FUN_1000_2496`, `FUN_1000_12be`; constants none. | medium |
| 87 | `FUN_1000_253e` | `DeleteGdiObjectWrapper` | releases/deletes GDI wrapper. Evidence: 12 lines; calls `FUN_1000_2496`, `FUN_1000_12be`; constants none. | medium |
| 88 | `FUN_1000_2564` | `CreateCompatibleDcObject` | allocates DC wrapper and reports GDI errors. Evidence: 38 lines; calls `FUN_1000_25f0`, `FUN_1000_4422`, `FUN_1000_4472`, `FUN_1000_a344`; constants `0x1000`, `0x50`, `0x686`, `0xffff`, `0x10`. | medium |
| 89 | `FUN_1000_25f0` | `InitDcState` | initializes DC state structure. Evidence: 8 lines; calls none visible; constants none. | medium |
| 90 | `FUN_1000_260c` | `MapLogicalPoint` | maps/scales logical coordinates. Evidence: 35 lines; calls `FUN_1000_2090`; constants `0xf0`, `0x10`, `0x364`, `0x14`. | medium |
| 91 | `FUN_1000_26e8` | `PrepareTextOrFontMetrics` | builds GDI text/font measurement state. Evidence: 36 lines; calls `FUN_1000_3706`, `FUN_1000_114a`, `FUN_1000_1666`, `FUN_1000_38ca`; constants `0x1000`, `0x14`, `0x87`, `0x2000`, `0xfff0`. | medium |
| 92 | `FUN_1000_27a2` | `ClampCoordinate` | clamps/sign-normalizes coordinate range. Evidence: 15 lines; calls none visible; constants `0x36`, `0x1ffe`, `0x1fff`. | medium |
| 93 | `FUN_1000_2840` | `InitGuiFramework` | initializes Win16 GUI/GDI framework globals. Evidence: 59 lines; calls `FUN_1008_0d88`, `FUN_1008_02c6`, `FUN_1000_3370`, `FUN_1000_12f2`; constants `0x82`, `0x80`, `0x86`, `0x84`, `0x7a`. | medium |
| 94 | `FUN_1000_2970` | `LookupOrCreateGdiWrapper` | maps raw GDI handle to wrapper. Evidence: 41 lines; calls `FUN_1000_62c8`, `FUN_1008_601a`, `FUN_1000_06c0`, `FUN_1000_62f4`; constants `0x10`, `0xe`, `0x20`, `0x22`, `0x24`. | medium |
| 95 | `FUN_1000_2a14` | `RemoveGdiWrapper` | removes GDI handle association. Evidence: 6 lines; calls `FUN_1000_6356`; constants none. | medium |
| 96 | `FUN_1000_2a26` | `DestroyGdiMap` | destroys global GDI handle map. Evidence: 25 lines; calls `FUN_1000_63ae`, `FUN_1000_6196`; constants `0x18`, `0x10`, `0x22`, `0x24`, `0x0`. | medium |
| 97 | `FUN_1000_2a8e` | `GdiObjectDtor` | generic GDI object destructor. Evidence: 24 lines; calls `FUN_1000_5d24`, `FUN_1000_5fe8`; constants `0xffff`, `0x38`, `0x1000`, `0x3c`, `0x50`. | medium |
| 98 | `FUN_1000_2c0a` | `CreatePenOrBrushWrapper` | creates/attaches a GDI pen/brush-like object. Evidence: 17 lines; calls `FUN_1000_1fc4`; constants `0x26`, `0xff`, `0x109`, `0x1000`, `0x1e`. | medium |
| 99 | `FUN_1000_2c50` | `CreateStockGdiWrapper` | wraps a stock GDI object. Evidence: 34 lines; calls `FUN_1000_35c8`, `FUN_1000_12fc`; constants `0x8000`, `0xf000`, `0x14`, `0x1000`, `0x0`. | low |
| 100 | `FUN_1000_2d0c` | `GuiDerivedDtor` | destructs a derived GUI/GDI wrapper. Evidence: 11 lines; calls `FUN_1000_171c`, `FUN_1000_1666`; constants `0x4d38`, `0x16`. | medium |

## Cross-version conclusions

- DOS functions `1000:0052–155A` expose the wall/object/USE/teleport subsystem; `1560–1FC6` is dominated by fixed-point projection and VGA planar rendering; `2772–2CF4` is checked resource-file I/O/decompression.
- DOS `1000:0704` is the central USE dispatcher. It reaches paired doors, key/card checks, special class-3 walls, pickups and object activation.
- DOS `1000:0C5F` is the missing per-tick wall mover: paired wall coordinates change by exactly 2 units until their targets are reached.
- DOS `1000:13F4` plus `1000:12C4` resolves teleport classes and finds a free adjacent destination/facing.
- Windows first-100 addresses are mostly framework scaffolding. Gameplay equivalence should be searched in later NITE3W segments by strings, table strides and behavioral XREFs, not by same ordinal/address.
- The audit identifies multiple split/overlapping boundaries (`00A2`, `04BE`, `1187`, `11D2`, `1236`, `28F8/28FE`). Raw 16-bit assembly must be authoritative before porting these bodies.

## Recommended next pass

1. Repair the seven suspect DOS function boundaries in IDA Free and export exact assembly bytes.
2. Build semantic cross-references from DOS `HandlePlayerUse`, `TickMovingAndSpecialWalls`, `ResolveTeleportDestination` and `AdvanceActorAnimation` into NITE3W.
3. Continue with functions 101–200 in both binaries; for NITE3W this should move beyond generic framework code toward application/game classes.