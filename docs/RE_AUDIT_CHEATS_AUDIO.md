# Nitemare 3D reverse-engineering audit: cheats + audio

Date: 2026-09-17

## Executive status

This audit separates **direct original evidence** (NITE3W.EXE, SND.DAT, official technical notes/manual) from **secondary/reimplementation evidence** (OpenNitemare3D). A field is only marked 100% when the available original artifacts support a complete structural/behavioral conclusion.

## 1. Cheat system

The original game exposes four cheat modes:

| Cheat | Confirmed behavior | Status |
|---|---|---:|
| Omniscient (all-knowing / all seeing) | Infinite Magic Eye and Crystal Ball power. F9 wall automap and F10 monster automap still remain user toggles. | 100% behavior |
| Omnipotent (all-powerful) | Gives all weapons, infinite ammunition, and invulnerability. Official documentation explicitly states weapons gained can remain after disabling the cheat. | 100% behavior |
| Omnificent (all-cunning) | Monsters do not consider the player an enemy while sneaking; firing breaks the passive condition. Exact per-guard internal state transition still needs full binary xref tracing. | 95% behavior / ~70% internals |
| Omnifarious (all things) | Grants collectible items available in the level; official examples include weapons, keys, ID cards and Pentagrams. | 100% behavior / internal grant table not fully traced |
| Shareware/registration gate | EXE contains the four menu labels and the text `Cheat modes are only available ... complete trilogy`; reconstruction preserves the gate. | 95% |
| Cheat persistence/config layout | Flags are known behaviorally but full CONFIG.SAV byte-level field map is not yet complete. | 50% |

Important interaction details:
- Omniscient does not automatically force F9/F10 on; it prevents their power resources from running out.
- Omnipotent changes survivability/ammunition semantics rather than merely pre-filling inventory.
- Omnificent is an AI perception/hostility rule, not invisibility rendering.
- Omnifarious is an inventory/puzzle-access cheat, not a no-clip mode.

## 2. SND.DAT structure

Directly parsed from the supplied original `snd.dat`.

- Fixed 960-byte directory area = 160 records × 6 bytes.
- Each record is little-endian `{uint16 length, uint32 offset}`.
- Index 0 is an `IBK` instrument bank.
- Indices 1..15 are valid Standard MIDI files (`MThd`), Type 1.
- Indices 16..33 are reserved/empty.
- Indices 34..110 are 77 non-empty sound-effect samples.
- Directory entry 111 has zero length and end offset equal to the total archive size (sentinel).
- Remaining directory slots are unused/zero.

Therefore the logical sound index range used by the game is 0..110.

## 3. Original playback format

A direct WAVEFORMAT structure occurs in `NITE3W.EXE` at file offset `0x2C288`:

- format tag: PCM
- channels: 1
- sample rate: 11025 Hz
- average bytes/sec: 11025
- block align: 1
- bits/sample: 8

This confirms that SFX entries 34..110 are raw 8-bit mono PCM at 11025 Hz.

The original technical notes additionally state:
- General MIDI music is played through the Windows multimedia `MCISEQ` sequencer device via Midi Mapper.
- Sound effects use the Windows `waveaudio` device.
- Drum mapping assumes MIDI channel 10 (legacy Windows Midi Mapper could redirect to 16 on some drivers).

## 4. MIDI inventory

All 15 music entries are Standard MIDI Type 1, PPQN=240 and contain channel-10 percussion.

| ID | bytes | duration (s) | tracks | active MIDI channels |
|---:|---:|---:|---:|---|
| 1 | 20517 | 148.504 | 26 | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 |
| 2 | 15264 | 71.964 | 27 | 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 |
| 3 | 13427 | 97.778 | 27 | 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 |
| 4 | 16990 | 164.571 | 26 | 1, 2, 3, 4, 10 |
| 5 | 18840 | 95.947 | 14 | 1, 2, 3, 10 |
| 6 | 21717 | 140.428 | 27 | 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16 |
| 7 | 12677 | 124.180 | 25 | 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 |
| 8 | 10321 | 54.927 | 28 | 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 |
| 9 | 7939 | 57.600 | 25 | 1, 2, 4, 10 |
| 10 | 8943 | 37.806 | 25 | 1, 2, 3, 10 |
| 11 | 3238 | 92.500 | 27 | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 |
| 12 | 4873 | 101.667 | 26 | 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 |
| 13 | 14031 | 111.219 | 28 | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 |
| 14 | 4229 | 62.419 | 28 | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 |
| 15 | 8403 | 51.429 | 20 | 1, 2, 3, 4, 10 |

