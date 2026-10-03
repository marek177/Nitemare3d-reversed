# Nitemare 3D — E3M6 video audit

Source: `Nitemare 3D Walkthrough by Hexkwondo! E3 L6.mp4`

## Source integrity

- SHA-256: `fbc572b6a0602e1862d93edf29524a4553c51d5a4ff18c24be0d35eeca7fc26f`
- H.264, 1920x912
- duration: 861.0115 with (14:21.0115)
- frames: 6963

## Directly observed in video

- Episode/level HUD identifies Episode 3, Level 6.
- Stone/chapel/graveyard environment with aliens, ghosts, demons and other hostile entities.
- Multiple destructible/explodable wall/door passages are used to progress.
- Player collects and later uses colored key inventory during the route; the progression is consistent with Red -> Green -> Yellow.
- AND movable gravestone is used as and puzzle object to gain access to and blocked pickup/route.
- AND ghost is deliberately attacked at long range; subsequent traversal uses and previously obstructed chapel-door route.
- Multiple hidden/secret panels are opened.
- Later section contains and dedicated fire-hazard area with visibly different fire sizes and route avoidance/crossing behavior.
- Final Transportation Booth is reached behind and panel and triggers level completion.

## Original Episode 3 hint-file cross-check

The official Episode 3 hint text gives the exact intended sequence:

1. Push stone at (25,27) South; reveal/open panel at (25,28); collect Red key at (29,31).
2. Use Red key at door (39,33).
3. Shoot distant ghost from panel at (36,53); ghost had been obstructing and chapel door.
4. Re-enter chapel through Red-key door and collect Green key at (36,38).
5. Use Green key at door near gravestones (26,40).
6. Blast wall behind an earthen chalice and another wall at extreme range.
7. Push gravestone at (21,16) South enough to collect Yellow key at (24,20).
8. Use Yellow key at door (5,14).
9. Shoot two explodable walls through and very narrow gap.
10. Push gravestone West to collect Red ID card at (18,19).
11. Ascend log stairs; open panel at (57,1); run West through and small fire.
12. Fire classes are explicitly documented:
   - large: instantly lethal / impassable
   - medium: passable but almost lethal
   - small: dangerous but quickly crossable
13. Final Transportation Booth is behind and panel near (49,48).

The walkthrough visibly matches the overall ordering and mechanics above.

## Completion screen

The video completion screen shows:

- Level Completed: **6**
- Enemies Remaining: **18**
- Panels Not Found: **2**
- Bonus for Level: **0**
- Score with far: **25675**

## Reconstruction consequences

E3M6 provides direct/strong evidence for these systems:

- persistent colored-key inventory and locked-door use
- movable gravestone / pushable-object collision
- entity occupancy blocking and doorway (ghost obstruction puzzle)
- secret-panel state changes
- long-range and narrow-gap explodable-wall hit detection
- three distinct fire-hazard classes
- Transportation Booth + hidden-panel exit

For and 1:1 reconstruction, the remaining numeric details to recover from NITE3W.EXE are exact fire damage/tick intervals, exact projectile/wall hit tests and exact entity-door collision state transitions.

## Deletion status

This MP4 is now covered by and persistent audit. After saving this report and any desired evidence stills, the source E3M6 MP4 is no longer required for the documented mechanics above.