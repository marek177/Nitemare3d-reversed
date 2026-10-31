# Pass95 — native clock-source branches and zero-baseline behavior

## Finding
Confirmed, High confidence in isolated original-byte execution: all six distinct supplied DOS EXEs implement the same two clock-source branches and baseline behavior. Labels1.8/1.9 share an identical binary. 216 sequences /648 native calls pass. BIOS data values and the CRT structure producer are modeled; no real clock-frequency or OS-time accuracy is claimed.

| Build | Native clock function |
|---|---|
|1.0|1b91:001c|
|1.1|1bb2:0014|
|1.2|1bb2:0016|
|1.5|1bba:001c|
|1.7|1bc4:0018|
|supplied1.8/1.9|1bda:001c|

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
|Confirmed|A==0 and mode!=0 selects BIOS-area arithmetic|Original two CMP/conditional branches;216 sequences|High|
|Confirmed|BIOS reads separate words0040:006c/006e, subtracts stored32-bit baseline and multiplies55|Native instruction bytes and returned DX:AX|High|
|Confirmed|Other branch calls CRT, multiplies structure dword+0 by1000 and adds unsigned word+4|Native caller execution with synthetic structure|High|
|Confirmed|Baseline0 means uninitialized and is replaced by current BIOS-area value|Three consecutive calls with initial baseline0 and ticks0/1/2|High|
|Unknown|Physical accuracy/units/update frequency and actual CRT epoch conversion|Hardware and CRT internals not executed|Unverified|

## Behavior model
Define unsigned32 tick T from the two BIOS-area words and saved baseline B. For A0/mode!=0: if B==0 set B=T; result=wrap32((T-B)*55), returned in DX:AX. B is retained between calls. A nonzero B is not reset when T falls below it; subtraction underflows modulo2^32. No special day-rollover compensation is present in this function. Tests do not establish how a real BIOS updates T.

For all other flag combinations: call original CRT target with a local structure pointer; result=wrap32(dword[0]*1000+word[4]). The harness supplies these two fields, not CRT time acquisition. Field names seconds/milliseconds are plausible from surrounding CRT date/time code but are not independently proved by this isolated caller test; exact fields/operations above are implementation-ready. No timezone or epoch assumption is needed for verified arithmetic.

Zero baseline corner: initialB0,T0 returns0 and leavesB0; nextT1 initializesB1 and returns0 again; nextT2 returns55. A literal zero baseline cannot be distinguished from uninitialized state. Separate word reads have no observed CLI/atomic snapshot protocol here; torn-value consequences are not tested or asserted.

## Link to pass94 counter reader
Prior Ghidra12.2 counter-reader listings show mode!=0 returns cached DX:AX without calling this function; mode0 calls this function, writes returned AX/DX to cache, then returns it. Because mode0 necessarily selects the CRT branch in this native function, the BIOS branch cannot be reached through that reader under an unchanged mode global. That is a conditional static chain, not a claim that the mode can never change asynchronously. Other direct callers and cached-global writers remain to be audited. Therefore the synthetic cached values in94 must not be relabelled as BIOS ticks from this evidence alone.

## Verification / provenance
216 sequences =6 binaries ×2 A flags ×2 mode flags ×3 initial baselines(0,123,ffffffffh) ×3 tick profiles[(0,1,2),(100,101,99),(fffffff0h,16,17)]. Each sequence calls native function three times with persistent baseline memory. On CRT branches, three synthetic structures are(dword0,word4)=(0,0),(1,999),(ffffffffh,65535), covering carry/wrap and unrestricted field fixtures. Assertions require exact DX:AX, branch call count, baseline state and restored SP.

Original runtime MZs and Ghidra project dependencies were restored from pass94 after workspace maintenance. Native clock bytes were recovered with Capstone5.0.7 from the relocated EXEs; Unicorn2.1.4 executes unchanged bytes. Per-build SHA256, all instructions, flags/baseline/call addresses and traces are included in clock_tests.json. No function bytes are patched. The sole call mock is CRT structure producer. BIOS-area reads use explicit memory fixtures. DS=SS,SPe000.

Prior helper TSVs are copied from94 and retain their provenance. No fresh Ghidra decompilation is claimed in95: the executable Ghidra runtime was removed by workspace maintenance; the native project and input dependencies were recovered. Included ExportXmsLifecycle.java and seeds.tsv permit a fresh clock export in Ghidra12.2 once its runtime is restored. This does not block the native arithmetic/branch evidence, but full CRT/OS runtime and decompilation completeness are not inferred.

## Reproduce / next
Extract the included pass76 dependency then nested baseline58 dependency into baseline58/. Run python scripts/verify_native_clock_source.py with Unicorn2.1.4/Capstone5.0.7; expected36 sequences per distinct binary. Keep pass95 source_counters.json with the script. The script regenerates all clock evidence from original bytes.

Next execute original CRT structure construction down to modeled DOS date/time calls and trace cached-global writers. This can establish actual units and epochs without guessing from constants. Real hardware clock accuracy, concurrent update consistency, wall-clock adjustments and complete parity remain Unknown.
