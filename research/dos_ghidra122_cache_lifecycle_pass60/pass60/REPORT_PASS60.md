# Pass60 — cache reset and XMS release lifecycle

## Finding
Confirmed, High: mode1 of the original cache-management routine calls XMS unlock then free according to the historical allocation flag, without clearing that flag or the handle. Repeated direct invocations repeat both requests, and driver failures do not prevent the sequence. Mode2 clears cache headers and resets the used-block count; later DOS versions additionally invalidate owning records' cached pointers, while DOS1.0 leaves those fields unchanged in this routine.

768 controlled scenarios pass across six distinct supplied DOS images, each invoking the selected mode twice. Original dispatcher, reset loops and original unlock/free wrappers execute. Only the indirect XMS driver boundary is mocked. Buffers, ownership records and resource-table contents are synthetic. This is local lifecycle behavior, not proof that the full game actually invokes a release twice.

## Versioned evidence
Exact addresses, pointer tables, slot counts, dynamic-table segment and executable SHA256 are in lifecycle.json. V1.9 function1767:002a, mode1 branch1767:01e8–020a, mode2 branch1767:020c–0298. Mode1 uses historical flag DS:350a and handle DS:3504. Mode2 writes used DS:3508=0. Current enable flag DS:3cce is a different field.

| Structure | Slot/header layout | Mode2 in DOS1.0 | Mode2 in DOS1.1–1.9 supplied |
|---|---|---|---|
|First fixed cache|10 far pointers,6-byte header,8192-byte payload|Clear header; owner record unchanged|If header+4 owner is nonzero, clear owner+6 dword; clear header|
|Sound cache|4 far pointers,6-byte header,8192-byte payload|Clear header|Clear header|
|Variable cache|Far-pointer array,2-byte header,3072-byte payload|Not present in this routine|For each active owner, clear owner+6 dword; clear header|
|Used-block count|u16|Set0|Set0|
|Resource source-offset fields|Record+2 / resource table dwords|Unchanged|Unchanged|

Names 'owner' and 'cached pointer' describe the observed pointer relationship: header words point to near records whose+6 field contains the cached far pointer. Identifying every asset class represented by these records is not part of this pass.

## Mode1: release sequence
```
if historical_enable !=0:
    unlock(saved_handle)  # driver AH0d
    free(saved_handle)    # driver AH0a
return
```
Confirmed: the routine checks the historical flag, not the current enable byte. Both flag and handle remain unchanged afterward. The original wrappers translate manager failures into DX status, but this caller does not branch on either result. In the simulated failure case both requests return AX0/BL80; free still follows unlock. A second call with the same history flag issues unlock/free again. The test does not prove a real manager frees twice successfully, nor that repeated higher-level shutdown is reachable.

## Mode2: reset sequence
The routine clears all fixed-cache headers. In later versions it first invalidates the cached far pointer at owner+6 when the header's owner word is nonzero. It also resets the variable-cache owner headers and cached pointers for the configured slot count. It finally resets used-block count to0. Current enable, historical enable, XMS handle and capacity are retained.

All8192 payload bytes in each of14 fixed blocks and all3072 bytes in each selected variable block remain byte-identical. The mode does not zero payload contents. Owner source offsets at+2 and the entire474-byte synthetic79-entry resource table, including negative offsets, also remain unchanged. This is an observable local contract; how callers refresh source offsets or otherwise coordinate resource lifetime remains Unknown.

DOS1.0 has no variable-cache loop here and does not clear owner+6 for the first fixed cache. This is a verified version difference, not a claim that DOS1.0 uses an invalid pointer in gameplay. Zero owner headers do not cause unrelated owner records to be rewritten. A second reset reaches the same header/pointer state without additional driver calls.

Mode3 is also probed: it takes the dispatcher's return path and leaves all tested state unchanged. Mode0 initialization was investigated separately in pass59; it is not executed by this pass.

## Matrix and assertions
For later images:3 modes(1,2,3) x2 history flags x2 current-enable flags x2 active-owner settings x3 variable-slot counts(0,1,3) x2 driver outcomes=144 scenarios each,720 total. DOS1.0 omits the variable slots:48 scenarios. Combined768, each with two calls. Driver outcomes are both successful requests or both requests failing AX0/BL80.

Assertions compare complete fixed/variable payloads and headers, all owner-record bytes, all79 resource records, used counter, unchanged capacity/enable/history/handle, expected driver AH/handle order, and return DS/CS/SP. Driver handle1234 is synthetic. There is no file or audio output in this experiment.

## Static caller evidence from Ghidra12.2
A read-only export found three direct call sites per image, with immediate arguments0,1,2. V1.9:
| Argument | Call site | Containing function |
|---:|---|---|
|0|1476:012f|1476:00ce|
|1|1476:01c6|1476:0192|
|2|1d25:081a|1d25:0812|

Per-build exact instruction contexts are in *.callers.tsv. These xrefs establish direct sites only; they do not prove global call counts, exclude indirect paths or determine the complete lifetime of the containing functions.

## Confidence and next test
High for tested local reset/release behavior and version difference. Unknown: real driver error recovery, higher-level re-entry guards, heap-block deallocation elsewhere and resource-table restoration after used-count reset. Next: trace the mode2 caller's surrounding resource-loading sequence to locate offset reinitialization; investigate mode1's containing function and its callers before describing repeated-release behavior as a gameplay bug. Full-game1:1 parity remains unverified.
