# Nitemare 3-D — Episode 3 Level 3 reconstruction/video-audit status

Date: 2026-09-17

Source walkthrough located in the supplied Library: `Nitemare 3D Walkthrough by Hexkwondo! E3 L3(1).mp4`.

## Evidence status

The E3M3 walkthrough was the last Episode 3 level without a dedicated audit record. In this pass the level has been cross-correlated against two independent original/data-derived sources:

1. the original Episode 3 `HINTS3.TXT` route description;
2. the MAP.3/OBJECTS.3/WALLS.3-derived catalogue.

The current tool runtime could locate/materialize the MP4 but could not reliably seek/sample its frames, so this document does **not** invent timestamps, completion-screen values or direct visual observations. A literal frame-by-frame video pass remains the only unfinished part of the E3M3 audit.

## Confirmed E3M3 map/data identity

The MAP-derived catalogue confirms:

- player start: **(7,5)**, facing North;
- Red key object `0x05`: **(27,17)**;
- Green key object `0x06`: **(36,30)**;
- Blue key object `0x07`: **(4,62)**;
- Yellow ID-card object `0x0A`: **(62,46)**.

These coordinates independently match the intended progression documented by the original hint file.

## Confirmed intended progression

The original Episode 3 hint data documents this route:

1. Leave the initial room, head South through two sets of double doors and progress by shooting out red doors.
2. Reach the red door at **(22,31)**.
3. Reach another red door at **(25,40)**; blasting it reveals the fiery-dog themed area.
4. Collect the **Green key at (36,30)**.
5. Continue until another shootable red door reveals the fiery-monkey themed area.
6. Return to the double doors at **(8,10)**, enter the chapel with the Green key and ascend the log stairs.
7. Collect the **Red key at (27,17)**.
8. Return to the fiery-monkey branch and collect the **Yellow ID card at (62,46)**.
9. Progress through the red-key section; a second explicitly documented Red-key door is at **(2,58)**.
10. Collect the **Blue key at (4,62)**.
11. Reach the log stairs at **(24,51)** and ascend.
12. Pass the **Blue-key door at (59,5)** to reach the Transportation Booth.

## Reconstruction consequences

E3M3 is strong MAP/HINT evidence for the following reusable systems:

- chained shootable/explodable barrier progression;
- themed wall/door transitions (fiery dog / fiery monkey sections);
- persistent multi-colour key inventory;
- repeated use of the same Red key at more than one lock in one level;
- Yellow ID-card acquisition as separate inventory state from coloured keys;
- stair-warp progression;
- final Blue-key lock leading into the Transportation Booth route;
- deliberate backtracking: key acquisition opens a previously visited branch instead of only linear forward progression.

The repeated Red-key use is especially important for the reconstruction: coloured keys must be represented as persistent permissions/inventory flags, not consumed as one-shot items when a matching door is opened.

## Source-code integration

`src/game/Episode3LevelData.hpp` records only evidence-backed E3M3 coordinates and object IDs. It intentionally does not encode unverified combat numbers or guessed video timestamps.

`tests/episode3_level_data_test.cpp` protects the core E3M3 pickup/lock coordinates from accidental regression.

## Remaining direct-video work

To close E3M3 as a literal video audit, still extract from the MP4:

- source SHA-256 / exact duration / reported frames;
- timestamps for key pickups and key-use messages;
- stair selector presentation;
- Transportation Booth/green-transition frames;
- completion screen: enemies remaining, panels not found, bonus and score;
- any enemy/SFX/weapon behavior not derivable from MAP/HINT data.

Until that pass is completed, E3M3 should be described as **MAP/HINT reconstruction-audited, direct MP4 frame audit pending**.
