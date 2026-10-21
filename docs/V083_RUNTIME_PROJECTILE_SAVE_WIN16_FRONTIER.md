# V083 — remaining runtime and cross-build acceptance frontier

Date: 21 October 2026. Evidence consolidation, not a new runtime test.

## Projectile
The controlled DOS2 original runtime established one 0→1→2→0 projectile lifecycle. The E2M10 outer scheduler repeated-call backedge is statically verified, but natural stale-slot resurrection/ABA remains unobserved. Next capture must log slot index, generation/owner, state, x/y, deadline, writer IP, scheduler depth and RNG before/after every nested pool visit. Distinguish a true second pass from an IRQ between instructions.

## SAVE/LOAD
V064 established a DOS2 pre-first-update LOAD boundary for selected player scalars. V074 established two DOS2 fixed-length save records; Win16 uses a distinct format, with V065 confirming X/Y/yaw by causal mutation. The first post-LOAD full world/renderer frame, cache rebuild, RNG and projectile deadlines remain unclosed. Compare source slot, restored pointers, first scheduler pass, first image selection and framebuffer; do not equate scalar restoration with first-frame parity.

## Win16
V059/V065 prove bounded original Win16 SAVE/LOAD behavior, but they do not close the Win16 message loop, rendering and audio timing. Keep version-specific WinG palette mapping and OS callback interleaving separate from DOS contracts.

## Scope
Do not raise global full-parity percentages or label all classes/levels accepted on the strength of these bounded witnesses.
