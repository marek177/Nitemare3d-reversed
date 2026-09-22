# Nitemare 3-D project findings delta — 2026-09-22

This file records the newest findings recovered in the current Nitemare3D project conversations after the earlier cross-thread consolidation. It is intentionally conservative: direct executable/data facts are separated from strong inference and open targets.

Evidence labels: `VERIFIED_EXE`, `VERIFIED_DATA`, `VERIFIED_SAVE_LAYOUT`, `BEHAVIORAL`, `STRONG/INFERRED`, `PARTIAL`, `TODO`.

## 1. GUARD13 resolved: Dracula-Bat internal second form

Previous repository notes that described GUARD13/class `0x14` as an unknown or apparently unused identity are superseded.

Direct lethal-path evidence shows Dracula class `0x11` transforms in place to class `0x14`:

```text
OBJECT+06: 0x11 -> 0x14
GUARD+10:  0xFF
GUARD+0B:  0x08
GUARD+0C:  0x02
GUARD+06:  1
sequence/frame-related value: 0x23
transformation event/sound request: 0x22
```

The transformed actor therefore receives a fresh 255-strength phase. Score dispatch gives class `0x11` zero points and class `0x14` 200 points. Normal Bat class `0x08` is a separate class worth 25 points.

Current model: Dracula is a two-phase actor: Dracula `0x11` -> Dracula-Bat `0x14`, each phase initialized/restored to 255 strength.

Status: class writer/HP/state reset `VERIFIED_EXE`; high-level name Dracula-Bat `STRONG`, supported by the explicit Dracula writer and Bat-related behavior/resource linkage.

## 2. GUARD25/class 0x20 profile narrowed

Class `0x20` is still visually unnamed, but the audit now constrains it:

- strength 255 on normal/special creation paths;
- generic AI profile observed around state `07`, next-state `02`, strategy 0;
- score value 50;
- class lies outside the explicit combat resistance jump table `0x0C..0x1F`;
- no confirmed dedicated alert/attack/death SFX mapping;
- no confirmed normal MAP spawn or visible sprite identity.

Best current classification: `INFERRED` cut/unfinished/fallback class. Do not assign a monster name until a writer/spawn/SEQDEF/IMG chain proves one.

## 3. OBJECT runtime corrections

The old 80-byte OBJECT hypothesis is obsolete. Direct indexing and save layout prove:

- OBJECT stride `0x1C = 28` bytes;
- capacity 350;
- base `0x6D66`;
- count `0x7E58`.

Relevant fields:

- `+06` class;
- `+07` GUARD index for guard objects;
- `+0C:+0E` map-cell far-pointer/binding;
- `+10/+12` world X/Y;
- `+14/+16` render/spatial-ordering fields, semantics still PARTIAL;
- `+18` projected/view-space vertical baseline read by the damage producer; definitely not world Y.

The damage base is:

```text
((OBJECT+18) - global_53EE) * 8 + random()%25
```

Because this depends on projection plus RNG, exact ammunition counts per enemy are not fixed class constants.

## 4. GUARD record correction retained

The old 98-byte GUARD hypothesis is obsolete. Direct indexing/save layout prove:

- stride `0x1A = 26` bytes;
- capacity 100;
- base `0x93AE`;
- count `0x7E5E`.

Verified fields include timer `+06`, OBJECT link `+08`, strategy `+0A`, state `+0B`, next-state `+0C`, HP `+10`, octant `+11`, resoct `+12`.

State dispatcher range is `0x00..0x15`; state `0x15` is the pain/hit reaction state.

## 5. Combat special cases

The player->GUARD producer confirms these class/weapon behaviors:

- Penelope `0x15`: zero normal weapon damage in the audited producer; separate helper side path exists.
- Dr. Hamerstein `0x16`: literal damage 3 only when global `0x7E52 == 3`, otherwise zero, before difficulty scaling.
- Cannon `0x19`: zero damage in this producer.
- Ghost `0x1A`: only Magic Wand damages it (`/2`); other weapons return zero.
- Alien #1 `0x1E` and Alien #2 `0x1F`: Magic Wand returns zero; other weapons are reduced.
- Baddie #1/#2 `0x0F/0x10`: non-wand path uses literal `/256`, usually collapsing small positive damage to zero.
- Dracula-Bat `0x14` uses the same explicit transform family as Dracula phase 1 (`/8`, `/2`, `/2`, `/8`).

Difficulty global `0x4C14` remains cross-confirmed:

| value | player -> enemy | enemy -> player | GUARD timing |
|---:|---:|---:|---:|
| 0 | x2 | /2 | slower |
| 1 | x1 | x1 | baseline |
| 2 | /2 | x2 | faster |

## 6. Weapon/ammo anchors

