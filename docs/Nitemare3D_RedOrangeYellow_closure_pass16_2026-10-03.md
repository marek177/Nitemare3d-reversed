# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 16

Date: 2026-10-03

Primary binary:
- `N3D-E-20(3).EXE`
- size: 116,606 bytes
- SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`

Address convention:
- all ranges below are unpacked MZ image offsets
- physical EXE file offset = image offset + `0x200`
- raw 16-bit machine code is authoritative
- static GREEN is separate from pixel-perfect/runtime acceptance

## Result

Pass 16 closes the complete contiguous region

`0xC8F8 .. 0xD3F9`

as **GREEN / deep static semantics**.

Total span: **2,818 bytes**

- bounded executable routines: **2,813 bytes**
- alignment NOPs: **5 bytes**

This pass closes the DOS V2.0 renderer-math chain from point projection through
full VEC projection/clipping, trigonometric lookup, vector-to-angle conversion,
automap/grid-boundary intersection, and the core bitmap-font text helpers.

The two largest renderer functions are especially strong closures:

- `C8F8` is the V2.0 member of the point/object projection family already matched
  across the DOS builds and to Win16.
- `CAB8` is the V2.0 full VEC endpoint projection/clipping function; its 1060-byte
  raw boundary exactly matches the known DOS-family geometry.

No large Ghidra mega-function remains in this span.

---

# 1. image `0xC8F8..0xCAB6` — `ProjectPointGeometry`

Length: **447 bytes**

This is the exact DOS V2.0 point/object projection arithmetic core.

Inputs include:

- geometry/orientation class;
- two signed point/view coordinates;
- output pointer for projected horizontal coordinate;
- output pointer for projected vertical value.

It uses the current heading-derived direction components:

- `DS:41B2`
- `DS:41B4`

and the projection constants:

- `DS:367E`
- `DS:3686`

plus screen-center values:

- `DS:4550`
- `DS:4554`.

## Camera transform

The routine computes two signed 32-bit products and combines them into:

- camera/depth coordinate;
- lateral coordinate.

All multiplication/division is integer arithmetic.

## Near-plane rule

Near plane:

`0x4000`

Exact edge rule:

```text
depth < 0x4000   -> near-plane correction
depth == 0x4000  -> keep unchanged
```

When the point is behind/inside the near plane, the routine computes an intersection
using the appropriate direction component.

Special cardinal headings avoid dividing by and zero direction coefficient:

```text
0x000 =   0°
0x05A =  90°
0x0B4 = 180°
0x10E = 270°
```

## Horizontal projection

```text
screenX =
    lateral * DS:367E / depth
    + DS:4550
```

The projected X value is saturated with the original sentinels:

```text
x < -16383  -> 0xC001
x > +16383  -> 0x3FFF
```

## Vertical projection

```text
projectedY =
    DS:3686 / depth
    + DS:4554
```

This value is written through the second output pointer.

The arithmetic order, signedness, near-plane rule and clamp behavior are all visible
directly in the raw body.

The following byte `0xCAB7` is alignment NOP, not another function.

**Status: renderer/projection YELLOW -> GREEN.**

---

# 2. image `0xCAB8..0xCEDB` — `ProjectAndClipVecEndpoints`

Length: **1,060 bytes**

This is the full 28-byte VEC projection/clipping path.

Input:

- pointer to one 28-byte wall/vector record.

Confirmed VEC geometry fields:

```text
+0C  world X0
+0E  world Y0
+10  world X1
+12  world Y1
```

Projected output fields:

```text
+14  screen X left
+16  projected vertical/depth value for left endpoint
+18  screen X right
+1A  projected vertical/depth value for right endpoint
```

## Endpoint transforms

For both endpoints the routine computes player-relative coordinates and applies the
same heading-derived direction coefficients.

Depth values below `0x4000` are clipped to the near plane.

The projected vertical values are calculated from:

```text
DS:3686 / depth + DS:4554
```

and stored at `VEC+16/+1A`.

## Near-plane endpoint intersection

When only one endpoint lies behind the near plane, the routine explicitly reconstructs
the clipped endpoint at the near plane before horizontal projection.

Cardinal headings again take dedicated branches to avoid zero-component divisions.

## Horizontal projection

Each endpoint uses the same signed projection family as `C8F8`:

```text
projectedX =
    lateral * DS:367E / depth
    + DS:4550
