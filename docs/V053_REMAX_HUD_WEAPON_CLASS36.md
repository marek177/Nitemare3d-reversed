# Nitemare 3D RE MAX v0.53 — DOS HUD reindex and Win16 weapon-class 0x36 closure

**Date:** 19 October 2026

## Evidence boundary

This pass combines two recent original-static audits. It does not add a new original gameplay runtime capture.

## DOS 1.9 -> DOS 2.0 HUD dispatcher correction

The previous interpretation "DOS v2.0 added a new HUD algorithm at ID 9" was incorrect.

The corrected mapping is:
- IDs 0..3 retain their indexes;
- DOS v2.0 inserts a new action at **ID 4**;
- old DOS1.9 actions 4..8 become DOS2 actions 5..9.

The old DOS1.9 ID8 block and the new DOS2 ID9 block are both 73 bytes and retain the same local instruction structure after accounting for shifted data offsets and a relocated helper target.

### Inserted DOS2 action 4

The new ID4 obtains an attribute through a helper using constant 0x0C and then joins the same drawing tail as action 3.

The observed common drawing arguments correspond to the side-HUD region:
- x = 256;
- y = 162;
- width = 62;
- height = 36.

The exact resulting palette/color semantics are still open because the helper chain has not yet been fully reduced to final pixels.

## DOS2 damage signal -> HUD sequence

A nonzero result from the measured damage-processing helper writes `DS:417A = 3` before later HP/death guards.

The subsequent HUD branch produces the action sequence:

`4 -> 4 -> 4 -> 3`

for the static `DS:417A=3` case.

This is a local call-count consequence, not proof that the four calls equal four visible display frames.

## Win16 v1.10 class 0x36 weapon pickups

The high MAP IDs `0x25..0x28` are classified as object class `0x36` in the checked Win16 v1.10 data/logic path.

Their four variants map to ownership bits and ammo initialization:

| MAP high ID | variant | ownership bit | ammo set | ammo pool |
|---:|---:|---:|---:|---|
| 0x25 | 0 | 0x01 | 50 | laser/shared |
| 0x26 | 1 | 0x02 | 50 | wand |
| 0x27 | 2 | 0x04 | 50 | silver |
| 0x28 | 3 | 0x08 | 50 | laser/shared |

Variants 0 and 3 intentionally use the same laser/plasma ammunition storage in the checked code path.

The pickup path also updates ownership, weapon-selection state subject to its guards, clears the collected map/object marker and emits the class-specific event/sound path.

## Corrections and open work

The old decorative names associated with corresponding WALLS/IMG resources are not sufficient to classify these gameplay markers as mere scenery.

Still open:
- prove the equivalent DOS `map ID -> pickup` path rather than assuming Win16 identity;
- close the exact color/pixel output of DOS HUD action 4;
- reduce the far helper used by DOS action 9;
- runtime-observe the new DOS2 damage-HUD sequence;
- determine why the Win16 maps remove the corresponding high-byte markers.

No proprietary binary or data is included in the repository.
