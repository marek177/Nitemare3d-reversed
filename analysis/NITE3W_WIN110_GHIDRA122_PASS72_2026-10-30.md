# Win110 pass72 — A344 message wrapper ABI

## Finding
Confirmed / High: A344 replaces its first argument FFFF with the resource ID, dispatches through application virtual slot+54, and returns the virtual method's AX after destroying a temporary string. The evidence establishes the wrapper contract, not rendered UI or actual resource text.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Constructor0D08 receives local address BP-0C | A34D–A351 | High |
| Confirmed | Loader3250 receives that address and argument BP+0A | A356–A35B | High |
| Confirmed | Only first argumentFFFF is replaced with resource ID | A360–A366; all65536 first-argument values tested | High |
| Confirmed | Application pointer comes from DS081C; its first far pointer supplies virtual table | A369–A374 | High |
| Confirmed | Far virtual call uses ES:[DI+54] | A382–A384 | High |
| Confirmed | AX saved before0D8E cleanup and restored afterwards | A388–A394; all65536 method results tested | High |

## Behavior model
Entry argument words BP+6=first/context, BP+8=flags, BP+0A=resource ID. The semantic label context/help ID is Inferred / Medium; the exact numeric forwarding is Confirmed / High.

1. Construct temporary string at BP-0C through0D08.
2. Call3250(temporary,resourceID). A344 does not test its return value.
3. If first==FFFF, set first=resourceID.
4. Call application virtual slot+54. Stack words immediately before CALLF are application near pointer, first/context, flags, temporary.word0, DS.
5. Save AX, destroy temporary through0D8E, restore AX and caller SI/DI/BP, RETF6.

For pass71's handler calls, this yields effective first/contextF10A with flags1030 for memory exceptions; generic calls use contextF108/F109 with flags0010. Actual text and precise interpretation of those flags remain unresolved.

Static loader3250 calls3282 with a256-byte local buffer; nonzero returned length triggers0E26 assignment, and3250 returns a boolean. This pass does not execute3250 or prove which resource text is loaded.

## Verification
131,152 cases passed:65,536 first/context words at resourceF10A and flags1030;65,536 virtual return values at firstFFFF/resourceF108/flags0010;80 combinations of four first values, five resource IDs, and four flag values. The sample sets overlap deliberately and totals count executions.

Original A344 instructions execute. Four call sites are stubbed before dispatch:0D08 creates a synthetic string data pointer7200;3250 validates resource forwarding; virtual slot+54 checks all five stack words and ES/DI;0D8E models cleanup. All stubs consume only their declared argument words and skip the original CALLF. Nonvirtual stubs return AXDEAD to prove the wrapper does not use their return values; virtual result is controlled independently. The virtual call is intercepted before reading its target function pointer. No underlying virtual method, string allocator, resource loader or Windows API runs.

DS=SS1048 is intentional for near local string addresses; CS2000 maps NE1, synthetic application7000 has virtual table5000:6000. The complete A344 body except relocation-bearing direct CALLF bytes is checked against the preserved Ghidra12.2 native listing and raw executable. Direct calls are intercepted before their selectors are used, so no instruction patch is necessary. Original executable SHA256:12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.

Reproduce using `python3 pass72/verify_message_wrapper.py` with Unicorn2.1.4. No fresh Ghidra database mutation or real Win16 process execution occurred.

## Implementation-ready findings
Keep resource ID distinct from flags and first/context. Apply FFFF substitution before dispatch. Forward string as DS:dataPointer. Preserve virtual return across string cleanup. A344 itself continues even when the loader return indicates failure; the resulting string then depends on constructor/loader behavior, which this test does not establish.

## Unknowns and next test
Trace3282 to actual resource lookup and inspect the runtime application object's+54 method. Resolve failure-path text state by executing real0D08/3250/0D8E helpers under declared API boundaries. Confidence High for wrapper argument/return behavior; real text and UI behavior Unknown.
