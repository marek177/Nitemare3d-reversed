# Win16 1.10 — Ghidra12.2 pass31: configuration viewport arithmetic

## Finding
Confirmed High: original1010:5208 arithmetic prefix derives nineWORDs from globalWORD4BD4. All65536 input bit patterns passed original-instruction microexecution against an independent wrap-aware model. Prefix has no range guard; next projection/table helpers are excluded. Renderer semantics of these geometric fields are inferred from formulas and callers, not pixel-parity evidence.

## Evidence
|Status|Claim|Source|Confidence|
|---|---|---|---|
|Confirmed|Input is globalWORD4BD4, not stack argument|5208,5213,521D|High|
|Confirmed|Signed shifts and16-bit subtraction wrap precede derived coordinates|520B..5250|High|
|Confirmed|NineWORDs53E0..53F0 are written, neighboring sentinelWORDs unchanged|65536 cases|High|
|Confirmed|No local range validation before E4B2 and2960 calls|5208..525E|High|
|Inferred|Fields describe viewport dimensions,bounds and center|Formulas and subsequent projection rebuild|Medium|
|Unknown|Allowed UI width range and downstream behavior of malformed widths|UI and callees excluded|Low|

## Behavior model
Let s16 interpret the lowWORD as signed, and let every stored result wrap modulo65536. Compute H=s16(W)>>1; L=s16(320-W)>>1; T=L>>1. The second shift forT acts on already shiftedL; do not replace wrap-sensitive arithmetic by unrestricted host division.

|Address|Exact local value|
|---|---|
|53E0|W|
|53E2|H|
|53E4|L|
|53E6|L+W-1|
|53E8|T|
|53EA|T+H-1|
|53EC|L+H|
|53EE|T+(H>>1)|
|53F0|53EE<<4|

ForW304: dimensions304×152,boundsx8..311,y4..155,center160/80,scaledY1280. ForW319:center159/79;W320:center160/80. W321 producesL=T=FFFF. W0 produceswidth/height0 but right159,bottom79, so do not infer a valid drawable rectangle for arbitrary input. Negative bit patterns are arithmetic fixtures, not established reachable UI values.

## Verification
EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.27 instruction encodings verified against native Ghidra listing. Original bytes5208..5253 execute underCS2000,DS=SS1048; no helper stubs. Stop5254 beforeE4B2. Exhaustive65536 inputs checkall18 outputbytes and2-byte sentinels on each side. No projection table rebuild, floating-point approximation or gameplay runtime used.

Static callees: E4B2 derives projection values at3A6A/3A6E/3A72/3A76 with division;2960 rebuilds arrays2C7E/2E80. Their semantics and boundary failures are not closed by this prefix test. The decompiler's default scalar widths must not replace raw16-bit SAR/SUB behavior.

## Implementation-ready findings
Use explicit signed16 interpretation, wrap subtraction before shifting, and truncate stores. For short config reads, the possibly mixed firstWORD flows into these exact formulas in5208; integration with its callees remains untested. Preserve actual global input use even when caller also pushes a widthWORD.

## Unknowns and next test
ExecuteE4B2 with original arithmetic helpers and identify zero-divisor inputs; then2960 output tables. Establish valid UI range and actual first render after configuration/load.1551 internal entries retain native decompile success,310 EXTERNAL entries separate;1401 undefined executable bytes remain unresolved.

## Confidence
High for exhaustive local arithmetic. Medium for viewport naming; no pixel or full-frame parity claim.
