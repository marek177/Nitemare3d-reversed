# USE / interaction closure delta — 2026-09-28

This note updates the 2026-09-25 working coverage estimate after a focused Win16 1.10 USE/interactions closure pass.

## Coverage change

| Subsystem | Previous working range | 2026-09-28 working range | State |
|---|---:|---:|---|
| USE / interactions — static semantics | 75–90% legacy combined estimate | **96–98%** | Core dispatcher, class/state effects and dormant branches substantially closed |
| USE / interactions — original-runtime parity | — | **90–95%** | Controlled repeated-use/moving-state/demo parity still required |

This is an evidence-coverage estimate, not byte-count coverage and not a claim of recovered original source.

## Closed in this pass

- retail dynamic-door class mapping is joined to executable USE access rules:
  - 0x31/32 ordinary V/H;
  - 0x33..38 colored-key locked V/H across three environment sets;
  - 0x39/3A ID-card / transport-chamber V/H;
  - 0x3B/3C remote-controlled V/H;
  - 0x3F/40 curtain V/H;
  - no audited retail assignment for 0x3D/3E;
- direct door and remote-terminal credential checks do not clear key/card masks in the audited handlers;
- contextual menu actions are closed:
  - action 25 = Cancel;
  - 26 = Floor select;
  - 27 = Climb up -> raw-wall delta +1;
  - 28 = Climb down -> raw-wall delta -1;
  - 29 = Go down -> raw-wall delta -1;
  - 30/31 = remote door open/close;
  - 32/33 = remote cannon enable/disable;
- the old label "action 29 = StairCancel" is corrected;
- floor menu record +02 is generated as targetRawWallId-currentRawWallId and passed to the common warp helper;
- the warp helper finds the target raw-wall cell, selects an available adjacent destination, commits player to tile center and sets cardinal facing;
- object class 0x26 is SAFE:
  - correct combination sets a subtype-derived state;
  - subsequent reward codes 6..11 grant four colored keys and two ID cards;
  - state 1 is the empty-container path;
- object class 0x27 is TRUNK:
  - first USE opens/arms the subtype reward;
  - second USE grants health/ammo/Magic Eye/Crystal Ball/Red key by subtype;
  - subsequent USE displays "It's empty!";
- object class 0x29 is ACTION / Episode-1 Radio:
  - active only in E1M9;
  - starts the scripted dance-music sequence;
- E1M2 SPECIAL1 is the Office morphing chalkboard (wall ID 0x56), with resource timer/state 0x96 and SFX request 0x44;
- E1M7 SPECIAL1 is the Kitchen fuse-box power-repair path;
- the GUARD-family USE hook is narrowed to one exact condition: GUARD state 0x0C displays "I've nothing left!";
- GUARD states 0x0C and 0x0D are now classified as retail-dormant/legacy-compatible: retained handlers, but no recovered normal writer across the audited Win16 and DOS state graphs.

## Remaining before 100%

1. regression-test all USE paths against original runtime/demo behavior:
   - repeated USE;
   - missing credential;
   - doors in intermediate states;
   - SAFE/TRUNK already-empty states;
   - floor/stair facing and destination;
   - E1M2/E1M7/E1M9 scripts;
2. verify any remaining presentation-only side effects where the gameplay state transition is already known.

The main remaining gap is therefore **behavioral parity**, not the core USE dispatcher architecture or the former GUARD-state-0x0C semantic question.
