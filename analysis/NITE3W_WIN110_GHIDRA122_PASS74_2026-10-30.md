# Win110 pass74 — resource module provenance

## Finding
Confirmed / High: on the nonnull application path,5D24 copies its BP+0E argument into application+14, and5E94 copies that same word into both DS081E and DS0820 before calling GETMODULEFILENAME. The resource loader3282 subsequently uses0820. This connects its module argument to startup input rather than a hardcoded constant.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Application pointer loaded from081C, zero bypasses field initialization | 5D5B–5D63 | High |
| Confirmed | Caller frame wordBP+0E stored at application+14 | 5D67–5D6A | High |
| Confirmed |5D24 calls5E94(application) |5D85–5D86 | High |
| Confirmed | application+14 copied independently to081E and0820 |5E9D–5EA6 | High |
| Confirmed | Same application+14 supplied to GETMODULEFILENAME with260-byte SS buffer |5EA9–5EB5 | High |
| Confirmed |3282 pushes0820 as LOADSTRING module argument |3285–3293 | High |

Captured exact direct operands matching0820 have one explicit store at5EA6 and12 read sites. This is a scoped listing search, not proof that no indirect, overlapping or bulk write exists anywhere in the program.

## Startup chain
Static preserved export shows37C2 pushes0832 first before the five-argument call2A8E at37E0.2A8E forwards its five arguments to5D24 at2AA9. Startup3718 initially stores DI into0832 at3736 after the INITTASK call. Therefore the fifth argument reaching application+14 originates from that saved startup register on this normal path. Interpreting this as the current application instance handle is Inferred / Medium from its API usage; the actual INITTASK register contract and a Windows-loaded handle were not executed in this pass.

## Verification
65,537 original-code cases passed. All65,536 fifth-argument WORD values are propagated through the actual5D24 fragment from5D5B, its CALLF5E94, and the original5E94 prefix, stopping immediately before GETMODULEFILENAME at5EB5. Each case checks all five application fields+14,+16,+18,+1A,+1C, both module globals and the four pending API argument words. An additional null-application case checks the bypass and unchanged globalsAAAA/BBBB.

Synthetic caller frameBP=D000, initialSP=CFF0, application7000, DS1048, SS4000, CS2000. One internal far selector at5D89 maps to2000. No function stubs or Windows API execution occur; execution stops at the API boundary. Prefix/native instruction bytes except relocation-bearing CALLF fields are compared with the raw EXE. This does not execute the rest of5E94 or full startup. Original EXE SHA256:12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.

Run `python3 pass74/verify_resource_module.py` with Unicorn2.1.4. Sources: preserved Ghidra12.2 export and original NE executable; no fresh Ghidra database update occurred.

## Implementation-ready findings
Initialize instance and resource-module globals from the same application+14 word on this startup path. Preserve the null-application bypass. Keep0820 separate from081E because later indirect reassignment has not been excluded. Pass0820 through the loader rather than assuming a universal module number.

## Unknowns and next test
Resolve actual Windows startup handle semantics and test any resource-module override path. Trace application+22/0822 title fallback and the virtual UI method to identify dialog caption/owner. Real resource-module resolution remains Unknown. Confidence High for tested propagation, Medium for instance-handle interpretation.
