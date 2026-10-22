# Nitemare 3D — všetky dostupné runtime a statické poznatky, konsolidácia k 22. 10. 2026

**Rozsah:** Od historických DOS/Win16 MZ/NE auditov po V089. Tento dokument je **prepojovací index**, nie tvrdenie, že bol každý pôvodný experiment dnes znovu spustený. Nezverejňuje komerčné EXE/IMG/MAP, raw snapshoty ani používateľove súkromné trace archívy. Súčasný binárny projekt stále hlási **v0.78**; neskoršie V087–V089 označujú výskumné a diagnostické doplnky.

## Aktívne originálne runtime dôkazy (R)

| Oblasť | Už namerané na origináli | Zdroj / presný limit |
|---|---|---|
| DOS 2.0 DEMO seed/RNG | 8/8 v 4 oprávnených reláciách, 18/18 v 3, 35/35 v 2; prvý seed1→0029E2C0, 41 | [V063](V063_REMAX_DEMO_RNG35_DEPTH.md), [V076](V076_REMAX_DEMO_TIMING_CONTEXT.md): RNG rovnosť bez rovnosti scheduler/input |
| Controlled projectile | jeden životný cyklus 0→1→2→0; ďalšie varianty a natural hit otvorené | [V056](V056_REMAX_FRONTIER_CONSOLIDATION.md), [V083 frontier](V083_RUNTIME_PROJECTILE_SAVE_WIN16_FRONTIER.md) |
| DOS2 player/collision | E1M1 krok 11, jeden clipped krok 6, blokovaná Y=3291 v danom scenári | [V081](V081_DOS20_LIVE_E1M1_PLAYER_COLLISION_RUNTIME_SK.md) |
| E1M1 input/rotation | 22 pôvodných ľavých otočení −6 v jednom kontexte; Up+Down a Left+Right konflikt; Alt+arrows strafe | [V083](V083_DOS20_LIVE_E1M1_UP_LEFT_INPUT_SK.md), [V084](V084_DOS20_LIVE_E1M1_OPPOSING_KEYS_SK.md), [V084B](V084B_DOS20_LIVE_E1M1_ALT_STRAFE_SK.md) |
| FIRE/USE/Alt bit masks | 1 716 RAM vzoriek, 24 transition events, 8/8 Ctrl/Alt/Space mask; stale boundary samples not lost ticks | [V085/V086](V085_V086_DOS20_LIVE_E1M1_ACTION_MASKS_SK.md) |
| ↑+→/release, ↑/↓ | 734 originálnych E1M1 vzoriek a 12 fáz (host polling ~12 ms); stopped translation near wall, rotation after release of ↑ | [22.10 runtime](DOS20_E1M1_COMBINED_KEY_RUNTIME_2026-10-22_SK.md) |
| Pickup + Ctrl firing | pickup ammo 0→50; Ctrl tap/continuous 1–8s hold = one ammo decrement in tested route; another press after release rearmed | [22.10 FIRE session](RE_DOS20_FIRE_PICKUP_20261022_SK.md): prior original-run report, not reexecuted in this commit |
| Win16 v1.0,1.3,1.6,1.8,1.10 | WinG 1.0 lab reached E1M1 with each version; Win v1.10 saved/loaded a moved view | [V051](V051_REMAX_WIN16_WING_RUNTIME.md), [V059](V059_REMAX_WIN16_SAVE_LOAD.md): first post-LOAD CPU/frame still unknown |
| Palette and original display | DOS2 21 fade uploads, original RGB cache normalization | [V062](V062_REMAX_DOS20_PALETTE_FADE.md), [V066](V066_DOS20_DISPLAY_ORACLE_SK.md): original↔original, not original↔modern |

## Original/static code and asset facts (S)

