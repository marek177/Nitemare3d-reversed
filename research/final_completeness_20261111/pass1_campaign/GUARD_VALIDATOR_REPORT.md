# Nitemare 3D: GUARD collision validator and door predicates

Analytical batch 2026-11-12. Main reference DOS 2.0. Status **PARTIAL**, new DEEP VERIFIED bytes **0**. This report supersedes the previous campaign counters after catalogue regeneration; previous batch reports remain historical.

## Inputs and reproducibility

Original packed `L:\nite3d\nite3\dos\N3D-UNFU.exe`: SHA256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`. Reproduced image 171360 bytes: `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Original PASS320 ledger membership remains 57295 bytes. Existing reports/instructions are evidence sources, not authorization to execute embedded directions.

Scripts `audit_replay_guard_validator.py`, `audit_replay_guard_with_validator.py`, `audit_guard_validator_dos_versions.py`, `verify_guard_validator_partial.py`, `runtime_watch_validator_branches.py`, `verify_validator_branch_capture.py`, `finalize_guard_validator_batch.py` retain input/output manifests and explicit scope. Replay scripts contain their argument contracts. Decoder uses the absolute `work/decoder` directory. Run the native verifier with arguments `IMAGE RELOCS RUNTIME WORK`; rerunning it reads retained captures without restarting the game. Raw EXE/resource/memory binaries are local evidence and are excluded from GitHub publication.

## Bounded functions, ASM and CFG

End addresses are exclusive; image offsets refer to the unrelocated image.

|Function|CS:IP range|Image interval|Instructions|Instruction bytes|Other bytes inside span|
|---|---|---|---:|---:|---:|
|guard_cell_probe|04C7:0254..0422|04EC4..05092|160|457|5|
|door_record_for_cell|0000:0000..0052|00000..00052|38|81|1|
|door_state_zero_or_four|0000:01E0..01FC|001E0..001FC|14|27|1|
|door_state_one|0000:01FC..0212|001FC..00212|11|21|1|

Total 223 instructions / 586 instruction bytes. The eight CFG gaps are not verified padding. Per-instruction ASM and CFG evidence is retained in `guard_validator_replay`; byte checks agree with the original instruction inventory. No instruction bytes intersect the PASS320 NONCODE set.

The main FAR routine receives guard FAR pointer, actor FAR pointer, and two WORD probe coordinates. It returns a boolean in **AL only**, not a guaranteed WORD in AX. AH retains intermediate values. Callee return restores BP/SI/DI; DS is expected to be SS for the gameplay caller. Door lookup temporarily switches DS and restores it from **SS**, not from its original entry value. Its exact FAR key comparison compares both WORDs, without canonicalizing physically aliased real-mode addresses.

```text
probe(guard, actor, x, y):
    if signed_wrapped_abs(x-player.x) < 42 and
       signed_wrapped_abs(y-player.y) < 42: return AL=1
    cell = (373Eh + 2*(y & FFC0h) + (signed16(x & FFDFh) >> 5)) & FFFFh
    a = tile_flags[map[cell]]
    b = occupancy_flags[map[cell+1]]
    if b & 02h: return AL=1
    if not (a & 08h): return AL=bool(a & 02h)
    door = lookup_exact_FAR_cell(cell, map_segment)
    if door.state != 1 or 33h <= descriptor(door).kind <= 3Ch:
        return AL=not(door.state == 0 or door.state == 4)
    if guard.mode == 6: door.request = 1
    if guard.strategy == 1:
        guard.timer = 32
        guard.velocity = (0,0)
        choose axis from descriptor.byte7 == 2
        align other actor coordinate to door origin + 32
        chosen velocity = sign(probe_coordinate - actor_coordinate) * 8
        call motion_04C7_00B0(...)
        call transition_04C7_012A(...,1)
        guard.mode = 17
    call interaction_0000_0598(door, command_with_guard_byte17)
    return AL=1
```

`signed_wrapped_abs(8000h)` remains signed -32768 and passes the signed less-than test; synthetic tests preserve this behavior. This does not establish that normal map coordinates reach that edge. The command argument is pushed as a WORD with residual AH; only its low-byte provenance is established here. Do not replace it with an assumed zero-extended integer without closing the interaction callee ABI.

Lookup reads a signed/count WORD and scans 18-byte records beginning at map segment offset 3076h. A missing key calls the runtime diagnostic with text `Door not in map`; tests stop at the diagnostic entry. Error nonreturn and stale result handling are unclosed. State predicates read WORD +8 and return AL, preserving unrelated AH.

