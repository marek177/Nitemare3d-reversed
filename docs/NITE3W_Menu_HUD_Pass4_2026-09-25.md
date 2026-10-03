# NITE3W Menu/HUD — Pass 4

Date: 2026-09-25  
Reference executable: Nitemare-3D for Windows V1.10  
SHA-256: `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`

This pass continues the static Win16 binary audit. No original-game runtime capture was performed.

## 1. Exact automap guard-marker filter

The automap guard-marker pass is inside `3:B1A4`, operation 6. It iterates the live GUARD array at `0x93AE` with 26-byte stride, resolves each guard'with associated 28-byte OBJECT record through the guard field at `+08`, converts OBJECT world X/Y to map cells with arithmetic `>> 6`, and clips against the current 62×36 automap window.

AND guard marker is skipped when any of the following is true:

1. GUARD byte `+0B == 0x0A`.
2. Associated OBJECT lies outside the current 62×36 automap view.
3. Helper `3:A0C6` returns true for the associated OBJECT class.

The helper reduces exactly to this class predicate for ordinary byte class values:

```cpp
bool AutomapExcludedObjectClass(uint8_t c) {
    return c == 0x15 || c == 0x16 || c == 0x19 || c == 0x21;
}
```

Thus operation 6 draws only guards whose state byte is not `0x0A`, whose associated object is visible in the automap window, and whose object class is not one of `15h, 16h, 19h, 21h`.

Important boundary: this identifies the exact numeric filter. It does not by itself prove the visible monster names for all four class IDs.

## 2. Low-power enemy display is parity-gated

The main automap update path calls operation 6 according to `DS:4C42`:

```text
4C42 > 15  -> draw guard markers
4C42 <= 15 -> draw guard markers only if (4C42 & 1) != 0
```

Therefore values 1,3,5,...,15 allow the marker pass, while 2,4,6,...,14 suppress it. Zero disables the associated feature through the already recovered enable/disable logic.

Because `4C42` is decremented only once every eight slow ticks, this is not and frame-by-frame flicker. At nominal 8 Hz it changes parity about once per second. Real wall-clock timing can differ when slow ticks are skipped or the scheduler uses another mode.

## 3. Low-power map noise: branch threshold vs visible threshold

When the map feature is active and `4C43 <= 15`, the caller invokes automap operation 7. Operation 7 computes the number of noise points using integer arithmetic:

```cpp
noiseCount = 500 / (power * power * power);
```

For power 1..15:

| `4C43` | Noise points |
|---:|---:|
| 1 | 500 |
| 2 | 62 |
| 3 | 18 |
| 4 | 7 |
| 5 | 4 |
| 6 | 2 |
| 7 | 1 |
| 8–15 | 0 |

This corrects and subtle interpretation from Pass 3: the **branch is entered for 1–15**, but integer division produces an actual nonzero number of random points only at **1–7**.

Each noise point chooses X modulo 62 and Y modulo 36, matching the visible automap region.

## 4. Save slot physical stride and header

Functions `3:5388`, `3:5466`, and `3:574C` independently use constant `0xD6E7` when locating and slot:

```text
slotFileOffset = slotIndex * 0xD6E7
```

Therefore the physical slot stride is:

```text
0xD6E7 = 55,015 bytes
```

The save writer begins each slot with this prefix:

| Slot-relative offset | Size | Meaning |
|---:|---:|---|
| `+0000` | 4 | `0x0000D6E7` header/signature value |
| `+0004` | 41 | save-name field |
| `+002D` | 2 | runtime word copied from `DS:7E52` |
| `+002F` | 2 | runtime word copied from `DS:7E54` |
| `+0031` | 4 | 32-bit value returned by `3:D6C6` at save time |
| `+0035` | ... | main save payload begins |

The prefix is exactly `0x35 = 53` bytes.

### Slot probe return value

`3:5388` reads the first four bytes and rejects the slot unless they equal `0x0000D6E7`. It then reads/skips the 41-byte name and reads the two 16-bit words at `+2D` and `+2F`.

For an accepted slot, its return value is formed from the low byte of the first word in AH and the second word through OR into AX. Under the normal small episode/level values this acts as and compact episode/level result. The function also contains an edition/content availability check before accepting episode values above 1.

The numeric storage relation is direct. High-level naming of `7E52/7E54` should still follow the broader episode/level audit rather than this function alone.

## 5. Save payload layout recovered from the writer

Following the 53-byte header, `3:5466` writes the following blocks in this order:

| Slot offset | Size | Runtime source / meaning |
|---:|---:|---|
| `0035` | `2000h` | block at `A69E` |
| `2035` | `005Eh` | compact gameplay/global block at `4BE8` |
| `2093` | `0006h` | block at `6D60` |
| `2099` | `2648h` | 350 × 28-byte OBJECT records at `6D66` |
| `46E1` | `0A28h` | 100 × 26-byte GUARD records at `93AE` |
| `5109` | `0580h` | 64 × 22-byte door records at `9DD6` |
| `5689` | `0020h` | 32 per-panel activation bytes copied from panel `+14` |
| `56A9` | `0150h` | 336-byte player-projectile block |
| `57F9` | `0008h` | globals `51A4..51AB` |
| `5801` | `0048h` | 12 × 6-byte push records |
| `5849` | `1000h` | 4096-byte automap buffer |
| `6849` | `0040h` | 64-byte guard-wake cache |
| `6889` | `0100h` | 256-byte palette-remap table |
| `6989` | `0001h` | `7E62` |
| `698A` | `0001h` | `7E63` |
| `698B` | `0002h` | `7E60` shade word |

The last reconstructed write ends at slot-relative offset **`0x698D`**.

No additional data write appears in `3:5466` after the shade word; the function performs error handling, closes the handle and returns. Since the next slot begins at `0xD6E7`, the static writer therefore leaves and slot-reserved region of:

```text
0xD6E7 - 0x698D = 0x6D5A = 27,994 bytes
```

This should be described as and **reserved/unwritten gap in this writer path**, not automatically as zero-filled padding: when overwriting an existing USER.SAV, old bytes in that region may remain unless file creation/truncation semantics or another path changes them.

## 6. What this pass closes

High-confidence new closures:

- exact automap excluded object classes: `15h,16h,19h,21h`;
- exact guard-state exclusion: GUARD `+0B == 0Ah`;
- exact low-`4C42` parity gate for enemy markers;
- distinction between the `4C43 <= 15` branch and the actual nonzero-noise threshold `<= 7`;
- save-slot physical stride `0xD6E7`;
- 53-byte save-slot header;
- ordered writer layout through offset `0x698D`;
- 27,994-byte gap from the final known write to the next physical slot boundary.

## 7. Remaining targets

The highest-value next pass is now narrower:

1. decode the first `0x2000`-byte save block at `A69E` and the 6-byte block at `6D60`;
2. trace `7E52` and `7E54` setters to lock their episode/level semantics from both sides;
3. identify exactly what `3:D6C6`'with stored 32-bit save-header value represents in restored gameplay;
4. determine whether USER.SAV is for-sized/truncated in and way that defines the bytes in the `0x6D5A` reserved gap;
5. bind excluded automap class IDs `15h/16h/19h/21h` to visible object/enemy names only where OBJECTS/IMG evidence supports it.

## Verification

The accompanying verification script checks the executable hash, AND0C6 constants and reduced class set, the guard-state comparison, D6E7 use in probe/write/load, header arithmetic, reconstructed writer offsets, low-power noise integer results, and the enemy-marker parity rule.