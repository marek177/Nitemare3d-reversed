# BSF pass20 — original sscanf and parser numeric integration

## Finding
Confirmed across six distinct DOS EXEs: original integer conversion distinguishes `%i` base detection from `%d` decimal parsing, and tested16-bit outputs wrap on overflow. With the actual converter executing, BSF parser signed upper-only guards accept converted negative words, including decimal32768 ->8000. This closes the conversion stub used in pass19 for the tested strings.

## Evidence
816 executions completed:204 standalone original sscanf cases without any hooks/stubs and612 original command-parser + sscanf cases with only effect dependencies mocked/fatal stopped. No DOS/graphics runtime is executed. Both suites use initial DS=SS=startup data segment and controlled SP=f800, leaving room for the original CRT stack allocator and its preserved bound global. The initial exploratory SP=e000 setup reached CRT stack-error output before conversion; it is not counted among completed tests. No executable patch or stack-check bypass is used.

Standalone:17 strings x%i/%d x6 builds. Strings:0,1,-1,+15,0x10,010,09,0Xf,leading-space12x,empty,x,+,-,65535,65536,32768,-32769. Original sscanf wrapper, strlen, scanner, integer conversion and stack allocator execute. Checks cover far return, SP/DS restoration, two destination canaries and equality of observed AX/output words across builds. The values are primary observations, not a separate modern-CRT conformance oracle. Output destination is seededbeef to detect no-conversion writes.

Integration: same17 numeric strings x commands B,C,b,c,o,p x6 builds =612. Command text is actual `%letter<number>%`; original parser copies its numeric buffer and calls original sscanf/CRT, which now runs fully. A code hook observes but does not bypass the conversion call/return. Tests assert returned conversion status/output word against the documented lexical model, parser success/fatal branch, color byte, effect calls/arguments, delimiter pointer, column count and return/guards. Color/rectangle/graphic producer helpers remain mocked. Fatal callee is not executed.

V1.9 sscanf21ea:27e8 ->scanner21ea:0d3a; corresponding wrapper entries/hashes are in original_scanf.json. Complete standalone observations and integration conversion results are in evidence. The parser remains1d25:1070 in V1.9.

## Observed conversion behavior
| Input | %i output | %d output |
|---|---|---|
| 0x10 | 0010 | 0000 |
| 010 | 0008 | 000a |
| 09 | 0000 | 0009 |
| 0Xf | 000f | 0000 |
| leading space12x | 000c | 000c |
| -1 | ffff | ffff |
| 65535 | ffff | ffff |
| 65536 | 0000 | 0000 |
| 32768 | 8000 | 8000 |
| -32769 | 7fff | 7fff |

All rows above return conversion count1; output values are hexadecimal16-bit words. Original standalone empty input and sign-only + or- return AX=ffff and preservebeef. Standalone x returns0 and preservesbeef. These results do not imply arbitrary-width overflow semantics beyond the samples. In parser integration, the closing percent supplies an additional nonnumeric character; failed numeric strings are required to return a status other than1 and take the parser fatal branch.

Because parser bounds compare signed16-bit words, converted8000/ffff pass limits15/31/255. For byte consumers only low8 is forwarded; o/p producers receive the full negative word. Conversely -32769 wraps to positive32767 and fails these upper bounds. Graphic safety for such indices is not established because producers are mocked.

## Ghidra12.2 changes
Copied pass19 projects into pass20/projects. Added analyst label/signature `SscanfNearString`: near input offset wordSP+4,near format offset wordSP+6,near destination offsets in variadic stack arguments, signed16-bit AX return. This replaces the prior misleading void/guessed prototype. Updated parser evidence comments to distinguish original conversion execution from still-mocked effects. Each build exports sscanf and parser stock C (12 completed targets), explicit return/parameter storage and unchanged instruction/function-entry inventory hash. Existing entry count remains3479; no global decompiler-count increase or parity percentage.

## Confidence and unknowns
Confirmed/High for tested integer strings, near-string ABI and original parser integration. Unknown: all scanf formats/floats/field widths,longer or unmapped input,full32-bit or extreme-length numeric overflow,actual color/graphic producers,integrated framebuffer and game caller reachability. Supplied1.8/1.9 remain identical. Full1:1 gameplay/render parity stays open.

## Reproduce
`/usr/bin/python3 scripts/verify_bsf_scanf.py` and `/usr/bin/python3 scripts/verify_bsf_commands_original_scanf.py` with Unicorn. Inputs include pass7 EXEs/specs/instructions,pass18 layout metadata and pass19 parser metadata. `python scripts/run_pass20_types.py` updates copies of pass19 using configured Ghidra12.2/JDK25. Updated projects,C,storage audits,hashes and logs are archived. Next execute original o/p graphic producers against actual resource tables, then layout/bitmap integration.
