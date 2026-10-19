# Nitemare 3D RE MAX v0.74 — DOS2 two-slot USER.SAV record structure

**Date:** 19 October 2026

A natural DOS2 E1M1 continuation saves two different gameplay checkpoints into two slots and then loads the second slot before the first gameplay update.

Key observed facts:

- one slot record is 54,758 bytes;
- a two-slot USER.SAV is 109,516 bytes = 2 × 54,758;
- each record begins with dword 54,758;
- the slot name begins at record+4;
- saving slot1 leaves the entire original slot0 record byte-identical.

This is direct evidence that, for the tested DOS2 first two slots, records are concatenated fixed-size units and writing the second record does not rewrite the first.

The second slot stores a later gameplay state. On LOAD, stopped at the main-update entry before the first gameplay update, live DS matches slot1 for the already identified fields:

- HP = 6;
- ammo = 15;
- score = 325;
- X = 2020;
- Y = 3035;
- angle = 270.

The known scalar offsets are therefore stable relative to record base for both slot0 and slot1 in this tested file.

The gameplay sequence also naturally reaches score 325 and a visible Frankenstein encounter, but the many missed shots and ongoing damage prevent deriving enemy HP or exact damage cadence from this run.

Open: more than two slots, other levels/episodes/builds, complete record layout, RNG/world/projectile restoration and the first executed post-load update.
