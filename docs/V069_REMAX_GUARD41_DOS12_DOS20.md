# Nitemare 3D RE MAX v0.69 — GUARD41 DOS1.2/DOS2 comparison

**Date:** 19 October 2026

This pass adds two new original-runtime checkpoints and a version-data comparison around GUARD41.

## DOS1.2 after state0A

A new natural DOS1.2 run reaches the already closed state09 epilogue and then the next confirmed outer scheduler checkpoint. The 26-byte GUARD41 record is unchanged across that boundary:
- state remains 0x0A;
- HP remains 0.

A byte change later in the 64-byte window belongs to the following GUARD record, not GUARD41.

This closes one immediate post-state0A checkpoint but does not prove long-term cleanup/drop behavior.

## DOS2 natural dead GUARD41 state

Two separate natural DOS2 DEMO sessions provide an early and a later WORLD/GUARD checkpoint. In the later checkpoint GUARD41 is observed with:
- state 0x0A;
- HP 0;
- linked object index unchanged.

This proves that the original DOS2 DEMO route naturally reaches a dead GUARD41 state. The two snapshots are not one uninterrupted death trace, so the exact DOS2 HP-to-zero writer, death RNG, score/map cleanup and any drop remain open.

## Version/data context

DEMO.1 is byte-identical between the compared full DOS distributions. MAP.1 differs in 46 bytes, all in high bytes of cells; E1M11 differs at only four high-byte positions while all 4096 low bytes match. OBJECTS.1 differs in source-name text on 28 rows while corresponding IDs/class marks/descriptions stay aligned. EXE and IMG.1 differ.

Therefore identical DEMO input bytes do not by themselves imply identical runtime RNG/resource behavior across DOS1.2 and DOS2.

## Later bounded DOS2 evidence

The 2026-10-20 [post-death integration](DOS20_GUARD41_POSTDEATH.md) records reported original DOS2 00→09 and 09→0A writers, RNG #19 and state9 epilogue entry. Separate natural captures still do not establish the full uninterrupted fatal-to-state0A timing interval.
