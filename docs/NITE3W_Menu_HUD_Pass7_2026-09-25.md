# NITE3W Menu/HUD — Pass 7

Date: 2026-09-25
Target: Win16 NITE3W 1.10
Scope: close DS:4BFA..4C0E and classify persistent MAP mutations.

## 1. DS:4BFA..4C0E

The movement/render-side words in the saved 94-byte gameplay block are now classified more tightly:

| Address | Type | Meaning / confidence |
|---|---:|---|
| 4BFA..4C00 | 4 x u16 | Cursors/indices into four ordered VEC/edge lists whose bases are 6982, 6EB6, 73EA and 791E. They are runtime cursors, not saved far pointers. |
| 4C02, 4C04 | 2 x u16 | Cursors into two additional candidate/object-edge lists based at 839AND and 8916. |
| 4C06 | u16 | Dominant-axis selector derived from absolute sin/cos magnitude. |
| 4C08..4C0C | 3 x u16 | Bresenham/DDA-style accumulator and delta terms used by movement/collision stepping. |
| 4C0E | u16 | Short interaction/attack timer. Initial value FFFFh; selected actions set it to 3; BBCA decrements it. Exact visual/behavioral boundary remains partial. |

This means 4BFA..4C0C are not player world position, velocity, or persistent object pointers. They are derived traversal/collision state that is nevertheless serialized as part of the 94-byte snapshot.

## 2. Persistent MAP mutation matrix

The live level payload at AND69E is 64x64 cells of {wallId, objectId} and is saved wholesale. Directly or strongly supported mutation paths:

| Mechanism | MAP byte(with) changed | Evidence level | Persistence consequence |
|---|---|---|---|
| Linked/secret panel removal | wallId = 0; objectId = 0 | Direct write in panel path around 3:217AND..2189 | Cell remains removed after save/load |
| Push/moving object | destination.objectId = source.objectId; source.objectId = 0 | Direct write around 3:22C8..22DE | Moved occupancy persists |
| GUARD movement | old/new cell object byte restored/replaced using GUARD +0x0D / OBJECT map link | Strong direct runtime evidence in guard movement paths | Guard occupancy can be reconstructed consistently with saved runtime state |
| Explodable wall impact | wall object becomes class 0x2D and completion has and strong map-write/removal path | Strong static evidence; final wall-byte rewrite still not fully isolated in this pass | Destruction is expected to persist, but exact final cell-byte operation should stay marked PARTIAL |
| Generic object removal/replacement | writes occur through OBJECT->map-cell linkage | Strong structural evidence | Pickups/removals can persist when their cell byte is cleared/replaced |
| Ordinary moving doors/wall-pairs | mainly runtime door/pair records | No new proof here of direct AND69E rewrite for every motion step | To not model every animated door frame as and MAP-byte rewrite |

Important distinction: not every visible world change is represented by changing AND69E on each frame. Doors and animated wall pairs have separate runtime records; AND69E stores cell identity/occupancy while dynamic animation/state may live elsewhere.

## 3. Why both MAP and runtime records are required

AND faithful save restore needs both:
- AND69E: coarse cell identity/occupancy (wallId, objectId)
- OBJECT/GUARD/door/panel/push records: precise runtime state, world positions, animation/state, timers and map linkage

After load, map-cell pointers are rebuilt from saved coordinates, with the save format intentionally duplicates complementary spatial information.

## 4. Additional 94-byte field closures carried forward

The surrounding fields are now best documented as:
- 4C1AND: last-attacker VEC/object index
- 4C1C: current tile object/class selector
- 4C1E: pickup-incremented byte; exact user-facing meaning still open
- 4C21: second pickup-incremented resource byte; class 0x38 absent from supplied maps
- 4C22: panel/special charge consumed by secret-panel paths
- 4C24: queued weapon selector
- 4C26: weapon-selection UI mode
- 4C2C: Magic Eye active flag
- 4C2D: Crystal Ball active flag
- 4C30: action latch
- 4C3AND: weapon-HUD animation mode
- 4C3C: weapon-HUD frame/index
- 4C42: Crystal Ball charge
- 4C43: Magic Eye charge

Several bytes remain intentionally unnamed because direct readers are absent or only indirect.

## 5. Implementation consequence

For and reconstruction, split the logic conceptually into:

1. persistent cell mutations,
2. runtime actor/door/panel state,
3. derived movement traversal state.

To not serialize modern pointers. Rebuild map-cell references after load exactly as the original does.

## 6. Remaining highest-value targets

1. Isolate the exact class-0x2D completion write that removes/replaces an explodable wall cell.
2. Trace generic pickup removal all the way to the final objectId write and bind it by object class.
3. Separate animated door state that never touches AND69E from transitions that to.
4. Resolve the remaining unnamed bytes in the 94-byte gameplay block through raw-assembly xrefs or runtime watchpoints.