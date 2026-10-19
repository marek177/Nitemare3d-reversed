# Nitemare 3D RE MAX v0.56 — recent-days evidence frontier consolidation

**Date:** 19 October 2026

## Purpose

This release is a consolidation checkpoint after exhausting the currently available high-value findings from the recent evidence bundles that were not yet represented in main.

It intentionally contains **no new global completion percentage**. The point is to preserve what is now closed, what is only controlled/static, and what still requires original-vs-port acceptance.

## Recent evidence now represented in the repository

The version chain v0.49→v0.56 now includes:

1. clean-room Linux portability fixes and SDL3 smoke evidence;
2. DOS1.2 DEMO RNG through the GUARD41 lethal branch;
3. a complete bounded GUARD41 death outcome through score +100 and map marker clear;
4. Win16 WinG laboratory startup through rendered E1M1 in all five tested builds;
5. DOS2 random-event timer RNG branch with exact state/result/countdown writes;
6. controlled DOS2 projectile free→flying→impact→free lifecycle;
7. E2M10 repeated outer-scheduler static backedge and conditional stale-slot/ABA model;
8. DOS1.9→2.0 HUD action reindex and the inserted DOS2 action4;
9. Win16 v1.10 class36 weapon pickup mapping for MAP high IDs 0x25..0x28;
10. 31-level cross-build marker census and controlled E1M1 A/B visual effects;
11. Win16 v1.10 236-vs-256 managed-palette rule;
12. DOS DEMO seed-helper / reader / last-record static narrowing.

## Explicit remaining frontier

The following remain OPEN and should block any claim of strict 100% parity:

- complete DEMO RNG ledger across all later draws/records and exact EOF transition;
- natural E2M10 second/nth projectile-pool visits proving or disproving stale resurrection/ABA;
- projectile→GUARD damage/SFX and all FB/FD/FE lifecycle variants;
- first post-LOAD frame including RNG/deadline/cache/pointer rebinding and short-I/O behavior;
- canonical 64,000-byte indexed framebuffer + palette zero-diff against the original;
- Win16 movement/USE/door/RNG/scheduler timing parity across all five builds;
- active audio/PCM/OPL/MIDI event and waveform/timing parity;
- full end-to-end scenario matrix original vs clean-room port.

## Evidence discipline

A static opcode match, a controlled runtime branch, a clean-room unit test and a strict original-vs-port zero-diff test are different evidence classes.

The versioned C++ evidence headers deliberately preserve these distinctions. Open booleans in `N3DV056FrontierStatus.hpp` are guardrails against accidentally promoting local closure into a global parity claim.

## What to do next

New GitHub releases should now be driven only by a genuinely new closure:
- natural runtime reachability;
- a newly closed original-static caller/writer graph;
- a cross-build semantic delta with verified consequences;
- or an original-vs-port differential acceptance result.

Repackaging already integrated facts should not increase the version number or parity percentage.
