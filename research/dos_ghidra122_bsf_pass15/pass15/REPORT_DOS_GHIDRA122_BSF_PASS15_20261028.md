# BSF pass15 — mode4 text consumer and far-free ownership

## Finding
Confirmed across six distinct DOS images: a direct mode4 caller receives a far text pointer, emits all bytes before the first NUL except the last byte, then calls original far free once with the original pointer. Original far free marks the preceding allocation header free by ORing bit0; for segment0 it returns without touching that header.

## Evidence
192 passing executions: eight text samples x segment0/5000 x offset0200/fffc x6 builds. Samples: empty,A,AB,ABC,A NUL B,e9 Z,A CR LF,and each build's real decoded mode4 resource. Original full caller and original far free execute in Unicorn. Only BSF dispatch return pointer and formatted character-output call are mocked; neither original loader nor DOS console is executed here.

Checks include dispatch argument4, one dispatch/free call, original pointer passed to free, actual printf format `%c`, signed16-bit character argument, expected output bytes/hash, header transformation, far return and stack. Buffers are written using16-bit offset wrapping to exercise caller boundary behavior atfffc. Initial header bytes80a5 become81a5 for nonzero segment and stay80a5 for segment0. This is an artificial valid mapped-memory setup; segment0 tests prove the guard behavior, not practical loader output reachability.

V1.9 caller1d25:1630, dispatch call1d25:1638, output1d25:1663, far-free call1d25:167d ->21ea:2056. Per-build entries, instruction bytes and input/output hashes are in mode4_owner.json. The real resource is the decoded mode4 block from pass7; the harness appends the loader's trailing NUL.

## Behavior model
Save original far pointer P. While *P!=0 and byte at16-bit offset(P)+1!=0: invoke formatted output `%c` with sign-extended current byte; increment offset modulo65536. Stop before final non-NUL byte. Call far free(original pointer), even for empty or one-byte strings. Therefore empty/A emit nothing,AB emitsA,ABC emitsAB,A NUL B emits nothing,A CR LF emitsA CR. This is a byte-emission contract, not a claim about final screen appearance or CRT newline processing.

Far free for segment!=0 ORs1 into the byte at16-bit offset(pointer)-2 in that segment. It does not call DOS memory release or coalesce blocks in this routine. That bit matches the free-marker convention in pass14's original allocator; later reuse/coalescing is a separate behavior to verify. For segment0 the routine does nothing.

The callsite catalog preserves all direct near/far dispatch references found in Ghidra instruction exports plus the second word argument passed through the generic text consumer. These static references do not alone prove runtime reachability or complete indirect-call coverage. Generic mode3/5 rendering and ownership are not dynamically established by this pass.

## Confidence and limits
Confirmed/High for original mode4 consumer and far-free code under injected dispatch/output dependencies. Unknown: actual formatted-output/DOS behavior, UI trigger reachability, other BSF text consumers, allocator reuse/coalescing and all mode3/5 paths. No Ghidra function/body edit or global decompiler coverage increase; current projects remain pass14. Full gameplay1:1 parity remains open. Supplied1.8/1.9 still identify one identical image.

## Reproduce and next step
Run `/usr/bin/python3 scripts/verify_bsf_mode4_owner.py` (Unicorn) and `python scripts/catalog_bsf_callers.py`. Archive includes reconstructed EXEs, prior stock caller C used for discovery, instruction exports, pass7 specs and decoded mode4 resources. Next: generic text consumer ownership/line parsing and allocator reuse of a released block.