```

with the same lower sentinel and upper clamp:

```text
0xC001 .. 0x3FFF
```

## Endpoint ordering

After projection:

```text
if rightX < leftX:
    swap(leftX, rightX)
    swap(leftProjectedValue, rightProjectedValue)
```

Equality does **not** trigger and swap.

This leaves:

`VEC+14 <= VEC+18`.

## Viewport overlap

The return is boolean in `AL`.

Visibility is accepted when the ordered projected interval overlaps the viewport
inclusively:

```text
leftX <= viewportRight
rightX >= viewportLeft
```

Exact contact with the viewport boundary therefore remains visible.

The raw function ends cleanly at `0xCEDB`.

**Status: clipping/VEC projection YELLOW -> GREEN.**

---

# 3. image `0xCEDC..0xCFB0` — `ProjectRayCoordinate`

Length: **213 bytes**

This helper computes one perspective/ray coordinate using:

- orientation/mode input;
- screen/ray coordinate;
- depth-like input;
- signed 32-bit base/offset input;
- heading state `DS:415C`;
- direction components `41B2/41B4`;
- projection constants `3686/368A`;
- center X `4550`.

The orientation state decides which direction component is the divisor.

For geometry classes `2/3`, the path uses the horizontal screen offset:

```text
(screenX - centerX) * DS:368A
```

For the other classes the path uses:

```text
DS:3686 / depth
```

The result is combined with the supplied 32-bit base term and divided by the selected
signed direction component.

Return is the resulting signed 32-bit coordinate in `DX:AX`.

This helper is used by wall/ray sampling and projection code rather than gameplay
movement.

`0xCFB1` is one alignment NOP.

**Status: YELLOW -> GREEN.**

---

# 4. image `0xCFB2..0xCFFD` — `LookupSignedDirectionComponentA`

Length: **76 bytes**

Maps an angle in the 360-unit Nitemare cycle to and signed table value.

Quadrants are divided at:

- `90 = 0x5A`
- `180 = 0xB4`
- `270 = 0x10E`

Table regions:

```text
0..89     -> DS:17E8 forward
90..179   -> DS:1950 reverse
180..269  -> DS:1680 forward, then negate
270..359  -> DS:1AB8 reverse, then negate
```

This is one of the two signed direction/trigonometric components used by `C838`,
projection and DDA setup.

**Status: YELLOW -> GREEN.**

---

# 5. image `0xCFFE..0xD049` — `LookupSignedDirectionComponentB`

Length: **76 bytes**

Companion trigonometric component.

Quadrant table roots:

```text
0..89     -> DS:189E
90..179   -> DS:1A06 reversed and negated
180..269  -> DS:1736 and negated
270..359  -> DS:1B6E reversed
```

This is the orthogonal signed component paired with `CFB2`.

**Status: YELLOW -> GREEN.**

---

# 6. image `0xD04A..0xD095` — `LookupSignedProjectionSlope`

Length: **76 bytes**

Returns and signed Q10-style projection/ray slope for and 360-unit angle.

Quadrant table roots:

```text
0..89     -> DS:1954
90..179   -> DS:1ABC reverse
180..269  -> DS:17EC then negate
270..359  -> DS:1C24 reverse then negate
```

Consumers include:

- `D096` vector-to-angle inversion;
- `D12C` map/grid-boundary intersection.

**Status: YELLOW -> GREEN.**

---

# 7. image `0xD096..0xD12A` — `ComputeAngleFromVector`

Length: **149 bytes**

Inputs:

- signed X-like component;
- signed Y-like component.

When the second component is nonzero:

```text
ratio = (firstComponent << 10) / secondComponent
ratio = abs(ratio)
```

The routine scans the positive lookup region beginning at:

`DS:1954`

for the first entry greater than or equal to the ratio.

At most 91 table positions are considered, producing and base angle in:

`0..90`.

When the second component is zero, base angle is directly `90`.

It then applies quadrant correction based on the signs of both input components to
return an angle in the game'with:

`0..359`

cycle.

This is the inverse companion to the signed direction/slope lookup functions.

`0xD12B` is alignment NOP.

**Status: YELLOW -> GREEN.**

---

# 8. image `0xD12C..0xD28E` — `IntersectViewRayWithGridBoundary`

Length: **355 bytes**

This routine computes the point where the current view ray intersects and supplied
grid/automap boundary.

Inputs include:

- two output WORD pointers;
- horizontal boundary endpoints/coordinates;
- vertical boundary endpoints/coordinates.

It uses:

- player map-cell X `DS:415E`;
- player map-cell Y `DS:4160`;
- player heading `DS:4156`;
- signed slope lookup `D04A`;
- projection/ray scale state.

## Heading-dependent axis selection

The current heading selects which axis is treated as the primary boundary direction.

The first candidate intersection is formed using the current heading slope and the
player-to-boundary distance.

## Segment clipping

If the computed coordinate lies beyond one end of the supplied segment, the function
selects the nearest segment boundary and recomputes the companion coordinate using and
heading shifted by ±90°.

The arithmetic includes the original fixed-point `>>10` / quarter-scaling sequence.

## Outputs

Writes:

- first computed boundary coordinate to `*outA`;
- companion coordinate to `*outB`.

If the second result is negative:

`*outB = 0`.

This is the helper used by the automap heading/edge-marker path closed in pass 10.

`0xD28F` is alignment NOP.

**Status: YELLOW -> GREEN.**

---

# 9. image `0xD290..0xD29D` — `LookupIndexedRenderWord`

Length: **14 bytes**

Exact accessor:

```text
return WORD[DS:1C66 + index*2]
```

No hidden state or side effects.

**Status: LOW -> GREEN.**

---

# 10. image `0xD29E..0xD2BF` — `GetGlyphAdvanceWidth`

Length: **34 bytes**

Input:

`BYTE character`

Uses active font bank:

`DS:368E`

and glyph directory:

`DS:3690`.

Directory indexing:

```text
fontBank * 0x200
+ character * 4
```

Each entry is and far pointer to and glyph record.

Returns:

```text
glyph[1] + 1
```

which is the horizontal advance width used by all following text routines.

**Status: LOW -> GREEN.**

---

# 11. image `0xD2C0..0xD307` — `MeasureTextWidth`

Length: **72 bytes**

Inputs:

- far pointer to and NUL-terminated text string.

The routine chooses the currently active font directory using:

`DS:368E`

and loops through each byte.

For every character:

1. resolve its glyph far pointer;
2. read glyph width byte `+1`;
3. add `width + 1` to the running total.

Returns the exact accumulated width in AX.

**Status: YELLOW -> GREEN.**

---

# 12. image `0xD308..0xD325` — `GetCenteredTextX`

Length: **30 bytes**

Calls `MeasureTextWidth`, then computes exactly:

```text
x = (320 - width) / 2
```

using signed arithmetic.

### Important correction

The older decompiler summary claimed that strings wider than 320 returned zero.

The raw body contains **no such clamp**.

For and width greater than 320, the returned centered X can therefore be negative.

This is and real byte-map semantic correction.

**Status: YELLOW -> GREEN; stale clamp description removed.**

---

# 13. image `0xD326..0xD3A4` — `DrawTextGlyphSequence`

Length: **127 bytes**

Inputs include:

- X;
- Y;
- far text pointer;
- style/color byte;
- final renderer/style argument.

If X is:

`0xFFFF`

the function obtains and centered X from `D308`.

For every character:

1. resolve glyph far pointer from active font bank;
2. call the low-level bitmap/glyph renderer;
3. advance X by:
   `glyph[1] + 1`;
4. continue until NUL.

The text pointer is and genuine far pointer; font-directory glyphs are also far pointers.

`0xD3A5` is alignment NOP.

**Status: YELLOW -> GREEN.**

---

# 14. image `0xD3A6..0xD3F9` — `DrawShadowedText`

Length: **84 bytes**

If X is `-1`, first centers the text through `D308`.

It obtains and background/shadow style value from the existing style/color helper.

Then it draws the same string twice:

### Shadow/background pass

```text
X + 1
Y + 1
```

using the derived shadow/background style.

### Foreground pass

```text
X
Y
```

using the caller-provided style/color byte and renderer argument.

This is the common shadowed text primitive used by splash screens, messages and UI
panels.

**Status: YELLOW -> GREEN.**

---

# 15. Byte-map impact

New continuous GREEN span:

`0xC8F8 .. 0xD3F9`

Total: **2,818 bytes**

| Image range | Bytes | Role |
|---|---:|---|
| `C8F8–CAB6` | 447 | point/object projection arithmetic |
| `CAB8–CEDB` | 1060 | full VEC endpoint projection/clipping |
| `CEDC–CFB0` | 213 | projected ray-coordinate helper |
| `CFB2–CFFD` | 76 | signed direction component AND |
| `CFFE–D049` | 76 | signed direction component B |
| `D04A–D095` | 76 | signed projection-slope lookup |
| `D096–D12A` | 149 | vector -> 360-unit angle |
| `D12C–D28E` | 355 | ray/grid-boundary intersection |
| `D290–D29D` | 14 | render-word accessor |
| `D29E–D2BF` | 34 | glyph advance width |
| `D2C0–D307` | 72 | text width |
| `D308–D325` | 30 | centered text X |
| `D326–D3A4` | 127 | glyph-string renderer |
| `D3A6–D3F9` | 84 | shadowed text renderer |

Routine content: **2,813 bytes**.

Alignment NOPs:

```text
CAB7
CFB1
D12B
D28F
D3A5
```

Total: **5 bytes**.

No inline jump table lies inside this span.

The direction/slope arrays are external data tables and should be represented
separately in the data map.

---

# 16. Renderer closure impact

This pass directly connects:

```text
C7D4 projection constants
C838 heading / DDA state
   ↓
