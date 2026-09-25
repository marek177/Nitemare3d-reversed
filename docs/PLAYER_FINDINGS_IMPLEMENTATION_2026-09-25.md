# Player findings implemented in C++ — 2026-09-25

## Provenance and scope

Base: `54f92605adc8233cd217f2630fc9fc9197ecac39` on `main`.
This update promotes existing, documented Win16 V1.10 findings into runnable
semantic helpers. It is **not new disassembly or a new original-game trace**.
The original EXE was not available in this session. Prior audit evidence labels
are retained as provenance, not re-certified by these reconstruction tests.

Sources read at the base commit:

| Source | Git blob | Used evidence |
|---|---|---|
| `docs/PLAYER_HEALTH_RE.md` | `9e99ee59d61cac2877025be098f294debeae5a6b` | HP writes, unsigned receiver, state-2 gate, separate HUD clamp, fixed additions |
| `docs/PLAYER_COLLISION_RE.md` | `cd56924e8540bcb5c9348dddc78ea96d4d8f184f` | Mapped-type property builders, numeric door states, signed tile conversion and MAP binding |
| `docs/HUD_UI_RE.md` | `d2dc9aaa93917a21565599ee46ae1967dcf3d0c9` | Boundary: coordinate HUD reader, portrait thresholds, UIF slots and right panel are not proved here |

## Newly executable semantic subsets

| Original address (segment 3) | New C++ helper | Contract / limit |
|---|---|---|
| `8C09..8C98` | `health::applyEnemyDamage` | Skip Omnipotent or state 2; unsigned lethal comparison; HP zero/state 2 on lethal damage. Returns an outcome; does not play the death animation or sound. |
| `A4CE..A502` | `health::clampForHud` | Unsigned minimum with 100, written back to HP. Not merely visual clipping. |
| `1CD2..1CE3`, `D048..D064` | `health::applyFixedPickup` | If HP <100, add 20 or 30 without premature clamping. Item names, consumption, score and shifted D018 branch are not supplied. |
| `BA30` and documented restore sites | `health::restoreTo100` | Write 100 to HP only. This is not a respawn and does not clear game state. |
| `24C3..2548` | `collision::wallPropertiesForMappedType` / `buildWallProperties` | Construct the wall-property byte from the runtime mapped type. |
| `255D..25E8` | `collision::objectPropertiesForMappedType` / `buildObjectProperties` | Construct the object-property byte from the runtime mapped type. |
| `1476` | `collision::doorStateAllowsPassage` | True for numeric states 0 and 4 only. No speculative open/closed labels. |
| `8A20` | `collision::worldToTile` / `mapCellByteOffset` / `postMoveCell` | Floor division by 64, two-byte MAP cells, event 0x16 only on containing-tile change. Caller performs the actual commit/event dispatch. |

The headers use nested `health` and `collision` namespaces. They are independent
value-level modules and do not dereference original segmented pointers.
`PlayerRuntime.hpp` now exposes the documented HP, game-state, tile-coordinate
and MAP-cell far-pointer component addresses. Its previous claim that HP was
still unbound is removed.

### Important distinctions preserved

- `99 + 20` can be **119 temporarily**, then becomes 100 at the HUD writeback.
- Final enemy damage is already difficulty-scaled by A1EA; the receiver does
  not apply difficulty a second time.
- The enemy receiver tests state **2**, not every state >=2. The separate
  state-3 hazard/death receiver is not generalized into this helper.
- A zero-HP value alone is not substituted for the original state gate.
- Collision half-extent **27** describes an AABB, not a circular radius.
- MAP IDs, definition-file classes and runtime **mapped types** are not
  interchangeable. Property builders explicitly take DS:8196/8296 mapped types.
- Wall bit 0x40 is not renamed as a hard-block flag. The wall/object touch
  dispatcher and its side effects are outside these pure table builders.
- Signed conversion gives `worldToTile(-1) == -1`, unlike truncating `/64`.
- MAP offsets are relative to the runtime cell buffer, not archive-file offsets.
  Rejecting out-of-map coordinates is a modern safety contract, not original
  out-of-bounds behavior evidence.

## Integration fault found during this update

Compiling `InventoryRuntime.hpp` together with `PlayerRuntime.hpp` at the base
commit fails: the key/card/pentagram address constants, all-pentagrams mask and
`hasAllPentagrams` have conflicting or repeated definitions.

`PlayerRuntime.hpp` now includes the canonical inventory header instead of
redefining those names. Values and inventory behavior are unchanged; inventory
address declarations now consistently use the canonical header's `uintptr_t`
type. The prior invalid-bit safety correction remains unchanged.
This compilation failure was reproduced locally before the edit.

## Validation actually performed

The new always-on `player_reconstruction_test.cpp` performs **2,273,801 checks**
per run, including all 256 HP and damage values across states 0..3 and both
immunity values, all mapped-type bytes, all 65,536 door-state API inputs,
all signed 16-bit world coordinates, INT32 extremes, MAP boundaries and
post-move event behavior. These are synthetic reconstruction checks.

- GCC 14.2 and Clang 17: Debug, optimized Release with `NDEBUG`, and UBSan
  with nonrecovering errors: **6 successful runs**, zero failures each.
- Self-contained headers and forward/reverse include ordering: **12 successful
  syntax-only compilations** across the two compilers.
- The existing CTest registration module was exercised in an **isolated subset
  harness** with the new real test: Debug, Release and RelWithDebInfo all pass.
- Pinned local copies of existing edited/dependency files were verified against
  their Git blob hashes. `git diff --check` passed.

The new target is registered before `RegressionTests.cmake`, preserving the
existing opt-in original-data test behavior and all previous targets.

## Reproduction on a complete checkout

```sh
cmake -S . -B build -DN3D_ENABLE_SDL3=OFF -DBUILD_TESTING=ON -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release --target n3d_player_reconstruction_test
ctest --test-dir build -C Release -R '^n3d_player_reconstruction_test$' --output-on-failure
```

A direct helper-only validation needs no original data or SDL:

```sh
c++ -std=c++20 -O2 -DNDEBUG -Isrc tests/player_reconstruction_test.cpp -o player_test
./player_test
```

## Not completed or claimed

This does **not wire the helpers into the SDL viewer or replace
`LevelState::tryMovePlayer`**. Full one-unit axis stepping, corner/sliding
semantics, CF60 touch side effects, mutable door updates, hazard state 3,
actual HUD drawing, portrait/UIF mappings and original trajectory matching
remain separate integration/audit work.

A complete repository build, all older tests, MSVC/Windows builds, original
NITE3W runtime execution and proprietary-data tests were not run. The local
container could not resolve GitHub for cloning; source reads/writes used the
connected GitHub tool. No overall reverse-engineering percentage is raised
from the synthetic test count. Previous MFC, renderer and runtime-safety work
is preserved.
