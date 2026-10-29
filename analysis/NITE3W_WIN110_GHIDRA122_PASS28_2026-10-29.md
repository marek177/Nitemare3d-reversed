# Win16 1.10 — Ghidra12.2 pass28: config open binary descriptor

## Finding
Confirmed High: config reader52AE supplies mode8000h to CRT open54D4. For the tested successful directINT21 route, this forces descriptor textbit80 clear regardless of default byte0945.6144 original-routine cases passed. This links config-open mode to the binary read branch recovered in passes26/27, within the controlledOS contract.

## Evidence
|Status|Claim|Location|Confidence|
|---|---|---|---|
|Confirmed|Config open caller supplies8000h|1010:52EF..5303|High|
|Confirmed|Mode8000 suppresses localtextbit80 beforeOSopen|1008:54EB..5504|High|
|Confirmed|Mode8000 issuesDOSopenAX3D00|5504..551F|High|
|Confirmed|Successful open queries4400, setslocal40ifdeviceDL80|5557..5575|High|
|Confirmed|Disk route queries4300,attrbit1 mapsdescriptor10|5721..5742|High|
|Confirmed|Descriptor flag final01/11disk,41device;allbit80clear|576E..5774|High|
|Confirmed|Successfulhandle0 is valid atCRTlevel but config caller skipsit|5778..5782;52AE5308|High|
|Unknown|ActualOS responses/errors andDOS3CALL route|INT21stubbed|Low|

## Behavior model
Initial local descriptorflags=0. Mode8000 bypasses default textmode logic. OSopen returns handle;4400 device query may add40. Diskfile attribute query adds10 forreadonlybit. Open publishes flagsOR1 at0876+handle, then returns handle. For testdisk cases flags01or11, neither EOF02 nor text80 is set. Prior read results therefore apply to this freshly opened descriptor when runtime remapping0A94=0 and the directINT21 route is used.

Handle0 is an important interface mismatch: CRTaccepts and recordsit, but config controller requires signedhandle>0 and skipsread/close for0. Real reachability of that handle assignment depends on process handle state and remains unmeasured.

## Verification
EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.6144 cases=all256 default0945 bytes ×device0/80 ×attributes0/1/2/FF ×handles0/1/19,limit20.237 instruction comparisons cover native54D4 body;17 importedCALLF encodings normalized from native listing, allunexecuted becauseCS370Ebit0=0. Originalroutine executesfullsuccesspath tofarreturn. OSINT21 hook validates service sequence/openpathpointer and injects successfulresponses. Checksall20 descriptorflagbytes andAX,DS,BP,SP. Errors/create/truncate/extendedhandles excluded; no filebytes read inthispass.

## Implementation-ready findings
Treat config open mode8000 as explicitbinary mode; donot derive textmode from0945 here. Preserve readonly/device bits independently of textbit. Combine withpass27 only under stated branch conditions; this is separatefunction evidence, not integratedwholeconfigload or actualWin16runtime.

## Unknowns and next test
Integrate52AE+54D4+5798 with controlledOS; verify0A94 andCS370E actualinitialization; testopenfailures anddescriptorlimit boundary. WholeLOADfirstframe andgameplayparity remainopen.1551 internalentries retainnative decompilationsuccess,310 EXTERNALentries separate.1401 undefinedexecutablebytes remainunresolved.

## Confidence
High for tested successfulmode8000 route; no claim for excludedpaths or actualOS.