| Area | Static closure and limit |
|---|---|
| DOS/Win16 versions | MZ unpacking, NE fixup-aware call graph, five Win16 clocks/WinG palettes [status v5](PROJECT_STATUS_UNIFIED_V5_2026-09-30.md) |
| Cross-build MAP | 31 levels × 4 marked 0x25–0x28 cells = 124 selected cleared Win16 high bytes, DOS E1M1 controlled A/B visual effect, class36 weapon pickups on Win16 | [V053](V053_REMAX_HUD_WEAPON_CLASS36.md), [V054](V054_REMAX_CROSSBUILD_MAP_PALETTE.md) |
| DOS HUD v1.9→2.0 | new action ID4 inserted, original ID8→ID9, hit signal DS:417A=3 yields static 4→4→4→3, not four guaranteed visible frames | [V053](V053_REMAX_HUD_WEAPON_CLASS36.md) |
| GUARD | original GUARD41 state/death plus local state21 saved state; P0 multi-actor and bosses remain | [V050](V050_REMAX_GUARD41_DEATH_OUTCOME.md), [V058](V058_REMAX_GUARD41_STATE09.md), [v0.78 integration](BULK_UPDATE_20261020.md) |
| MAP→VEC and scheduler | 4-pass static MAP producer and typed records; E2M10 repeated scheduler route identified, natural ABA not yet shown | [v0.78 integration](BULK_UPDATE_20261020.md), [V083 frontier](V083_RUNTIME_PROJECTILE_SAVE_WIN16_FRONTIER.md) |
| Win16 OOM, string/clock | hidden callback, caller/fixup repair, v1.10 archived BP−2 stack evidence separate from SHA checked original v1.8 | [Win16 OOM](WIN16_OOM_CALLBACK_HIDDEN_CODE_ISLAND_20261020.md), [Win16 archive](WIN16_V110_TIMER_ARCHIVED_BYTE_CLOSURE_20261020.md), [string/OOM](WIN16_STRING_TRIO_OOM_SCALAR_ALIAS_20261020.md) |
| Ghidra cache alias | indexed 21FD:0006+i×001C render/damage pool +0x18; separate 21FD:264E+i×001A metadata, candidate order renderer→projectile→later projection | [22.10 Ghidra audit](RE_STATIC_GHIDRA_CACHE_20261022_SK.md): archive static; runtime freshness OPEN |

## Bounded renderer parity and research (B/M)

- Original VEC pool has **592** unique 28-byte records and **304** owner columns in the inspected checkpoint [V068](V068_DOS20_VEC_POOL_OWNER_AUDIT_SK.md). DDA nearest-wall control disagrees on four columns; ownership is not generic DDA.
- V078 reproduces **1 520/1 520 original 22CA corrected U** outputs; V079 reproduces **1 808/1 808 captured CEDC outputs**; those are stage-local parity for captured operands [V078](V078_DOS20_TEXTURE_U_22CA_RUNTIME_SK.md), [V079](V079_DOS20_CEDC_PERSPECTIVE_RUNTIME_SK.md).
- V080 uses real DOS2 IMG and shade; at one original x=8 wall writer, **42/42** indexed output pixels agree. Mid-render pre/post accumulator alignment matters: correct U106 vs incorrect U109 [V080](V080_DOS20_AUTHENTIC_IMG_WALL_RUNTIME_SK.md). This is **not** a complete 64k frame.
- Modern tool V088 is a synthetic **state first-diff gate**, and V089 emits **frame-based SDL preview-only CSV**. These two schemas **cannot be directly compared** [V088](GAMEPLAY_DIFF_V088_2026-10-22.md), [V089](PREVIEW_FRAME_TRACE_V089_2026-10-22.md).
- Active C++ viewer still uses **diagnostic DDA Raycaster.cpp**. Full native original-wall pipeline is under test; do not state pixel-perfect full remake or swap live rendering without paired zero-diff.

## What remains OPEN

**P0:** exact original-tick/fire/USE/secret-door timing; E2M10 natural ABA and stale-depth; boss/special deaths and projectile natural hits; 64,000 indexed + 768 DAC same-tick candidate comparison; full DEMO EOF RNG/input/scheduler chronology; first post-LOAD frame and cache; original↔candidate player/state parity. **P1:** Win16 full message-pump and WinG palette timing; audio/MIDI/PCM determinism; complete 31+1 map suite.

## Trace correctness and original identity

For DOS2 official reference in recent original runs, the unpacked **N3D-E-20.EXE SHA-256 = 552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301** (independently matched against the user's uploaded historical ZIP on this update). **IMG.1 and MAP.1 hashes vary by distribution**; use matching per-test asset manifest, not a different build's file of the same name. Guest DS and host /proc PID can change between sessions; never treat a stale mapping as reference truth.

**Important:** Many catalogued earlier observations are backed by local/private original traces or archived reports; compiling synthetic CI today does not rerun them. The generated [full source index](RE_ALL_EXECUTED_SOURCE_INDEX_20261022_SK.md) lists all available versioned/static/runtime docs in the repository. The machine-readable [register](RE_EVIDENCE_REGISTRY_20261022.json) identifies curated key claims and their exact evidence class.

Next task protocol: [paired-parity bridge](RE_ALLINONE_PARITY_BRIDGE_20261022_SK.md).
