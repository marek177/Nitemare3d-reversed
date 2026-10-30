# Pass93 — calibration-derived writers of input limit globals

Confirmed, High confidence in isolated native tail execution: both SI/DI source words from92 are written by the same post-measurement routine in each supplied distinct DOS binary. Original arithmetic executes in378 cases. Supplied1.8/1.9 are identical. Measurement acquisition, rendering/timer behavior and full startup are not executed, so real runtime bounds are not yet established.

| Build | Writer function |
|---|---|
|1.0|1b91:019e|
|1.1|1bb2:0196|
|1.2|1bb2:0198|
|1.5|1bba:019e|
|1.7|1bc4:019a|
|supplied1.8/1.9|1bda:019e|

## Exact executed post-measurement formula
M is unsigned32 local BP-4; R is signed16 global divisor (supplied1.8/1.9 DS3cc2). Original IDIV computes q=trunc_toward_zero(1000/R), then CWD sign-extends q before unsigned32 comparison against M. Define wrap32 and low16 explicitly:

A = unsigned_max(M, unsigned32(sign_extended_q))
T = wrap32(A+2) >> 2
SI_source = low16(T), except T==0 forces1
D = floor(wrap32(A*360+1400)/2800)
DI_source = low16(max(D,1))
extra_source = wrap16(2*SI_source)

The32-bit MUL high half is discarded before division: EDX is cleared. SI minimum check tests the full shifted32-bit value before storing only AX. Hence these are not saturated16-bit results and broad unsigned input fixtures can wrap. R0 raises CPU divide exception0 in this tail. Negative R fixtures sign-extend a negative q into a large unsigned minimum when q!=0; no claim is made that real startup intentionally supplies negative/zero R.

For nonnegative A without relevant overflow/truncation, SI_source=max(1,floor((A+2)/4)); DI_source=max(1,floor((A*360+1400)/2800)). Those simpler forms must not replace full wrap behavior outside their valid domain.

## Measurement stage: static only
Fresh Ghidra listing/C shows preceding repeated helper calls, two counter snapshots and unsigned32 difference divided by10. A conditional second ten-iteration sequence includes a different helper, then tail derives these globals. This suggests calibration/timing provenance (Inferred, Medium), but physical units, timer scale and actual measurement range remain Unknown until those helpers are analyzed. No FPS or milliseconds identity is assigned merely from constants1000/360/2800.

Recovered Ghidra direct references identify this writer for both globals; indirect or missed writes are not excluded. Source globals are beyond file-backed bytes in at least one supplied runtime MZ: their initial runtime values cannot be read directly from EXE payload. Do not infer valid initial values from zero-filled emulator mapping; these tests explicitly provide tail inputs and observe resulting writes.

## Verification
378 cases =6 binaries ×9 M values(0,1,10,64,65,1000,65535,65536,ffffffffh) ×7 R values(0,1,18,70,1000,-1,-32768). Native execution begins at MOV AX,1000 immediately before rate IDIV, ends before POP SI/LEAVE/RETF, with BP-4 measurement explicitly set. No calls or mocks occur in this block. Assertions compare all3 written words to independent wrapped formula, or require trap0 for R0. DS=SS,BPd000,SPc000. Prior ratio outputs and earlier measurement guards are deliberately outside execution; this is not a whole-function run.

Evidence calibration_tests.json includes exact SHA256, entry/stop/rate/output globals. source_limits.json records original92 metadata. Fresh Ghidra12.2 writer decompilation succeeds for all6 builds; full reference inventories and other consumers are included. Some surrounding input collector exports still fail as documented92; writer success does not fix that CFG.

## Reproduce / next
Extract included pass76 dependency and nested baseline58 to baseline58/. Run python scripts/verify_calibrated_input_limits.py with Unicorn2.1.4 and included pass93 evidence; expected63 passed per binary. ExportConfigReferences.java/seeds reproduce read-only global-reference and containing-function exports in Ghidra12.2/JDK25.

Next analyze counter/read and repeated measurement helpers, rate-global producers and keyboard flag origin, then execute complete calibration. True runtime argument ranges, physical units, hardware behavior and whole-game parity remain open.
