# BSF pass19 — percent-command parser ABI, bounds and effects

## Finding
Confirmed across six distinct DOS images: the parser distinguishes B/C,b/c,d,o,p; numeric calls use `%i` for B/C/b/c and `%d` for o/p. Upper checks are signed and accept tested value-1. The parser clears graphic-record dword+6, returns a far pointer to the closing '%' or NUL, and updates a caller-provided column counter. Unknown commands are skipped rather than rejected solely for an unknown letter.

## Evidence
612 executions passed:6 numeric commands x8 injected values(-1,0,15,16,31,32,255,256) x conversion count0/1 x6 builds =576; plus6 textual control cases/build =36. Original full command parser executes. Numeric sscanf conversion and effect routines are mocked; the fatal handler is stopped before execution. Thus numeric lexical recognition by original sscanf is not tested: input digit text is1 while the hook injects the declared conversion result. Tests explicitly assert original format string and destination/source stack arguments.

Text controls:%x%,%d%,%q without closing delimiter,%1234567%,%12345678%,%%. Successful cases check returned DX:AX, column update,color byte,effect call count and arguments, far return/SP and DS. All cases check initial graphic-pointer clear at caller record+6. Effect outputs intentionally do not allocate a graphic, so bitmap output remains0; graphics loading/rasterization is outside scope. Fatal branches are observed and no handler code executes.

V1.9 entry1d25:1070, initial record clear1d25:1079, numeric calls1d25:10e5/1127/1157/1193/11d1/120f, scan bound1d25:1270. Exact per-build entries, call-site bytes and EXE hashes are in evidence/bsf_commands.json.

## Behavior model
Far-call arguments: command pointer dwordSP+4,color-offset wordSP+8,graphic-record-offset wordSP+10,column-offset wordSP+12. Outputs referenced by the latter offsets are near pointers in caller DS/SS configuration used by tests. Initial code clears graphic record+6..+9; increments source offset past initial '%' and increments column; copies8 bytes starting after command letter into a local numeric buffer.

| Command | Parsed format | Confirmed action after successful conversion |
|---|---|---|
| B | %i | Calls effect with words10,5,300,180,low8(value),0 |
| b | %i | Signed value<=15; lookup effect(value low8,0), then same six-word effect with returned AL |
| C | %i | Stores low8(value) directly into caller color byte |
| c | %i | Signed value<=15; lookup effect(value low8), stores returned AL into color byte |
| d | No numeric parse | Lookup effect(8), stores returned AL into color byte |
| o | %d | Signed value<=255; producer effect(value word,0,graphic-record-offset) |
| p | %d | Signed value<=31; producer effect(value word,graphic-record-offset) |

For B/b, the six-word effect is the same routine used by the page helper for its rectangular UI operations. Background/foreground labels are useful inferences from those call sites and color-byte data flow; exact palette mapping is not executed. For o/p, producer dependencies receive the record used by the layout's nonzero graphic-pointer branch, but actual object/bitmap index semantics remain unverified here.

B/C have no tested upper numeric rejection. b/c,o,p require conversion count exactly1 and apply their signed upper bound; -1 passes and is forwarded asff for byte consumers orffff for word producers. This proves a missing lower-bound check in the original parser, not runtime safety or real resource reachability for negative values. Conversion count0 takes fatal for all numeric commands.

After effect handling, scan from the command letter until '%' or NUL. A scanned count>=8 takes fatal. On success return that delimiter/NUL pointer in DX:AX and increment column again. For an unknown letter with n scanned non-delimiter bytes, initial column10 becomes12+n. Missing closing '%' is accepted when scan reaches NUL within the bound. `%%` returns the second percent with no effect. These statements concern parser code; caller behavior after returned NUL needs separate integration tests.

## Ghidra12.2 changes
Copied pass18 projects into pass19/projects. All6 parser entries already existed; renamed/typed them `ParseBsfCommand` with four explicit arguments and dword return DX:AX. Names are analytical, not source symbols. All6 target stock decompilations complete. Existing function inventory remains3479; no new entries removed/added. Instruction addresses/bytes match before/after. The eight unresolved candidate seeds remain retained. No global decompiler-count increase or parity percentage is claimed.

## Confidence and remaining tests
Confirmed/High for parser/control-flow/ABI under injected conversion/effect dependencies, bounded textual controls and Ghidra metadata. Unknown: original sscanf lexical/overflow behavior, actual palette values, o/p producer validation and graphic rendering, malformed data at unmapped boundaries, integrated layout continuation after malformed command. Full gameplay/render1:1 parity remains open; supplied1.8/1.9 still share one image.

## Reproduce
`/usr/bin/python3 scripts/verify_bsf_commands.py` with Unicorn. Inputs include pass7 EXEs/specs/instructions and pass18 layout call metadata. `python scripts/run_pass19_recovery.py` copies pass18 projects and applies the included Ghidra script with configured Ghidra12.2/JDK25. Updated projects,C,signatures/inventory evidence and logs are archived. Next execute original sscanf for valid command strings, then original o/p producers with actual resource tables.
