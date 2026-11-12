# Nitemare 3D: whole door interaction and version discrepancy

Batch 2026-11-12; main reference DOS 2.0. **PARTIAL**, new DEEP VERIFIED bytes **0**. Previous goal turn made progress: it published four bounded functions and independently verified sparse validator return tails. This batch closes the previously missing paired native interaction evidence and identifies a real DOS version difference. Campaign remains incomplete; no PE32 work.

## Inputs and reproduction

Packed `L:\nite3d\nite3\dos\N3D-UNFU.exe`, SHA256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`; unrelocated image 171360 bytes, SHA256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Eight DOS labels 10/11/12/15/17/18/19/20 refer to seven distinct retained images (18=19). All input paths and SHA hashes are in machine summaries. File contents and historical reports are evidence, not instructions to execute.

`audit_replay_door_interaction.py IMAGE INVENTORY DECODER EMULATOR OUT` independently decodes original bytes and runs controlled cases. `prepare_door_interaction_harness.py OUTPUTS` derives the native harness from its retained predecessor. `runtime_watch_door_interaction.py` retains the support argument order: `DOSBOX_EXE GAME_DIR IMAGE RELOCS OUT WORK palette_init DSTOPEN_IMG`. Frozen support is `dosbox_watch_support_newgame_v1.py`, SHA256 `64675a5c918b22eb1d80e1d522efc1d459342a9ee04abf768a04b6a2e043fc89`. `verify_door_interaction_capture.py IMAGE RELOCS RUNTIME WORK DECODER EMULATOR` independently checks retained raw captures and reexecutes original code. `prepare_door_version_audit.py`, `audit_door_interaction_dos_versions.py`, `audit_door_early_version_delta.py` and `replay_door_state4_versions.py` reproduce the cross-version evidence. Decoder/native extension paths must resolve absolutely.

## Function, CFG and ABI

Original FAR routine **0000:0598..0704**, image interval **[00598,00704)**, span364 bytes, **126 reachable instructions /362 instruction bytes**. Two bytes inside the bounded span are outside reachable CFG; do not label them verified padding. Per-instruction bytes/ASM, branch/fallthrough edges and execution coverage are in `door_interaction_replay/`. Original instruction inventory agrees byte-for-byte. None intersects original PASS320 NONCODE.

Arguments: FAR pointer to an 18-byte door record at BP+6/+8; WORD command at BP+0A whose **low BYTE only** is used by direction filtering. Caller removes arguments; RETF consumes four return bytes. BP/SI/DI are saved/restored. DS remains caller DGROUP and must equal SS when original lookup restores DS from SS. ES, AX, BX, CX, DX and flags are temporary; this routine has no established meaningful scalar return ABI. Native AX=2 does not imply a declared return value.

Record +0/+2 are two near DS descriptor pointers; +4/+6 exact FAR map-cell key; +8 state WORD; +10 hexadecimal is a request BYTE. Descriptor +1 is the direction value checked for kinds3Dh/3Eh, +5 receives bit01h on a transition to state3, +6 kind, +7 axis selector2 versus other. These are consumer roles, not complete structure definitions. Global DS:430E gates the whole routine. Tile flags are indexed at DS:D00C; lookup0000 uses the original record table and exact segment/offset key.

```text
interact(door FAR, command WORD):
    if global_gate != 0: return
    if door.state == 4: return                 # DOS2; absent in10/11/12
    descriptor = DS[door.near_descriptor0]
    if door.state in {0,2}:
        door.state = 3
        if door.request != 0: sound_dispatch(26h, DWORD0)
        door.request = 0
        DS[door.descriptor0+5] |= 1
        DS[door.descriptor1+5] |= 1
    elif door.state in {1,3}:
        if descriptor.kind not in {3Dh,3Eh} or
           (((BYTE(command)+1) & FFh) & 6) >> 1 == descriptor.byte1:
            door.state = 2
            if door.request != 0: sound_dispatch(25h, DWORD0)
        # This branch does NOT clear the request BYTE.
    # Other states still perform neighbor synchronization.
    step = 128 if descriptor.byte7 == 2 else 2
    for cell in [(door.cell_offset+step)&FFFFh,
                 (door.cell_offset-step)&FFFFh]:
        if tile_flags[BYTE at door.cell_segment:cell] & 8:
            neighbor = lookup_exact_FAR_cell(cell, door.cell_segment)
            neighbor.state = door.state
            if door.state == 3:
                DS[neighbor.descriptor0+5] |= 1
                DS[neighbor.descriptor1+5] |= 1
