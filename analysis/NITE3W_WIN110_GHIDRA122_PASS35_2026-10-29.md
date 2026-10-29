# Win16 1.10 — Ghidra12.2 pass35: linear column table consumer

## Finding
Confirmed High:1010:366A consumes the recovered byte/WORD tables as clipped source start and fractional phase for a textured vertical column.720 original-routine cases match the complete65536-byte controlled destination buffer. Optional palette remapping is included. This is controlled memory rendering, not actualWinG or full-game pixel parity.

## Evidence
|Status|Claim|Source|Confidence|
|---|---|---|---|
|Confirmed|idx=2*(bottom-53EE)+1; signedbottom>=53EA selects clipping|3679..36A3|High|
|Confirmed|Clipped branch usesBYTE2C7E+idx andWORD2E7E+2idx|36CD..36D8|High|
|Confirmed|StepDWORD comes from247E+4idx; sourcecolumn offset=column*64|36A8..36C3|High|
|Confirmed|Destination uses selector51A0,lowBYTEstartY×320+x; rowstride320|36DD..36EE,371B|High|
|Confirmed|Optional remap usesSS:8094 lookup and fractionalADD/ADC sourceadvance|3728..3742|High|
|Confirmed|ReturnsAX1 for testedpaths|3746..374C|High|
|Unknown|Actualcaller input constraints and planar output|Excluded|Low|

## Behavior model
If bottom<53EA,startY=bottom-idx,count=idx+1; otherwise startY=53E8,count=53E2 and use clipping table offsets. Source starts at suppliedfarbase+column*64. Table byte adds integer source advance and tableWORD seeds fraction. Each outputbyte is sourcecolor or palette[sourcecolor]. Destination advances320; source advances highWORD(step) plus carry from fraction+lowWORD(step). This establishes a direct use for the2960 tables without assuming their meaning from formulas alone.

The routine initializes only lowBYTE of localflag atBP-8 but compares its fullWORD at36C8. Highbyte0/1 fixtures were tested. They change whether table access occurs for unclippedcases, but produced no outputdifference in thisfixture range because relevant starttable values arezero. No claim of reachable rendering defect follows. Clipped branch alwayssets lowbyte1. The apparent optimization test at3702 branches to the immediatelynext instruction and does not create multi-column writes in thislinear routine.

## Verification
EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.93 native instruction encodings checked.720 cases=bottom81..170 ×remap0/1 ×stackflaghigh0/1 ×sourcecolumn0/3. Geometry supplied for304×152 viewport,top4,bottom155,centerY80,x23. TestCS2000,DS=SS1048,source5000:0,destination7000:0. Source64KB deterministic pattern and reverse256-byte palette. Step and clipping tables supplied independently from recovered formulas; original2930/2960 not executed here. No helperstubs orOS hooks. Entire64KB destination,AX,SP,DS,BP checked. Test preserves16-bit pointerwrap and uses originalinstructions forADD/ADC and paletteXLAT.

## Implementation-ready findings
Use clipping table pairs to seed integer/fractional source position before linear column iteration. Preserve lowBYTE startY behavior and16-bit pointerwrap. Distinguish these controlledpixel results from hardware framebuffer/WinG parity. Planar3E44 statically shows analogous table reads andVGAplane writes, but has not been executed in thispass.

## Unknowns and next test
Connect original2930/2960 generators to366A, auditcaller bounds, then executeplanar3E44 withVGAport/plane model. Fullgame rendering and firstframe afterLOAD remainopen.1551internalentries retainnative decompile success,310EXTERNALentries separate;1401undefined executablebytes remainunresolved.

## Confidence
High for testedlinearcolumn byteoutput, limited for actualgame/hardware behavior.