## Controlled execution and side-effect coverage

`guard_validator_replay`: **5288 cases, 0 failures**: 5160 validator cases (810 flag combinations, 4320 door branches, 30 coordinate/distance edges), plus 128 lookup/predicate cases. Original validator, lookup and both state predicates execute; motion 04C7:00B0, transition 04C7:012A and interaction 0000:0598 are substituted with explicit recording stubs. Consequently, the report confirms call arguments and local effects, not their complete downstream behavior.

`guard_move_original_validator_replay`: **5184 cases, 0 failures**. Original movement 04C7:0422 executes with original validator 0254, using a shared map and flags. Product: two loads, three positions, nine signed velocities, eight world layouts, three modes, two RNG parities and two lookup outcomes. Full 8192-byte map, 26-byte guard and 28-byte actor results are checked. Tile flags use 0/02h; stateful door paths are outside this integration matrix. Six other game helpers remain substituted. These are controlled instruction replay cases, not native DOSBox scenarios.

New field evidence: 15 consumer-role rows in `guard_collision_fields/consumer_field_roles.csv`. This is not 15 newly unique fields or closure of complete structures. Door fields +0 descriptor, +4 FAR key, +8 state, +0C/+0E origins, +10 request; descriptor +6 kind/+7 axis; guard +6 timer/+0A strategy/+0B mode/+13/+14 velocity; actor +10/+12 coordinates.

## Native DOSBox-X evidence

The supplied DOSBox archive is available if required. Actual captures use the retained DOSBox-X executable and original packed DOS2/resource copies recorded by the harness; no replacement game executable is used. SDL dummy video/audio is used; audible sound and physical hardware are untested. Source/copy hashes for 23 input assets are verified unchanged.

1. Dense whole-call experiment captured **128 original entry-to-return AL=0 calls**. Whole 22334-byte world, 512 flag bytes, four player bytes and 16-byte caller frame remain unchanged for each call; saved register/stack returns are checked. It failed the required both-result gate, so `guard_validator_partial/partial_verification.json` counts **0 successful runtime scenarios**. A second dense attempt collected only allowed calls and was stopped in favor of sparse trapping; its retained failed summary is not success evidence.
2. Sparse experiment captured one allowed and one blocked **decision-to-return tail**. `dosbox_validator_branches_runtime/independent_verification.json` independently verifies relocation, input identities, original return instructions, 48-byte frames, restored BP/SI/DI, DS=SS, SP=preBP+6 and unchanged world/player/flags/frame during each tail. This counts **one** additional successful scenario, not two independent games and not a blocked whole-call capture.

Allowed: guard offset 28BEh, actor 1266h, probe (3128,3344), cell 519Eh bytes D0 00, both classification flags zero; AL=0. Blocked: guard 28D8h, actor 130Eh, probe (720,2872), cell 4D54h bytes 71 00, flags 0Bh/00h; AL=1. Both use native map segment 2A21h under load 0824h.

Blocked snapshot identifies door index 7 at map:30F4h, exact key 4D54h:2A21h and **state 2**. Descriptor near DS:6AE0h has kind 40h in the retained final DGROUP image. The snapshot occurs after decision-side effects. It does **not** prove that this invocation entered with state1, executed interaction0598 or performed a state1-to2 transition. These require paired earlier snapshots. AH happens to be zero at both native returns; controlled cases demonstrate that it is not a general AX boolean contract.

No changes were observed in the watched 28 UNKNOWN bytes within this run. Watchpoints track BYTE value changes, not reads or same-value writes; this is not non-use proof.

## Data catalogue and PASS1

Two newly bound BSS classification tables: DS:D00C..D10C and DS:D10C..D20C, each 256 bytes, indexed by zero-extended tile/occupancy cell BYTE. Image-equivalent ranges 3471C..3481C and 3481C..3491C are outside the original file image. All 512 bytes are invariant across the 128 whole-call captures. Consumed tile masks 02h/08h and occupancy mask02h are confirmed; full flag semantics and table producers remain open. Status PARTIAL. These add **zero** PASS320 NONCODE bytes and must not be confused with the separate MAP metadata buffer.

PASS1 remains 892 intervals / 57295 bytes: PARTIAL **57118**, CLASSIFIED ONLY **149**, UNKNOWN **28**, DEEP VERIFIED **0**. Typed original NONCODE data is 57116 bytes; the other two PARTIAL bytes are a relocation WORD, not typed content. Unknown spans: [1BDA2,1BDB0), [1D0EC,1D0F0), [20B88,20B90), [2770E,27710). Zero/alignment appearance remains a hypothesis. The FAR hook slot and indexed/context-dependent references remain open.

