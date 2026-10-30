# Nitemare3D Win16 1.10 — pass99, 2026-10-30

## Finding
Confirmed: runtime descriptor1048:0594 identifies CWnd, size26 bytes, creation callback1000:1AEC. Successful creation branch2970 stores the returned object through the second-map insertion slot, restores the previous full far allocation handler, and sets the configured handle member. Preserved Ghidra12.2 native export and original machine-code microexecution; no fresh Ghidra run or live Windows/game execution.

## Evidence
|Status|Claim|Source and location|Confidence|Reason|
|---|---|---|---|---|
|Confirmed|Descriptor0594 name pointer resolves to1000:059E, bytes `CWnd`.|EXE file2C5D4 descriptor; file0A5E name; NE10 selector relocation0596→NE1|High|Original bytes plus relocation-chain record.|
|Confirmed|Descriptor+4=001A (26 bytes); descriptor+8 callback offset1AEC, selector relocation059E→NE1.|EXE file2C5D8 and2C5DC; native_evidence.json|High|Do not confuse DS:059E selector relocation with code1000:059E name.|
|Confirmed|1AEC forwards nonzero object to114A, RETF2.|1AEF–1AFD|High static|Original listing; callback not executed here.|
|Confirmed|2970 installs1008:12D2, calls factory06C0 with owner+20 descriptor, gets second-map slot and stores returned pointer.|29B5–29E3|High within stub contract|Original2970 and original601A/5FF0 execute; factory and insertion are explicit stubs.|
|Confirmed|Normal return restores old handler including high word, sets configured first member, duplicates key into next word only mode2.|29E5–2A10|High|72 cases, three prior handlers and three modes, even/odd object addresses.|
|Unknown|Actual CWnd constructor114A effects, real factory/map allocation and exception interruption.|Not executed|—|Successful nonzero synthetic objects only.|

## Behavior model
After misses in both maps, install reserve handler1008:12D2 while saving old DX:AX. Call06C0(owner.descriptor). Obtain insertion value slot62F4(owner+10,key), write object to that slot, restore saved handler, set word[object+owner.memberOffset]=key, and when mode2 also set next word to key. Return object. The handler remains installed during both factory and insertion. Failure/nonlocal paths do not inherit this normal-return restoration guarantee.

## Verification
**72 cases**: modes1/2/FFFF × old handlers00000000/12345678/FFFFFFFF × keys1/0011/8000/FFFF × returned objects7400/7501. Lookup62C8 returns misses; factory06C0 returns chosen nonzero object; insertion62F4 returns slot6006. Stubs consume callee arguments6/2/4 bytes. Original2970 and original601A→5FF0 execute; checks active handler at factory/insertion, stored value, handle words, full restoration, AX and SP/BP/SI/DI.

DS=SS1048, CS2000; handler routines mapped3000. CALL selectors29BE/29EE/6026 normalized to3000; PUSH selector29B6 normalized to native1008. Stored handler value1008:12D2 is checked as data and never executed. No allocation, CATCH, actual constructor or actual map insertion occurs. Descriptor resolution independently uses original bytes and preserved NE relocation-chain records.

EXE SHA256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`; NE1 file04C0, NE2 fileE8A0, NE10 file2C040. Sources:verify_handle_creation.py,verification.json,native_evidence.json,baseline48/pass48-results/listing.tsv and baseline48/pass2/relocation_chain_sites.json.

## Implementation-ready findings
Global owner4250's configured descriptor0594 is CWnd, not an untyped arbitrary allocation. Its size26 agrees with a short wrapper object; role naming beyond CWnd remains inferred. Preserve temporary handler through both factory and map insertion, restore full pointer before final handle writes, and preserve mode2 dual-member creation behavior. Do not assume the handler restores after a throw or that null factory returns are checked: this pass establishes only successful normal return.

## Unknowns and next test
Execute original callback1AEC→114A in a bounded fixture and resolve final CWnd vtable. Then follow its deleting destructor to link the prior virtual+4 cleanup evidence to a concrete routine. Separate CATCH/THROW and allocator failure from the successful path.

## Confidence
High for descriptor identity and successful branch ordering under stated stubs; actual object construction and full program behavior remain unverified.
