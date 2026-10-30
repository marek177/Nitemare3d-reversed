# Win110 pass73 — embedded exception strings and resource loader

## Finding
Confirmed / High: original EXE embeds the exact messages selected by the exception handler. Original3250→3282 forwards the resource ID and module word DS0820 to LOADSTRING; zero returned length bypasses string assignment.

## Evidence
| Status | Resource ID | Embedded text | Confidence |
|---|---|---|---|
| Confirmed | F108 | Internal application error. | High |
| Confirmed | F109 | Command failed. | High |
| Confirmed | F10A | Insufficient memory to perform operation. | High |

These are decoded directly from NE RT_STRING type8006, block ID8F11, file offset36770, allocated length368 bytes. Individual length-prefixed string offsets and raw bytes are in verification.json. Resource parsing uses the original NE header and resource-table shift4, rather than a substring search. All numeric RT_STRING blocks are decoded as sixteen length-prefixed byte strings each. Windows runtime module selection is not proven to use this EXE in every context; actual display of these texts remains Unknown.

## Behavior model
3250 reserves256 local bytes and calls3282(buffer,resourceID). 3282 pushes DS0820,resourceID,DS,buffer,255 before LOADSTRING at3293. It passes AX back unchanged. 3250 tests AX as a nonzero word, invokes0E26(destination,buffer,length) only when nonzero, and returns AX1 after assignment orAX0 without assignment. Neither path clears the destination explicitly in3250. Destination contents after loader failure therefore depend on its previous construction/state; this pass does not execute string constructors or assignment.

This closes the resource-ID-to-embedded-text link for the policy in passes71–72. The result does not establish the real dialog owner, Windows flags, or selected application virtual method.

## Verification
65,536 cases passed, covering every WORD resource ID. Original3250 and3282 instructions execute. The LOADSTRING call is stubbed with a lookup against the independently parsed current EXE string table, writing at most254 payload bytes plus NUL for count255; missing/empty strings return0. The assignment0E26 call is intercepted and checked for destination, exact bytes and length; it does not allocate or mutate a real string object. 107 identifiers contain nonempty fixture strings and take the assignment path. This number describes this modeled lookup, not observed Windows loads.

The stub checks all five LOADSTRING argument words, including synthetic module5555 from DS0820. Every case checks the boolean return, final SPD008 from entryD000, and preserved BP/SI. DS=SS1048, CS2000. One internal selector at3260 is normalized to2000 for3250→3282. Imported call and assignment selectors are never executed because their call sites are intercepted. No real Windows API executes.

Reproduce `python3 pass73/verify_resource_loader.py` with Unicorn2.1.4. Original EXE SHA256:12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Preserved native Ghidra12.2 listing is included for inspection; no fresh Ghidra database update occurred.

## Implementation-ready findings
Use the exact embedded strings above for these IDs when reproducing this executable's resources. Preserve module selection through0820 rather than hardcoding a universal module. Keep zero-load return separate from successful assignment. Do not clear a preexisting destination solely because LOADSTRING returns0 unless its constructor/caller requires that behavior.

## Unknowns and next test
Trace writes to0820 to identify the resource module on the normal startup path. Execute0D08/0E26/0D8E to establish empty-string and ownership behavior. Actual module lookup and rendered Win16 dialog remain Unknown. Confidence High for embedded text and isolated loader control flow under the declared API model.
