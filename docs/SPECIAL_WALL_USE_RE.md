# Special-wall USE families — additional NITE3W.EXE decoding

Date: 2026-09-17

This supplements `docs/USE_INTERACTION_RE.md` with deeper decoding of the `seg3:277A` special-wall dispatcher and its cross-segment targets.

## NE relocation correction

The far-call target offset alone is not sufficient to name the target segment in a Win16 NE image. The segment-3 relocation chains were decoded and prove:

| call site in seg3 | target offset | relocated target segment |
|---:|---:|---:|
| `277A` family -> `C126` | `C126` | **segment 3** |
| `277A` family -> `20CE` | `20CE` | **segment 4** |
| `277A` family -> `1F6A` | `1F6A` | **segment 4** |
| `277A` family -> `2076` | `2076` | **segment 4** |
| `277A` default -> `1EE0` | `1EE0` | **segment 4** |

Status: **VERIFIED_EXE**.

## Four-pentagram mask — global `0x4C45`

The object-touch dispatcher `seg3:CF60` has a jump table for OBJECT classes `0x2F..0x3D`. Class **`0x3C`** reaches `seg3:D158`, where:

```text
bit = 1 << OBJECT[+01]
0x4C45 |= bit
```

The Omnifarious cheat path at `seg3:B162..B176` writes `0x0F` to `0x4C45` along with the other all-inventory state.

The special-wall handler `seg3:C126` tests the four low bits of `0x4C45`. Its static pointer table resolves to these exact strings:

| bit | missing-item string |
|---:|---|
| `0x01` | `The Red Pentagram` |
| `0x02` | `The Green Pentagram` |
| `0x04` | `The Blue Pentagram` |
| `0x08` | `The Yellow Pentagram` |

The same handler begins with the exact message:

```text
This is the portal to the
"Other Side".   You cannot
pass through until you have
collected all 4 pentagrams!

You need to find :-
```

Therefore:

- `0x4C45` = **four-pentagram possession mask**;
- OBJECT class `0x3C`, indexed by OBJECT `+01`, is the **pentagram collectible class**;
- the four values of `OBJECT+01` correspond in order to Red, Green, Blue, Yellow.

Status: **VERIFIED_EXE**.

## `0x15..0x18` special-wall family — portal / mirror / pentagram gate

`seg3:277A` routes mapped wall types `0x15..0x18` to `seg3:C126`.

`C126`:

1. copies the portal-to-the-Other-Side text into its local message buffer;
2. appends each missing colored pentagram name according to `0x4C45`;
3. has a dedicated branch for mapped type `0x16` using the string:

```text
The mirror crack'd
from side to side!
```

4. for mapped type `0x15`, `0x4C45 == 0x0F` opens a distinct success/transition path rather than the missing-pentagram message path.

The family can therefore be classified as the **Other Side portal / Mirror of Destiny / four-pentagram gate family**. Exact visible meaning of each of `0x15`, `0x16`, `0x17`, `0x18` still requires per-level wall-definition correlation, but `0x15` and `0x16` already have strong direct behavioral identities in the executable.

Status: **VERIFIED_EXE** for message/mask/control flow; per-type visual labels **PARTIAL**.

## `0x19..0x1C` — exact colored-key gates

`seg4:20CE` computes:

```text
keyIndex = mappedWallType - 0x19
keyBit   = 1 << keyIndex
present  = (0x4C28 & keyBit) != 0
```

`seg3:BCB6` resolves the key-name table exactly:

| wall type | index | key |
|---:|---:|---|
| `0x19` | 0 | Red key |
| `0x1A` | 1 | Green key |
| `0x1B` | 2 | Blue key |
| `0x1C` | 3 | Yellow key |

The handler builds either `You use the <key>` or `You need a <key>`. On success it calls `seg3:ACB8`, which only plays SFX `0x32`; the key mask is not cleared. Thus this special-wall key path uses **reusable keys**.

Status: **VERIFIED_EXE**.

## ID-card table

The two-card pointer table used by `seg3:BCEA` resolves exactly to:

| index | card |
|---:|---|
| 0 | Red ID card |
| 1 | Yellow ID card |

Door classes `0x39..0x3A` test bit `1 << OBJECT+01` in global `0x4C29` and call `BCEA` on failure. This proves `0x4C29` is the ID-card possession mask.

Status: **VERIFIED_EXE**.

## `0x25..0x2C` — combination-check family

`seg4:2076` uses the raw-wall-variant search helper `seg3:2334`, compares the current raw wall state to the expected/canonical state, and on mismatch enters the UI path backed by the combination text area.

The original data segment contains:

```text
What's the combination?  0000000
01532
080993
372535
I'm sorry, that is not
the correct combination.
```

Therefore mapped types `0x25..0x2C` belong to the **combination-check / combination-lock family**. Multiple raw wall IDs can map to the same logical type; the raw ID encodes the visible/state variant that this handler validates.

Status: **VERIFIED_EXE** for family identity and validation structure; exact type -> code/state association remains **PARTIAL**.

## Raw-wall variant helpers

`seg3:2334(mappedType, startingRawId)` searches raw wall IDs until the runtime mapping table `0x8196[rawId]` equals the requested logical type.

`seg3:2426(mappedType)` scans the current 64x64 map and returns the highest raw wall ID currently present for that mapped type.

These helpers explain why special walls cannot be reconstructed as a simple single-byte logical enum: several graphics/state variants may share one mapped wall type.

Status: **VERIFIED_EXE**.

## Scripted wall type 8 — Episode 1 special cases

`seg3:C0A2(targetCell)` is reached from USE for mapped wall type `8`. It explicitly checks Episode 1 and has separate branches for level numbers 2 and 7 (1-based level numbering in the branch logic).

The level-7 branch references the exact messages:

```text
Well done!  You fixed the power!
You already fixed it!
```

and changes persistent runtime state before redisplaying the scene. Thus wall type 8 includes at least an Episode-1 scripted **power-repair interaction** in E1M7; the E1M2 action is a separate special case and is not yet given a user-facing name.

Status: **VERIFIED_EXE** for the level checks and E1M7 message/effect family; E1M2 exact label **PARTIAL**.

## Remaining special-wall work

Still unresolved before the special-wall dispatcher can be called complete:

- exact names/level roles for default types `0x0D..0x14` handled by `seg4:1EE0`;
- exact role of types `0x1D..0x24` handled by `seg4:1F6A`;
- exact code/raw-state mapping for `0x25..0x2C`;
- exact per-type visual labels for `0x15..0x18` beyond the portal/mirror control flow already proven;
- xrefs for `Open remote doors` / `Close remote doors` to the exact wall type and state transition;
- E1M2's type-8 scripted action.
