# Win16 1.10 — Ghidra12.2 pass32: projection arithmetic and divide faults

## Finding
Confirmed High: all65536 width bit patterns were tested through original1010:E4B2 with53E2 supplied as the arithmetic-shift half of53E0, matching5208. WidthWORD0,1,FFFF yields zero denominator and original32-bitIDIV atE50C triggers a divide exception in Unicorn. No actualWin16 exception handling or UI reachability is established.

## Evidence
|Status|Claim|Source|Confidence|
|---|---|---|---|
|Confirmed|First divisor is20480; signed16 width×12000 forms signed32 numerator|E4B4..E4CC|High|
|Confirmed|Second product is signed16 height×33600; storedDWORD then shifted left4 with32-bit wrap|E4D0..E4FA|High|
|Confirmed|Final division uses sign-extended wrapped32 numerator and prior quotient|E502..E50F|High|
|Confirmed|Fault cases0,1,FFFF occur after first threeDWORD stores;3A76 unchanged|Exhaustive original execution|High|
|Unknown|Whether malformed widths can enter through actual menu/config in a real run|UI/config reachability untested|Low|

## Behavior model
Let W=s16(53E0),H=s16(53E2)=W>>1 and trunc mean signed division towardzero. q=trunc(W*12000/20480); storeDWORD3A6A. p=H*33600; storeDWORD3A6E. n=wrap32(p<<4); storeDWORD3A72. Finally storeDWORD3A76=trunc(s32(n)/q). Whenq=0, originalIDIV faults before finalstore. No quotientoverflow was observed for any tested width under thisH relation.

Forwidth304,q178,p5107200,n81715200,result459074. Width320 givesq187,result459978. Width8192 yieldsn=-2092957696 andresult-436032 because of32-bit shiftwrap. Hostunbounded multiplication would differ. These malformed-width fixtures do not prove actual player-visible defects.

## Verification
EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.42 instruction encodings checked against nativeGhidra listing.65536 original-routine cases; no helperstubs. TestCS2000,DS=SS1048. Checks first12outputbytes for everyinput; finalDWORD and restoredSP/SI/DI for successfulreturns; interruptnumber0 and faultIP E50C plus unchanged finalDWORD forfaults. Harness recreates Unicorn after eachfault: reusing an interrupted instance initially produced a pending doublefault, which was a harnessstate issue and is excluded from finalresults. Errorhandling of an actualWin16 OS was notexecuted.

## Implementation-ready findings
Preserve signed16 input interpretation, signeddivision truncation and32-bit shiftwrap. Do not replace arithmetic with floatingpoint or unbounded products. Keep fault behavior distinct from UI validation policy; inputconstraints must be recovered before deciding which invalid configurations the remake should accept.

## Unknowns and next test
Execute2960 table builder and then full5208 chain withvalidUI widths. Trace UI/config validation and actualWin16 exception handling if fault reachability is demonstrated. Renderer/pixelparity and firstframe afterLOAD remainopen.1551internalentries retainnative decompilationsuccess;310EXTERNALentries separate.1401undefinedexecutablebytes remainunresolved.

## Confidence
High for exact arithmetic and controlledprocessor faults, limited for fullgame consequences.
