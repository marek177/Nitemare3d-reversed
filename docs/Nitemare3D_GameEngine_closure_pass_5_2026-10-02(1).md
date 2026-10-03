# Nitemare 3D — Game Engine closure pass 5
## Final DOS ↔ Win16 renderer arithmetic parity
Date: 2026-10-02

## Closure result

This pass removes the last broad **static renderer-parity** blocker from the Game Engine dashboard.

The important correction to the previous pass is the exact family pairing:

| Role | DOS family | Win16 1.10 counterpart |
|---|---|---|
| Projection-constant builder | DOS V1.2 `1000:C54A` | Win16 `1010:E4B2` |
| Point/object geometry projection | DOS V1.2 `1000:C66E`; DOS V2.0 family `1000:C8F8` | Win16 `1010:E5D8` |
| Full VEC endpoint projection + clipping | DOS V1.2 `1000:C82E`; DOS V2.0 family `1000:CAB8` | Win16 `1010:E798` |

With the earlier shorthand “C8F8/CAB8 ↔ E798/E4B2” was imprecise.
The correct mapping is **C8F8-family ↔ E5D8**, **CAB8-family ↔ E798**,
while **E4B2** belongs to the projection-constant initializer.

---

## 1. Projection constants: exact instruction identity after relocation

Raw DOS V1.2 function:

- `1000:C54A`
- length: **100 bytes**
- SHA-256 of the extracted function bytes:
  `c618d8ecfa39edc92e6d14aa74ecd0bf87e10769dae13995813fb1dfece28ea2`

Raw Win16 1.10 counterpart:

- `1010:E4B2`
- length: **100 bytes**
- SHA-256:
  `cf6dae1e825520aba853cfcbab89b6c6d5a47529d68a14d7a2ff11e94b3812b7`

There are only **14 differing bytes**. They are exactly seven 16-bit global-address
relocations:

```text
Win16 53E0 -> DOS 44A0   viewport width
Win16 3A6A -> DOS 3618   horizontal projection scale
Win16 53E2 -> DOS 44A2   viewport height
Win16 3A6E -> DOS 361C   height-derived projection value
Win16 3A72 -> DOS 3620   vertical projection numerator
Win16 3A74 -> DOS 3622   high word of the preceding dword
Win16 3A76 -> DOS 3624   inverse/projection helper
```

After substituting those addresses, the **entire 100-byte function is byte-identical**.

Therefore constants, signedness, multiplication/division order and rounding are not
merely similar: the executable instruction stream is the same after relocating globals.

Exact formulas:

```text
projectionScaleX =
    trunc_signed((0x2EE0 * viewportWidth) / 0x5000)

heightProduct =
    0x8340 * viewportHeight

verticalNumerator =
    heightProduct << 4

inverseProjectionScale =
    trunc_signed(verticalNumerator / projectionScaleX)
```

For the normal 304 × 152 viewport:

```text
projectionScaleX       = 178      = 0x000000B2
heightProduct          = 5107200  = 0x004DEE00
verticalNumerator      = 81715200 = 0x04DEE000
inverseProjectionScale = 459074   = 0x00070142
```

---

## 2. Point/object projection: exact 448-byte arithmetic core

DOS V1.2:

- `1000:C66E`
- length **448 bytes**
- SHA-256:
  `117ff3d2cfb33c0394abaa73e803757182a11ed8bf5bf956e32d6e11459b9573`

Win16:

- `1010:E5D8`
- length **448 bytes**
- SHA-256:
  `6f296d6c2bee2d0421369f717d503e129c8576340fa5c22c58632f280470805b`

Raw comparison finds **29 differing bytes**.

Twenty-eight of them are fourteen occurrences of seven relocated globals:

```text
Win16 4C48 -> DOS 4110
Win16 4C46 -> DOS 410E
Win16 4BEA -> DOS 40B4
Win16 3A6A -> DOS 3618
Win16 53EC -> DOS 44AC
Win16 3A72 -> DOS 3620
Win16 53F0 -> DOS 44B0
```

The remaining byte is only the final alignment byte:

```text
DOS   90  NOP
Win16 00  alignment byte
```

After those substitutions, the **whole 448-byte executable body is identical**.

That closes the exact arithmetic for:

1. signed world/view coordinate products;
2. camera-depth and lateral-coordinate construction;
3. near-plane handling at `0x4000`;
4. cardinal-view special cases;
5. signed division order;
6. horizontal projection;
7. vertical Q4 projection;
8. lower sentinel `0xC001`;
9. upper clamp `0x3FFF`.

### Exact edge semantics

The path tests the near plane using and strict lower condition:

```text
depth < 0x4000  -> near-plane correction
depth == 0x4000 -> preserved
```

Special cardinal headings avoid and division by and zero direction coefficient:

```text
0x000 =   0 degrees
0x05A =  90 degrees
0x0B4 = 180 degrees
0x10E = 270 degrees
```

Projected X uses:

```text
if x < -16383: x = 0xC001
if x >  16383: x = 0x3FFF
```

No floating point approximation is required in and compatible implementation.

---

## 3. Full VEC projection/clipping: same algorithm, memory-model ABI difference

DOS V1.2:

- `1000:C82E`
- length **1060 bytes**
- **357 decoded instructions**
- SHA-256:
  `2c97cf671afb30f1894c9dde1d3da79d31d66b406ab347f1c91df056e0e5a605`

