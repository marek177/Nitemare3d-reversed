# Nitemare 3D RE MAX v0.46 — runtime acceptance sync

Date: 18 October 2026.

## Evidence boundary

This release synchronizes the newest DOSBox-X evidence into main. It separates natural runtime, controlled runtime, static opcode evidence and bounded reconstructed contracts. It does not claim complete original-vs-port parity, complete DEMO determinism, framebuffer zero-diff or audible audio zero-diff.

Primary build fingerprints:
- DOS v2.0 packed N3D.EXE: a3fa02335e1d8bc531918f3bfaa66217aef65c81e562a2fdf1c749be652ca485
- DOS v2.0 unpacked N3D-UNFU.exe: 552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301
- DOS v1.2 unpacked N3D-12.exe: f7074660ed26525d2cc5ccd16a6e5ac011f29aaf819dc8ca24ebe39f0fd793e5

## PASS16 scheduler boundary

A natural DOS2 E1M1 run captured one scheduler invocation at four boundaries:

C24B before PROJECTILE -> C250 after PROJECTILE -> C26F before INPUT -> C274 after INPUT.

The sampled 8x42-byte projectile pool was unchanged across these dumps while the clock advanced. A short CPU trace caught IRQ execution on the PROJECTILE call boundary before entry to the callee, so exact compatibility code must not assume IRQ can occur only after projectile processing.

PASS16 also corrects PASS15 alias attribution: DS:012D/012F/081E and WORLD:586D/586F/5F5E are physical aliases in the measured layout, not independent GUARD/OBJECT writes.

## GUARD PASS17-PASS22

The original DOS2 runtime now has bounded witnesses for a substantial AI path:

07 -> 02 -> 00 -> 03 -> 04 -> 00/05 -> 06 -> 03.

PASS17 observed real state00 timer underflow 0000 -> FFFF. PASS18 observed state04 damage: Frankenstein/class09 changed player HP 100 -> 86 (14 damage), then Mummy/class0A changed 86 -> 82 (4 damage), each with one RNG draw.

PASS20 closes an important timing detail: state05 is not initialization-only. The strategy planner itself sets state06 and calls movement once. In the measured pair timer FFFF -> 8; Frankenstein moved 2784 -> 2776 in state05. Eight later state06 visits reduced timer 8 -> 0 and returned each measured record to state03.

PASS21/22 close the selected double-block branch. With state06 and both X and Y blocked, the original calls RNG once: odd output negates vx and even output negates vy. A separate controlled run reached this branch from the original state05 planner without modifying GUARD or RNG state; one state05 update consumed one planner RNG draw and then a second collision-bounce RNG draw.

These are scoped runtime closures, not all-class GUARD parity.

## Weapons runtime

Original DOS1.2 and DOS2 now both have runtime witnesses for keyboard weapon selection through the ownership mask, pending/commit/raise, correct hitscan/projectile mode, pistol ammo consumption, held FIRE with Multi Plasma and the shared plasma pool for weapon IDs 0 and 3.

In one fixed-12000 test sequence, held Multi Plasma changed plasma ammo 60 -> 37; switching back to Single Plasma retained 37. This is an environment-scoped witness, not a universal rate.

## RNG/palette

A natural DOS2 run captured RNG seed 1 -> 0x0029E2C0, return 41, and the consumer 41 % 240 + 160 = 201. The same path reached live VGA DAC index writes for 0xEB and 0xE3. Palette/effect code must therefore be included in the global RNG ledger.

## Shutdown runtime

The shutdown matrix now includes an observed no-XMS configuration where missing XMS is non-fatal and guarded XMS cleanup is skipped.

A configuration-reachable digital shutdown branch executed INT63 AH=0D music stop, AH=07 digital stop and AH=04 digital IRQ restore, followed by restoration of the saved IRQ7/INT0F vector. The sampled digital stop was idle; the active DSP/DMA sub-branch was not executed.

## Remaining P0

- Complete DEMO seed=1 RNG chronology.
- Active projectile FB-FE spawn, movement, impact, damage, cleanup and nested pool reentry.
- E1M9 Skeleton/Dancers accepted-hit lifecycle.
- SAVE/LOAD first post-load frame and error/short-transfer behavior.
- Exact scheduler/IRQ reentry beyond bounded traces.
- 64,000-byte indexed framebuffer plus live palette zero-diff.
- Win16 runtime parity and active WORX/PCM/OPL/SB timing.

No original commercial executable or data asset is distributed by this release.
