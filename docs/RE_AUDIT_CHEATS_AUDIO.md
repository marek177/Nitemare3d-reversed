# Nitemare 3D reverse-engineering audit: cheats + audio

Date: 2026-09-17

This audit separates direct original evidence (`NITE3W.EXE`, `SND.DAT`, official technical notes/manual) from secondary/reimplementation evidence (OpenNitemare3D). A field is marked 100% only when the available original artifacts support a complete structural/behavioral conclusion.

## Cheat system

| Cheat | Confirmed behavior | Status |
|---|---|---:|
| Omniscient | Infinite Magic Eye + Crystal Ball power; F9/F10 remain explicit map toggles. | 100% behavior |
| Omnipotent | All weapons, infinite ammo, invulnerability; gained weapons can remain after disabling. | 100% behavior |
| Omnificent | Guards/monsters ignore the player while sneaking; firing breaks the passive condition. Exact per-guard transition/xrefs still need tracing. | 95% behavior / ~70% internals |
| Omnifarious | Grants collectible level items; official examples include weapons, keys, ID cards and Pentagrams. | 100% behavior / grant internals pending |
| Shareware gate | EXE contains all four menu labels plus the complete-trilogy restriction message. | 95% |
| CONFIG.SAV persistence | Behavioral flags are known; full byte layout/xrefs are not. | 50% |

Important: Omniscient is not an automatic map-on switch; Omnipotent is not merely a one-time ammo refill; Omnificent is an AI hostility/perception rule rather than rendering invisibility; Omnifarious is inventory/puzzle-access rather than no-clip.

## SND.DAT structure — direct parse

- Fixed directory: **960 bytes = 160 records × 6 bytes**.
- Record format: little-endian `{uint16 length, uint32 offset}`.
- ID 0: `IBK` instrument bank.
- IDs 1..15: valid Standard MIDI (`MThd`), Type 1.
- IDs 16..33: reserved/empty.
- IDs 34..110: 77 logical SFX IDs; **72 contain PCM data**.
- Empty SFX placeholders: **62, 72, 75, 76, 77**.
- Aliases: **69 and 70 point to the same PCM block**; **73 and 74 point to the same PCM block**.
- Directory entry 111 is a zero-length end sentinel whose offset equals the archive size.
- Remaining directory slots are unused/zero.

The exact per-ID lengths, offsets and calculated durations are in `analysis/snd_index_audit.csv`.

## Original SFX playback format

Direct `WAVEFORMAT` found in `NITE3W.EXE` at file offset **0x2C288**:

- PCM (`wFormatTag=1`)
- mono
- **11025 Hz**
- 11025 bytes/s
- block align 1
- **8-bit**

Therefore data-bearing SFX entries are raw **8-bit mono PCM at 11025 Hz**. This supersedes the approximate 10989-Hz value used by OpenNitemare3D.

Original technical notes independently state that General MIDI uses Windows `MCISEQ` through Midi Mapper, while effects use `waveaudio`. The game expects drums on MIDI channel 10 (some old Midi Mapper drivers remapped that destination to 16).

## MIDI inventory

All 15 music entries are Standard MIDI Type 1, PPQN=240 and use channel-10 percussion.

| ID | bytes | duration (s) | tracks |
|---:|---:|---:|---:|
| 1 | 20517 | 148.504 | 26 |
| 2 | 15264 | 71.964 | 27 |
| 3 | 13427 | 97.778 | 27 |
| 4 | 16990 | 164.571 | 26 |
| 5 | 18840 | 95.947 | 14 |
| 6 | 21717 | 140.428 | 27 |
| 7 | 12677 | 124.180 | 25 |
| 8 | 10321 | 54.927 | 28 |
| 9 | 7939 | 57.600 | 25 |
| 10 | 8943 | 37.806 | 25 |
| 11 | 3238 | 92.500 | 27 |
| 12 | 4873 | 101.667 | 26 |
| 13 | 14031 | 111.219 | 28 |
| 14 | 4229 | 62.419 | 28 |
| 15 | 8403 | 51.429 | 20 |

