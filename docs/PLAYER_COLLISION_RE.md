# Player collision / movement — NITE3W.EXE

Date: 2026-09-17

This document records direct reverse-engineering results from the original Win16 `NITE3W.EXE` V1.10. It deliberately separates executable evidence from comparison with Catacomb Abyss / Wolfenstein 3-D.

## Evidence labels

- **VERIFIED_EXE** — directly demonstrated by original `NITE3W.EXE` disassembly.
- **INFERRED** — interpretation consistent with the executable but not yet completely named.
- **COMPARISON** — source-level similarity to another engine; not evidence that source was copied.

## Main movement chain

The player movement caller is at `seg3:8AAC` (raw file approximately `0x1EA6C`). When runtime byte `0x4BE8` is zero it calls the movement/collision routine at `seg3:8604` and then the post-move commit/update routine at `seg3:8A20`.

```text
seg3:8AAC  movement caller
    -> seg3:8604  movement / collision stepping
    -> seg3:8A20  post-move world/tile update
```

`seg3:8A20` is raw file `0x1E9E0`. It confirms:

- `0x4BF6` = player world X;
- `0x4BF8` = player world Y;
- `0x4BF2` = player tile X;
- `0x4BF4` = player tile Y;
- world to tile conversion is arithmetic `>> 6`;
- one tile is therefore exactly **64 world units**;
- changing the containing tile dispatches level event `0x16`;
- current MAP cell far pointer is stored at `0x4C10:0x4C12`;
- MAP address is `mapBase + ((tileY * 64 + tileX) * 2)`.

Status: **VERIFIED_EXE**.

## Player collision box

At `seg3:8604` (raw approximately `0x1E5C4`) the movement code expands the candidate position with constant `0x1B` (=27) on the collision axes before deriving the edge MAP cells.

The player collision shape used by this routine is therefore an axis-aligned box with half-extent **27 world units**, i.e. a **54 x 54 unit** footprint inside a 64 x 64 tile.

This should not be described as a circular radius: the executable is testing leading edges of an AABB.

Status: **VERIFIED_EXE**.

## Integer stepping / sliding

The setup code around `seg3:E552..E5D0` constructs signed movement components and a major/minor-axis error accumulator:

- globals `0x4C46` and `0x4C48` hold movement components;
- `0x4C06` selects the major axis;
- `0x4C08` is the accumulated error;
- `0x4C0A` / `0x4C0C` are error increments.

`seg3:8604` then advances the requested motion in **one-world-unit major-axis steps**, adding a minor-axis step when the integer error accumulator crosses its threshold. Each attempted axis step is collision-tested separately.

Consequences:

- movement is Bresenham-like integer line stepping rather than a single large vector collision test;
- X and Y can be accepted/rejected independently;
- if one component is blocked while the other remains clear, motion naturally slides along the obstacle.

Status: **VERIFIED_EXE** for the stepping/control flow; the name “Bresenham-like” is descriptive.

## MAP edge construction

The collision routine derives leading-edge tile addresses directly from the 27-unit box extent. Address arithmetic reduces to:

```text
cell = mapBase + ((tileY * 64 + tileX) * 2)
```

The first and second byte of the 2-byte MAP cell are then interpreted through prebuilt property tables rather than a naive `wallByte != 0` rule.

Status: **VERIFIED_EXE**.

## Collision helper at seg3:84F4

`seg3:84F4` (raw approximately `0x1E4B4`) receives the two adjacent cells along the player's leading edge plus the signed one-unit movement step. It returns the step when that edge is passable and zero when blocked.

Two runtime property tables are central:

- wall properties: `0x7E94[wallByte]`;
- object properties: `0x7F94[objectByte]`.

### Wall collision bits used by this helper

| bit | observed behavior | status |
|---:|---|---|
| `0x04` | hard blocking wall | **VERIFIED_EXE** |
| `0x08` | dynamic wall/door path; runtime door record is queried before deciding passability | **VERIFIED_EXE** |
| `0x40` | invokes the level-script/touch hook `seg3:BFD8`; the bit alone does not force blocking | **VERIFIED_EXE** |

For a wall with `0x08`, the helper resolves the dynamic-wall record through `seg3:1296` and the passability test at `seg3:1476`. The latter accepts runtime state `+0x0C == 0` or `+0x0C == 4`, and rejects the other observed states.

The exact human-readable names of those door states remain **PARTIAL**.

### Object collision bits used by this helper

| bit | observed behavior | status |
|---:|---|---|
| `0x02` | blocks player movement | **VERIFIED_EXE** |
| `0x04` | invokes object touch/pickup/special handler `seg3:CF60` | **VERIFIED_EXE** |

