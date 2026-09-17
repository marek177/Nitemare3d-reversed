# Nitemare 3D — E3M6 video audit

Source: user-supplied `Nitemare 3D Walkthrough by Hexkwondo! E3 L6.mp4`.

## Source integrity

- SHA-256: `fbc572b6a0602e1862d93edf29524a4553c51d5a4ff18c24be0d35eeca7fc26f`
- Duration: 861.135238 s
- H.264, 1920x912, 6963 video frames
- The source MP4 is evidence only and is intentionally not distributed in this repository.

## Confirmed / strengthened behavior

- Episode 3 uses multiple fire-hazard behaviors rather than one universal solid-fire behavior.
- Small fire is traversable and damages the player while crossing.
- Medium fire is also traversable but causes very severe health loss; this agrees with the original hint-book description that it is almost deadly.
- Large fire is the lethal/impassable class according to the original game documentation and is treated separately from the traversable classes.
- The practical E3M6 route therefore depends on hazard class, current health and exposure duration; collision code must not model all flames as solid walls.
- The walkthrough reinforces that fire damage is a gameplay hazard applied during traversal, not merely a decorative sprite effect.
- The level progresses into the Episode-3 crypt/hell visual area and finishes at the pentagram/control-panel exit area.

## Directly observed completion screen

- Level Completed: **6**
- Enemies Remaining: **18**
- Panels Not Found: **2**
- Bonus for Level: **0**
- Score so far: **25675**

## Reconstruction consequences

1. Keep an explicit fire-hazard classification (`Small`, `Medium`, `Large`).
2. Keep collision/passability separate from damage application.
3. Do not invent numeric damage-per-tick values yet; recover them from the original executable before marking damage timing 1:1.
4. Small and medium flames must permit player occupancy/traversal. Large flames must follow the original lethal/impassable behavior.
5. Integrate fire behavior with the future player-health/damage subsystem rather than hard-coding it into map rendering.

The evidence-bounded model is implemented in `src/game/HazardSystem.hpp`.

## Evidence status

- Fire class semantics: **video + original documentation supported**.
- Exact HP damage values: **unresolved**.
- Exact damage tick interval: **unresolved**.
- Exact object/wall IDs for every fire visual: **requires MAP/IMG/EXE cross-reference before declaring 100%**.

## Episode 3 video coverage after this audit

Audited/video-complete: **E3M1, E3M2, E3M6, E3M7, E3M8, E3M9, E3M10/Ending**.

Still requiring a full durable walkthrough audit: **E3M3, E3M4, E3M5**.
