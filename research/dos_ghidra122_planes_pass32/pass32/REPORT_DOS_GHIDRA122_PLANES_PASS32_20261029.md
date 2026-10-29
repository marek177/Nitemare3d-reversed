# VGA map-mask and group boundary — pass 32

## Finding
3,840 original scaled-column executions match the expected OUT port sequence and all bytes of a four-plane map-mask model. A local xLimit comparison enables grouping but does not clamp its end: x=0, xLimit=0, clipped index151 selects four columns and emits mask ff.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Routine outputs sequencer index2 at port3c4, duplicated-nibble group mask at3c5 | V1.9 1156:055b–0595; all test port traces | High |
| Confirmed | Lower four mask bits select the expected write planes | Original OUT + write events applied to explicit model; complete plane-byte comparison | High for stated model |
| Confirmed | xLimit is checked once before group growth, no per-column end clamp | V1.9 1156:0574–0593; 864 tested grouped cases extend past supplied limit | High locally |
| Unknown | Real caller ensures space for groups; complete VGA device and scanout equivalence | Not tested | Unresolved |

## Behavior model
For tested x>=0, i>64 and signed x<=signed xLimit, group=min(clipped?4:2,4-(x&3)); otherwise group=1. Let L=((1<<group)-1)<<(x&3). Original mask byte is L|(L<<4). The map-mask model uses its lower nibble to select planes; every memory write updates selected planes at the original offset, leaving all other bytes unchanged.

Example V1.9, width304, y155, i151, x0, limit0: return AX4; OUT3c4 byte2 then OUT3c5 byteff;152 row writes are replicated to all four planes. This demonstrates local behavior, not a proven visible gameplay defect. Limit semantics at callers remain unresolved; the analytical name xLimit should not imply a strict clip boundary.

## Verification
Run `/usr/bin/python3 scripts/verify_scaled_column_planes.py` with Unicorn2.x. Six distinct images × one viewport width304 × five y offsets31/32/75/76/200 × x0..7 × translation0/1 × limit offsets-1/0/1/3 × source offsets0200/ffc0 =3,840. The original reciprocal initializer, full setter and consumer execute with no callee mocks. Every test verifies memory address/value sequence, AX, DS/SP/far return, exact two OUT events and all four 64KiB plane arrays against an independently constructed expectation. Plane initial fill a5. Source-pointer arithmetic wraps at16 bits. Synthetic LUT inverts byte values.

This is a scoped VGA sequencer map-mask model. It does not model graphics-controller latches/write modes, chain4, memory mapping registers, DAC, display start, scanout or timing. Thus it advances plane-write evidence but does not establish full framebuffer/DAC parity. Preserved Ghidra12.2 exports supply locations; no project database edited. Supplied1.8/1.9 EXEs are identical.

## Implementation-ready findings
Preserve duplicated-nibble mask emission and lower-four plane selection. Preserve the initial signed limit guard and four-pixel plane-boundary stop; adding a per-column xLimit clamp would change local behavior. Verify caller contracts before treating this as a bug to fix.

## Unknowns and next test
Trace direct callers and their final argument: determine whether it is a last drawable x, grouping threshold or a guaranteed safe batch boundary. Verify real VGA setup before extending this model to framebuffer parity. Menu bounds remain unresolved.

## Confidence
High for local ports, masked model writes and group behavior; complete VGA hardware and gameplay results remain unknown.
