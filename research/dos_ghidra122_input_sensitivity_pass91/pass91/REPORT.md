# Pass91 — native Mouse/Joystick sensitivity helpers, 16-bit arithmetic and callsites

Confirmed, High confidence in original isolated helper execution: six distinct DOS binaries implement the same Mouse/Joystick helper formulas. Supplied1.8/1.9 are identical. No function calls, hardware or OS interrupts are mocked inside these helpers. The meaning of the argument units and actual input ranges at each caller remains Unknown.

## Exact arithmetic
Let S be unsigned sensitivity byte; a,b are signed16 arguments. Let s16(x) wrap to16 bits and reinterpret signed. Mouse divisor K=50, Joystick K=200:

p = s16(S*b)
q = trunc_toward_zero(p/K)
bound = s16(2*a)
result = signed_min(q,bound)

Original IMUL produces DX:AX, but CWD immediately replaces DX by the sign extension of low AX before IDIV. Therefore the full multiplication result is discarded. This must not be replaced by a32-bit multiplication/division in a parity implementation. Original ADD CX,CX also wraps the bound. Comparison JLE is signed; no lower clamp or absolute-value operation exists in either helper.

Example present in tests: S100,b1000 gives low product86a0h = -31072. For a100, Mouse result -621 and Joystick -155, despite all input values being positive. These are explicit arbitrary-word boundary fixtures; no game-visible negative-motion bug is inferred without proving actual caller ranges. In nonoverflow positive domain, formula reduces to min(floor(S*b/K),2*a), but that simplification must retain its domain restriction.

| Build | Mouse helper | Joystick helper |
|---|---|---|
|1.0|1681:05a2|1681:05c0|
|1.1|1689:05a6|1689:05c4|
|1.2|168a:05a2|168a:05c0|
|1.5|168f:05a0|168f:05be|
|1.7|1699:059c|1699:05ba|
|supplied1.8/1.9|16af:05a0|16af:05be|

## Verification
4536 cases =6 binaries ×2 helpers ×6 sensitivity bytes(0,1,50,100,128,255) ×7 first args(-32768,-1,0,1,100,16384,32767) ×9 second args(-32768,-1000,-1,0,1,100,257,1000,32767). Assertions compare native AX to independently calculated signed wrapped formula and require normal return/restored SP. Original relocated MZ bytes execute unchanged under Unicorn2.1.4. DS=SS,SPe000; sensitivity byte explicitly set. No actual mouse/joystick state is read by these functions. Exact EXE SHA256/global locations retained in input metadata.

## Caller evidence and limits
A static original instruction-audit scan finds7 direct Mouse callsites and6 direct Joystick callsites per binary (78 total). direct_callers.json retains six instructions before and two after each call, using exact E8 signed displacement or9a far target decoding. This is an inventory of available decoded direct calls, not proof of no indirect or missed callers.

Supplied1.8/1.9 Mouse16af:0423 pushes first arg100 and an original absolute-value calculation as second, then compares result against10. Other Mouse sites within the input routine use SI as first arg and coordinate differences as second. Joystick16af:0a4c negates a local value and forwards it with SI. Their ranges, SI origin, signed special cases and application to movement remain unverified. Do not name these arguments tick count, speed or pixels merely from helper formula.

Fresh Ghidra12.2 exports decompile both helpers per binary (12 functions) and preserve original instruction bytes. This corroborates local arithmetic but does not prove complete surrounding input recovery.

## Reproduce / next
Extract included pass76 dependency and nested baseline58 to baseline58/. Run python scripts/verify_input_sensitivity.py with Unicorn2.1.4 and pass91 input_locations.json:756 passed per binary. Included Ghidra script/seeds reproduce read-only exports against pass76/project N3D_Runtime54/inputs.

Next trace SI and raw deltas in the surrounding native input collector, then enabled/disabled branches and device calls. Hardware input, scheduler timing, movement effect and full parity remain open.
