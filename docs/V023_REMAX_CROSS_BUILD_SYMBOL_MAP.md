# v0.23 RE MAX — cross-build behavior/symbol map

v0.23 introduces a behavior-oriented symbol registry.

The goal is to stop treating matching offsets as evidence of matching behavior. A behavior ID can now have one symbol per build, each with its own address and confidence.

## Initial DOS v2.0 symbols

The map includes confirmed DOS v2.0 anchors for:

- special-wall lookup;
- object-by-tile lookup;
- paired-wall runtime construction/state/motion;
- player USE;
- door auto-close;
- map-object activation.

`1000:0E50` remains present only as an OPEN moving-object/runtime candidate.

## Initial Win16 v1.10 symbols

The map includes confirmed Win16 symbols for:

- GUARD state dispatcher `3:7B55`;
- GUARD pain-return handler `3:807E`;
- HUD dispatcher `3:A3B6`;
- automap dispatcher `3:B1A4`;
- menu/save dispatcher `4:27DE`.

## Cross-build pairing rule

A behavior is considered a confirmed cross-build pair only when:

1. both builds have an address;
2. both entries are CONFIRMED.

For example, the DOS v2.0 GUARD dispatcher at `1000:59F0` is currently STRONG while Win16 `3:7B55` is CONFIRMED, so the pair is intentionally not promoted to CONFIRMED parity yet.

Missing equivalents are stored as unresolved rather than guessed.

## Why this matters

Earlier reverse-engineering notes contain valid addresses from different builds, but copying those offsets across versions caused several false assumptions. The v0.23 map makes the intended workflow explicit:

`BehaviorId -> build-specific symbol -> confidence -> evidence`

The next step is to extend the registry using exact/strong fuzzy matches and runtime fingerprints, especially for USE, wall motion, GUARD states, player collision and projectile lifecycle.
