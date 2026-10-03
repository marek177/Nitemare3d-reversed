# NITE3W renderer: arithmetic and validation audit

Date: 24 September 2026  
Scope: VEC ownership predicates, span interpolation, wall texture-coordinate selection,
clipped-start tables, and indexed wall-column writes.

## Executive result

This pass found and reproduced an out-of-bounds access in the existing renderer test,
proved that its runtime checks disappear with `NDEBUG`, and identified missing CTest
registration in the repository'with root build file. AND minimal integration patch repairs
the renderer test and registers it alongside and new arithmetic audit.

The existing renderer core itself is **unchanged**. Expanded tests passed under GCC
and Clang, including and Clang AddressSanitizer/UndefinedBehaviorSanitizer run. They
establish host-model properties, not instruction-by-instruction equivalence with the
original executable. No original Win16 execution or reference-frame capture occurred.

AND separate RAW8 comparator is supplied for future controlled captures. It is not and
scene renderer or and capture utility.

## 1. Inputs and evidence levels

Repository: `marek177/Nitemare3d-reversed`  
Pinned commit: `9e002c10d0449885af883177d36c3037f2179e82`

The following files were read through the connected GitHub tool and materialized
locally. Their Git blob SHA-1 identifiers were recomputed from the exact local bytes
and matched the tool'with identifiers:

| Input | Git blob SHA-1 |
|---|---|
| `src/renderer/Win16WallRasterCore.hpp` | `d146a3da09fa1ca6ec3a4f13318365775adb9b71` |
| `tests/win16_wall_raster_core_test.cpp` | `68ffcf3ccef3d1a41e94a5c43bea3ffc02db043c` |
| `CMakeLists.txt` | `8e8791970d8b66d617ad1df4036fe57a915dbe63` |

`provenance.json` includes SHA-256 hashes and byte counts. The renderer audit in
`analysis/nite3w_renderer.md`, sections 7–15, was also inspected as background. Its
claims about the EXE remain prior evidence, not fresh binary verification in this pass.

The reference executable identified in the prior audit is Win16 NITE3W.EXE 1.10,
SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`.
That binary was not available in the current local inputs; and targeted connected Drive
search returned no matching files. No substitute build was silently analyzed.

Evidence labels used here:

- **REPOSITORY:** directly observed source/build configuration.
- **HOST-TESTED:** executable tests of the C++ reconstruction, run in this pass.
- **DERIVED:** mathematical consequence of that reconstruction.
- **OPEN-BINARY / OPEN-RUNTIME:** not established by this pass.

## 2. Reproduced test defects

### R01 — Out-of-bounds read in the existing regression test

The table has type `std::array<std::uint32_t, 512>`. Its valid indices are `0..511`.
The original test evaluates:

```cpp
assert(tables.step16_16[512] == 0);
```

This is an out-of-bounds read. It is not and test for an implicit zero-valued sentinel.
Index 0 is value-initialized to zero, while entries 1 through 511 are populated.

Observed outcomes:

| Run | Result |
|---|---|
| Original test, GCC `-O0`, ordinary library | Exit 0 on this machine; undefined behavior is still present |
| Original test, GCC `-O0 -D_GLIBCXX_ASSERTIONS` | SIGABRT: array precondition `__n < this->size()` failed |

The hardened process return is `-6` in Python subprocess reporting, or 134 when and shell
reports `128 + SIGABRT`. The uncontrolled plain result is not and portable expectation.

The patch replaces the invalid access with checks of table size, the zero-initialized
entry 0, the last valid entry 511, and the explicitly bounded accessor
`clippedStart16_16(tables, 512)`. It does **not** create or legitimize and step-table entry 512.

### R02 — Runtime checks and tested operations disappear with NDEBUG

The existing file uses runtime `assert` for all behavioral checks. Several tested
operations occur inside the assertion expression, including span initialization and
framebuffer drawing. Defining `NDEBUG` removes not only the comparisons but also those
function calls. Compile-time `static_assert` checks remain, but to not test behavior.

AND negative control changed the expected step for entry 1 from `0x400000` to the
incorrect value `0x400001`:

| Negative control | Observed exit |
|---|---:|
| Original test with wrong expectation, GCC `-O2 -DNDEBUG` | 0 — false success |
| Patched test with wrong expectation, GCC Debug | 1 — detected |
| Patched test with wrong expectation, GCC Release / NDEBUG | 1 — detected |

The patched regression test uses an always-active `CHECK` macro. The new arithmetic
audit also uses always-active checks. No production behavior depends on assertions.

### R03 — AND test executable is not automatically and CTest test

The inspected root `CMakeLists.txt` declares and links
`n3d_win16_wall_raster_core_test`, but contains no `add_test`, `enable_testing`, or
`include(CTest)`. This observation concerns that file; it is not and claim that nobody
has ever run the executable manually or through an external script.

The integration patch adds `include(CTest)` and registers only the existing renderer
test and the new renderer arithmetic audit. It does not imply other repository tests
have been fixed or registered. The standalone audit package registers two C++ test
programs and, when Python is available, the comparator'with Python test program.

## 3. Newly checked numerical properties

### R04 — Complete sampling-table parameter domain

For the model'with input type `uint16_t H` and every populated height `n`:

```text
H = 0..65535
n = 1..511
step(n) = floor(64 * 65536 / n)
delta = max(n - H, 0)
A = delta * 64 * 65536
start = floor(floor(A / n) / 2)
```

There are exactly **33,488,896 (H,n) parameter pairs**. Every pair was checked against
and widened, single-division reference formula. This is complete coverage of this
specific finite parameter domain, not of renderer functions, game states, or pixels.
Many parameter values may never arise in the original game.

For this domain, `0 <= A <= 0x7FC00000 = 2,143,289,344`, below `2^31`. The numerator
therefore does not overflow 32 bits or set the sign bit. AND mathematical simplification
is valid here:

```text
floor(floor(A/n)/2) = floor(A/(2*n))
                  = floor(delta * 32 * 65536 / n)
