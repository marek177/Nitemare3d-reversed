# Nitemare 3D DOS — hard static closure

Date: 2026-09-29

## Result

- Original working estimate ~50–55 increase unikátnych DOS functions/entrypointov was podhodnotený, because exporty Ghidry at the same time **rozdeľovali some functions on falošné podfunkcie and other real functions pohlcovali**.
- Reference DOS 1.9 hard-census našiel **85 real hide/missing entrypointov** (plus 1 falošný interior target `2000:530E`).
- All **85/85 has corrected/určenú boundary and semantic klasifikáciu at least on úrovni specific subsystému**.
- Semantic confidence: **48 High**, **14 Medium-High**, **23 Medium**, **0 Unknown**.
- Moreover is uzavretých **10 unikátnych rodín explicitných decompiler failures**. During dvoch large incorrect function was identify total **17 falošných function labels/splitov**.
- DOS 1.8 provided v this sade is binary totožný with DOS 1.9, so its addresses are same.

This is uzavretie on úrovni **static boundary + functional/semantic classes**. Does not mean to restore original name from source code; during 23 Medium item remains name working and exact higher purpose possible still spresniť runtime trace.

## 85 hide/missing entrypointov — kategórie

| Skupina | Count |
|---|---:|
| runtime | 21 |
| game | 16 |
| engine | 13 |
| ui | 7 |
| graphics | 6 |
| renderer | 5 |
| resource | 5 |
| callback | 4 |
| input | 4 |
| platform | 2 |
| stub | 1 |
| timing | 1 |

## Cross-version binary mapovanie 85 entrypointov

Map uses najbližší unikátny 16-byte identical anchor v okolí reference entrypointu DOS 1.9. Column v CSV contains also distance anchoru and mieru confidence map.

| Version | High | Medium-High | Medium |
|---|---:|---:|---:|
| DOS 1.0 | 65 | 20 | 0 |
| DOS 1.1 | 73 | 12 | 0 |
| DOS 1.5 | 76 | 9 | 0 |
| DOS 1.7 | 77 | 8 | 0 |
| DOS 2.0 | 82 | 2 | 1 |
| DOS 1.8 | 85 (binary identical with 1.9) | 0 | 0 |

## 10 explicitných decompiler-failure rodín

| DOS 1.9 | Working name | Kategória | Confidence |
|---|---|---|---|
| `1000:0AEA` | `UpdateMovingLinkedBoundaryRecords` | engine/boundary-record | High |
| `1000:4A86` | `ParseCommandLineOptions` | platform/command-line | High |
| `1000:9E32` | `DispatchMappedEffectCode_2F_3D` | game/effect-dispatch | Medium-High |
| `1000:9E98` | `DispatchTypeDependentEffectA` | game/effect-dispatch | Medium-High |
| `1000:86D2` | `DispatchObjectClassAction_9_31` | engine/object-dispatch | Medium-High |
| `2000:0556` | `IsBoundaryCodeCompatibleWithDirection` | engine/boundary-record | High |
| `2000:2BDA` | `RuntimeFormattedOutputCore` | runtime/crt | High |
| `1000:5F74` | `ApplyDamageAndHandleDeathOrPain` | game/combat | High |
| `1000:9CD6` | `DispatchTypeDependentEffectB` | game/effect-dispatch | Medium-High |
| `1000:9540` | `InitializeObjectBehaviorFromMapType` | engine/object-init | High |

## 85 hard-census entrypointov

