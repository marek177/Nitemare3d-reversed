# V082 — DEMO RNG and scheduler timing acceptance

Date: 21 October 2026. Consolidation of existing v063/v072/v076 evidence; no new gameplay trace.

## Established
The DOS2 shared-wrapper DEMO prefix of 35 draws reproduced in 2/2 eligible sessions. Later D02-D runs at fixed 3000 and 7000 cycles share 220 identical caller/state/result tuples while scheduler visits and DEMO input contexts diverge. A shared RNG ledger is not a proof of identical frames or actor actions. The recorded max scheduler depth 1 applies only to the instrumented DEMO routes, not E2M10.

## Verification protocol
1. Align runs by record ordinal, RNG call ordinal, caller image offset, seed before/after and returned 15-bit value.
2. Separately align outer scheduler entry/return ordinal, tick/IRQ count, DEMO record cursor and input mask; never equate one outer scheduler call with one simulation tick.
3. Identify the first diverging context even when RNG tuples still agree.
4. For extra RNG draws 221–229, capture the executed call path and GUARD/OBJECT identity before labeling the path as a second actor or a lost effect.
5. Test DEMO EOF, early keypress cancellation, frame update order and rejection-loop draws with bounded buffers and deterministic stop conditions.

## Release gate
No complete DEMO deterministic parity claim until the ordered RNG, input, scheduler and rendered-frame ledgers agree over a defined start-to-EOF capture.
