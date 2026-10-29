# Projected-height record producer — pass39

## Finding
720 original interpolation-producer executions recover the source of span increment and starting accumulator. 696 complete and24 intentionally extreme cases fault on signed division overflow. Two direct callers per image link this producer to span preparation, but ordinary gameplay record reachability remains unverified.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Producer writes18-byte record fields+4,+8,+a,+e | V1.9 1201:001a–012c; original calls and independent arithmetic oracle | High |
| Confirmed | Increment is signed16.16 endpoint slope | V1.9 0038–004a | High |
| Confirmed | Initial accumulator adjusts for record's clipped left x and baseline | V1.9 00f6–0126 | High |
| Confirmed | Two direct callsites in span preparation | V1.9 1201:017d/01d5; catalog in producer.json | High static |
| Unknown | Tested endpoint combinations occur in actual scenes | Synthetic endpoint tests; no full scene traversal | Unresolved |

## Behavior model
Analytical args: near record, x0,y0,x1,y1 (five16-bit words). Let dx=s16(x1-x0), dy=s16(y1-y0), L=record.word2, R=record.word6, baseline=viewport center shifted4 (V1.9 DS4552). div truncates toward zero; s32 wraps products and sums.

```
slope = div(s32(dy << 16), dx) if dx != 0 else 0
if dy == 0:
    leftY = rightY = y0
    accumulator = s32(s16(y0-baseline) << 16)
elif dx == 0:
    leftY, rightY = y0, y1
    accumulator = s32(s16(y0-baseline) << 16)
else:
    leftY = s16(y0 + div(s32(s16(L-x0)*dy), dx))
    rightY = s16(y0 + div(s32(s16(R-x0)*dy), dx))
    accumulator = s32((s16(y0-baseline)<<16) + s32(s16(L-x0)*slope))
```

Store leftY at+4, rightY+8, slope dword+a, accumulator dword+e. The renderer consumes high word+10 before incrementing dword+e by+a (pass38). Nonzero slopes are thus explicitly produced by original preparation arithmetic; this is stronger than a manually supplied increment, but it does not by itself prove a particular scene produces the approximation witness.

## Verification
`/usr/bin/python3 scripts/verify_height_producer.py` with Unicorn2.x. Six images × six endpoint-x pairs × five endpoint-y pairs × four clipped-left offsets =720. Baseline1280; record right=left+9. Tests include zero width, flat/rising/falling interpolation, reversed endpoints, clipping/extrapolation and16-bit extremes. Complete producer executes without mocks; checks four output fields, far return, stack and DS. Overflow example dx=-1,dy=-32768 traps IDIV; exception hook stops before DOS handling.

Direct-call catalog is a static supplemental extraction in producer.json; rerunning the emulator script regenerates dynamic evidence and function bodies, not that supplemental catalog. Original EXE hashes and Ghidra12.2 instruction bodies included. No project database edits. Supplied1.8/1.9 share one EXE. No real scene/VGA/DAC or full-game parity claim.

## Implementation-ready findings
Preserve endpoint-difference wrapping, signed16.16 slope, clipped-left accumulator adjustment and distinct dx0/dy0 branches. Using integer endpoint interpolation alone is insufficient: the accumulator separately multiplies truncated fixed slope, which can differ in rounding.

## Unknowns and next test
Execute span preparation callsites through producer and consumer together using controlled per-column ownership data. Trace actual endpoint producers and their bounds. Establish real scene slopes/assets before claiming the pass38 approximation is observed during gameplay. Menu limits remain open.

## Confidence
High for producer arithmetic and static preparation links; actual scene reachability unresolved.
