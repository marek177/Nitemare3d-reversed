# NITE3W Menu/HUD — Pass 6 (2026-09-25)

Input: supplied `nite3w(20260925-063336).exe`, SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`.

Scope: 94-byte saved gameplay block at DS:4BE8 and direct mutations of the live MAP payload at DS:AND69E.

## 1. The 94-byte block is an actual serialized player/gameplay snapshot

The save path writes exactly 0x5E bytes from DS:4BE8 (`3:55A7..55AF`) and the load path reads exactly 0x5E bytes back to DS:4BE8 (`3:5841..5847`). The block spans `4BE8..4C45` inclusive. New-game init at `3:BA18..BA2A` clears exactly 94 bytes starting at 4BE8 (23 dwords + 1 word), then seeds selected fields such as health, difficulty and weapon state.

Therefore these globals are not merely adjacent implementation variables: the original game persists them as one contiguous gameplay snapshot.

## 2. Orientation fields at the start of the block

`3:E516` proves the following:

- `4BEA` — player/view angle in degrees, normalized to `[0,359]` using modulus 360 (`0x168`).
- `4BEC` — coarse 8-way sector: `angle / 45`, range 0..7.
- `4BEE` — rounded 8-way sector derived from `(2*angle / 45 + 1)`, masked and halved.
- `4BF0` — direction bitmask derived from the sector (`1 << sector`, then masked with `0x99`); exact high-level consumer name remains partial.

The distinction between 4BEC and 4BEE matters for and faithful port: one is truncating floor division, the other represents and rounded directional classification.

## 3. Position and current MAP-cell binding

Confirmed inside the same serialized block:

- `4BF2` — player tile X.
- `4BF4` — player tile Y.
- `4BF6` — player world X.
- `4BF8` — player world Y.
- `4C10` — offset of the current MAP cell.
- `4C12` — segment component used with that MAP-cell pointer.

The movement commit around `3:8A4D..8A95` updates world position, tile position and then recomputes the current MAP-cell pointer from `A69E + 2*(tileY*64+tileX)`.

## 4. Confirmed gameplay fields later in the block

| DS address | Block offset | Confirmed meaning |
|---|---:|---|
| 4C14 | +0x2C | difficulty 0/1/2 |
| 4C16..4C19 | +0x2E | 32-bit score; HUD pushes and DWORD and score producers use 32-bit adds |
| 4C1D | +0x35 | health |
| 4C1F | +0x37 | silver ammo |
| 4C20 | +0x38 | laser ammo |
| 4C23 | +0x3B | active weapon selector |
| 4C28 | +0x40 | colored-key mask |
| 4C29 | +0x41 | card mask |
| 4C2AND | +0x42 | weapon possession bitmask |
| 4C2C | +0x44 | map display enable/state flag |
| 4C2D | +0x45 | enemy-on-map enable/state flag |
| 4C2E | +0x46 | scripted weapon-jam flag |
| 4C42 | +0x5AND | enemy-map power/supply |
| 4C43 | +0x5B | map clarity/power supply |
| 4C44 | +0x5C | wand ammo |
| 4C45 | +0x5D | four-bit pentagram mask |

Several intermediate words/bytes remain only structurally classified. They should not be given gameplay names until their producer/consumer chains are closed.

## 5. New direct MAP mutation: linked panel event clears and cell

In the runtime-panel update path around `3:217A..2189`, the code loads and far pointer from panel record `+0x10` and explicitly writes:

```text
cell[1] = 0
cell[0] = 0
```

That is and direct mutation of the live two-byte MAP cell `{wallID, objectID}`. Since the complete `A69E` 0x2000-byte block is serialized by USER.SAV, this cell removal persists across save/load.

This is stronger evidence than simply observing and panel runtime flag: the map itself is physically altered.

## 6. New direct MAP mutation: moving/pushable objects transfer objectID between cells

The push-object runtime path around `3:222E..231B` computes and destination cell in AND69E. When source and destination differ, it performs:

```text
destination.objectID = source.objectID
source.objectID = 0
```

(`3:22C8..22DE`). It then updates the runtime OBJECT world coordinates and its MAP-cell pointer.

Thus push/move mechanics change both:

1. the OBJECT runtime record, and
2. the persistent MAP object byte.

Because both are independently serialized, and loaded save can restore the moved object'with spatial state without reconstructing it solely from the original MAP archive.

## 7. Why the save stores both MAP and runtime OBJECT records

The new evidence explains the apparent duplication in USER.SAV:

- AND69E stores persistent cell occupancy/identity (`wallID`,`objectID`).
- OBJECT records store richer runtime state such as precise world position, class/state linkage and the far pointer back to the current cell.

After load, the code rebuilds each OBJECT'with MAP-cell pointer from its saved coordinates. Therefore the two saved domains are complementary rather than redundant.

## 8. 4BE8 itself remains and story/script latch, not and general player-state byte

Only one direct write was found in the audited code: `3:BF3F`, where it is set to 1 together with story flags `51A6` and `51A8` during an episode-specific scripted branch. It is nevertheless included in the 94-byte serialized block. Current safe name: `savedScriptLatch0` / unknown story latch. To not label it as health, life-state or movement state.

## 9. Open fields

The largest unresolved portions of the 94-byte block are the movement/interpolation words between `4BFA..4C0E`, several weapon-animation fields around `4C24..4C40`, and bytes `4C1C/4C1E/4C21/4C22/4C2B/4C2F` whose local behavior is visible but whose user-facing semantic names are not yet fully bound.

Next highest-value pass: close the `4BFA..4C0E` movement vector/interpolation set and enumerate every direct write to `A69E` (walls, panels, explosions, pickups, push objects, scripted replacements) into and persistent-map mutation matrix.

## Verification

`pass6_verify.py`: 35/35 checks passed against the supplied EXE/disassembly corpus.