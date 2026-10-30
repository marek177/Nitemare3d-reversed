# Pass61 — original resource teardown and versioned nested deallocation

## Finding
Confirmed, High: the direct mode2 caller is a resource-teardown routine. It resets cache state, frees entries in two registries, then walks28-byte records and clears class-indexed pointers after freeing them, preventing repeated IDs from freeing that same class pointer again during the walk. DOS1.0 has an additional nested10-byte-record/far-pointer deallocation stage in its second registry; later supplied images use a direct8-byte-stride pointer registry.

324 scenarios pass across six distinct supplied DOS images, with two complete teardown invocations per scenario. Original teardown, original mode2 reset, original near-heap free and DOS1.0's original far-heap free all execute. No callee or interrupt service is mocked in these tests. The heap headers, registries, records and cache buffers are synthetic; this does not establish correctness of the full allocator or actual asset lifetimes. Supplied1.8/1.9 share one image.

## Evidence
Fresh Ghidra12.2 read-only instruction/C exports and direct-caller contexts are included. The export role name 'loader' was retained from initial triage; function purpose was refined to teardown from its actual instructions. No program names, functions or bytes were changed.

V1.9 teardown1d25:0812–08ac:
1. Call cache controller1767:002a with mode2.
2. Signed count DS:6270, registry DS:4314, stride8: pass each first word to near-heap free21ea:3cb2.
3. Signed count DS:6272, registry DS:3d24, stride8: likewise free each first word.
4. Signed count DS:626e, object segment DS:256a: read unsigned class byte at ES:000a, increment object address by1c each iteration. Fetch near pointer DS:3d22+class*8. If nonzero, free it, re-read the class byte and clear the class pointer.

The complete per-version locators, heap helper instructions and exact traces are in teardown.json. Names 'object' and 'class' describe the indexed28-byte-record pattern; asset identity remains Inferred until tied to actual records.

## Original heap helpers
V1.9 near helper21ea:3cb2 compares the pointer against a lower anchor word at DS:20e0+6. Pointers at/below that bound are skipped. Otherwise it sets bit0 in the byte at pointer-2 and lowers the free-search word at anchor+8 if appropriate. The fixture uses bound5000h, initial searchfffeh and valid pointers above the bound. Null entries in the first two registries reach this helper and are skipped by its own bound check.

DOS1.0 far helper219b:214e loads the passed far pointer into ES:SI and, when ES!=0, sets bit0 at ES:[SI-2]. A segment-zero probe0000:0202 is skipped by this helper. This is actual helper execution, not a simulated deallocation callback. Calling the marking helper is not equivalent to proving a full allocator free/coalescing contract.

## Version difference in second registry
| Version group | Registry traversal |
|---|---|
|DOS1.0|Each8-byte row has a signed child count at+0 and a near child-array pointer at+6. Walk children at stride10; call the original far free on child+6 dword, then near free on the child array.|
|DOS1.1/1.2/1.5/1.7/supplied1.8–1.9|Walk8-byte rows and near-free the first word directly.|

The first registry remains a direct8-byte-stride pointer list in all tested images. The class-indexed final pass also exists in all images. Neither first-registry nor second-registry pointers/counts are cleared by this routine. On a second direct invocation they are processed again. The final class-pointer entries, however, were zeroed during the first walk and therefore cause no further class frees. This local observation does not prove higher-level teardown re-entry in gameplay or a double-free fault.

## Matrix and assertions
6 images x3 first counts(-1,0,2) x3 second counts(-1,0,2) x3 final counts(-1,0,5) x2 null/non-null fixture variants=324 scenarios. Counts are compared signed: negative and zero skip their loops.

Final-walk class IDs are[2,2,5,3,5], including duplicates and a null class5 pointer. Decoy data at the corresponding near DS address differs from the real ES record bytes; the exact observed free arguments prove the segment-based reads. Later versions and DOS1.0 each run their real near-free helper. DOS1.0 additionally runs three synthetic child far pointers per nonempty second registry; two nested rows have child counts2 and1. Every scenario invokes the full teardown twice.

Assertions cover exact ordered near/far free arguments, mode2 reset events before heap work, cleared class pointers, retained first/second table pointers and counts, header allocation-bit mutations, minimum free-search pointer, used-count reset and restored DS/CS/SP. No interrupts occur. The test stops at the synthetic far-return address only after the original routine returns normally.

## Higher-level gate and restoration limit
Ghidra finds one direct caller of the teardown in each image. V1.9 caller1d25:095e calls it at0969 only when byte DS:1c9a==0. With a nonzero flag it skips teardown and resets mode DS:6268 to0; the routine then clears that flag, stores its first argument in DS:626a and calls additional resource/transition functions including1d25:0404 and1d25:08ae. The exact caller instructions and diagnostic C are exported.

The gate is Confirmed statically; the semantic meaning of DS:1c9a and full transition reachability remain Unknown. The teardown itself does not restore negative source offsets. Resource-offset restoration should be traced through those following calls, not attributed to the reset/free routine. No claim is made here that a particular following call restores them.

## Confidence and next test
High for tested local teardown ordering, duplicate-ID suppression, heap marking and version difference. Unknown: real asset structures, complete allocator semantics, transition flag meaning, higher-level re-entry and source-offset rebuilding. Next: trace1d25:0404 and1d25:08ae (and corresponding earlier-version functions) from file input to record/table writes. Full-game1:1 parity remains unverified.