Track-marker metadata is present in several songs (for example `Intro`, `Again`, `Bridge`, `Bass/Drums`, `Rhodes`, `Sax`, `Fugue`, `Pipes`, `Organ`). Exact music-ID -> level/menu usage still requires full EXE call-site mapping or audio matching against walkthrough captures.

## 5. SFX semantic IDs

The archive indices are original and exact. The following semantic names are currently cross-checked from OpenNitemare3D and gameplay evidence, but should remain marked as secondary until every original EXE call site is traced:

- 42 PLAYER_DIE
- 43..45 human guard deaths
- 46 witch death
- 48,49,52,53 witch alerts
- 58 magic wand
- 59,60 revolver/silver pistol variants
- 61 turret/cannon fire
- 65 plasma weapon
- 66 bat alert
- 67 bat death
- 68 skeleton attack
- 69 curtain open
- 70 curtain close
- 71 hidden panel open
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
- 105 ghost alert
- 106 ghost death

Unknown semantic slots remain especially 34..41, 47, 50,51,54..57,62..64,72..77,79,80,85,92..96,98,99,102..104,107..110.

## 6. Completion table

These percentages are evidence-coverage estimates, not byte-count percentages.

| Area | Current completion | What remains before 100% |
|---|---:|---|
| MAP/IMG/OBJECTS/WALLS/DEMO archive structures | 95% | edge cases, every unused/reserved field |
| SND.DAT container structure | 100% | complete |
| SFX PCM format | 100% | complete |
| MIDI file inventory/technical format | 100% | complete |
| MIDI ID -> exact game usage mapping | 45% | trace all EXE music-selection call sites / match gameplay audio |
| SFX index table/offsets/durations | 100% | complete |
| SFX semantic ID mapping | 50% | identify all currently unnamed indices from original EXE |
| Weapon SFX | 85% | original EXE call-site confirmation for every fire/alternate event |
| Enemy SFX | 60% | complete GUARD-type -> alert/attack/death ID matrix from EXE |
| Menu/UI SFX | 20% | identify indices and every menu event |
| Cheat behavior | 98% | only low-level state transitions/config persistence remain |
| Cheat binary implementation | 65% | trace exact flags, xrefs, apply/consume branches and CONFIG.SAV fields |
| WinG/DISPDIB display backend | 90% | remaining special paths |
| Renderer geometry/projection | 75% | exact clipping/sampling/special wall branches |
| 1:1 raycaster | 55% | full segment/offset function reconstruction |
| Door/warp/key/card/pushable behavior | 85% | exact EXE dispatcher/xrefs for remaining variants |
| Level-specific scripts | 80% | remaining script dispatch internals |
| Enemy GUARD class/object inventory | 95% | minor naming/unused variants |
| Enemy AI state machine | 40% | full state table, LOS/hearing/path/reaction transitions |
| Enemy HP/speed/reaction/damage | 20% | recover original numeric tables/branches |
| Weapon behavior qualitative | 75% | exact timings/damage/multipliers |
| Weapon numeric damage/timing | 25% | original damage routine and constants |
| Sound backend/API behavior | 90% | exact MCI/wave lifecycle and volume handling call graph |
| Menu/HUD/status flow | 75% | exact original state machine and all UI SFX |
| Overall direct NITE3W.EXE reverse engineering | ~48% | most remaining work is AI, damage, raycaster branches, sound call-sites |
| Overall behavioral reconstruction | ~78% | close remaining unverified mechanics/numeric behavior |

## 7. Highest-value next targets

To move fastest toward 100%:
1. Trace the original SFX playback routine and enumerate every immediate/index argument xref; this should close most unknown sound names.
2. Trace the MCI music-selection table and map MIDI 1..15 to menu/episodes/levels.
3. Trace the four cheat flag addresses through damage, ammo, automap and guard-perception code.
4. Recover the GUARD state table and damage routine.
5. Finish the 1:1 raycaster clipping/texture-sampling branches.