Several tracks contain marker metadata such as `Intro`, `Again`, `Bridge`, `Bass/Drums`, `Rhodes`, `Sax`, `Fugue`, `Pipes`, and `Organ`. Exact MIDI-ID -> menu/level usage still requires original EXE call-site tracing or audio matching against walkthrough captures.

## Current semantic SFX map

These names are cross-checked from OpenNitemare3D/gameplay and remain secondary until every original EXE sound-call xref is recovered:

- 42 player death
- 43..45 human guard deaths
- 46 witch death
- 48,49,52,53 witch alerts
- 58 magic wand
- 59,60 silver-pistol/revolver variants
- 61 turret/cannon fire
- 65 plasma weapon
- 66 bat alert; 67 bat death
- 68 skeleton attack
- 69/70 curtain open/close logical IDs (same PCM sample in original archive)
- 71 hidden panel
- 78 Magic Eye pickup
- 81 key pickup
- 82 weapon pickup
- 83 Crystal Ball pickup
- 84 plasma-ammo pickup
- 86,87 human guard alerts
- 88..90 generic monster alerts
- 91 skeleton alert
- 97 Frankenstein attack
- 100 level end
- 101 radio tune
- 105 ghost alert; 106 ghost death

Unresolved semantic IDs include 34..41, 47, 50,51,54..57, 63,64, 73,74,79,80,85,92..96,98,99,102..104,107..110 plus the exact purpose of the empty aliases/placeholders.

## Completion table

Percentages are evidence-coverage estimates, not byte-count coverage.

| Area | Completion | Remaining work to reach 100% |
|---|---:|---|
| MAP/IMG/OBJECTS/WALLS/DEMO structures | 95% | unused/reserved fields and edge cases |
| SND.DAT container structure | **100%** | complete |
| SFX PCM format | **100%** | complete |
| MIDI technical inventory | **100%** | complete |
| MIDI ID -> exact game usage | 45% | trace EXE MCI selection table / match captures |
| SFX ID/offset/length/duration table | **100%** | complete, including empty slots and aliases |
| SFX semantic mapping | 50% | recover unnamed sound xrefs from EXE |
| Weapon SFX | 85% | original EXE call-site confirmation for every event |
| Enemy SFX | 60% | complete GUARD -> alert/attack/death matrix |
| Menu/UI SFX | 20% | identify exact IDs for navigation/select/error/menu events |
| Cheat behavior | 98% | only low-level edge semantics remain |
| Cheat binary implementation | 65% | exact flags/xrefs/config persistence/guard branches |
| WinG/DISPDIB backend | 90% | remaining special paths |
| Renderer geometry/projection | 75% | clipping/sampling/special-wall branches |
| 1:1 raycaster | 55% | full original control-flow reconstruction |
| Door/warp/key/card/pushables | 85% | remaining dispatch/xrefs |
| Level-specific scripts | 80% | remaining internal script dispatch |
| GUARD class/object inventory | 95% | minor unused variants/naming |
| Enemy AI state machine | 40% | states, LOS/hearing/path/reaction transitions |
| Enemy HP/speed/reaction/damage | 20% | numeric tables/branches |
| Weapon qualitative behavior | 75% | exact edge cases |
| Weapon numeric damage/timing | 25% | original damage routine/constants |
| Audio backend/API behavior | 90% | exact MCI/wave lifecycle/volume call graph |
| Menu/HUD/status flow | 75% | exact state machine + UI sound mapping |
| Overall direct `NITE3W.EXE` RE | **~48%** | AI, damage, raycaster branches, audio call-sites dominate remainder |
| Overall behavioral reconstruction | **~78%** | remaining unverified/numeric behavior |

## Fastest path toward 100%

1. Trace the original SFX playback routine and enumerate every caller/index argument.
2. Trace the MCI song-selection table and map MIDI 1..15 to menus/episodes/levels.
3. Trace all four cheat flag addresses through damage, ammo, automap and guard perception.
4. Recover the complete GUARD state table plus hit/damage routine.
5. Finish 1:1 raycaster clipping and texture-sampling branches.
