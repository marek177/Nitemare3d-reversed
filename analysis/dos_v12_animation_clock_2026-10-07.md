# DOS v1.2 animation clock and deadline reconstruction (2026-10-07)

## Status

**Promoted to code:** direct static evidence, cross-checked against the recent DOS v1.2 runtime captures.

This note intentionally separates confirmed semantics from capture-only correlations. Secret-door, scheduler, renderer, projectile and guard candidate offsets from the runtime batches are not assigned gameplay names here until their writer/reader xrefs are closed.

## 32-bit current tick at DS:07EC

The DOS v1.2 disassembly repeatedly treats `DS:07EC`/`DS:07EE` as one 32-bit current-time value:

- `0800:2419` loads `EAX <- dword [07EC]` and compares it to `dword [SI+08]`.
- `0800:24D8`/`24DE` load low/high words from `07EC`/`07EE`, add the sequence delay, and store the result back to record `+08/+0A`.
- The same deadline pattern is visible in the animation paths around `0800:7E27`, `0800:800A`, `0800:8072`, `0800:AEEC`, and `0800:AF73`.

The branch is an unsigned `deadline > currentTick` test. A record advances only when its deadline is less than or equal to the current tick.

## Reconstructed routine 0800:2410

Observed record fields:

| Offset | Width | Meaning in this routine |
|---|---:|---|
| `+02` | byte | random-table variant index |
| `+03` | byte | current animation frame |
| `+06` | byte | runtime class used by special branches |
| `+08` | dword | next animation deadline |

Observed sequence-definition fields:

| Offset | Width | Meaning in this routine |
|---|---:|---|
| `+00` | word | frame count / terminal frame threshold |
| `+02` | word | delay added to current tick |
| `+04` | word | optional random-window table pointer |

The routine:

1. returns if `deadline > currentTick`;
2. increments the frame byte;
3. applies class-specific behavior for `0x07`, `0x2D`, and `0x2F`;
4. otherwise either wraps by frame count or uses the optional eight-entry random-window table;
5. writes `deadline = currentTick + frameDelay` using 32-bit wraparound arithmetic.

Class `0x2D` performs a far call to `0FAD:072E` when the terminal frame is reached. The new clean-room helper reports this as `CompletionCallbackRequested` instead of inventing the callee's still-unclosed engine semantics.

## Random-window table

For the optional table, the routine indexes eight words at `table + 4 + variant*2`.

- low byte: frame copied into the runtime record when a window is selected;
- high byte: non-zero span participating in the `start + span > frame` test;
- reselection uses `RNG & 7` until an entry with non-zero span is selected.

The reconstruction exposes these two bytes as `RandomFrameWindow { startFrame, span }`. This describes the verified arithmetic without claiming an original source-level type name.

## Runtime-capture correlations kept provisional

The recent v1.2 capture set also produced stable scenario-correlated regions (for example around `4CD8`, `4DC2`, `4D7A`, and `4128`). They are useful watchpoint candidates, but the current static dump does not yet provide direct DS-memory xrefs for those offsets. They therefore remain research candidates and are not promoted to named runtime globals in this commit.
