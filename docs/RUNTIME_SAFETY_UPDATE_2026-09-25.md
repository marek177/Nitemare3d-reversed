# Runtime safety and CTest update — 2026-09-25

## Scope and provenance

Based on `main` commit `fadb68316a19d9673d759998afffdea7035cfb31`.
Existing source copies used for local validation were checked against their Git
blob SHA values before editing. This is a narrow modern-C++ safety correction,
not a new claim of original Win16 runtime equivalence or completed EXE analysis.
The MFC/window registry work in the parent commit is preserved unchanged.

## Code changes

- `InventoryRuntime.hpp`: indices 0..7 retain their existing behavior. Indices
  8..255 return false for membership and do not modify the mask when granted.
  Validation happens before the shift, eliminating undefined large shifts.
- `ProjectileRuntime.hpp`: coordinate subtraction is widened to `int64_t`
  before subtracting. The square guard-hit tolerance remains inclusive at
  +/-9 on both axes. Projection remains enabled only beyond +/-20 on at least
  one axis; it is still not a projectile lifetime or despawn condition.
- `runtime_safety_test.cpp`: always-on checks independent of `assert`/`NDEBUG`.
  Each all-mode run executes 298,121 checks: all 256 inventory masks with all
  256 bit indices, typed-enum edge cases, and a coordinate matrix covering
  both INT32 limits, both axes, boundary values, and square corners.
- `RegressionTests.cmake`: registers the directory's `n3d_*_test` executables
  with CTest when `BUILD_TESTING` is enabled. Assertion-based tests retain
  checks in Release through target-local `-UNDEBUG` or `/UNDEBUG`.
  The game/core production compilation flags are not changed.

The original-data pushable integration test is opt-in using
`N3D_TEST_DATA_DIR`. An unset directory does not register that test; this is
not a reported pass. A supplied non-directory is rejected at configure time.
The path may contain spaces. No proprietary game data is added.

## Validation actually performed

Before the fix, GCC UBSan reproduced both failures against the pinned sources:

```text
InventoryRuntime.hpp: shift exponent 32 is too large for 32-bit unsigned int
ProjectileRuntime.hpp: -2147483648 - 1 cannot be represented in int
```

After the fix, the new runtime-safety test and the existing
`projectile_runtime_test.cpp` both passed with GCC 14.2 and Clang 17 in Debug,
optimized Release, and UBSan configurations: 12 successful executable runs.
Each runtime-safety run reported 298,121 checks and zero failures. An additional
optimized run with `-DNDEBUG` still defined passed the same checks.

The CTest module was exercised in an **isolated harness**, not a full project
build: the two real tests above plus a compile-time assertion-enabled probe
passed in Debug, Release, and RelWithDebInfo. A separate synthetic argument
probe verified the opt-in data path, including spaces; it did not execute the
original pushable test. `BUILD_TESTING=OFF` registered no tests, and an invalid
data path was rejected. `git diff --check` passed.

## Reproduce on a complete checkout

```sh
cmake -S . -B build -DN3D_ENABLE_SDL3=OFF -DBUILD_TESTING=ON -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
```

With original episode data available, additionally configure with
`-DN3D_TEST_DATA_DIR="path/to/original/data"` to register the pushable test.

## Not validated by this update

A full build of the complete repository, all other existing test binaries,
MSVC/Windows compilation, the original-data pushable integration test, the
SDL3 viewer, and runtime comparison with the original NITE3W executable were
not run in this session. The local environment could read individual sources
through the GitHub connector but could not clone/download the complete repo.
No changes are made here to unresolved CF60/object-touch semantics, player
collision reconstruction, MFC ownership, or renderer fidelity. No overall
reverse-engineering completion percentage is inferred from these fixes.
