# v0.27 RE MAX — projectile lifecycle evidence graph

v0.27 consolidates the projectile runtime into one build-scoped lifecycle graph.

## DOS v2.0 anchors

- allocation: `0800:7EDE`
- secondary init: `0800:7F96`
- movement/collision: `0800:8142`
- scheduler: `0800:8230`
- render/projection: `0800:B2D4`

The DOS path confirms the 8-slot, 42-byte pool and state transition from active flight into impact.

## Win16 v1.10 anchors

- allocation/template init: `1010:9AAC`
- movement setup: `1010:E516`
- small-step movement: `1010:9D30`
- collision test: `1010:9B64`
- flight/impact animation: `1010:9E20`
- projection/cache write: `1010:CC7C`
- save/load: `1010:5466`, `1010:574C`

The Win16 evidence closes the composite 42-byte record and the lifecycle:

`Free(0) -> Flying(1) -> Impact(2) -> Free(0)`

## Confirmed invariants

- 8 slots
- 42-byte stride
- embedded 28-byte OBJECT at +0x0E
- guard collision tolerance effectively +/-9 on both axes
- impact sets embedded OBJECT flag bit 0x10
- state lifecycle 0->1->2->0

## Strong but not yet implementation-safe

### Newly spawned projectile moves on following tick

Static scheduler ordering strongly indicates projectile update runs before input/FIRE allocation, so a projectile allocated by the current FIRE event starts moving on the next update. This still needs a one-tick runtime trace.

### Full pool preserves ammo

Win16 static flow checks for a free slot before calling the ammo helper. This is STRONG, not promoted globally across all builds.

### Stale projection cache

Embedded OBJECT projection/cache fields around +0x18/+0x19 may survive slot reuse and participate in damage. This remains one of the most important projectile edge-case experiments.

## Remaining closure work

- exact wall vs object vs GUARD collision ordering;
- multi-GUARD scan behavior;
- dynamic door/secret-wall collision timing;
- pool-full behavior in DOS v2.0;
- stale projection-cache refresh rules;
- exact impact-animation deadline timing;
- cross-build pairing of each lifecycle phase.