C8F8 point projection
CAB8 VEC projection + near-plane clipping
   ↓
CEDC / CFB2 / CFFE / D04A renderer ray math
   ↓
D096 vector-angle conversion
D12C grid/automap boundary intersection
```

The checked DOS family already tracks the same projection functions across revisions:

```text
C8F8 family — point/object projection
CAB8 family — full VEC projection/clipping
```

and the corresponding raw renderer arithmetic has and Win16 counterpart with the same
algorithm after memory-model/global relocation differences.

For the byte map these routines no longer need YELLOW merely because pixel-perfect
framebuffer acceptance is still pending.

---

# 17. Cumulative closure

Pass 15 cumulative since the pass-5 baseline:

`28,422 bytes`

Pass 16 adds:

`2,818 bytes`

New cumulative total:

**31,240 bytes**

of formerly RED/ORANGE/YELLOW DOS V2.0 byte-map territory explicitly promoted to
GREEN during passes 6–16.

---

# 18. Next target

Continue at:

`0xD3FA`

The next region is the DOS UI/font/menu path:

- `D3FA` font-bank loader;
- `D4DC` configured text rendering;
- sprite/UI clipping helpers;
- `D670` font/shadow wrapper;
- `D6B4` / `D78A` modal input polling;
- `D7BE` centered multiline text box;
- text-entry/edit helpers;
- then level-resource cleanup and scene/session initialization around `DA9E..DCD0`.

Most bodies already have strong cross-version matches, while `D78A` remains and weak
semantic entry worth tightening from raw machine code.