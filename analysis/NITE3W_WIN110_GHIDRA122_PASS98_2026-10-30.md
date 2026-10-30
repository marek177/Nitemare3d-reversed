# Nitemare3D Win16 1.10 — pass98, 2026-10-30

## Finding
Confirmed: global owner4250 is configured with member offset14 and width mode1; its adjacent maps are4250/4260. Original2970 returns first-map hits unchanged, refreshes the configured member on second-map hits, and returns0 immediately for key0. Creation is a distinct branch. Preserved Ghidra12.2 exports and original EXE microexecution; no fresh Ghidra run or live Win16/game execution.

## Evidence
| Status | Claim | Source and location | Confidence | Reason |
|---|---|---|---|---|
| Confirmed |12E2 supplies owner4250, mode1, member14, runtime descriptor0594 to2930. |12E2–12EC;2930 stores+20/+22/+24|High|Exact native argument pushes and stores.|
| Confirmed |Other owners are4548:(mode1,member4,descriptor0746),44F2:(mode2,member4,0696),451C:(mode1,member4,06D6). |3360;1008:02B6/0D78|High static|Native immediate arguments; constructors not executed in this pass.|
| Confirmed |Key0 returns0 without lookup; first-map hit returns value without member refresh. |2976–2997|High|All65536 keys on first-hit path, including zero bypass.|
| Confirmed |Second-map hit writes key to object+configuredMember then returns object. It writes one word even when mode2. |2999–29B3|High|All65536 keys on second-hit path with mode2 and poisoned following word.|
| Confirmed |New-object branch uses descriptor owner+20, stores factory result in second map, restores old allocation handler, writes key member; mode2 additionally duplicates key into next word. |29B5–2A0A;06C0|High static only|Native listing; creation branch not executed in this pass.|
| Inferred |4250/4260 are permanent and temporary HWND wrapper maps. |Constructor member14, prior132C/1356 HWND field14, lookup order2970 and value cleanup2A26|Medium|Roles fit concrete access chain; real runtime wrapper classes and creation callback remain unexecuted.|
| Unknown |Factory failure/null return, exception recovery and concrete created class behavior. |06C0/Windows CATCH branch not executed|—|No safe completion claim for failed creation.|

## Behavior model
2970(owner,key): if key0 return0. Find first map; if hit return value. Find second map; if hit set word[value+owner.memberOffset]=key and return value. Otherwise install reserve-failure handler12D2, create via06C0(owner.descriptor), obtain insertion slot in second map and store returned object, restore previous handler, set object member to key (and next word if mode exactly2), return object.

This separates an important detail: second-map reuse only refreshes one word, whereas creation mode2 writes two.2A26 cleanup clears one or two words according to mode before its virtual+4 callback. For owner4250 the mode is1, member14; prior attachment132C sets object+14 from HWND, supporting the HWND-field connection.

## Verification
**131,072 cases**: all WORD keys for first-map hit and for second-map hit. Original2970 zero/reuse branches execute.62C8 calls298B/29A2 are intercepted before CALLF; fixture writes near output pointer, returns boolean, and consumes6 argument bytes. No actual map search here; earlier passes independently executed62C8/6280. DS=SS1048; CS2000, original code bytes unchanged. Synthetic object7400, member14=AAAA and following wordBBBB. Width2 intentionally tests reuse asymmetry. Checks return AX, lookup receiver/order, exact fields, SP/BP/SI/DI. No factory, allocator, Windows or object destructor executed.

EXE SHA256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`; NE1 file04C0, NE2 fileE8A0. Sources: verify_handle_reuse.py, verification.json, native_listing.json and baseline48/pass48-results/listing.tsv. Raw descriptor selector words are relocation chain links; class names are not inferred from unrelocated bytes in this pass.

## Implementation-ready findings
Keep lookup priority first map then second. Preserve key0 bypass and first-hit no-write behavior. On second-map hit update exactly the configured first member word. Do not copy the creation mode2 dual-word write into reuse. Global owner4250 configuration is descriptor0594, offset14, width1; owner44F2 uses width2. Full failed-creation behavior remains TBD.

## Unknowns and next test
Resolve descriptor0594 name and create callback using NE relocation chains, then follow callback1AEC and actual window wrapper destruction. Execute successful creation with declared stubs and verify temporary-map insertion, handler restoration and member write; separately inspect failure/nonlocal exception paths.

## Confidence
High for native configuration and tested reuse branches; Medium for permanent/temporary role naming; no game parity claim.
