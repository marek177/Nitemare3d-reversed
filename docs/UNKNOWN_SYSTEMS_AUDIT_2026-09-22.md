# Unknown systems audit — 2026-09-22

This report consolidates unresolved and newly prioritised targets from the
cross-session Nitemare 3-D analyses. It is an audit plan, not a claim that
every hypothesis is present in the original game. Evidence labels are
intentional: `VERIFIED_EXE`, `VERIFIED_DATA`, `VERIFIED_SAVE_LAYOUT`,
`BEHAVIOURAL`, `INFERRED`, `PARTIAL`, and `TODO`.

The machine-readable counterpart is `src/re/UnknownSystemsAudit.hpp`, covered
by `n3d_unknown_systems_audit_test`.

## Highest-value end-to-end chain

```text
GUARD AI -> attack sequence/frame event -> projectile or weapon
 -> collision -> damage/difficulty -> strength <= 0
 -> death/sound -> score, drop, morph or removal
```

This chain can resolve AI timing, projectile representation, damage/immunity,
SND mapping, score assignment, Dracula-to-Bat behaviour and hidden spawn paths.

## Current evidence anchors

| Area | Confirmed/high-confidence anchor | Remaining question |
|---|---|---|
| GUARD | base `0x93AE`, stride 26 B, capacity 100; states `00..15`; pain `15h`; score switch `08..20` | exact state names, movement/LOS/attack timing, GUARD26–30 |
| Combat | strength `+10`; health `0x4C1D`; ammo `0x4C1F/0x4C20/0x4C44`; difficulty `0x4C14` | visible enemy/projectile binding, RNG/resistance, fire probability |
| Runtime | OBJECT count `0x7E58`; GUARD count `0x7E5E`; OBJECT 28 B | runtime spawn/despawn and projectile record type |
| Walls | property tables `0x7E94/0x7F94`; dispatcher target `SEG3:2334–247A` | handler table and common trigger/script mechanism |
| Renderer | VEC 28 B/1000; lists 333; owner `0x53FE`; occlusion `0x58FE`; spans 50×20 B; sprites 100×18 B | conflict math, flags `04/08/10`, texture-U and animation |
| MAP | 514 B header plus 64×64×2 payload; 31 supplied levels including E1M11 | header fields and technical level ceiling |
| Saves | USER.SAV slot `0xD6E7`; unknown block `0xC403`, 336 B; word `0xD6E5` mirrors `0x7E60` | semantic ownership and event diffs |
| Resources | SND directory 160×6 B; MIDI IDs 1–15; SFX 34–110; FLI deltas | event-to-SND map, UIF reserved slots, playback fidelity |
| NE/BSF | Win16 NE has 10 segments; BSF has six known xrefs | relocation classification and BSF algorithm |

## New discovery targets

### GUARD decision tree and sequence events

Audit every read/write of GUARD `+06`, `+0A`, `+0B`, `+0C`, `+0E`, `+10`, then
join it to sequence-definition and SND calls. A sequence may encode frame
duration, attack event, sound, movement and next-sequence transitions. Do not
assign HP, speed, alert radius or immunity per visible name until class binding
is recovered.

Classify GUARD26–30 by creation and use. Candidates include dancer, projectile,
helper, scripted replacement or unused classes; existence alone proves none of
these interpretations.

### Spawn, collision and projectile classification

Partition count/record writes into level load, wall trigger, drop, projectile,
replacement and removal. Build a matrix for `PLAYER×WALL`, `PLAYER×OBJECT`,
`PLAYER×GUARD`, `PROJECTILE×WALL`, `PROJECTILE×GUARD`, `GUARD×WALL` and
`GUARD×GUARD`. Record exact `TEST/AND/OR/CMP` masks before naming flags.

### Death, score and morph

The recovered score switch gives Dracula class `0` and Demon class `250`.
That is direct score-dispatch evidence, not proof that Dracula-to-Bat is absent.
Trace `strength <= 0` through death sequence, sound, score, counter, object
replacement, item drop and final removal.

### Wall dispatcher and E2M4 `0x37`

Create `wall class -> handler -> condition -> map write -> sound ->
animation/resource -> object/guard write` for `WARP_L*`, `WARP_*`, `WARP_E*`,
`WARP_S2`, `CONTROL`, `SPECIAL1`, `ONE_SHOT`, `REVWALL` and `DOOR*`.
E2M4 cell `(61,54)` with wall `0x37` is a candidate anomaly, not proof of a
deleted class. Compare MAP, WALLS.2 and EXE handler domains first.

### Renderer, timing and hidden content

Keep the established projected-boundary-vector model. Audit VEC `+01/+02/+03/
+04/+08`, flags `04/08/10`, owner conflict `FUN_1018_3564`, texture-U
`FUN_1010_6422`, and animation path `FUN_1010_65A6`. Locate RNG/seed and main
logical tick; DEMO records are 8 B but determinism still requires evidence.

Use four hidden-content sets: `DEFINED`, `PLACED`, `REFERENCED`, `EXECUTED`.
Report `DEFINED−PLACED`, `REFERENCED−PLACED`, `DEFINED∩PLACED−EXECUTED`, and
`EXE handlers−known classes` across IMG, OBJECTS, WALLS, SND, UIF, MAP and EXE.

## Prioritised next passes

1. GUARD state/sequence/SND XREF join and GUARD26–30 classification.
2. Wall dispatcher plus E2M4 `0x37` validation.
3. Attack-to-damage-to-death-to-score/morph trace.
4. RNG/main tick and DEMO determinism.
5. MAP header differential and USER.SAV 336-byte event diff.
6. BSF consumer/version diff and NE relocation classification.
7. Mathematical hidden-content scan and UIF/SND/FLI edge cases.

Do not publish one overall percentage. Keep format knowledge, executable
control-flow recovery and behavioural equivalence as separate progress axes.
