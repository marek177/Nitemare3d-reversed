# Player movement / collision closure delta — 2026-09-28

This note updates the 2026-09-25 working coverage estimate after a focused Win16 1.10 closure pass.

## Coverage change

| Subsystem | Previous working range | 2026-09-28 working range | State |
|---|---:|---:|---|
| Player movement / collision | 80–90% | **90–95%** | PARTIAL — static semantics substantially closed; runtime trajectory parity remains |

The range is an evidence-coverage estimate, not byte-count coverage and not a claim of original-source recovery.

## Closed in this pass

- wall-property bits 0x01, 0x02, 0x04, 0x08, 0x10 and 0x40 now have traced behavioral roles;
- dynamic-door controller states 0..4 are named from executable lifecycle evidence;
- state 4 is produced by GUARD death finalization for a retained corpse/object in a dynamic-door cell and behaves as a passable corpse hold-open/disabled-door state;
- the blocked player-step path is traced through the Win16 waveOut SFX routine;
- runtime SFX index 1 maps to SND.DAT directory entry 33, which is an empty/reserved retail slot;
- the CF60 touch dispatcher is joined to retail KEY, IDCARD, FOOD, WEAPON, AMMO, CRYSTALB, MAGICEYE, PENTAGRAM and SCROLL classes;
- CF60 cases 0x31/0x32/0x34/0x35/0x37/0x38 have no class assignment in the audited retail class tables and no Win16 1.10 OBJECT+06 writer; they are retained as legacy/dead dispatcher cases rather than invented retail items.

## Remaining before 100%

The principal remaining gap is behavioral parity:

1. reproduce the exact one-unit major/minor-axis stepping trajectory over long movement sequences;
2. validate corner sliding and the order of X/Y collision attempts;
3. validate moving-door interaction during partial open/close states;
4. validate touch-trigger and pickup side effects during edge/corner traversal;
5. compare deterministic trajectories against original demo/runtime captures.

Static reverse engineering is therefore much closer to closure than the older 80–90% range, but 100% is intentionally withheld until original-runtime parity is demonstrated.