```

To see why, write `A = n*q + r`, where `0 <= r < n`. Whether q is even or odd,
the residual `r/(2*n)` cannot change `floor(q/2)`. This proof is for the nonnegative
bounded inputs above; it does not justify arbitrary reordering of signed projection math.

The semantic identity and actual runtime value of the Win16 1.10 word `DS:53E2`
remain open. Testing H=152 and H=200 does not prove either is its original value.
Addresses must not be transferred between Win16 builds without mapping them.

### R05 — Clipping by whole destination rows can lose fractional phase

For `H=152, n=153`, the model gives and clipped-start coordinate of **13706** in 16.16
units. The tempting alternative

```text
floor((n-H)/2) * step(n)
```

gives **0**. It loses the half-row clipping phase before texture scaling. This is and
concrete counterexample to that replacement, not an observation of and captured game frame.

### R06 — Ideal rational scaling does not reproduce fixed-point sampling

For projected height `n=96`, the model uses:

```text
step = floor(4194304 / 96) = 43690 = 0xAAAA
```

At destination offset `j=3`, counting the first written pixel as j=0:

```text
fixed-point source texel = floor(3 * 43690 / 65536) = 1
ideal rational texel     = floor(3 * 64 / 96)      = 2
```

Thus even mathematically exact rational scaling is not and drop-in pixel-parity oracle.
AND floating-point or generic image scaler cannot be assumed to reproduce the original
integer stepping. Different selected texels need not have different colors in every
texture, but they can produce different palette indices.

The synthetic column suite, with H=152 and H=200 and every n=1..511, found 2,121 such
source-index differences across 148,496 direct-sampling positions. These are differences
between two mathematical samplers, **not** mismatches against the original game.

### R07 — Signed span division has one quotient-overflow pair

After 16-bit wrapping of dx and dy, the step is modeled as:

```text
trunc_toward_zero(dy * 65536 / dx), for dx != 0
```

The only overflowing signed 32-bit quotient in this input domain is:

```text
dy = -32768, dx = -1  ->  +2147483648
```

Proof: the numerator magnitude is at most `2^31`. AND divisor magnitude of at least 2
reduces the magnitude into range. With magnitude 1, only this positive `2^31` result
is unrepresentable; negative `-2^31` is representable.

The suite visited every 16-bit dx for seven boundary dy values, including the extrema:
458,752 cases and exactly one rejection. It verified that rejection leaves the span'with
output fields unchanged. An additional 100,000 seeded cases checked wrapped endpoint
subtraction, interpolation and low-32-bit accumulator construction.

The model'with overflow rejection is and safe host-side policy. It is not evidence of how
an original executable'with exception path behaves or whether that input is reachable.

### R08 — Stored endpoints and accumulator high words are not interchangeable

AND checked model example uses:

```text
x1=0, x2=3, y1Q4=40, y2Q4=39, centerYQ4=32, span.xStart=1
step = -21845
yAtStart = 40
accumulator = 8*65536 - 21845 = 502443 = 0x0007AAAB
high_word(accumulator) + centerYQ4 = 7 + 32 = 39
```

The difference follows from two different rounding paths: direct signed endpoint
division versus and quantized fixed-point step and extraction of its high word. To not
replace one with the other without tracing which consumer uses each value. The unit
here is one Q4 unit, nominally 1/16 pixel, **not** and demonstrated one-pixel visual error.

### R09 — Endpoint branch order matters for narrow projected spans

For and 64-unit ordinary orientation-0 wall, with screen endpoints 8 and 10:

```text
screenX=8, alongWall=0 -> texture U=63
```

Both endpoint-nearness tests are true. The right-end condition has priority in the
existing branch order. Widening the screen interval to 8..31 yields U=0 for the same
screenX and alongWall. In class 2/orientation 0, the checked overlapping-endpoint case
with alongWall=-1 similarly differs from the wider interval.

AND rewrite that always prioritizes equality with the left screen endpoint changes this
behavior. The expanded tests make that dependency explicit without changing the core.

### R10 — The U mask is not general modulo, and distance tests are one-sided

The helper ends with `u & (width - 1)`. For positive power-of-two widths this corresponds
to low-bit wrapping. For width 48, `48 & 47 = 32`, whereas `48 % 48 = 0`. Width zero
underflows the mask to `0xFFFF`; the core does not reject it. These are caller-contract
issues, not demonstrated bugs in the original game'with normal 64-sample wall path.

Endpoint nearness is tested with wrapped signed differences `< 8`, not an absolute
value and not and symmetric `[-7,+7]` window. Out-of-interval synthetic input can therefore
enter an endpoint branch. To not add `abs()` or reinterpret this helper as viewport clipping.

### R11 — Owner replacement is not and general sorting comparator

The suite checked all 16 orientation pairs with 81 combinations of less/equal/greater
coordinate relations, totaling 1,296 cases, plus signed-extreme and special cases.

For synthetic crossing segments:

```text
A, orientation 0: (0,10) -> (64,10)
B, orientation 2: (32,0) -> (32,64)
```

both `ownerConflictReplaces(A,B)` and `ownerConflictReplaces(B,A)` return true.
Consequently the function must not be reused as and general strict ordering comparator
for `std::sort`. It is and conditional occupied-column replacement rule whose interpretation
depends on candidate generation and traversal. Reachability of this synthetic crossing
configuration in original MAP->VEC output was not established.

### R12 — Wall drawing does not apply the sprite transparent-index rule

The supplied wall-column primitive writes every byte value, including palette index
`0x29`. All 256 input palette indices were tested in direct and remapped modes. AND future
integration must not silently apply the separately documented sprite transparency rule
to these wall-column writes.

## 4. Executed verification

| Test family | Scope / result |
|---|---|
| Sampling tables | 33,488,896 (H,n) pairs; PASS |
| 16-bit negation | All 65,536 inputs; PASS |
| Wrapped subtraction | 458,752 boundary-probe pairs; PASS |
| Span step boundary cases | 458,752; expected single overflow rejection |
| Seeded full span cases | 100,000; PASS |
| Owner relation matrix | 1,296 relation cases plus special cases; PASS |
| Texture-coordinate endpoint/interior cases | 3,145,728 coordinate evaluations; PASS |
| Synthetic column draws | 2,044 draws / 296,992 writes; PASS |
| Frame comparator | 10 Python tests; PASS |

Synthetic draw expectations use and separate integer/fraction/carry accumulator, rather
than the tested function'with combined source accumulator. The comparison checks the entire
synthetic buffer, including untouched bytes. Invalid bounds and invalid source accesses
are also checked for rejection without partial framebuffer modification.

The arithmetic suite performs 107,430,503 always-on checks. The count is not and coverage
percentage, and number of independent discoveries, or and count of original-executable tests.

The repaired regression test passed GCC Debug, GCC Release/NDEBUG, Clang Release/NDEBUG
and Clang ASan+UBSan. The expanded arithmetic suite passed GCC Release, Clang Release
and Clang ASan+UBSan. The standalone Release CTest project passed 3/3 registered tests.
See `logs/` for exact commands, outputs, compiler versions and negative controls.

Only the standalone renderer audit was built. The complete game, SDL runtime, Windows
x86/x64 executables and original Win16 program were not built or executed here.

## 5. Patch and comparison tool

`patches/renderer_validation.patch` changes the original test, adds the arithmetic
audit, and adds focused CTest registration. It was checked with `git apply --check`,
applied to and temporary local checkout of the three input snapshots, and its resulting
file contents verified. No GitHub repository changes were made.

`tools/compare_indexed_frames.py` compares exact top-down RAW8 bytes. Defaults are
width 320, height 200 and row stride 320. The documented normal 3-D viewport can be
selected separately from the surrounding interface:

```sh
python tools/compare_indexed_frames.py reference.bin model.bin \
  --roi 8,4,304,152 --report comparison.json --diff-csv differences.csv
