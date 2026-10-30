# Pass92 — input collector SI/DI limit producer and modifier precedence

Confirmed, High confidence in original sub-block execution: all six distinct supplied DOS binaries load SI and DI from two global words; flag20h doubles them with16-bit wrap; flag40h then overrides both to1. Supplied1.8/1.9 are identical. This identifies local provenance of the bound argument passed to sensitivity helpers in pass91, without asserting full collector execution or physical key identity.

| Build | Block entry | Flags byte | SI source word | DI source word |
|---|---|---|---|---|
|1.0|1681:07a8|DS3da8|DS43b2|DS43b4|
|1.1|1689:07ac|DS3eae|DS44b8|DS44ba|
|1.2|168a:07a8|DS3eae|DS44b8|DS44ba|
|1.5|168f:07a6|DS3e7e|DS4488|DS448a|
|1.7|1699:07a2|DS3ec0|DS44ca|DS44cc|
|supplied1.8/1.9|16af:07a6|DS3f50|DS455a|DS455c|

## Formula and meaning limit
For each source word g, output register =1 if flag40h, else s16(2*g) if flag20h, else g. Bit40h wins when both flags are present. No range check on source words in this block. Example g16384 with20h yields-32768. Actual producer ranges of these globals remain Unknown, so no game-visible overflow fault is inferred.

Original Mouse/Joystick callsites from91 pass SI as the helper's first argument; helper then computes signed wrapped2*arg1 as upper bound. The block therefore proves where that local register value is obtained and which modifiers change it. It does not establish tick/speed/pixel units, physical modifier keys or that every later path preserves SI unchanged. DI is also prepared here for neighboring movement/rotation paths; final target semantics remain open.

## Verification
1176 cases =6 binaries ×4 masks(0,20h,40h,60h) ×7 SI source words ×7 DI source words. Each source ranges -32768,-1,0,1,100,16384,32767. Native bytes execute from the first flag load through the final override; harness stops at following TEST before movement dispatch. No function calls or interrupts occur; none are mocked. Assertions compare original SI/DI against independent wrap/override formula and unchanged SP. Explicit DS=SS,SPe000, synthetic source/flag globals. Original EXE SHA256, exact block bytes/addresses and stop address included.

Block discovery searches decoded original instruction audit for flag20h, SI global load and final MOV DI,1, independently for each build. This is not an execution of full input collector or its entry branch. No input hardware or actor movement is tested.

## Ghidra recovery boundary
Fresh Ghidra12.2 full collector exports: DOS1.0 and1.7 decompile successfully;1.1,1.2,1.5,supplied1.8/1.9 report Low-level Error: Bad instruction count exceeded. Full TSV evidence is preserved, including failures. A successful isolated block experiment does not resolve those missing/misdecoded areas. Do not count this pass as complete recovery of the collector.

## Reproduce and next
Extract included pass76 dependency plus nested baseline58 to baseline58/. Run python scripts/verify_input_limit_producer.py with Unicorn2.1.4; expected196 passed per distinct binary. Included sensitivity_locations.json supplies previously established input code segment; baseline audit supplies native instruction lookup. Ghidra script/seeds reproduce full collector export attempt read-only against pass76/project N3D_Runtime54/inputs.

Unknown: writers/ranges/units of the SI/DI source globals, origin/physical meaning of flag bits, complete collector CFG and later register flow, hardware effects and parity. Next repair collector decoding around dispatch tables and trace writers of the two limit globals before claiming actual runtime bounds.