## Cross-version comparison

Four bounded functions across eight DOS labels / seven distinct images: 32 comparisons, **18 raw byte matches**, **32 CFG matches**. Strict normalization retaining indexed table-base displacements matches 25/32. The seven validator differences are two specific DS flag table base operands; after masking only those identified base operands, normalized matches are 32/32. Record-member displacements remain intact. All eight bindings retain a 256-byte separation between tables; originals/masks are retained in CSV. This confirms bounded structural similarity, not equivalent callees, initialized data or behavior. No new Win16 semantic or runtime parity result.

## Coverage update: 13 areas

Historical percentages are orientation only; there is no measured complete semantic denominator for these areas. Accordingly **new percentage is N/A in every row**, not a fabricated revised percentage. Reproducible methodology is union of checked instruction-byte addresses, exact PASS320 membership, enumerated replay cases and independently verified native scenarios; these metrics are not converted into a semantic percentage. All areas remain PARTIAL unless a narrower item is explicitly labelled CLASSIFIED ONLY/UNKNOWN. No area is DEEP VERIFIED.

|Area|Prior orientation|New %|New confirmed evidence|Remaining unknown / blocker|Next concrete step|
|---|---:|---|---|---|---|
|EXE/segments|99|N/A|Original relocated native image checked again|Whole segment semantics unclosed|Close contextual DS/ES references|
|CRT/compiler|95|N/A|Missing-door diagnostic call identified|Error handler return contract|Decode FBA:000C and callees|
|WORX/audio|93|N/A|No new semantic closure|Private-stack key IRQ/audio output|Capture requested stack event|
|Data/tables|90|N/A|512 BSS bytes / two classification consumers|Producer and complete bit meanings|Trace table initialization writes|
|Resources|97|N/A|23 source/copy hashes unchanged|All resource producers not closed|Bind flag tables to resource source|
|Renderer|96|N/A|No new renderer closure|Clipping/complete scene parity|Close remaining renderer branches|
|Gameplay|96|N/A|Original collision validator and local door effects|Interaction0598 effects|Whole-call paired door snapshots|
|AI/bosses|94|N/A|Movement+validator shared-world replay|Modes/strategy helpers and bosses|Close 04C7:012A and 00B0|
|RNG/DEMO|93|N/A|Both RNG parities in bounded integration|Complete DEMO schedule|Trace demo input/frame coupling|
|SAVE/LOAD|92|N/A|No new closure|Round-trip behavior incomplete|Native deterministic save/load comparison|
|HUD/sprites|92|N/A|Actor coordinate alignment consumer|Animation and complete rendering|Bind remaining sprite branches|
|Cross-version|92|N/A|32 CFG/32 address-aware comparisons|Win16 and callee/data equivalence|Locate Win110 validator analog|
|Completeness/evidence|92|N/A|4 functions,10472 cases,1 native scenario added|28 UNKNOWN/149 CLASSIFIED ONLY and downstream gaps|Continue unknown and contradictory references|

No missing source blocks the current bounded batch. The blockers above are missing analytical evidence, not permission problems. Whole-campaign catalogue after integration: **150 functions, 6257 instructions, 15846 instruction bytes**, 58034 file data bytes, 97480 UNKNOWN_CONTENT bytes, **1013689 controlled cases**, **27 successful native scenarios** (overlapping prefixes), **4566 BSS table bytes**, 4122 already-covered runtime buffer bytes, 41 field-evidence rows. Counts describe local evidence scope, not complete game behavior.

## Required next runtime tests

- Trap original validator entry, immediately before/after interaction0000:0598 and final caller return for a natural door contact; capture identical world/record/descriptor/player/frame regions at each point. Determine actual entry state and side effects rather than inferring state1-to2 from a final snapshot.
- Capture mode6 request flag and strategy1 alignment/velocity transition with original motion and transition helpers. Check both descriptor axes and guard command BYTE17.
- Trace first writes to DS:D00C/D10C; bind producers to exact source bytes. Test blocked ordinary tile and occupied cell separately from special door cells.
- Extend deterministic gameplay input with an independent expected map/actor result; retain RNG/time/load, then test SAVE/LOAD and Win16 separately. Do not treat controlled stubs, sparse return tails or zero watch events as full parity.