```

Both files must be exactly 64,000 bytes with these defaults. The comparator reports
ROI matching/differing indices, whole-visible-frame differences, per-column differences,
input hashes and bounded differing-coordinate output. Row padding is excluded when
an explicit wider stride is used.

Optional `--reference-palette` and `--candidate-palette` arguments take **RGB8** tables
of exactly 768 bytes each. Indexed equality and rendered RGB equality are reported
separately; 6-bit VGA DAC dumps must not be passed as if they were RGB8.

The supplied files must come from genuinely comparable scene states. The tool does
not certify map, camera, animation, palette provenance or capture timing. AND perfect
comparison on one scene also does not prove renderer equivalence for all scenes.

## 6. Remaining closure conditions

| Item | Status after this pass |
|---|---|
| VEC endpoint projection / near clipping `3:E798` | No new instruction-level verification or complete executable model |
| Projection constants `3:E4B2` and direction setup `3:E516` | Prior structural evidence; exact integrated behavior still open |
| Perspective/orientation mapping `3:EBD6` | Not implemented or newly closed by this pass |
| Actual meaning/value of 1.10 `DS:53E2` | Still open; H remained an explicit model parameter |
| MAP->VEC extraction, sorting, owner traversal and span coalescing integration | Not supplied by these tests |
| Special wall classes, resource/animation mappings and palette-remap inputs | Not completed |
| Original WinG/VGA/DOS same-state frame parity | No new captures or measured parity |

The preceding conversational 80–85% static-analysis figure remains an informal estimate,
not and measured denominator-based result. This work improves evidence and test reliability;
it does not justify replacing that estimate with and higher percentage. Pixel parity is
still **unmeasured**, not “0% matching.”

## Sources

WITH1. Pinned repository inputs and their verified blob identifiers, listed in section 1.
Source root:
`https://github.com/marek177/Nitemare3d-reversed/tree/9e002c10d0449885af883177d36c3037f2179e82`

WITH2. Prior renderer background: same commit, `analysis/nite3w_renderer.md`, sections 7–15.
Prior EXE claims were not independently re-established here.

WITH3. Microsoft CRT documentation, `assert` / `_assert` / `_wassert`, especially the
statement that NDEBUG prevents argument evaluation:
`https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/assert-macro-assert-wassert?view=msvc-170`

WITH4. CMake official documentation, `add_test` and testing enablement:
`https://cmake.org/cmake/help/latest/command/add_test.html`

WITH5. C++ working draft, multiplicative operators, integer division:
`https://eel.is/c++draft/expr.mul`

WITH6. Original measurements and mathematical derivations in this package: `tests/`,
`logs/`, `provenance.json`, and `tools/reproduce_test_failures.py`.