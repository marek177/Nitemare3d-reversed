# NITE3W — pass 3: five najslabších areas

Date: 2026-09-25

## Result

Third pass continues v same piatich oblastiach: BSF, MIDI selection, level scripts, OBJECT runtime and sound events. Original NITE3W.EXE nor plný assemblerový export was not v this kole available, therefore nepribudli new binary confirmed functions and percentá sa nemenia.

### New report-supported aliasy

| FUN | Proposal name | Area | Reason |
|---|---|---|---|
| FUN_1010_2334 | FindFirstWallIdByClassCode | sound/events | skenuje 256-element wall-class table; 247AND ho uses for class D |
| FUN_1010_8AND20 | UpdatePlayerDoorFamilySelector | sound/events | aktualizuje map-cell pointer player and last valid class-D selector 4C1C |
| FUN_1010_71DC | MoveGuardAndUpdateDoorFamilySelector | sound/events | guard movement path writes class-D selector to GUARD+0E |
| FUN_1010_0EF6 | InitializePersistentScriptFlags | scripts | initializes block 51AND4..51AB |
| FUN_1010_8B06 | DispatchPlayerWeaponFire | sound/object | rozdeľuje fire path, after success calls wake gate and attack-sound helper |
| FUN_1010_5466 | WriteUserSaveRuntimeState | object runtime | serializuje USER.SAV runtime blocks including projectile poolu |
| FUN_1010_574C | RestoreUserSaveRuntimeState | object runtime | restores runtime blocks and derived links/timery |

## Important upresnenia

1. `FUN_1010_2334` is not door lookup specific inštancie. Is sken class tables for first ID danej classes.
2. `4C1C` and `GUARD+0E` nesú last zaznamenaný selector classes D; neidentifikujú jednoznačný map coordinate bod.
3. `FUN_1010_8B06` is not only sound routine. Sound is up to subsequent step after successful fire path and shot-triggered wake mechanizme.
4. `FUN_1010_0EF6` intentionally nedostáva name with specific default value, because stored story-flags report has rozpor between opisom initialization block and row for 51AND5.
5. `FUN_1010_5466`/`574C` have dostatočne stabilnú rolu save/restore runtime state; named individual internal rebasing fields remains open.

## Still without safe name

- Exact MIDI selector for menu/episode/level/DEMO: audio/MCI cluster is lokalizovaný, but address rozhodovacej functions nie.
- BSF: historical aliasy remain only kandidáti, until sa neoveria rodičia šiestich `nite3d.bsf` XREFov and exact byte-by-byte algoritmus.
- FUN_1010_B5E4: is class-dependent consumer same DOOR-family selectoru v guard state 0x0F, but its purpose is not enough on finálne named.

## Register

Pass 2 small 36 items. Pass 3 adds 7 report-supported aliasov, total 43 items v registri. This is not 43 binary completion auditov.