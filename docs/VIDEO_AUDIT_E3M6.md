# Nitemare 3D — E3M6 video audit

Source: user-supplied `Nitemare 3D Walkthrough by Hexkwondo! E3 L6.mp4`.

## Scope

This audit records behavior that can be supported by the supplied walkthrough. It does not assign original numeric damage, timing or AI constants unless those values are separately recovered from `NITE3W.EXE`.

## Confirmed / strengthened behavior

- Episode 3 uses multiple visually distinct fire hazards rather than one universal fire tile behavior.
- Small fire is traversable and damages the player while crossing.
- Medium fire is also traversable but causes very severe health loss; this agrees with the original hint-book description that it is almost deadly.
- Large fire is the lethal/impassable class according to the original game documentation and is treated separately from the traversable classes.
- The practical E3M6 route therefore depends on hazard class, current health and exposure duration; collision code must not model all flames as solid walls.
- The walkthrough reinforces that fire damage is a gameplay hazard applied during traversal, not merely a decorative sprite effect.

## Reconstruction consequences

1. Add an explicit fire-hazard classification (`Small`, `Medium`, `Large`).
2. Keep collision/passability separate from damage application.
3. Do not invent numeric damage-per-tick values yet; recover them from the original executable before marking damage timing 1:1.
4. Small and medium flames must permit player occupancy/traversal. Large flames must follow the original lethal/impassable behavior.
5. This behavior should be integrated with the future player-health/damage subsystem rather than hard-coded into map rendering.

## Evidence status

- Fire class semantics: **video + original documentation supported**.
- Exact HP damage values: **unresolved**.
- Exact damage tick interval: **unresolved**.
- Exact object/wall IDs for every fire visual: **requires MAP/IMG/EXE cross-reference before declaring 100%**.
