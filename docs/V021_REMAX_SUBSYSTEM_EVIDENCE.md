# v0.21 RE MAX — subsystem evidence map

v0.21 adds a build-scoped subsystem evidence layer for DOS v2.0.

## Purpose

The project already knows many concrete routine addresses, but the remaining parity work depends on comparing runtime traces without accidentally converting an address hypothesis into a behavioral claim. This layer centralizes those addresses with confidence labels.

## Encoded subsystem anchors

- GUARD loop/state dispatcher: `5F26`, `59F0`
- player movement/collision: `6914`, `6378`, `6488`
- projectile scheduler/movement: `8230`, `8142`
- action/FIRE path: `89A2`, `8F12`
- secret-panel update: `0AEA`
- projectile render/projection: `B2D4`
- OBJECT runtime candidate: `0E50` — remains OPEN

## Encoded runtime regions

- projectile pool: `DS:41B6`, size `0x150`
- GUARD pool base/stride anchor: `DS:264E`, `0x1A`
- secret-panel record: `34F6`, `0x0E`
- SPAN pool: `4D6E`, `0x38E`

## Relative-order verification

The new helper can test only a local invariant when both addresses are present in a captured trace.

Example target:

`8230 projectile scheduler` before `89A2 action dispatcher`.

This is intentionally different from claiming the complete FAST/MAIN scheduler order.

## Confidence boundary

- Projectile-before-FIRE order: STRONG.
- Exact OBJECT mutation/deactivation order: OPEN.
- Exact FAST/MAIN subsystem interleaving: OPEN.

The next evidence step remains a one-tick DOSBox-X trace. v0.21 makes that trace easier to classify and compare against the current static model.
