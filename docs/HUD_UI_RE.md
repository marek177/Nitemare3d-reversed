# HUD / UIF.DAT reverse-engineering notes

Updated: 2026-09-22

This document consolidates the current HUD/UI findings from screenshots, gameplay video analysis, UIF.DAT work, and the recovered runtime globals. It intentionally separates confirmed observations from hypotheses that still need an EXE xref/runtime watchpoint.

## Screen organisation

The original Nitemare 3D screen is split into a 3D viewport plus a persistent lower status/HUD area. The lower area is not part of the world renderer and contains fixed-layout UI elements.

Observed HUD groups:

- player portrait / face state
- episode:level display
- score
- three numeric/stat bars at the left-center block
- current weapon icon
- player map-cell coordinates shown below the weapon icon, e.g. `3,36` and `16,47`
- inventory/key/card/pentagram icon grid
- right-most black rectangular panel

## Player coordinates

The small two-number field under the current weapon icon is a map position display, not a timer.

Observed examples include:

- `3,36`
- `16,47`

The values are consistent with tile/cell coordinates inside the 64x64 map rather than raw world-space X/Y. The runtime player coordinates are known at `0x4BF6` and `0x4BF8`; the remaining task is to trace the HUD draw function that converts them to the displayed cell pair and confirm the exact shift/divisor.

Status: **VISUALLY CONFIRMED**, conversion formula **PARTIAL**.

## Fixed layout

The HUD appears to use fixed screen-space rectangles rather than a dynamic layout system. Each icon slot and text/numeric field has a stable position across gameplay screenshots.

Expected implementation model:

```text
HUD background/frame
  -> portrait rect
  -> episode/level digits
  -> score digits
  -> stat bars/digits
  -> weapon icon rect
  -> coordinate digits
  -> inventory slots
  -> right-side panel
```

Exact pixel rectangles still need to be measured from original 320x200 captures rather than browser-scaled screenshots.

## Portrait / face state

The portrait changes with player condition. Gameplay captures show at least multiple health-dependent appearances, including a healthy face and visibly damaged states.

The likely implementation is a small discrete lookup table selected from health ranges, not a continuously generated effect.

Still to recover from EXE/UIF.DAT:

- exact number of portrait frames
- exact HP thresholds
- whether special non-health states exist (death, temporary pain flash, god/cheat state)
- UIF.DAT entry indices for each portrait

Status: **behavior visually confirmed**, exact state machine **UNKNOWN/PARTIAL**.

## Numeric fields

The HUD contains digit-based fields for:

- episode:level
- score
- stat values
- player cell coordinates

The visual style strongly suggests sprite/glyph blitting rather than a general proportional font. The code audit should search for a digit draw helper that accepts value, screen position, width/padding, and optionally a separator (`:` or `,`).

Status: **VISUALLY CONFIRMED**, exact UIF entry mapping **UNKNOWN**.

## Ammo/stat bars

The three left-center counters are displayed as numeric values beside horizontal or framed meter artwork. Known runtime ammo globals include:

- silver ammo: `0x4C1F`
- laser ammo: `0x4C20`
- wand ammo: `0x4C44`

Normal gameplay cap is 100. Silver/laser audited logic also has a signed-byte boundary at 127.

A HUD audit should determine whether the displayed values are read directly from these globals or copied through a cached HUD state.

Status: runtime values **VERIFIED_EXE**, HUD reader path **OPEN**.

## Weapon icon

The large weapon graphic changes according to active weapon selector `0x4C23`:

- 0: Single Shot Laser
- 1: Magic Wand
- 2: Silver Pistol
- 3: Continuous Laser
- `0xFF`: none/unset

The remaining task is to bind each selector to exact UIF.DAT graphics.

Status: selector **VERIFIED_EXE**, sprite indices **OPEN**.

## Inventory grid

The inventory area uses fixed icon slots. Known runtime bitmasks include:

- colored key mask: `0x4C28`
- ID-card mask: `0x4C29`
- pentagram mask: `0x4C45`

The four pentagram bits are already recovered:

- bit 0: Red
- bit 1: Green
- bit 2: Blue
- bit 3: Yellow

For ordinary keys/cards the exact per-bit color/card mapping still needs direct binding to door classes and the corresponding HUD slot graphics.

Status: bitmask globals **VERIFIED_EXE**, visual slot mapping **PARTIAL**.

## Right-side black panel

The large black rectangle at the far right of the status bar is consistently visible in captures. Its exact runtime purpose is not yet proven.

Do **not** currently label it as automap in source code without an EXE/UIF xref. Candidate uses to test include:

- automap/minimap display
- transient text/status messages
- reserved/unused UI viewport
- episode-specific display

The next audit should search for draw/copy calls whose destination rectangle falls inside this region and identify their callers.

Status: **UNKNOWN**.

## UIF.DAT audit targets

To move HUD/UI toward 95-100%, identify every UIF.DAT entry by dimensions and usage xrefs, especially:

1. status-bar background/frame
2. portrait frames
3. digits and separators
4. weapon icons
5. key/card icons
6. pentagram/special-item icons
7. bar/meter components
8. empty inventory slot artwork
9. any graphics whose dimensions match the right-side panel

The strongest method is to correlate each UIF entry with its blit destination in the EXE rather than assigning names by appearance alone.

## HUD draw-pipeline audit

Recommended xref/runtime procedure:

1. Find UIF.DAT loader and resulting image/pointer table.
2. Xref every UI image pointer into the main gameplay loop.
3. Group blits by fixed destination Y coordinate in the lower screen region.
4. Identify numeric digit helper(s).
5. Watch runtime globals `0x4BF6`, `0x4BF8`, `0x4C1F`, `0x4C20`, `0x4C44`, `0x4C23`, `0x4C28`, `0x4C29`, `0x4C45` while triggering HUD changes.
6. Determine whether HUD uses dirty flags/cached previous values or redraws all elements each frame.
7. Trace all writes/draws into the right-most panel rectangle.

## Current confidence estimate

- fixed HUD layout: ~95%
- coordinates field identity: ~95%
- weapon-selector logic: ~98%
- ammo source globals: ~100%
- inventory source masks: ~95%
- portrait health-state logic: ~60-70%
- UIF.DAT entry-to-widget mapping: ~50-70%
- right-side panel purpose: <50%
- HUD refresh/dirty-update strategy: <50%

The HUD subsystem should be one of the faster areas to raise above 90% once the UIF.DAT xrefs and gameplay HUD draw function are isolated.
