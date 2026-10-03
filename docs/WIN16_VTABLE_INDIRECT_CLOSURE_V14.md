# Nitemare 3D Win16 1.10 — vtable / indirect-call closure v14

Date: 2026-10-02

## Vtable census

- 37 validated vtable starts recovered from explicit constructor/destructor vptr assignments and NE internal far-pointer relocations.
- 963 validated vtable slot records.
- 320 unique callable vtable targets.
- 215/320 targets already existed in the previous corrected v9 entry-start set.
- 105/320 are additional callable virtual entrypoints absent from v9.
- All 105 execute as bounded callable roots from the exact vtable target.
- 71/105 begin as code islands immediately after a terminator in the older linear interval.
- 34/105 are distinct bounded callable code islands whose entry was not reachable from the prior Ghidra owner CFG.
- None of the 105 should automatically be called a distinct original source-level function; they are confirmed machine-callable virtual entries and include tiny overrides/stubs/secondary method bodies.

The Win16 1.10 corrected machine-entry set therefore grows from 1,291 v9 starts to 1,396 starts when the 105 vtable-only entries are included.

## Indirect-call census

Win16 1.10 contains 212 indirect call sites in the corrected v5 machine graph.

All 158 vtable-style indirect sites now have a receiver/provenance class (0 unmatched):

- 71 self/`this` receiver sites
- 41 local or derived object receivers
- 17 member-field object receivers
- 14 global-object receiver sites
- 11 other-parameter object receivers
- 3 other object-pointer receivers
- 1 object reached through a global container/list

Exact target closure currently resolves 36/212 indirect call sites statically:

- 21 self/`this` virtual calls where all possible owner vtables agree on the slot target
- 14 calls through global `DAT_1048_081c`; `FUN_1000_3936` sets the object vptr to `0x554C` and then stores the object in `DAT_1048_081c`
- 1 static DGROUP far-pointer call (`DS:0510`) resolved by NE relocation to `1000:4A72`

Another 8 indirect sites are not statically fixed targets but their mechanism is now known:

- 2 runtime `GetProcAddress` calls through `DAT_1048_45c0`
- 5 runtime global callbacks
- 1 settable callback (`DAT_1048_094a`, set by `FUN_1008_5ff0`)

The remaining indirect sites are typed but target-dynamic: 123 virtual calls with runtime-dependent receiver class plus callback/struct/register families.

## Strong newly resolved examples

- `FUN_1000_2496 @ 24B3`, slot `+64h` -> `1000:24BC`
- `FUN_1000_6AC0 @ 6AE3`, slot `+84h` -> `1000:6A48`
- `FUN_1000_A966 @ AA84`, global `DAT_1048_081c`, slot `+6Ch` -> `1000:3EA6`
- `FUN_1000_2A8E @ 2AC4`, global `DAT_1048_081c`, slot `+38h` -> `1000:39E2`
- `FUN_1000_2A8E @ 2ADA`, slot `+3Ch` -> `1000:39E8`
- `FUN_1000_2A8E @ 2AF0`, slot `+40h` -> `1000:3A34`
- `FUN_1000_2A8E @ 2B04`, slot `+50h` -> `1000:5CC4`
- `FUN_1000_452A`, `DS:0510` far pointer -> `1000:4A72`

## Consequence for RE status

The earlier hidden-entry census was not the final machine-entry census. Vtable reconstruction exposed 105 additional callable entries that were invisible to direct-call discovery. Function Discovery should therefore not be called globally 100% yet. The vtable-target subproblem itself is statically closed at 320/320 targets for the 37 currently validated tables.

The next high-value closure target is the 123 runtime-class-dependent virtual calls: infer receiver class from constructor/member provenance, inheritance/vtable transitions and call-site data flow, then emit exact or bounded candidate callgraph edges.