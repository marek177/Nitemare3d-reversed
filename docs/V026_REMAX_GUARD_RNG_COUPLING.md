# v0.26 RE MAX — GUARD RNG/state coupling

v0.26 binds the known DOS v2.0 RNG callsites to GUARD/animation consumers only where the current evidence supports the association.

## Confirmed couplings

### 0x2478 — animation variant

The animation path uses `RNG & 7` with a rejection loop. This is important because one animation decision can consume a variable number of draws and shift the shared RNG stream.

### 0x525E — GUARD state 06 blocked-axis decision

When both axes are blocked:

- exactly one RNG draw is consumed;
- bit 0 set -> flip stored X direction;
- bit 0 clear -> flip stored Y direction;
- no second movement commit is performed.

### 0x58A7 — GUARD state 13 timer

Exactly one RNG draw feeds:

`timer = RNG % 80 + 8`

giving 8..87.

## Strong but not fully closed

The planner cluster:

- `5666`
- `56A6`
- `573F`

is bound to GUARD planner/timer-direction logic with STRONG confidence. The precise per-call consumer/order remains a runtime-trace target.

`85AD` is bound to damage/pain ordering with STRONG confidence, but its exact branch consumer remains to be closed by trace.

## v0.35 direct original-byte correction

The v0.26 list of **20** direct callsites was incomplete. The fingerprinted
DOS v2.0 unpacked image contains **22** occurrences of the direct far-call
opcode to `0FBA:01A0`. The missing sites `8860` (damage `RNG&7`)
and `886C` (damage `RNG&15`) are reachable from the original 23-entry
class jump table at `882E`. `887C` handles `RNG&31` for classes `11..14`.
These branches are class-specific and each executes one RNG call if reached.

All **22 direct opcode sites** now have an instruction-local consumer binding
in `N3DV026GuardRngCoupling.hpp`:
- `5582`: GUARD state 7/8 conditional activation; `RNG%8` writes timer,
  then state 1;
- `B276`: projected OBJECT variant `RNG&7`; can repeat until an
  accepted descriptor entry, independently of the SPAN `2478` consumer;
- `9C98/9CC2/9D6E/9F0C/9F36`: class-specific sound selector arithmetic;
- `9A68/9A77`: two sequential scene-effect position values;
- `9FE3/A047`: resource selector `RNG%7` with resource-byte rejection;
- `A12B`: effect timer `RNG%240+160`;
- `85AD` and GUARD planner sites retain their prior STRONG semantic or
  ordering evidence where not fully closed.

**Important:** `CONFIRMED` in this table refers to immediate disassembled
instructions and operands, not actual runtime entry, enemy visible-name
identity or global ordering. Absence of `Unassigned` entries does NOT imply
the full behavior or all RNG aliases are proven.

The branch `CMP SI,7; JE retry` after `IDIV 7` in `9FE3/A047` is
provably unreachable for the known unsigned 15-bit RNG result. The *separate*
retry when a resource-table byte is zero remains reachable in principle.

See [v0.35 evidence and tests](V035_REMAX_RNG_22_CALLSITE_CENSUS.md).

## Why this matters for DEMO parity

The RNG stream is shared across AI, animation, damage and other systems. A single extra draw changes every later result.

The closure criterion remains:

1. start from DEMO seed 1;
2. record every direct RNG caller in order;
3. validate state_before/state_after/result;
4. bind the consumer;
5. identify the first unexpected/missing draw.

v0.26 provides the static coupling registry needed for that comparison.