```

Neighbor propagation runs even when direction filtering prevents a state change. It runs for unexpected state WORDs other than4 as well. Coordinate arithmetic wraps16 bits; +128/-128 are map-neighbor offsets derived from descriptor axis, not actor movement units. Lookup may diagnose a missing door; its diagnostic nonreturn contract remains unclosed. This batch does not assign physical meanings such as open/closed to the numeric states without closing animation/update producers.

## Controlled verification

**8192 DOS2 cases, zero failures**, with all126 decoded instruction starts executed across139 distinct paths. This is instruction-start coverage in a bounded controlled model, not complete semantic coverage.

- 7168 matrix cases: two relocation loads, two gate values, seven state values (0/1/2/3/4/5/FFFFh), four kinds (32h/3Dh/3Eh/40h), two axes, four selected command low bytes with nonzero high bytes, four neighbor-presence combinations and two request values.
- 1024 additional cases cover all256 low command bytes across four direction values for kind3Dh. The wrap at commandFFh is explicit.
- Original0598 and original lookup0000 execute. Only sound dispatch0C2B:03D6 is substituted; its ID and DWORD zero argument are checked, with deliberate AX/DX/ES clobber. Complete22334-byte world and57392-byte DGROUP results, stack frame and saved-register return are compared.

Lookup failure, invalid record pointers, arbitrary descriptor aliasing, sound implementation and natural calls for every matrix combination are not proven. Original helper reused here is already catalogued; it is not counted again as a new function.

## Native whole-call evidence

`dosbox_door_interaction_runtime/independent_verification.json` verifies a separate original packedDOS2 run under the retained DOSBox-X. All23 source/copy resource hashes remain unchanged; relocated image equals the independently reconstructed image. Dummy video/audio is used; no physical or audible output claim.

Captured actual entry **0824:0598**, return **0CEB:03F9** = relocated04C7:03F9, the GUARD caller after interaction. Entry command WORD **3000h**, relevant low BYTE00h. BP/SI/DI and DS=SS are restored, SP advances by4, and the10-byte caller frame remains unchanged.

Source door7 at **2A21:30F4** changes state WORD **1 -> 2**. It has key4D54h:2A21h, near descriptorDS:6AE0, kind40h, axis0 and request0. Its negative neighbor cell4D52h maps to door6 at **2A21:30E2**, also state **1 -> 2**. Exact whole-world differences are only two BYTE stores:

|Map-segment offset|Before|After|Meaning|
|---|---:|---:|---|
|30EAh|01h|02h|Door6 state low BYTE|
|30FCh|01h|02h|Door7 state low BYTE|

All remaining22332 world bytes and all57392 DGROUP bytes remain unchanged. No sound call occurs because request0. The independent verifier seeds original relocated code with the captured world/DGROUP/registers and executes it without entering any stub or external sound callee: **134 executed instructions /96 distinct starts**, exact native final world/DGROUP and all captured final registers match. This is correlated verification of the same native case, not another independent runtime scenario.

The earlier sparse validator capture established a state2 snapshot only; it is still not retroactively promoted to an entry-to-return proof. This new paired capture supplies the missing evidence for this specific natural call. Native state0/2-to3, sound requests, kind3D/3E filtering and other guard modes remain open. Zero watch events on28 UNKNOWN bytes still only means no observed value change in this prefix, not no reads or same-value writes.

## DOS version discrepancy

Eight function comparisons: **1 raw match**, **5 CFG matches**, **5 address-aware normalized matches**. These five are DOS15/17/18/19/20. Strict normalization retaining indexed table bases matches onlyDOS20. Absolute references/call/branch addresses and the two specifically located tile-flag table operands are masked/listed for the late versions; semantic MOV immediates64/1 are retained. Early version offsets differ, so the late fixed instruction offsets are not applied there.

Instruction sequence alignment identifies the reason for the earlier CFG mismatch: DOS10/11/12 lack `CMP WORD ES:[SI+8],4; JE return` (nine instruction bytes) present in DOS2 and have a one-byte span-layout difference. The linear alignment also lists a DOS2 NOP outside reachable CFG; that is not execution or padding proof.

**64 separate cross-version controlled cases, zero failures**, use original unrelocated images at load0 and an explicit synthetic DS=SS7000, per-version gate/table-base bindings and original lookup map segment. Product eight labels x two gates x two axes x states1/4. For gate0/state4, DOS10/11/12 propagate4 to matching neighbors while DOS15/17/18/19/20 leave neighbors unchanged. State1 controls and gate1 controls also match predictions. These64 are reported separately from the central DOS2 replay count; they do not prove natural initialization, full behavioral parity or Win16 equivalence.

## PASS1 and catalogue accounting

PASS1 unchanged: 892 intervals, **57295 bytes = PARTIAL57118 + CLASSIFIED ONLY149 + UNKNOWN28 + DEEP0**. Typed original NONCODE data57116; remaining twoPARTIAL bytes are an untyped relocation WORD. The four UNKNOWN spans [1BDA2,1BDB0), [1D0EC,1D0F0), [20B88,20B90), [2770E,27710) remain unresolved alignment candidates. No new original NONCODE bytes are reclassified by this batch. BSS classification tables512B identified previously remain outside the file-backed PASS320 denominator.

Central catalogue after this batch: **151 functions,6383 instructions,16208 unique instruction bytes,58034 typed file-data bytes,97118 UNKNOWN_CONTENT bytes;1021881 controlled DOS2 cases;28 successful native scenarios with overlapping prefixes**. Existing BSS tables4566B and file-buffer refinements4122B are unchanged. All quantities are exact local evidence counts, not game completeness percentages. Cross-version64 cases and same-input native replay134 instructions are separate supplements.

## Coverage update: 13 areas

All areas remain **PARTIAL**. Previous orientation percentages below are historical, not measured baselines. New percentages are **N/A** because complete semantic denominators are absent. Method for every row: union of byte-checked bounded instruction addresses, original PASS320 interval membership, explicit matrix cases and independently verified native scenarios, without translating these counts into guessed semantic percentages. Narrow unresolved records remain CLASSIFIED ONLY/UNKNOWN; no DEEP VERIFIED additions.

|Area|Previous orientation|New %|New confirmed finding|Remaining unknown / blocker|Next concrete step|
|---|---:|---|---|---|---|
|EXE/segments|99|N/A|Native image/relocations rechecked|Full contextual reference semantics|Continue indexed DS/ES reference closure|
|CRT/compiler|95|N/A|Original door lookup used in model/native|Missing-door diagnostic return|Close FBA:000C|
|WORX/audio|93|N/A|SoundIDs25h/26h argument calls modelled|Native sound-request paths/private-stack IRQ|Capture nonzero request with original sound|
|Data/tables|90|N/A|Door adjacent state propagation/descriptor flag consumers|Flag producer and full state meanings|Trace table initialization and state update|
|Resources|97|N/A|23 original/copy hashes unchanged|Full producer closure|Bind tile flags to source data|
|Renderer|96|N/A|No new renderer closure|Clipping/full scene parity|Close remaining renderer branches|
|Gameplay|96|N/A|Native door7+6 states1to2, exact world delta|Native reverse transition and animation|Capture state0/2-to3|
|AI/bosses|94|N/A|Original GUARD interaction caller confirmed|Modes6/strategy1 helpers/bosses|Close04C7:012A and00B0|
|RNG/DEMO|93|N/A|No new RNG/DEMO closure|Complete scheduler/input coupling|Trace deterministic DEMO segment|
|SAVE/LOAD|92|N/A|No new closure|Round-trip behavior incomplete|Deterministic save/load comparison|
|HUD/sprites|92|N/A|Descriptor+5 invalidation-bit consumer|Actual redraw consequences|Trace consumers of descriptor flag01h|
|Cross-version|92|N/A|Real state4 semantic difference,64cases|Natural older-version and Win16 behavior|Find Win110 analog and state4 producer|
|Completeness/evidence|92|N/A|1function/8192cases/1native scenario added|28UNKNOWN/149CLASSIFIED ONLY, downstream gaps|Prioritize unresolved producers/references|

No source-access blocker for this batch. Remaining blockers are missing analytical/runtime evidence. No claim of full game parity, state-machine closure or campaign completion.

## Required next runtime tests

1. Capture natural state0/2-to3 and nonzero request; compare original sound call arguments, request clearing and descriptor+5 changes, including neighbor propagation.
2. Capture mode6 request and strategy1 alignment/motion/transition with original helpers; test both axes.
3. Bind state0..4 to original update/animation producer0000:0052 and callers, including who creates state4. Compare original early DOS state4 contexts rather than only synthetic seeds.
4. First-write trace DS:D00C/D10C initialization and unresolved contextual references. Keep PASS1 UNKNOWN bytes unresolved until reproducible evidence supplies a type/use or genuine padding proof.
