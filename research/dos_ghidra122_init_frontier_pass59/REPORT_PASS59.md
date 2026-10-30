# Pass59 — XMS initialization bounds, versioned record store and whole-project frontier

## Finding
Confirmed, High: after the tested initialization succeeds, XMS placement capacity is64..2048 KiB and the used counter is reset to0. The largest-block/query AX value is compared as signed16: input values8000h..ffffh disable this path rather than being clamped down to2048. A second store caller differs by version: DOS1.0 always requests8192 bytes; DOS1.1,1.2,1.5,1.7 and supplied1.8/1.9 use the unsigned product of two record bytes.

User scope remains the supplied DOS1.0–1.9 set. There are six distinct images because the supplied1.8/1.9 EXEs are identical. This does not establish status for other DOS2.0 or Win16 projects.

## Evidence and scope
The previous pass58 archive and runtime project were recovered after workspace maintenance. Its exact Library archive is included as a dependency. Ghidra12.2 PUBLIC20261016 and JDK25.0.2 were restored and run read-only against that project. Original relocated EXE bytes are executed with Unicorn2.1.4.

-864 phase scenarios with original initializer control flow and helper-call boundaries mocked.
-864 matched scenarios with original detect/query/allocate/lock/free wrappers executing; only INT2f multiplex, indirect manager calls and warning output are mocked. These are deeper checks of the same scenarios, not864 additional independent input combinations.
-120 record-store scenarios execute the original record helper, original placement routine and original move wrapper; manager boundary is mocked to success.
-12 fresh diagnostic C outputs and instruction exports cover initializer and record store across six images.

The initialization test starts at the post-heap XMS-enable check with an explicitly constructed established frame. It does not execute earlier heap allocation or full game startup. Driver presence, allocation handle1234 and lock address00123456 are synthetic boundary responses. Fatal/real driver execution and audio are not claimed.

## Initialization model (V1.9)
Original containing function1767:002a; isolated phase1767:016d onwards. Globals: enableDS:3cce, capacity3506, raw query3cb8, used3508, handle3504 and historical enable350a. Exact per-version globals/instructions/hashes in init_original_wrappers.json.

```
if enabled:
    if !detect_manager(): enabled=0
    else:
        raw=query_AX()
        capacity=raw
        raw_reported_field=raw
        used=0
        if signed16(capacity)>2048: capacity=2048
        if signed16(capacity)<64: enabled=0
        else:
            allocate(capacity)
            if signed16(status_DX)<0: enabled=0
            else:
                handle=returned_handle
                lock(handle)
                if signed16(status_DX)<0:
                    free(handle)
                    enabled=0
                    warning(...)
historical_enable=enabled
```
Confirmed: the raw reported field is saved before clamping. When the initial enable flag is0, capacity/used are not reset in this phase. On detection failure they likewise retain their prior values. Query then allocation failure leaves the clamped capacity and used0, but disables the path. Lock failure stores the handle before freeing it; this phase does not clear that handle afterward. The history flag records the final enabled state. Do not treat stale disabled globals as an active successful configuration.

Original wrappers perform INT2f AX4300 and4310 for manager detection/entry storage, then indirect manager calls AH08 query, AH09 allocation, AH0c lock and AH0a free. Tests verify these AH values and exact arguments while allowing the original wrappers to perform their AX/DX/BL translations. The protocol interpretation as XMS is consistent with the already recovered move descriptor; actual manager behavior remains outside this experiment.

Matrix:6 images x2 initial enable states x2 detection outcomes x9 query values(0,63,64,2047,2048,2049,32767,32768,65535) x2 allocation outcomes x2 lock outcomes=864. Trace order, capacity/raw/used/handle globals, final enable/history flags, normal return CS/SP and DS are asserted. All864 result dictionaries match between the direct-boundary and original-wrapper experiments.

## Conditional reachability result
For successful initialization,64<=capacity<=2048 and used=0. For the previously verified store rule, blocks<=64 for any length16. If all later updates use that rule and accepted updates maintain used<=capacity, the largest tentative sum is2112, far below65536. The byte offset is at most2097152 and cannot become negative through signed16(used). Thus pass58's used8000/ffff synthetic wrap/sign cases are excluded by this normal-state invariant. This is conditional on initialization and the analyzed update discipline, not a proof against arbitrary writes or alternate entry paths.

capacity_invariant.json checks the signed/clamp model for all65536 possible query words. These are model checks, not65536 machine executions. Values8000..ffff failing initialization are directly sampled in the original-code experiments; whether a particular real manager reports such values requires a separate manager-backed run.

Static xrefs to used are exported, but they are not an exhaustive write proof. For example, the module's mode2 reset at1767:0292 exists in the original bytes and can be missed after POP DS when static SS/DS context is incomplete. Hence the invariant's conditions are explicit.

## Record-store version difference
| DOS | Record helper | Length passed to placement routine |
|---|---|---|
|1.0|1739:02e4|8192, independent of record bytes0/1|
|1.1|1742:03ca|u8(record[0])*u8(record[1])|
|1.2|1742:03d6|u8(record[0])*u8(record[1])|
|1.5|1747:03d4|u8(record[0])*u8(record[1])|
|1.7|1751:03d0|u8(record[0])*u8(record[1])|
|1.8/1.9 supplied|1767:03d4|u8(record[0])*u8(record[1])|

The table is cross-checked against dimension_record.json locations. On success the helper stores negative placement offset in record+2 dword, leaves the source far pointer at+6 unchanged and returns AL1. On negative placement result it leaves the entire record unchanged and returns AL0. Only AL is a boolean contract; the rest of AX may retain offset/error bits. The meaning of the two byte dimensions and actual resource class remains Inferred, not asset-identified.

120-case matrix:6 images x5 byte pairs(1,1),(32,32),(255,255),(0,17),(16,64) x2 prior-used values(0,1) x2 capacities(0,64). Every10-byte record, exact move descriptor, used counter, AL and return CS/SP/DS are checked. Later versions can request65025 bytes for255*255 and round this to65536; this is not constrained by the sound-table preparer's8192 guard. Zero-product records still reach placement if its capacity check allows them; DOS1.0 still uses8192. These are synthetic records, not proof that shipped assets exercise the edge cases.

## Whole-project analysis frontier
Read-only Ghidra inventory:3469 function entries,773 computed call/jump sites;686 sites have no destination in getFlows(). These are investigation points, not missing-function counts or bugs. The inventory and120 ranked triage candidates are per build and contain no completeness percentage. ANALYSIS_FRONTIER.md retains priorities beyond XMS: segment context, real assets, full request chain, rendering, gameplay, save/load, DEMO and indirect control-flow targets.

## Limits and confidence
No project functions or bytes were modified. Initial native decompiler permission failure was diagnosed and corrected; final run opened the decompiler for all six images and generated12 diagnostic C files. Generated C still needs ABI/context review and is not an implementation specification on its own. High confidence for tested local control flow, capacity bounds under explicit conditions and version difference. Full startup, real manager reports, asset identities and full-game1:1 parity remain Unknown.
