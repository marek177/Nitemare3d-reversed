# Win16 1.10 — Ghidra12.2 pass33: table builder2960

## Finding
Confirmed High: original2960 builds511 byte entries and511 WORD entries using signed32 division after16-bit intermediate truncation.326 complete routine executions checked166586 entries and surrounding untouched bytes. No helpers were stubbed. Table consumers and rendered output remain untested.

## Evidence
|Status|Claim|Source|Confidence|
|---|---|---|---|
|Confirmed|Loop index i is DWORD1..511|2966,29B0..29B8|High|
|Confirmed|Height53E2 is signed16, subtracted from index; negative difference clamps0|2975..2989|High|
|Confirmed|Difference is shifted6 inCX16; highWORD of numerator comes from truncatedCX,lowWORD0|298B..2995|High|
|Confirmed|SignedIDIV by i then arithmetic32 shift1|2997..299A|High|
|Confirmed|Writes byte2C7E+i andWORD2E80+2*(i-1)|29A4..29AB|High|
|Unknown|Exact visible renderer role and valid input constraints|Consumers not executed|Low|

## Behavior model
Fori=1..511,H=s16(53E2),d=max(i-H,0). Let n=s32((((d<<6)&FFFF)<<16)). Thenv=trunc_signed(n/i)>>1. Storebyte(v>>16)&FF at2C7E+i; storeWORDv&FFFF at2E80+2*(i-1). Signed division truncates towardzero before the arithmetic shift. Do not combine these steps into one unsigned or unbounded expression.

Loop never uses divisor0. Entries end atbyte2E7D andWORD327C. Byte2C7E andgap2E7E..2E7F remain unchanged locally. Negative-height fixtures expose numerator wrapping; these are arithmetic tests, not established valid UI values. H511 and512 produce identical allzero entry payloads because everyi-H is nonpositive.

## Verification
EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.37 instruction encodings checked against nativeGhidra listing. Original2960..29BD,CS2000,DS=SS1048.326 heights:0..320 plus-32768,-1,511,512,32767. Eachrun compares1538-byte region2C7E..327F against independently constructed bytes, including sentinels. Checks far-returnIP,SP,BP,SI,DI.166586 entries checked; this is326 function executions, not166586 independent calls. No helperstubs,OS calls or game renderer.

## Implementation-ready findings
Preserve511-entry count, split byte/WORD storage,16-bit SHL truncation, signed numerator and two-stage division/shift rounding. Initial byte and gaps are not cleared by this routine; avoid inferring initialization elsewhere. Current evidence is exact table generation for tested heights, not a complete consumer specification.

## Unknowns and next test
Connect5208→E4B2→2960 in one original execution and audit consumers of2C7F/2E80. Verify valid UI width range and actualrender output.1551 internalentries retain native decompile success;310EXTERNAL entries separate;1401undefined executablebytes remain unresolved.

## Confidence
High for tested table bytes and local boundary behavior; limited for fullrender semantics.