| DOS 1.9 | Working name | Kategória | Confidence | DOS 1.0 | DOS 1.1 | DOS 1.5 | DOS 1.7 | DOS 2.0 |
|---|---|---|---|---|---|---|---|---|
| `1000:0000` | `Find18ByteRecordByCoordinates` | engine/object-record | High | `1000:0000` | `1000:0000` | `1000:0000` | `1000:0000` | `1000:0000` |
| `1000:052A` | `BuildType28RecordIndex` | engine/object-record | High | `1000:052A` | `1000:052A` | `1000:052A` | `1000:052A` | `1000:052A` |
| `1000:16CE` | `BuildNearestPaletteRemap` | graphics/palette | High | `1000:16C0` | `1000:16C0` | `1000:16CE` | `1000:16CE` | `1000:16CE` |
| `1000:17B4` | `RunPaletteTransitionEffect` | graphics/palette | High | `1000:17A6` | `1000:17A6` | `1000:17B4` | `1000:17B4` | `1000:17B4` |
| `1000:201A` | `MarkAll18ByteSlotsInactive` | engine/object-pool | High | `1000:200C` | `1000:200C` | `1000:201A` | `1000:201A` | `1000:201A` |
| `1000:21F0` | `CullRecordsOutsideViewBounds` | renderer/visibility | Medium-High | `1000:21E2` | `1000:21E2` | `1000:21F0` | `1000:21F0` | `1000:21F0` |
| `1000:2500` | `BuildOrUpdateVisibleRecordLists` | renderer/visibility | Medium | `1000:24F2` | `1000:24F2` | `1000:2500` | `1000:2500` | `1000:2500` |
| `1000:273C` | `Cleanup18ByteSlotPool` | engine/object-pool | High | `1000:271A` | `1000:271A` | `1000:273C` | `1000:273C` | `1000:273C` |
| `1000:32E2` | `InitializeLevelSubsystems` | engine/level-init | Medium | `1000:3242` | `1000:3288` | `1000:32E2` | `1000:32E2` | `1000:32E2` |
| `1000:3474` | `LoadOrPrepareResourceBlockA` | resource/io | Medium | `1000:3376` | `1000:33BC` | `1000:341E` | `1000:3476` | `1000:3474` |
| `1000:358C` | `LoadOrPrepareResourceBlockB` | resource/io | Medium | `1000:3486` | `1000:34CC` | `1000:3526` | `1000:358E` | `1000:358C` |
| `1000:38E6` | `LoadOrPrepareResourceBlockC` | resource/io | Medium | `1000:37D8` | `1000:381E` | `1000:3878` | `1000:38E8` | `1000:38E6` |
| `1000:3F4C` | `LoadPCX320x200FromResource` | graphics/resource | High | `1000:3CD0` | `1000:3D16` | `1000:3D70` | `1000:3DE8` | `1000:3F4C` |
| `1000:47BE` | `ResetInputOrControlFlags` | input/state | Medium-High | `1000:4542` | `1000:4588` | `1000:45E2` | `1000:465A` | `1000:47BE` |
| `1000:6942` | `ResetViewOffsetAndApplyTransform` | renderer/view | Medium | `1000:6664` | `1000:66E8` | `1000:6742` | `1000:67DE` | `1000:6942` |
| `1000:6C2A` | `ConfigureSystemHook` | platform/input-timer | Medium | `1000:694C` | `1000:69D0` | `1000:6A2A` | `1000:6AC6` | `1000:6C34` |
| `1000:6CD8` | `DrainInputQueueOrWaitRelease` | input | Medium | `1000:69FA` | `1000:6A7E` | `1000:6AD8` | `1000:6B74` | `1000:6CE2` |
| `1000:767A` | `CallbackReturn10` | callback/leaf | High | `1000:739C` | `1000:7420` | `1000:747A` | `1000:7516` | `1000:7684` |
| `1000:767E` | `GetGlobal3502` | callback/leaf | High | `1000:73A0` | `1000:7424` | `1000:747E` | `1000:751A` | `1000:7688` |
| `1000:7682` | `CallbackReturn4` | callback/leaf | High | `1000:73A4` | `1000:7428` | `1000:7482` | `1000:751E` | `1000:768C` |
| `1000:7686` | `GetConditionalDelta` | callback/leaf | High | `1000:73A8` | `1000:742C` | `1000:7486` | `1000:7522` | `1000:7690` |
| `1000:7ED4` | `AllocateEightSlotEffectRecord` | engine/effect-pool | Medium | `1000:7A5A` | `1000:7C7A` | `1000:7CD4` | `1000:7D70` | `1000:7EDE` |
| `1000:8314` | `QueryMouseDriverState` | input/mouse | Medium-High | `1000:7E9A` | `1000:80BA` | `1000:8114` | `1000:81B0` | `1000:831E` |
| `1000:832E` | `CallMouseDriverCommand` | input/mouse | Medium-High | `1000:7EB4` | `1000:80D4` | `1000:812E` | `1000:81CA` | `1000:8338` |
| `1000:90E0` | `ResolveMapCollisionOrTraversal` | engine/collision | Medium | `1000:8C6C` | `1000:8E8C` | `1000:8EE0` | `1000:8F7C` | `1000:90EA` |
| `1000:9242` | `TriggerFixedEffect44` | engine/effect | High | `1000:8DCE` | `1000:8FEE` | `1000:9042` | `1000:90DE` | `1000:924C` |
| `1000:9254` | `TriggerFixedEffect43` | engine/effect | High | `1000:8DE0` | `1000:9000` | `1000:9054` | `1000:90F0` | `1000:925E` |
| `1000:9524` | `AdvanceLevelWithEpisodeSpecialCase` | game/level-flow | High | `1000:909E` | `1000:92BE` | `1000:9324` | `1000:93C0` | `1000:952E` |
| `1000:9788` | `ResetOrRefillPlayerStatus` | game/player-state | Medium | `1000:92E8` | `1000:9508` | `1000:9588` | `1000:9624` | `1000:9792` |
| `1000:9BCA` | `DispatchCurrentWeaponOrState` | game/state-dispatch | Medium | `1000:972A` | `1000:994A` | `1000:99CA` | `1000:9A66` | `1000:9BE6` |
| `1000:9BFE` | `PlayState29EffectIfNeeded` | game/effect | High | `1000:975E` | `1000:997E` | `1000:99FE` | `1000:9A9A` | `1000:9C1A` |
| `1000:A096` | `TriggerActions18And2` | game/action | High | `1000:9BF6` | `1000:9E16` | `1000:9E96` | `1000:9F32` | `1000:A0B8` |
| `1000:A214` | `UpdateStatusEffectAudioVisuals` | game/status | Medium-High | `1000:9D74` | `1000:9F94` | `1000:A014` | `1000:A0B0` | `1000:A250` |
| `1000:A2FE` | `FormatResourceEntryByIndex` | ui/resource | Medium | `1000:9E5E` | `1000:A07E` | `1000:A0FE` | `1000:A19A` | `1000:A33A` |
| `1000:A466` | `UpdatePlayerStatusSubsystems` | game/status | Medium-High | `1000:9FC6` | `1000:A1E6` | `1000:A266` | `1000:A302` | `1000:A4A2` |
| `1000:A5E4` | `SelectEpisodeLevelTriggerData` | game/level-data | Medium | `1000:A13C` | `1000:A35C` | `1000:A3E4` | `1000:A480` | `1000:A620` |
| `1000:A722` | `ResolveMapTransitionTextOrTarget` | game/map-transition | Medium | `1000:A27A` | `1000:A49A` | `1000:A522` | `1000:A5BE` | `1000:A75E` |
| `1000:A964` | `ShowBlockedMovementMessage` | ui/game-feedback | Medium-High | `1000:A4BC` | `1000:A6DC` | `1000:A764` | `1000:A800` | `1000:A9A0` |
| `1000:A972` | `BuildPlayerAccessStateSnapshot` | game/access-state | Medium | `1000:A4CA` | `1000:A6EA` | `1000:A772` | `1000:A80E` | `1000:A9AE` |
| `1000:AAE0` | `ResolveAccessDoorKeyInteraction` | game/access-state | Medium | `1000:A638` | `1000:A858` | `1000:A8E0` | `1000:A97C` | `1000:AB1C` |
| `1000:AC5C` | `EnterEndOrCutsceneState` | game/state-transition | Medium | `1000:A7B4` | `1000:A9D4` | `1000:AA5C` | `1000:AAF8` | `1000:AC98` |
| `1000:BE52` | `DelayByTimerTicks` | timing | High | `1000:B9C2` | `1000:BBCA` | `1000:BC52` | `1000:BCEE` | `1000:BE8E` |
| `1000:BF2E` | `ResetFrameSubsystems` | engine/frame-init | Medium | `1000:BA8C` | `1000:BCA6` | `1000:BD2E` | `1000:BDCA` | `1000:BF6A` |
| `1000:C4DE` | `NoOpFarStub` | stub | High | `1000:C012` | `1000:C256` | `1000:C2DE` | `1000:C37A` | `1000:C51A` |
| `1000:C4E0` | `ShutdownOptionalSubsystemA` | platform/shutdown | Medium-High | `1000:C014` | `1000:C258` | `1000:C2E0` | `1000:C37C` | `1000:C51C` |
| `1000:C8BC` | `ComputeGeometryTransform` | renderer/geometry | Medium | `1000:C428` | `1000:C66C` | `1000:C6BC` | `1000:C758` | `1000:C8F8` |
| `1000:CA7C` | `ProjectOrClipObjectGeometry` | renderer/projection | Medium-High | `1000:C5E8` | `1000:C82C` | `1000:C87C` | `1000:C918` | `1000:CAB8` |
| `1000:F06E` | `ResolveMapTransitionOrTeleportCode` | game/map-transition | Medium | `1000:EBCA` | `1000:EDEE` | `1000:EE3E` | `1000:EEDA` | `1000:F0AA` |
| `1000:F994` | `ShowWeaponJammedMessage` | ui/game-feedback | High | `1000:F492` | `1000:F6B6` | `1000:F764` | `1000:F800` | `1000:F9D0` |
| `1000:F9A0` | `HandleInGameMenuCommand` | ui/menu | High | `1000:F49E` | `1000:F6C2` | `1000:F770` | `1000:F80C` | `1000:F9DC` |
| `1000:FD04` | `RuntimeRand` | runtime/crt | High | `1000:F80E` | `1000:FA26` | `1000:FAD4` | `1000:FB70` | `1000:FD40` |
| `1000:FDB2` | `BuildAndSortDirectionalRecordBuckets` | engine/record-index | High | `1000:F8BC` | `1000:FAD4` | `1000:FB82` | `1000:FC1E` | `1000:FDEE` |
| `1000:1B3E` | `DrawClippedPlanarSprite` | graphics/blitter | High | `1000:1B30` | `1000:1B30` | `1000:1B3E` | `1000:1B3E` | `1000:1B3E` |
| `1000:3D70` | `LoadPCX320x200FromFile` | graphics/file | High | `1000:3C5A` | `1000:3CA0` | `1000:3CFA` | `1000:3D72` | `1000:3D70` |
| `1000:4682` | `InitializeOrLoadGraphicDisplayResource` | graphics/resource | Medium | `1000:4406` | `1000:444C` | `1000:44A6` | `1000:451E` | `1000:4682` |
| `1000:9C1A` | `DispatchTypeDependentEffectC` | game/effect-dispatch | Medium-High | `1000:977A` | `1000:999A` | `1000:9A1A` | `1000:9AB6` | `1000:9C36` |
| `1000:A2CA` | `GetEffectOrResourceTableEntryByIndex` | resource/table | High | `1000:9E2A` | `1000:A04A` | `1000:A0CA` | `1000:A166` | `1000:A306` |
| `1000:AB98` | `ShowUnfoundKeysCardsStatus` | ui/debug-status | Medium-High | `1000:A6F0` | `1000:A910` | `1000:A998` | `1000:AA34` | `1000:ABD4` |
| `1000:AC82` | `VerifyFileXorChecksum` | resource/integrity | High | `1000:A7DA` | `1000:A9FA` | `1000:AA82` | `1000:AB1E` | `1000:ACBE` |
| `1000:F458` | `SelectSaveGameSlot` | ui/save-load | High | `1000:EFB4` | `1000:F1D8` | `1000:F228` | `1000:F2C4` | `1000:F494` |
| `1000:F59A` | `SelectLoadGameSlot` | ui/save-load | High | `1000:F0F6` | `1000:F31A` | `1000:F36A` | `1000:F406` | `1000:F5D6` |
| `1000:F67E` | `ConfirmAndSaveGame` | game/save-load | High | `1000:F1DA` | `1000:F3FE` | `1000:F44E` | `1000:F4EA` | `1000:F6BA` |
| `1000:F6EA` | `ConfirmAndLoadGame` | game/save-load | High | `1000:F246` | `1000:F46A` | `1000:F4BA` | `1000:F556` | `1000:F726` |
| `2000:218E` | `RuntimeStartupChecksumGuard` | runtime/crt | High | `2000:1C92` | `2000:1EAA` | `2000:1F5E` | `2000:1FFA` | `2000:21CA` |
| `2000:2340` | `RuntimeBuildArgvEnvironment` | runtime/crt | High | `2000:1E44` | `2000:205C` | `2000:2110` | `2000:21AC` | `2000:237C` |
| `2000:249C` | `RuntimeNoOpFarStub` | runtime/stub | High | `2000:1FA0` | `2000:21B8` | `2000:226C` | `2000:2308` | `2000:24D8` |
| `2000:249E` | `RuntimeFclose` | runtime/crt | High | `2000:1FA2` | `2000:21BA` | `2000:226E` | `2000:230A` | `2000:24DA` |
| `2000:2B68` | `RuntimeCloseAllStreamsWrapper` | runtime/crt | High | `2000:2770` | `2000:2884` | `2000:2938` | `2000:29D4` | `2000:2BA4` |
| `2000:34EC` | `RuntimeFormattedOutputParserCore` | runtime/crt | High | `2000:30F4` | `2000:3208` | `2000:32BC` | `2000:3358` | `2000:3528` |
| `2000:3B16` | `RuntimeOpenOrCreateFile` | runtime/DOS-io | High | `2000:371E` | `2000:3832` | `2000:38E6` | `2000:3982` | `2000:3B52` |
| `2000:3EE2` | `RuntimeStackAvail` | runtime/crt | High | `2000:3AEA` | `2000:3BFE` | `2000:3CB2` | `2000:3D4E` | `2000:3F1E` |
| `2000:420A` | `RuntimeStrcpy` | runtime/crt | High | `2000:3E12` | `2000:3F26` | `2000:3FDA` | `2000:4076` | `2000:4246` |
| `2000:440E` | `RuntimeCountOpenStreamsOrHandles` | runtime/crt | Medium-High | `2000:4016` | `2000:412A` | `2000:41DE` | `2000:427A` | `2000:444A` |
| `2000:4A98` | `RuntimeInitializeOnce` | runtime/crt | Medium-High | `2000:4668` | `2000:47B4` | `2000:4868` | `2000:4904` | `2000:4AD4` |
| `2000:4D94` | `RuntimeStrchr` | runtime/crt | High | `2000:4964` | `2000:4AB0` | `2000:4B64` | `2000:4C00` | `2000:4DD0` |
| `2000:4DBE` | `RuntimeStricmp` | runtime/crt | High | `2000:498E` | `2000:4ADA` | `2000:4B8E` | `2000:4C2A` | `2000:4DFA` |
| `2000:544A` | `RuntimeSpawnExec` | runtime/DOS-io | High | `2000:501A` | `2000:5166` | `2000:521A` | `2000:52B6` | `2000:5486` |
| `2000:581E` | `RuntimeCallbackHookOrErrorFallback` | runtime/crt | Medium | `2000:53EE` | `2000:553A` | `2000:55EE` | `2000:568A` | `2000:585A` |
| `2000:5834` | `RuntimeAccess` | runtime/DOS-io | High | `2000:5404` | `2000:5550` | `2000:5604` | `2000:56A0` | `2000:5870` |
| `2000:58AE` | `RuntimeGetDate` | runtime/DOS-io | High | `2000:547E` | `2000:55CA` | `2000:567E` | `2000:571A` | `2000:58EA` |
| `2000:58C8` | `RuntimeGetTime` | runtime/DOS-io | High | `2000:5498` | `2000:55E4` | `2000:5698` | `2000:5734` | `2000:5904` |
| `2000:00FA` | `FindRecordFromMapCellPointer` | engine/boundary-record | High | `1000:FC04` | `1000:FE1C` | `1000:FECA` | `1000:FF66` | `2000:0136` |
| `2000:0856` | `ScanMapAndBuildBoundaryRecords` | engine/boundary-record | Medium-High | `2000:035A` | `2000:0572` | `2000:0626` | `2000:06C2` | `2000:0892` |
| `2000:2B70` | `RuntimeFlushOrCloseAllStreams` | runtime/crt | High | `2000:2778` | `2000:288C` | `2000:2940` | `2000:29DC` | `2000:2BAC` |
| `2000:50C4` | `RuntimeBuildExecArgEnvironmentBlock` | runtime/DOS-io | High | `2000:4C94` | `2000:4DE0` | `2000:4E94` | `2000:4F30` | `2000:5100` |

## Opravy censusu

- `1000:0AEA` (`0AE0` v older build): jedna related function; Ghidra create 5 falošných internal functions.
- Command-line parser (`1000:4A86` v 1.9): jedna related function; across exportmi was 12 falošných splitov.
- `2000:530E`: is not separate function; is internal address runtime functions začínajúcej on `2000:50C4`.
- Runtime/CRT items are separate from game logic, so nebudú further nafukovať count 'unknown game functions'.