- active weapon `0x4C23`;
- Silver ammo `0x4C1F`;
- Laser ammo `0x4C20`, shared by single/continuous laser;
- Wand ammo `0x4C44`;
- shot consumption: 1;
- normal pickup: +20;
- forced/set value: 50;
- intended normal threshold/display cap: 100;
- Silver/Laser signed-byte quirk makes 127 the highest positive signed value in the affected memory-edit/HUD comparison paths.

Weapon jam `0x4C2E` is script-controlled, not random. E1M9 events `0x47` and `0x48` set/clear it.

## 7. Walk-over event distinct from USE

Changing player tile dispatches event `0x16`. This is distinct from the input mask `0x0200` USE/ACTION path.

This distinction is important for reconstruction:

```text
movement/tile transition -> event 0x16
USE key rising edge       -> input 0x0200 -> adjacent-cell interaction
```

Do not fold both into one generic interaction callback.

## 8. 4096-byte cell-state runtime block

Current save/runtime work indicates a 4096-byte, 64x64-sized state/visibility-like block: one byte per map cell is the strongest current structural interpretation.

Status: size/shape `STRONG`; exact bit meanings and all writers/readers remain `PARTIAL/TODO`.

High-value target: determine whether it stores visited/seen/state/trigger/occupancy information or a combination of cell-state flags.

## 9. ID translation/property-table targets

Known runtime property tables:

- wall properties: `0x7E94[256]`;
- object properties: `0x7F94[256]`.

A separate 256-byte translation/ID-table candidate around `D5E3` remains under audit. Its semantic name must not be promoted until read/write/XREF evidence closes the chain.

Unknown wall/property bits `0x04/0x10/0x20/0x40/0x80` must be resolved by individual call sites rather than copied from external ports. Some bits already have verified uses in specific property tables; the unresolved list refers to contexts where the secondary attribute grammar remains incomplete.

## 10. WARP_L1 / WARP_L2 clarification

`WARP_L1..L4` are data-defined colored-key locked wall/passage classes. They should not currently be described as generic teleport functions or scripts.

`WARP_1..8` and `WARP_E1/E2` are separate stair/dumbwaiter/elevator connection families. Any executable routine handling these classes must be named from its actual dispatcher behavior, not from the `WARP_L*` string alone.

Open target: map numeric wall class -> property flags -> USE/touch dispatcher -> key inventory test -> success/failure transition.

## 11. BSF version audit state

Audited DOS shareware BSF families include 1.0, 1.7, 1.8, 1.9 and 2.0; Windows and full variants are also distinct. Six `nite3d.bsf` references/XREFs were identified as the next exact IDA target.

Still open:

1. identify all six parent functions;
2. trace `fopen/read/seek/close` chains;
3. reconstruct the exact byte-by-byte verification/corruption algorithm;
4. compare algorithm changes across 1.0/1.7/1.8/1.9/2.0.

Do not claim serial/CD/online DRM from the current evidence.

## 12. Renderer corrections retained

The recovered original renderer model remains:

- 320x200 8-bit indexed framebuffer;
- WinG/DispDIB presentation path;
- projected wall-vector/span architecture rather than Wolf3D-style one-ray-per-column DDA;
- VEC pool 1000 x 28 bytes;
- four separately sorted VECLIST groups, each capacity 333;
- visible wall spans 50 x 20 bytes;
- projected sprite queue 100 x 18 bytes.

The four VECLIST groups must never be collapsed into a single 333-entry list in reconstruction code.

## 13. Runtime/source implementation consequences

Reconstruction/source code should encode only durable facts:

- OBJECT 28 B / GUARD 26 B corrections;
- class constants for Dracula `0x11`, Dracula-Bat `0x14`, GUARD25 `0x20`;
- Dracula morph HP reset 255 and known state/next-state/timer anchors;
- event `0x16` separate from USE `0x0200`;
- four VECLIST groups;
- ammo globals and difficulty ordering;
- `OBJECT+18` as a PARTIAL projected damage-baseline field, not world position.

Names for GUARD25, unresolved AI states, secondary wall bits, cell-state bits and translation tables must remain PARTIAL/TODO.

## 14. Immediate next targets

1. GUARD25 `0x20`: all writers, spawn reachability, SEQDEF/IMG/SND binding.
2. Complete Dracula `0x11 -> 0x14` sequence/sound/corpse chain.
3. Trace writer of `OBJECT+18` and settle `+14/+16/+18` projection/sort semantics.
4. Resolve 4096-byte cell-state block bit meanings.
5. Resolve Hamerstein gate global `0x7E52` completely.
6. Recover exact enemy attack cadence, projectiles and enemy->player class mapping.
7. Complete `ONE_SHOT`, `REVWALL`, `CONTROL`, `SPECIAL1`, mirror/pentagram dispatch.
8. Finish BSF six-XREF verification algorithm.
9. Resolve remaining SND.DAT class/state sound bindings from original call sites.
