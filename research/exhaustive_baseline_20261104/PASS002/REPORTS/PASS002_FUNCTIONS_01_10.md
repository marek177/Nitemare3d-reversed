# PASS002 — deep static analysis, functions 1–10

Ten individually numbered dossiers preserve exact bytes, decoded reachable ranges, CFG/basic blocks, direct callsites, instruction register/FLAGS/operand metadata, memory expressions, stack effects and hand pseudocode. This batch combines eight DOS functions and two Win16 functions. It is a focused batch, not a claim that these are the game's canonical first ten functions.

## New established evidence

- DOS0476:0326: the previously unresolved switch at0398 reads24 word entries atCS:039E..03CD. The full256-value selector domain is proven by unsigned guard afterCBW/subtraction. There are16 distinct targets; local closure increases69→159 instruction rows. The table is DATA, not code. All24 case effects are mapped separately.
- DOS0201:001A: 111 instructions, mixed16/32-bit signed fixed-point arithmetic on an18-byte caller record; recovered slope, endpoint values and fractional start, preserving wrapped16-bit differences and signed truncation. One input class causes real#DE: wrapped dx=-1 anddy=-32768 in firstIDIV. This is observed in isolated CPU execution, not assumed safe.
- DOS0201:012E: source table scan emits18-byte spans and invokes001A with two endpoint dwords. Error string is"MAXSEG exceeded (%d)". Output base4D6E differs from the100-slot initializer base50F2; shared stride does not prove same list.
- DOS0476:0078: debug.txt writer with first-write"w" and later"a" mode; file handle retained as sentinel after close. Helper library names remain inferred until deeper review.
- Startup prefix establishes DS=0x3771 at load_base0x1000, module-relative0x2771, under explicit syntheticDOS services. This does not propagate through unverified callees to the initializer.
- Win16 getters0003:0D9E and0DA4 return byte fieldsDS:4BE1/4BE2 zero-extended toAX and alterFLAGS viaSUB AH,AH. Adjacent getters are not the same field.
- Capstone5.0.7 in16-bit mode prints unprefixed98/99 asCWDE/CDQ. Original raw output retained; correctedCBW/CWD and register effects are attached and independently cross-checked with objdump and CPU behavior. PASS001 raw metadata remains historical, not silently rewritten.

## Experiments and limits

1,006 arithmetic-model cases,512 exhaustive getter cases,1,024 dispatch cases and1 synthetic startup-prefix experiment pass:2,543 new experiments. Of1,006 arithmetic cases, one deliberately expects#DE; remaining1,005 verify the entire64KiBDS region plus return/preserved-state properties. These are not original gameplay tests. Static-boundary completeness still requires alternate-entry,alias and caller-context proof; no fully exhaustive function-completion claim.

RAW Ghidra/IDA decompilation remains unavailable. Corrected pseudocode is explicitly hand reconstruction, with address comments. Cross-version signature locators retain UNKNOWN_MATCH where uniqueness/identity is not established; missing signatures never imply ADDED/REMOVED. A complete subsequent pass must recover cross-version CFGs at located functions before semantic classifications.

## Numbered function batch

|No.|Function|Instructions|Decoded bytes|Span bytes|Blocks|Local unresolved jumps|
|---|---|---:|---:|---:|---:|---:|
|1|DOS_2_0_0201_000A|6|16|16|3|0|
|2|DOS_2_0_0201_001A|111|272|275|10|0|
|3|DOS_2_0_0201_012E|66|177|177|14|0|
|4|DOS_2_0_0476_0326|159|441|496|46|0|
|5|DOS_2_0_0476_00CE|66|195|195|22|0|
|6|DOS_2_0_0476_0078|30|85|85|11|0|
|7|DOS_2_0_0476_0000|24|94|94|3|0|
|8|DOS_2_0_0768_0008|2|4|4|1|0|
|9|WIN_1_10_0003_0D9E|3|6|6|1|0|
|10|WIN_1_10_0003_0DA4|3|6|6|1|0|

See BATCH_01_10/ for ten25-section dossiers and per-instructionCSVs. Exact ranges are in FUNCTIONS_01_10_BOUNDARIES.csv; holes include padding/data and are not forcibly assigned as function instructions. CFG continuations aftercalls assume return and remain conditional on each callee's behavior.

Reproduce from the package parent directory: `python N3D_FUNCTION_RESEARCH/PASS002/TOOLS/batch10.py` after installing the pinned Capstone/Unicorn versions fromPASS001. Outputs are deterministic apart from generated filesystem metadata.


## Independent boundary and cross-version checks

GNU objdump independently matches all470 decoded instruction boundaries and bytes across the10 local bodies. This verifies decoder agreement, not all possible entry points. The math helper has111 instructions and identical relative CFG in all9 recovered DOS snapshots; differing instructions only read a relocated DS origin word. Exact instructions and the mapping are retained in ASM_DIFF/math_helper_cross_version_CFG.json and INSTRUCTION_LEVEL_DIFF_PASS002.csv. Both Win getter bodies have changed absolute field addresses in earlier builds, while opcodes, local CFG and FLAGS behavior remain the same; whole-program field identity remains open. Available-neighbor comparisons are in ADJACENT_VERSION_DIFF.json.
