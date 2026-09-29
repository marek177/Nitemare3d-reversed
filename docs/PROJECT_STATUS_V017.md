# Nitemare3D-Reversed v0.17 — runtime integration

Date: 2026-09-29

v0.17 moves already verified reverse-engineering results into the normal runtime headers.

## Source changes

- `src/game/CombatSystem.hpp`
  - executable-backed class × weapon resistance transform for classes 0x0C..0x1F;
  - Hamerstein special gate;
  - player-damage difficulty transform;
  - 255 high-end clamp.

- `src/game/GuardSystem.hpp`
  - positive-hit receiver result: ignored / pain / lethal;
  - non-lethal resoct=8 behavior;
  - explicit Dracula phase-2 reset constants.

- `src/game/ObjectSystem.hpp`
  - named predicates for verified OBJECT property bits;
  - unresolved 0x20/0x40 bits remain deliberately unnamed.

- `src/game/ProjectileRuntime.hpp`
  - explicit guard-collision/impact decision around the verified ±9 proximity test;
  - impact state value exposed without inventing lifetime semantics.

- `src/renderer/OriginalRendererFacts.hpp`
  - separates executable-backed sprite queue layout from behavioral-only
    directional/vertical sprite-selection observations.

## Evidence discipline

The v0.15 behavioral observations are not promoted to executable truth here.
No directional sprite formula or Bat vertical-motion formula is implemented
until the actual original selector/writer path is recovered.

## Regression target

`n3d_v017_runtime_integration_test` cross-checks the resistance matrix,
difficulty scaling, guard receiver, Dracula reset, OBJECT flags and projectile
collision decision.
