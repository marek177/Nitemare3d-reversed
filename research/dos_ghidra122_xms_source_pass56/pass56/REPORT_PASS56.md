# Pass56 — negative-offset cache source and rounded XMS move descriptor

## Finding
Confirmed, High: the cache's nonpositive-offset branch builds an XMS move request from a stored handle to conventional memory. Requested length is rounded up to a1024-byte multiple. The original wrapper converts driver failure AX0 into DX=(BL<<8), and its caller tests signedDX<0 to enter the fatal handler.

1344 scenarios pass across six distinct supplied DOS images. Both the original rounding/descriptor helper and original indirect-driver wrapper execute. The driver call itself is mocked and fatal handling stops at entry. No XMS manager or actual data copy is executed. Supplied1.8/1.9 are duplicate EXE images.

## Versioned evidence
| DOS | Rounded helper | Driver wrapper | Descriptor offset in scratch segment |
|---|---|---|---|
|1.0|1739:0266|1739:066a|0000|
|1.1|1742:034c|1742:07fa|0200|
|1.2|1742:0358|1742:0806|0200|
|1.5|1747:0356|1747:0804|0200|
|1.7|1751:0352|1751:0800|0200|
|1.8/1.9 supplied|1767:0356|1767:0804|0200|

Exact cross-version wrapper locations, globals, executable hashes and instruction bytes in xms.json are authoritative; the table is generated from these locations during packaging. Twelve diagnostic C outputs and instruction exports come from a fresh Ghidra12.2 read-only opening of pass54's full runtime-image project.

## V1.9 descriptor and source chain
Cache1767:0720–076e takes the alternate branch for resource source_offset<=0 and passes its two's-complement negation to helper1767:0356. For the normal negative-offset case, this supplies the magnitude. Resource IDs/assets and actual stored-handle allocation are not recovered here.

1767:0356–03d3 takes destination far pointer, source offset32 and length16. Scratch segment is loaded from DS:255e, XMS source handle from DS:3504. It writes this16-byte descriptor at scratch:0200:

| Offset | Width | Field | Verified value/model |
|---|---:|---|---|
|+0|4|transfer length|ceil(length/1024)*1024|
|+4|2|source handle|word DS:3504|
|+6|4|source offset|raw32-bit helper argument|
|+10|2|destination handle|0|
|+12|4|conventional destination|segment<<16 OR offset|

Original wrapper1767:0804–082b loads descriptor DS:SI, sets AH0b, and calls the far entry through game-data ES:[350c]. Its DS and SI are restored after the boundary returns. In the test fixture the scratch segment is5000, source handle1234, destination6000:0200. These are synthetic values, not recovered runtime allocations.

## Error result model
Confirmed from instructions and original-code runs:
```
call_driver(AH=0x0b, DS:SI=descriptor)
if driver_AX != 0:
    result_AX = driver_AX
    result_DX = 0
else:
    result_AX = 0
    result_DX = driver_BL << 8
restore_DS_and_SI()
if signed16(result_DX) < 0:
    fatal(...)
```
Thus AX0/BL80 and AX0/BLff trigger the caller's fatal branch; AX0/BL00 or BL7f do not. Nonzero AX with BL80/ff bypasses that branch. The low-error-code and unusual nonzero-AX cases probe bit-level behavior; they do not establish that a real driver returns those combinations. Do not simplify the caller to an AX==0 failure test when reproducing its exact behavior.

## Matrix and edge cases
6 builds x8 lengths x4 source offsets x7 driver responses=1344 scenarios. Lengths0,1,1023,1024,1025,8191,8192,65535. Offsets0,123,65536,ffffffff. Driver(AX,BL): (1,0),(1,ff),(ffff,80),(0,0),(0,7f),(0,80),(0,ff). Full descriptor bytes, AH, descriptor DS:SI, AX/DX, fatal condition, restored DS/SI and successful return CS/SP are asserted.

1023 and1024 both request1024 bytes;1025 requests2048;8191 and8192 request8192. Zero requests zero. The direct helper probe65535 requests65536, including the descriptor high word; it lies outside the cache's <=8192 accepted-size contract. Within that contract, the rounded transfer never exceeds8192. Actual XMS bounds/errors and padding contents are Unknown; the extra rounded bytes must not be assumed to be audible sample content.

## Decompiler limits
Generated C is diagnostic, not a verified specification. Current C aliases dynamic ES writes to static DS string labels and does not correctly model the wrapper's DX:AX status return in its caller (a stale high-word variable appears in the conditional). The assembly and original-code tests establish the descriptor and signed-DX branch independently. No project interfaces or bytes were changed in this pass. Next: apply the verified custom wrapper return ABI and represent dynamic scratch memory, then check the decompiler condition against these traces.

## Outcome
The two cache backing paths are now distinguished: positive offsets use the SND.DAT routine from pass55; nonpositive offsets invoke the rounded extended-memory transfer path through this helper. Confidence High for the local descriptor/register/state model. Actual XMS allocation lifecycle, asset reachability and complete audio/game1:1 parity remain Unknown.