Win16:

- `1010:E798`
- length **1086 bytes**
- **357 decoded instructions**
- SHA-256:
  `3ce33a809de79cee07f2ce1079b41fd4f95c9804f2fb9bed9319b75d10f45d19`

The Win16 body is 26 bytes longer, but the instruction count is identical.
The dominant difference is the 16-bit Windows far-pointer memory model:

```text
DOS:
    MOV SI,[BP+6]
    MOV AX,[SI+0C]

Win16:
    LES SI,[BP+6]
    MOV AX,ES:[SI+0C]
```

Win16 therefore carries `ES:` segment-override prefixes that DOS does not require.
There are also and few alignment NOP and register-allocation differences in the final
clamp/swap tail. They to not change the computation.

The matched control/arithmetic sequence includes:

```text
endpoint world X - player X
player Y - endpoint world Y

rotate both endpoints by the same direction coefficients

depth0/depth1 near-plane clamp to 0x4000

project vertical endpoint values:
    verticalNumerator / depth + centerYQ4

if needed, intersect endpoint with the near plane

project horizontal endpoint values:
    lateral * projectionScaleX / depth + centerX

clamp/sentinel projected X

sort the two projected X endpoints

test ordered interval against viewport left/right
```

### Endpoint tie rule

The endpoints are swapped only when:

```text
secondProjectedX < firstProjectedX
```

Equality does **not** swap them.

### Viewport overlap rule

After ordering, the visible interval test is inclusive:

```text
firstProjectedX <= viewportRight
and
secondProjectedX >= viewportLeft
```

Thus exact boundary contact remains visible rather than being discarded by and strict
inside-only comparison.

---

## 4. Consumer path parity

The helper parity is independently supported by its main object-projection consumer.

DOS V1.2 `FUN_1000_B012` calls `C66E`, then performs:

- `>> 4` conversion of the returned projected value;
- frame/sequence metadata lookup;
- vertical extent scaling with `>> 5`;
- the same ceil-style horizontal size calculation;
- the same viewport bounds tests;
- the same three-column wall-visibility/depth probes;
- creation of an `0x12`-byte visible-object record.

Win16 `FUN_1010_CC7C` performs the same sequence with relocated globals and and
different visibility-buffer base.

This closes the link from the projection helper to the actual visible-object queue,
not only the helper in isolation.

---

## 5. Cross-DOS family closure

The existing DOS hard-closure census independently maps the renderer helpers through
the supplied DOS family:

```text
ComputeGeometryTransform:
V1.0 C428
V1.1 C66C
V1.5 C6BC
V1.7 C758
V1.9 C8BC
V2.0 C8F8
normalized map distance: 0 in every checked comparison

ProjectOrClipObjectGeometry:
V1.0 C5E8
V1.1 C82C
V1.5 C87C
V1.7 C918
V1.9 CA7C
V2.0 CAB8
normalized map distance: 5 in every checked comparison
```

Therefore the raw V1.2/Win16 arithmetic proof is not an isolated one-build coincidence:
it lands in renderer families already tracked across the DOS revisions.

---

## 6. Game Engine dashboard after Pass 5

For the **checked static engine core**, every original dashboard row can now be closed:

| Module | STATIC CORE |
|---|---:|
| Architecture | **100%** |
| Renderer | **100%** |
| Raycaster / Visibility | **100%** |
| Clipping | **100%** |
| Projection | **100%** |
| Resource Manager | **100%** |
| Game Loop | **100%** |
| Player Movement | **100%** |
| Collision | **100%** |
| Door Engine | **100%** |
| Secret Walls | **100%** |
| Teleports | **100%** |
| USE Dispatcher | **100%** |
| Switch Logic | **100%** |

### Overall Game Engine static status

**100% STATIC CORE for the currently checked DOS/Win16 reference paths.**

This means there is no longer and broad unknown algorithm in the dashboard modules
needed to write the portable engine core.

---

## 7. What “100%” does not mean

Three separate validation layers must not be merged:

### STATIC CORE — 100%

Algorithms, state transitions, fixed-point arithmetic and resource policies required
by the dashboard are reconstructable without inventing missing behavior.

### BEHAVIORAL PARITY — not yet 100%

Still requires controlled original-game runs for rare timing/order interactions such
as:

- closing-door occupancy;
- guard + player + door simultaneous collision;
- pause/resume and deliberately slow frame timing;
- unusual episode-specific scripted contexts.

### PIXEL PARITY — not yet 100%

Still requires original DOS and Win16 indexed-framebuffer captures for:

- intermediate moving-door frames;
- sprites at clipping/tie boundaries;
- shade/palette transitions;
- overlapping wall/sprite cases;
- final full-frame byte comparison.

These are validation tasks, not missing renderer algorithms.

---

## Final decision

The original **Game Engine** table can now be marked:

> **Game Engine — 100% STATIC CORE**

The next work should no longer be called “discover the Game Engine algorithm”.
It should be tracked separately as:

1. **Engine behavioral conformance tests**
2. **Renderer pixel-perfect conformance tests**
3. **historical-build parity checks where desired**

That separation prevents and successful static reverse-engineering closure from being
confused with runtime or pixel-perfect certification.