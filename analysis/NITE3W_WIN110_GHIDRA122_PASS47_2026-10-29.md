# Win16 1.10 — Ghidra 12.2 pass47: GDI palette controller

## Finding
Confirmed, High within controlled boundaries: 288 original31AA controller executions establish mode2 call guards and argument order, plus bypass behavior for modes1/3/FFFF. Windows imports and3100 are intercepted before CALLF. This does not establish actual GDI side effects.

## Evidence
|Status|Claim|Source|Confidence|
|---|---|---|---|
|Confirmed|Mode2 ANIMATEPALETTE iff handle00BE nonzero|1010:3327..333E,72 mode2 cases|High|
|Confirmed|Stack arguments nearest SP: offset,SS,count236,start10,handle|Original pushes and call-site capture333E|High|
|Confirmed|Mode2 calls3100 iff byte46AF zero, independently of handle|3343..334A, all guard combinations|High|
|Confirmed|Modes1/3/FFFF bypass conversion, ANIMATE and3100|31D7..31E4,216 cases|High|
|Confirmed|All tested modes call GETDC and RELEASEDC; saved registers restored|31AA..335E with specified stubs|High|
|Unknown|Windows/3100 cache writes, rendering, real import failures|Not executed|Low|

## Behavior model
For every tested mode the routine creates a local palette buffer and obtains a DC. Mode2 converts236 RGB entries as pass46 established. With nonzero00BE it requests animation of entries10..245. Independently, zero46AF invokes3100 even when00BE is zero. Static3100 begins with its own nonzero00BE guard; its body was not executed here. RELEASEDC receives capturedDC2468 and window1357. Modes1/3/FFFF proceed directly to release after initialization. Mode0 is excluded.

## Verification
288 cases =4 modes ×3 handles(0/1/FFFF) ×3 reserve-byte values(0/1/FF) ×4 cache flags(0/1/80/FF) ×2 synthetic return values(0/FFFF).72 cases are mode2. Seed47 supplies768-byte palettes and16 cache bytes. Original EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. All non-CALLF instruction encodings in31AA match raw source.13 CALLF encodings are normalized to the native Ghidra listing; this is declared relocation normalization, not raw-byte identity. Only selected nonzero modes execute, and all reached calls are intercepted before CALLF.

GETDC stub returns2468 and consumes2 argument bytes. ANIMATEPALETTE consumes10 and returns0/FFFF.3100 has no effects and returns0/FFFF. RELEASEDC consumes4 and returns0/FFFF. Hooks skip the five-byte CALLF without creating a far return frame. Thus argument cleanup is a harness assumption, cross-checked by final stack restoration, not a discovered Windows ABI result. All calls, order, handles, animation arguments and944 palette bytes are checked. SP D004,BP E000,SI9876,DI5432,DS1048 restored; source/cache/flag unchanged only under these no-effect boundaries. Synthetic execution usesCS2000,DS=SS1048,DF0. Actual import effects and full Win16 runtime are not claimed.

## Implementation-ready findings
Retain independent handle and46AF guards. Do not make the3100 caller guard depend on00BE. Keep modes other than0/2 on the observed bypass route. The controller ignores the supplied animation/release return values along these paths. Cache preservation is conditional on unexecuted callees and cannot yet be made a whole-function guarantee.

## Unknowns and next test
Execute3100 with its Windows boundaries documented, then inspect2C02 and30F2 effects; investigate mode0 palette creation separately. Actual Win16 displayed output and palette/cache timing remain open. Internal decompilation baseline1551 entries and310 EXTERNAL entries remain separate;1401 undefined executable bytes unresolved.
