# Nitemare 3-D sprite/object spatial behavior audit

Date: 2026-09-27  
Release target: v0.15

## Scope

This note preserves new behavioral observations about sprite placement, view-dependent variants and collision without promoting them prematurely to executable-verified facts.

## Evidence boundary

The findings in this document are currently **BEHAVIORAL** unless explicitly stated otherwise. The exact Win16/DOS instruction paths that select vertical placement, directional sprite variants and per-object blocking flags still need to be recovered.

## 1. Vertical sprite placement classes

Observed game content requires more than a single "sprite stands on floor" rule.

At minimum the reconstruction must allow:

- floor-anchored sprites;
- mid-height sprites;
- ceiling-associated / ceiling-anchored sprites;
- unresolved/custom placement.

This is relevant to both decorative OBJECTs and GUARD rendering.

The existing OBJECT render/spatial fields around `OBJECT+14/+16/+18` remain candidates for part of this behavior, but only `OBJECT+18` currently has a directly verified executable read as a projected/view-space vertical baseline in the player-to-GUARD damage path. Do **not** rename those fields as vertical-anchor fields without writer-level evidence.

## 2. Bat behavior

Behavioral observation:

- Bat is not presented like a normal floor-attached GUARD.
- Its visible position is associated with the upper/ceiling region.
- During attack behavior its wings animate.
- It can remain approximately in place horizontally while moving vertically up/down over a limited range.

Reconstruction consequence:

- Bat must support an animated vertical offset/oscillation independent of ordinary floor-grounded GUARD movement.
- This should not yet be hard-wired to a guessed OBJECT/GUARD offset until the executable path is traced.

Status: **BEHAVIORAL**.

## 3. View-dependent object variants

Some non-GUARD OBJECTs visibly change sprite according to player viewing direction.

Observed example:

- bed front view;
- bed side view.

This establishes at least a two-variant directional object case. It does not prove that every such object uses exactly two views, nor that it uses the same octant selector as GUARD sprites.

Reconstruction consequence:

- object rendering needs a view-selection mode separate from ordinary animation;
- minimum model should support Fixed, Directional2, Directional4, Directional8 and Animated/Unknown modes.

Status: **BEHAVIORAL**.

## 4. Solid / blocked objects

Some decorative or environmental OBJECTs are impassable and participate in player collision.

This should remain a separate property from sprite anchor and view mode. A sprite may be floor/mid/ceiling anchored independently of whether it blocks movement.

Status: **BEHAVIORAL**, with executable flag/dispatcher mapping still open.

## 5. v0.15 code representation

`src/re/N3DV015SpriteFacts.hpp` records these observations conservatively:

- `VerticalAnchor`;
- `ViewMode`;
- `SpriteBehavior`;
- Bat behavioral fixture;
- Bed behavioral fixture.

The regression test ensures these facts remain explicitly marked as behavioral and are not silently upgraded to `VERIFIED_EXE`.

## 6. Next executable-analysis targets

1. Find writers/readers of `OBJECT+14/+16/+18` in sprite projection and placement.
2. Trace object-definition flags controlling solidity/blocking.
3. Find the selector for non-GUARD directional object frames.
4. Compare that selector with GUARD octant/resoct logic.
5. Locate Bat-specific state/class branches controlling vertical offset.
6. Recover vertical amplitude, cadence, bounds and attack-state coupling.
7. Determine whether ceiling/mid-height placement is table-driven, flag-driven or sequence-driven.
8. Cross-check DOS and Win16 implementations for the same spatial model.
