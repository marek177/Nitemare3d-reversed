# Pass 71 — reciprocal-driven texture column scaler

## Finding
Confirmed across six distinct supplied DOS binaries: the reciprocal table drives a vertical texture-column sampler, with 16.16 source stepping, optional color-table translation and VGA-plane widening. An additional stack-byte dependency is directly reproduced. Supplied1.8/1.9 are identical. No complete renderer or hardware parity is claimed.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Reciprocal base is table_start−4; entry d is floor(0x400000/d) | Indexed load bytes, pass70 table and original execution | High |
| Confirmed | Source column offset is argument3*64 | Shift-left6 and runtime fixture | High |
| Confirmed | Source sample i is base+floor((phase+i*R)/65536) | All emitted source-derived values compared independently | High |
| Confirmed | Optional translation uses SS lookup table | XLAT SS and translated-value fixtures | High |
| Confirmed | Horizontal span expands for d>64 and x<=right argument, stopping before byte boundary | Mask construction and original execution | High for tested alignments |
| Confirmed | Local high byte BP−7 affects source offset/fraction selection | Full-word compare after low-byte initialization, stack-byte fixtures | High local observation |
| Unknown | Actual high-byte value at normal gameplay call sites | Whole-call runtime stack traces not captured | Do not claim game-visible instability |

## Behavior model
Use the original 16-bit arithmetic and signed comparisons. Compute d=wrap16(2*(input_y−center)+1). The normal branch (signed input_y < limit) places the top at input_y−d and emits d+1 rows. The other branch uses configured top and visible-row count. Valid d in these fixtures is1..511. The reciprocal R=floor(0x400000/d) supplies integer and fractional source increments. Source begins at far_texture_offset + column_index*64. Each output advances destination offset by80; y is truncated to8 bits for the initial offset, x is shifted right2. The routine always uses the page_zero segment.

For the cropped branch, a byte table indexed by d adds to source offset and a word table indexed by d initializes fractional phase. Every output stores the selected source byte, including zero; this routine has no transparency test. Nonzero shade argument maps each sample through a256-byte SS translation table. Original DS is restored at exit. The shade branch temporarily stores the integer source step in a global word; no reentrancy guarantee is inferred.

The VGA mask starts as rotate8(11h,x&3). For d>64 and signed x<=right argument, the normal branch tries to add one neighboring plane; cropped tries three. Rotation carry stops expansion at the plane-byte boundary. Return AX is the number of selected adjacent pixels (1..4 in these paths). No cross-byte duplicate is emitted by this local mask-expansion code.

## Stack dependency
Only byte BP−8 is initialized to0/1. The source-adjustment branch tests word BP−8 against zero, including BP−7, which is not initialized in the observed body. Horizontal expansion later tests only the low byte. Tests entering with high byte1 and normal low byte0 therefore select crop offset/phase while retaining normal row count and normal widening policy. This is Confirmed for the local function under the explicit synthetic stack precondition; caller reachability and practical effect remain Unknown. A reconstruction must preserve or explicitly resolve this precondition rather than silently adopting the decompiler's inferred local type.

## Verification
300 cases pass:50 per binary. Normal denominators1,3,31,65,511 × four x alignments × raw/shaded; cropped d101 × four alignments × raw/shaded; plus two normal-branch high-stack-byte fixtures. Assertions cover every destination address/value/size, exact sequencer mask, row count, DS restoration and AX span. Synthetic source bytes, clipping tables, translation tables and page segment are supplied; reciprocal values use the independently verified pass70 formula. Original scaler executes unchanged with no mocked calls. OUT is observed, CPU memory is flat; actual VGA planes/scanout are not modeled here.

## Locations and discovery limit
DOS1.9 entry1156:04ce; reciprocal indexed words DS2650/2652, center4550, limit454c, top454a, visible4544. Per-build entries/globals are in column_scaler_tests.json; input hashes remain in baseline specs. Fresh Ghidra exports include exact instructions and decompilation. Ghidra direct xrefs to table base did not expose the indexed reader; it was located by matching displacement bytes in supplied instruction listings and exporting its containing function. This is not an exhaustive indirect-consumer inventory. A separate ES-relative write using the same numeric displacement is not automatically a write to this DS table.

## Unknowns and next test
Trace scaler callers for valid d, geometry and stack BP−7; recover construction of clipping offset/fraction tables and color maps. Compare integrated source sampling, actual assets, depth decisions and VGA output in a controlled original render. Overall confidence High for measured local arithmetic/branches, incomplete for full renderer reachability, timing and parity.
