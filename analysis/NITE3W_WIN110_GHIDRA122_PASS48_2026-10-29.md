# Win16 1.10 — Ghidra 12.2 pass48: palette readback and BGR0 conversion

## Finding
Confirmed, High within controlled import boundaries:2C02 requests256 palette entries and converts all256 to BGR0 atDS4D9A regardless of the supplied return count.768 executions verify this behavior and the zero-handle bypass. Actual Windows partial/failure filling remains Unknown.

## Evidence
|Status|Claim|Source|Confidence|
|---|---|---|---|
|Confirmed|00BE zero skips both calls and conversion|1010:2C07..2C0C;256 cases|High|
|Confirmed|GETPALETTEENTRIES requests start0,count256,far stack buffer|2C0E..2C1E;512 cases|High|
|Confirmed|Exactly256 outputs are B,G,R,0; source flag discarded|2C25..2C49; all1024 bytes checked|High|
|Confirmed|Return values0/1/255/256 do not change conversion length|Original instruction flow with full fixture buffer|High|
|Confirmed|WinG ordinal1006 receives handle4BD2,start0,count256,DS:4D9A|2C4B..2C59 call-site capture|High|
|Unknown|Real API failure or partial fill contents and actual display|API not executed|Low|

## Behavior model
Static3100 begins with its own handle00BE guard, then BEGINPAINT, SELECTPALETTE, REALIZEPALETTE,2C02,ENDPAINT,30F2. Static30F2 calls3080 only when46B0 zero. This pass executes2C02 itself, not that complete caller chain. The conversion writes the blue source byte to4D9A,green to4D9B,red to4D9C,and zero to4D9D, repeating at stride4. This separates the GDI RGB-entry layout from the WinG BGR0 table.

## Verification
768 cases=3 handles0/1/FFFF ×4 return values0/1/255/256 ×4 flags00C4=0/1/80/FF ×16 random1024-byte input buffers(seed48).512 cases convert256 entries;256 bypass. All1024 output bytes and two guard bytes checked, plus cache16 bytes,flag,SP/BP/SI/DS. Original EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Non-CALLF encodings match rawEXE; two import CALLF encodings normalized to native Ghidra listing. Calls intercepted before execution: readback writes all1024 fixture bytes regardless of return; both boundaries consume10 argument bytes and return the selected value. This cleanup and no-effect behavior is a harness assumption, not actual Windows execution. CS2000,DS=SS1048,DF0.

## Implementation-ready findings
Use a256-entry RGBflag to BGR0 conversion with ignored count result for this recovered routine. Retain the handle guard and request arguments. Do not invent a count-based clamp absent from the instructions. Cache preservation holds locally with the documented stubs; it is not proof of real GDI preservation. The full-buffer fixtures deliberately isolate return-count handling and do not demonstrate real API partial-write behavior or a reachable failure defect.

## Unknowns and next test
Integrate3100 with2C02 and document remaining import boundaries; inspect3080 presentation and real Win16 palette readback. An actual partial/failure API trace is needed to determine resulting buffer contents. Internal native decompile baseline1551;310 EXTERNAL entries separate;1401 undefined executable bytes unresolved. Overall confidence High for conversion and local guards, Low for unexecuted OS effects.
