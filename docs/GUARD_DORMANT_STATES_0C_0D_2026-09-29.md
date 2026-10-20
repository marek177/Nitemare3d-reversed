# GUARD states 0x0C / 0x0D dormant-state closure — 2026-09-29

## Result

The GUARD state dispatcher retains handlers for current states `0x0C` and `0x0D`, but the audited retail state graphs do not recover a normal writer that creates either state.

This changes their classification from "active state with unknown semantic name" to:

- **0x0C — retail-dormant / legacy-compatible state with retained USE message**
- **0x0D — retail-dormant sibling using the same sequence-refresh handler**

The historical pre-release names remain unknown.

## Win16 evidence

All four audited Win16 exports retain the state-`0x0C` interaction test:

| Build | interaction function |
|---|---|
| 1.3 | `FUN_1010_A91C` |
| 1.6 | `FUN_1010_AA90` |
| 1.8 | `FUN_1010_AA90` |
| 1.10 | `FUN_1010_AB3E` |

The test resolves the GUARD associated with the target map cell and displays:

```text
I've nothing left!
```

when `GUARD+0x0B == 0x0C`.

Writer scans over the current-state byte find no recovered literal current-state writer for `0x0C` or `0x0D` in any of the four builds.

For Win16 1.10 the raw generic state/sequence setter at `3:762C` has only three direct call sites. Their state pairs cover normal animation transitions, death/deferred-death transitions and hit/reaction transitions; none introduces current or next state `0x0C` or `0x0D`. Direct `nextState` writes likewise do not introduce either value.

Both states are nevertheless valid dispatcher inputs. They share handler `3:7E54`, which calls the directional/sequence update helper and leaves the current state unchanged.

## DOS evidence

The residual state-`0x0C` interaction check is also present in the audited DOS family:

| Build | interaction helper | direct 0x0C/0x0D current-state writer recovered |
|---|---|---|
| 1.0 | `FUN_1000_8C46` | no |
| 1.7 | `FUN_1000_8F56` | no |
| 1.8 | `FUN_1000_90BA` | no |
| 1.9 | byte-identical executable to audited 1.8 | no, same code image |
| 2.0 | `FUN_1000_90C4` | no |

DOS 1.8 and 1.9 `N3D-E` executables are byte-identical in the executable inventory (same size and SHA-256), so the 1.8 static result applies byte-for-byte to that supplied 1.9 executable.

## What this does and does not prove

It proves that the recovered normal retail graphs do not contain a known producer for these states while their handlers survived across platforms/versions.

It does **not** prove that the numeric states are impossible to execute. They can still be reached by:

- a crafted or corrupted USER.SAV record;
- direct debugger/memory editing;
- an external writer absent from the recovered graph;
- potentially an older/pre-release content path not present in the audited retail artifacts.

Therefore code should preserve the handlers when aiming for binary-compatible behavior, but gameplay logic should not invent a normal transition into them.

## Coverage impact

- GUARD state-ID/dispatcher/reachability subarea: working static coverage **97–99%**.
- Overall GUARD runtime/AI is **not** promoted to 97–99%; LOS/FOV/hearing, attack cadence, remaining strategy semantics and several state meanings remain open.
- USE/interactions static semantic coverage rises to **96–98%**, because the final major static USE-state ambiguity is now classified.
- USE original-runtime parity remains **90–95%** until repeated-use/moving-door/scripted-level traces are compared against the original runtime.
