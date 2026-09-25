# Projectile save/load subset implemented — 2026-09-25

## Scope and evidence

Base commit: `9d485e82a84ef1241eff7165c390c82eaff47970`.
This implements already documented Win16 V1.10 findings; it is not new EXE
disassembly, original-game execution, or a DOS-format implementation.

Primary project evidence at the base commit:

| Source | Git blob | Facts used |
|---|---|---|
| `analysis/nite3w_projectile_pool_2026-09-23.md` | `1a1329ea6b6ce4325181c51c0f3a593b419e0dc5` | Writer `FUN_1010_5466`, loader `FUN_1010_574C`, pool layout, embedded OBJECT, MAP-reference reconstruction |
| `src/game/ProjectileRuntime.hpp` | `74566b3a3a3d035315302693418d28c5ec7978b8` | Eight 42-byte records; slot-relative start `0xC403`, length `0x150` |
| `src/game/ObjectSystem.hpp` | `9b113feb4fdb52ba800a7f45d0aa79af5cdd51cd` | Embedded 28-byte OBJECT layout and preserved unknown members |
| `src/game/PlayerCollisionRuntime.hpp` | `cb41b5951e656c7d602e729d72fa54da5f4f8377` | Signed world-to-tile conversion and checked MAP-cell byte offset |
| `src/game/GuardSaveBlock.hpp` | `0f57725893dd98fdeafa048d9539d35d3d568dc0` | Existing slot-relative byte-copy API convention |

The audit describes the original pool at `DS:4C4A`, persisted in the half-open
slot interval `[0xC403, 0xC553)`. Each record is 14 movement/state bytes followed
by a 28-byte OBJECT. Projectile-relative `+0x16` holds the animation deadline,
`+0x1A/+0x1C` hold MAP offset/segment, and `+0x1E/+0x20` hold world X/Y.
Unknown bytes retain their existing offset-based names and original values.

## New executable API: `game/ProjectileSaveBlock.hpp`

| API | Behavior |
|---|---|
| `readProjectileSaveBlock` / `writeProjectileSaveBlock` | Copy exactly 336 bytes at the slot-relative offset. Reject short spans before writing. Do not modify adjacent panels, story flags, or other slots. |
| `decodeProjectileRecord` / `encodeProjectileRecord` | Convert every field explicitly in little-endian order. Preserve all 42 bytes, including unknown fields, unknown state values, signed words, deadlines and saved pointer components. |
| `decodeProjectilePool` / `encodeProjectilePool` | Bridge the raw block and the existing typed `ProjectilePool`, without resetting free/impact/flying records. |
| `tryRebindProjectileMapCells` | Rebuild all eight MAP references from saved X/Y and a supplied segment/base offset. Validate all inputs first; return false without partial mutation when invalid. |

The codec does not reinterpret file storage as packed structs or dereference
saved far pointers. It does not rely on host byte order. Cross-endian execution
was not tested; byte-order behavior is covered by literal byte fixtures.

The raw round trip and MAP rebinding are deliberately separate operations.
`write(read(slot))` preserves the saved references, whereas an explicitly
requested rebind changes only each record's four bytes at `+0x1A..+0x1D`.
Animation deadlines, error accumulators, coordinates, flags, state and cache
values are not reset or reinterpreted as elapsed time.

### Modern safety contracts, not new original-game findings

The caller must supply a span beginning at one selected physical save slot;
this API does not parse or select slots in the enclosing USER.SAV file.
Only the end of the projectile block is required, following GuardSaveBlock's
convention. A successful block read does not validate the rest of a save file.

Rebinding requires coordinates in the 64x64 map and the entire 8192-byte MAP
cell buffer to fit within a single 16-bit segment. A nonzero base offset is
supported up to 57344; the last cell then begins at offset 65534. The base is
not the MAP archive header offset. Crossing/normalizing segment boundaries is
not implemented. Segment values are stored as numbers, never host pointers.

The audit describes rebinding every saved projectile record. This helper also
checks free and unknown-state records, so an invalid coordinate in any of them
rejects the whole operation. This strict rejection policy is modern defensive
behavior, not a claim that the original loader rejects the same inputs. The
raw codec still round-trips such bytes losslessly.

## Example integration

```cpp
using namespace nitemare3d::game;
auto raw = readProjectileSaveBlock(slotBytes); // slotBytes: span of ONE slot
ProjectilePool pool = decodeProjectilePool(raw);
// Lossless edit/transport, with no load-time normalization:
writeProjectileSaveBlock(slotBytes, encodeProjectilePool(pool));
// For a separately requested original-layout load/rebind step:
if (!tryRebindProjectileMapCells(pool, loadedMapSegment, loadedMapOffset)) {
    // Handle invalid coordinates/base; pool has not been partially changed.
}
```

This does not install a modern host-side map pointer. A modern runtime should
use validated indices/references rather than dereferencing stored selectors.

## Validation actually performed

The new always-on test executes **2,622,248 checks per run**, independent of
`NDEBUG`. It checks a literal field-offset/byte-order fixture; all 256 byte
values at each of 42 positions; all 65,536 signed-word values across the 11
signed members; 512 full-pool patterns; deadline limits; every too-short span
length; shifted slot views and neighboring-byte preservation; all 4096 map
cells; invalid coordinates in every slot; all 65,536 MAP-base offsets; and
all-or-nothing/idempotent rebinding. All save buffers are synthetic.

- GCC 14.2 and Clang 17: new projectile test plus the existing player and
  runtime-safety tests in Debug, Release (`NDEBUG`) and nonrecovering UBSan:
  **18 successful executable runs**.
- Clang AddressSanitizer + UBSan: **one additional successful run** of the new
  test, including all short-span and unaligned-view cases.
- Self-contained new header and both include orders with PlayerRuntime:
  **six successful syntax-only compilations** across the two compilers.
- Isolated CMake/CTest harness with those three real tests: **9/9 test runs**
  pass across Debug, Release and RelWithDebInfo. This is not the full project.
- Existing local source/dependency copies match their pinned Git blob hashes.
  `git diff --check` passes. Only the new test target is added to CMake; the
  existing CTest module, prior player code and runtime safety fixes are unchanged.

Reproduce the helper test directly (no original data or SDL required):

```sh
c++ -std=c++20 -O2 -DNDEBUG -Isrc tests/projectile_save_block_test.cpp -o projectile_save_test
./projectile_save_test
```

On a complete checkout, the target is `n3d_projectile_save_block_test`, registered
before `cmake/RegressionTests.cmake` like the existing regression tests.

## Remaining work / no claim of completion

Full USER.SAV container loading, the loader's direction recalculation through
`FUN_1010_E516`, runtime clock/deadline reconciliation, ongoing projectile MAP
pointer updates, exact animation continuation, and wiring save/load into the
SDL viewer remain separate work. This update neither steps projectiles nor
changes collision/damage behavior. It does not increase an overall EXE-analysis
percentage from the synthetic test count.

The original EXE and original saved games were not available. A full repository
build, all older tests, MSVC/Windows execution, big-endian execution and original
Win16 save/load equivalence were not tested. GitHub source access and writes use
the connected tool; a direct container clone failed due to DNS resolution.