A separate neighboring-cell/path query at `seg3:2649..2778` also checks wall/object bit `0x02`, reinforcing its generic blocked/occupied meaning.

## Door/dynamic-wall runtime records

`seg3:1296` scans a runtime table at `0x9DD6` by MAP-cell far pointer. The records are **22 bytes** each. Initialization around `seg3:14A8..16D5` creates records for walls whose property table contains bit `0x08` and enforces a capacity of **64**; the executable contains `MAXDOORS exceeded (%d)`.

Thus:

```text
DoorRuntime base   = 0x9DD6
DoorRuntime stride = 0x16 = 22 bytes
Maximum doors      = 64
```

Status: **VERIFIED_EXE**.

## Property-table construction

### Wall property table — seg3:24C3..2548

The executable builds `0x7E94[]` from a runtime wall-type mapping table at `0x8196`.

Observed rules include:

- bit `0x04` for mapped types `0x01..0x30`;
- bit `0x10` for `0x2E..0x2F`;
- bit `0x08` for `0x31..0x40`;
- bit `0x01` when `0x04` or `0x08` is present;
- bit `0x02` for mapped types `0x01..0x40`;
- bit `0x40` for mapped types `0x47..0x48`.

Only the bits whose behavior has been traced should be given semantic names. `0x01` and `0x10` remain **PARTIAL**.

### Object property table — seg3:255D..25E8

`0x7F94[]` is built from object-type mapping table `0x8296`:

- bit `0x01`: type `0x06..0x3D`;
- bit `0x02`: type `0x08..0x2D`;
- bit `0x04`: type `0x2F..0x3D`;
- bit `0x08`: type `0x08..0x25`;
- bit `0x20`: type `0x2A`;
- bit `0x40`: type `0x04`.

For player collision, bit `0x02` is confirmed blocking and bit `0x04` is confirmed touch/interaction dispatch.

Status: **VERIFIED_EXE**.

## Reconstructed collision skeleton

```cpp
// Semantic names are reconstructed; addresses/conditions are from the EXE.
int TestLeadingEdge(Cell* a, Cell* b, int signedStep)
{
    const uint8_t wa = wallFlags[a->wall];
    const uint8_t wb = wallFlags[b->wall];

    if ((wa & 0x04) || (wb & 0x04))
        return 0;

    if ((wa & 0x08) && !DoorStateAllowsPassage(FindDoor(a)))
        return 0;
    if ((wb & 0x08) && !DoorStateAllowsPassage(FindDoor(b)))
        return 0;

    if (wa & 0x40) WallScriptTouch(a->wall);
    if (wb & 0x40) WallScriptTouch(b->wall);

    const uint8_t oa = objectFlags[a->object];
    const uint8_t ob = objectFlags[b->object];

    if (oa & 0x04) TouchObject(a);
    if (ob & 0x04) TouchObject(b);

    if ((oa & 0x02) || (ob & 0x02))
        return 0;

    return signedStep;
}
```

## Catacomb Abyss comparison

Catacomb Abyss `C4_WIZ.C` uses:

- a box derived from `x +/- size`, `y +/- size`;
- separate `ClipXMove()` and `ClipYMove()` calls;
- special-tile dispatch while colliding;
- actor/pickup touch checks during movement;
- axis separation that permits wall sliding.

Nitemare 3-D therefore has a **strong structural similarity** to the Catacomb collision design. However, the implementations are not identical: Nitemare uses a 27-unit player half-extent, precomputed two-byte MAP property tables, and one-unit Bresenham-like stepping instead of Catacomb's large-axis move plus repeated halving near a block.

Classification: **CATACOMB-LIKE / DERIVED-LIKE STRUCTURE**, not a copied-source claim.

## Wolfenstein 3-D comparison

Wolf3D's `TryMove` / `ClipMove` path attempts the full vector and, on failure, retries X-only then Y-only. Nitemare does not use that exact fallback structure: it steps the vector incrementally and collision-tests components during the walk.

Classification: **CONCEPTUALLY SIMILAR, ALGORITHMICALLY DIFFERENT**.

## Remaining TODO before calling collision 100%

- Name the remaining wall-property bits (`0x01`, `0x10`, and any rendering-only semantics).
- Fully label door runtime states at `DoorRuntime+0x0C`.
- Confirm all side effects of the hard-wall branch and `seg3:E3B0`.
- Tie object-touch classes to their exact item/special-object identities.
- Regression-test the reconstructed one-unit stepping against original gameplay/demo trajectories.
