# Win110 pass78 — allocation handler installation and exception boundary

## Finding
Confirmed / High:0772 installs1000:076A through601A→5FF0. Original allocator5AB0 dispatches to that handler after a failed allocation. The handler's first instruction calls4564, the previously recovered static memory-exception entry. This pass stops before that call executes.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed |5FF0 returns old far handler in DX:AX and stores new two-word pointer |5FF6–6013 | High |
| Confirmed |601A preserves that far return while discarding its forwarded arguments via frame restoration |601A–602B and256 pointer pairs | High |
| Confirmed |0777 suffix installs1000:076A and returnsAX1 |0777–0788 and integrated cases | High |
| Confirmed | Failed5AB0 dispatch reaches original076A |24 original-code boundary traces | High |
| Confirmed |076A begins CALLF4564, followed by XORAX,AX andRETF if that call returns |076A–0771 native listing | High |

The decompiler's5FF0 prototype exposes only a WORD return, but original code restores both old pointer words toDX:AX. Callers that save both registers must preserve this far value.

## Behavior model
`old=set_handler(newFarPointer);` performs unvalidated two-word replacement.0772 calls53CA first, then installs076A. Its53CA call is outside this pass's execution scope.078A stores0772'sAX1 to41B4, and0794 calls078A after0678, as shown in the static export.

The normal captured install target is exception-oriented:076A→4564. It is not a general automatic retry guarantee.5AB0 retries only if the handler actually returns nonzero;076A would return0 if4564 returned normally. Actual4564 exception transfer is outside this pass and was separately studied earlier.

Captured direct callers of601A include077D and28DE/2913/29BB/29EB. At28DA–28DE,2840 passes zero, then saves returnedAX/DX at28E6/28E9. This statically supports temporary handler suppression and later restoration rather than a globally immutable handler. Full2840/2970 lifecycle paths are not executed here.

## Verification
280 cases pass:256 deterministic random old/new32-bit pointer pairs through original601A→5FF0, verifying stored pointer, returnedDX:AX, caller-cleanedSPD004 and restoredBP; plus24 cases combining three previous handlers and eight sizes0,1,2,255,256,7FFF,8000,FFFF. Each integrated case executes0777 installation suffix, verifies stored1000:076A andAX1, then runs original5AB0 through modeled failed allocation to the real handler entry boundary. It checks lock/allocate/unlock order and normalized size on callback stack.

DS1048, SS4000, code CS2000/3000. The loaded immediate PUSH selector at0777 is normalized from the native export. Internal CALLF selectors at0780/6026 are remapped3000. After verifying the stored original callback selector1000, it is remapped2000 solely to execute the indirect call in the test layout. API calls LOCKSEGMENT,LOCALALLOC,UNLOCKSEGMENT are intercepted and return0. No actual callback body is replaced, but execution deliberately stops at076A before CALL4564. No Windows heap or THROW executes; full startup and53CA are not executed.

Run `python3 pass78/verify_handler_install.py` with Unicorn2.1.4. SHA256 original EXE:12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Preserved Ghidra12.2 export plus raw executable; no fresh Ghidra database mutation.

## Implementation-ready findings
Handler setters return the full old far pointer. Preserve bothAX andDX for temporary suppression/restore. Separate allocation failure returned with no handler from failure entering the installed exception handler. A retry-only implementation would lose the observed076A exception dispatch.

## Unknowns and next test
Execute the temporary disable/restore regions in2840/2970 to establish why they bypass exceptions and whether all exits restore the handler. A real Win16 failure/THROW test remains needed for runtime reachability and exception lifecycle. Confidence High for setter and indirect dispatch boundary; live exception transfer remains Unknown in this pass.
