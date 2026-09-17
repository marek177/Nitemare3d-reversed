# Nitemare 3-D — Episode 3 Level 4 / Level 5 video audit

Date: 2026-09-17

This audit covers the supplied Hexkwondo walkthrough videos for E3M4 and E3M5. MP4 source files are intentionally not included in this audit package. Video observations are kept separate from official hint-file cross-checks.

## Source integrity

### E3M4
- Source: `Nitemare 3D Walkthrough by Hexkwondo! E3 L4(1).mp4`
- SHA-256: `66ca5eb0c1088af202b2d46edd6d33b3dda284e0f32487b28747c32e14a91f2d`
- H.264, 1920x902
- Duration: 1898.904671 s (~31:38.9)
- Reported frames: 15123

### E3M5
- Source: `Nitemare 3D Walkthrough by Hexkwondo! E3 L5(1).mp4`
- SHA-256: `c49a792dffe3777993235f516cfb79fa666791cf89091fcaac9045d3e8adbf8a`
- H.264, 1920x1080
- Duration: 801.297415 s (~13:21.3)
- Reported frames: 24013

---

# E3M4

## Directly observed in the video

- Normal E3M4 gameplay begins after the Main Menu.
- Early progression repeatedly uses shootable/explodable wall sections, including red-moss/brick wall passages.
- The walkthrough traverses stone, brick, chapel and graveyard-style areas, opens containers/panels and accumulates multiple colored key items in the HUD.
- A chapel/stained-glass section appears in the middle portion of the route together with movable/obstructing objects.
- Later progression enters a much darker area followed by a long fire/demon-themed section with red demon imagery and hostile entities.
- The HUD late in the level shows the expected multi-key/card inventory progression.
- Near the end, a standard three-choice stair selector is displayed: `Climb up / Climb down / Cancel` (about 30:30 in the supplied video).
- The final route passes sliding/wooden doors into a small chapel/Transportation Booth area.
- The level exits through the standard booth/green-transition path.

## Official Episode 3 hint-file cross-check

The original hint text gives the intended E3M4 sequence:

1. Blast five consecutive red-moss walls at the start; an early inaccessible red key is explicitly a red herring.
2. Obtain the Blue key, then the Yellow key.
3. Enter the chapel; use the Blue lock, push boxes West and obtain the Green key.
4. Use the Yellow lock; ignore decoy boxes, open panels and obtain the Red key.
5. Use the Red lock to enter the dark area and reach the fiery demon-statue section.
6. Blast three red doors and collect the Red ID card.
7. Return, ascend log stairs and use the Green lock.
8. The hint explicitly warns of a stair trap that can require pushing boxes to partially block the stairs to escape.
9. Pass two sets of sliding doors in a specific left-then-right sequence to surprise two aliens.
10. Reach the Transportation Booth in the final small chapel.

The supplied video is visually consistent with this progression. Exact key-lock text popups are not asserted unless clearly captured in retained evidence frames.

## Completion screen

At ~31:30 the video shows:

- Level Completed: **4**
- Enemies Remaining: **6**
- Panels Not Found: **1**
- Bonus for Level: **0**
- Score so far: **12900**

## Reconstruction consequences

E3M4 is strong evidence for:

- repeated chained explodable-wall progression;
- multi-color persistent key inventory/locks;
- pushable-box puzzle objects;
- special stair selector UI;
- a stair/occupancy trap that depends on an obstructing movable object;
- ordered sliding-door traversal used to control enemy encounter geometry;
- ID-card inventory progression;
- standard Transportation Booth exit and completion screen.

---

# E3M5

## Directly observed in the video

- Normal E3M5 gameplay begins in the hell/skull-texture region.
- The route uses multiple secret panels and shootable/explodable entrances.
- Ghosts, demons and other Episode 3 enemies are fought during progression.
- Around 04:00 the video visibly shows a chest/pickup labelled `Pentagram of Good Health`, confirming that specific benefit pickup presentation in E3M5.
- Later sections transition from skull/hell corridors into pale stone/chapel/graveyard areas.
- A standard stair selector appears at about 10:14: `Climb up / Climb down / Cancel`.
- The final route reaches the large chapel region and then the Transportation Booth.
- A bright green transition precedes the completion screen.

## Important source discontinuity

This particular E3M5 walkthrough is **not fully continuous gameplay footage**. Around ~06:40 it cuts to an editorial/hint-booklet segment (the contact-sheet sequence includes the creator's `Sorry! Had a little Snafu here!` insert), and shortly afterward returns through the Main Menu before gameplay resumes.

Therefore:

- the supplied file can be fully audited as a source;
- but it cannot by itself prove every gameplay frame/event across that edited interval;
- a second continuous E3M5 capture would be required for literal 100% frame-continuous gameplay coverage.

## Official Episode 3 hint-file cross-check

The original hint text describes the intended E3M5 route:

1. Open the starting panels, blast the door and collect the Red key.
2. Open another panel, kill two ghosts and blast a distant entrance to expose a gravestone route.
3. Traverse the skull-head passage; push the gravestone North into the cleared gap and collect the Blue key.
4. Use the Blue lock, climb stairs and follow a chain of panels/doors to obtain the Green key.
5. Return and use the Red lock to enter the huge chapel area.
6. Solve or bypass the gravestone arrangement blocking access to the chapel.
7. Use the Green lock, collect the Yellow ID card and reach the Transportation Booth.

The visible portions of the walkthrough are consistent with this route, while the edited interval is treated as missing video evidence rather than reconstructed from the hint text.

## Completion screen

At the end of the file the video shows:

- Level Completed: **5**
- Enemies Remaining: **15**
- Panels Not Found: **4**
- Bonus for Level: **0**
- Score so far: **17675**

## Reconstruction consequences

E3M5 provides direct/strong evidence for:

- secret-panel chains;
- explodable entrances and long-range wall destruction;
- pushable gravestone puzzle traversal;
- persistent Red/Blue/Green key progression;
- the same three-option StairWarpSelector family used elsewhere;
- Pentagram benefit pickup UI (`Pentagram of Good Health`);
- large-chapel/gravestone blocking geometry;
- Yellow ID-card progression;
- Transportation Booth exit and standard completion transition.

---

# Coverage status after this audit

- E3M4: **audited; source is suitable for deletion after preserving this audit/evidence package.**
- E3M5: **audited, but source itself contains an editorial gameplay gap.** It is suitable for deletion if preserving this source gap in the audit is sufficient; do not call E3M5 "100% continuous frame coverage" without another capture.
- E3M6: already audited separately.
- E3M3 now has a dedicated MAP/HINT reconstruction audit and source-code anchor table in `docs/VIDEO_AUDIT_E3M3.md` / `src/game/Episode3LevelData.hpp`; the remaining gap is the literal direct MP4 frame/timestamp pass.
