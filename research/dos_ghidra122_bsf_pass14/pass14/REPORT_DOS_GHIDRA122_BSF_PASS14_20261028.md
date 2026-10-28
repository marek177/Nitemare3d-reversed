# BSF pass14 — far allocator ABI, length wrap, Ghidra signatures

## Finding
Confirmed for six distinct DOS images: BSF loader's allocator returns a far pointer in DX:AX, not AX alone. With an empty heap and null failure handler, original allocator accepts requests0..ffe8 when DOS memory allocation succeeds; larger requests return null without a DOS request. A zero request returns a nonnull pointer in the tested setup. Loader lengthffff wraps its allocation argument to0 and writes the NUL terminator one byte before that pointer due to16-bit offset addition.

## Evidence
204 targeted executions passed:132 allocator cases plus72 loader boundary cases. Original allocator, DOS block initialization, heap-list insertion and first allocation/split execute. Only DOS INT21 AH48 allocation is simulated: segment5000 on success or carry/error8 on failure. Heap head/list globals and failure callback are initialized to0; segment min/max globals are0. This establishes empty-heap behavior, not arbitrary existing-heap/coalescing/retry-handler semantics.

Allocator requests0,1,2,52,53,54,512,32767,ffe8,ffe9,ffff x success/failure x6 images =132. Assertions cover DOS request count, DX:AX, DS restoration, far return/SP and allocation-header word on success. Returned pointer is5000:0016; header word at5000:0014 equals `(size+1)&fffe` in these cases. Size0 yields header word0 and nonnull pointer0016; it must not be treated as a usable65536-byte allocation. Sizes>ffe8 return0000:0000 without DOS allocation.

Loader boundary lengths0,1,ffe7,ffe8,fffe,ffff x DOS allocation success/failure x6 images =72. Original loader and allocator execute through the terminator write; tests stop before original decoder, or before fatal allocation callee on null. Open/seek/read/close are simulated, read returns0 and leaves memory unchanged. Memory-write hooks check exact one-byte-zero terminator location; read arguments and decoder arguments are checked. This suite deliberately does not execute the oversized decode or claim a full out-of-bounds exploit/reachability result.

| Loader length | Requested allocation | Success-path observation |
|---|---|---|
| 0000 | 0001 | Pointer0016, NUL at0016 |
| 0001 | 0002 | Pointer0016, NUL at0017 |
| ffe7 | ffe8 | Accepted, NUL atfffd |
| ffe8 | ffe9 | Allocator returns null, loader fatal branch |
| fffe | ffff | Allocator returns null, loader fatal branch |
| ffff | 0000 | Nonnull zero-size pointer0016, NUL at0015 |

All addresses above are offsets in injected segment5000. At lengthffff the terminator falls in the preceding allocation header; the decoder would be called with lengthffff. The actual BSF lengths seen in pass7 do not reach this boundary. Real-world reachability of malicious/truncated headers and subsequent heap effects remain unknown.

V1.9 allocator21ea:2069, growth helper21ea:22e6, first-block allocator21ea:216c. Entry and global addresses are extracted independently for every image; hashes and observed DOS paragraph requests are in evidence/far_allocator.json. Loader observations are in loader_allocation_boundary.json.

## Ghidra12.2 changes
Fresh copies of pass7 projects are saved under pass14/projects. Added analyst names `AllocateFarBytes` and `SeekDosHandle`; these are analytical labels, not recovered source symbols. Allocator signature: one ushort at entry SP+4, raw dword return DX:AX. Seek signature: handle ushort SP+4, signed-offset bit pattern dword SP+6, origin ushort SP+10; raw dword DX:AX return. Seek ABI is supported by pass13's1008 cases; allocation ABI by this pass.

For each build, Ghidra decompiles allocator, seek and BSF loader after the two signature changes. Script hashes all instruction addresses/bytes plus all function entrypoints before and after; hashes must match. This verifies metadata-only changes without deleting candidate functions or modifying code. All18 targeted stock decompilations complete; no global success-count increase or semantic completeness percentage is claimed. Stock segmented-address artifacts can remain in other parts of the resulting C.

## Confidence and remaining unknowns
Confirmed/High for tested empty-heap allocation, far return ABI, exact length wrap/write location and metadata changes. DOS/heap provisioning is simulated. Unknown: existing-heap search/coalescing, failure callback retries, original DOS process memory setup, full decoder execution after zero-size allocation, real boundary reachability and BSF caller ownership. Supplied1.8/1.9 remain one identical image. Full gameplay1:1 parity remains open.

## Reproduce
Run `/usr/bin/python3 scripts/verify_far_allocator.py` and `/usr/bin/python3 scripts/verify_loader_allocation_boundary.py` (Unicorn). For metadata, run `python scripts/run_pass14_types.py` with the included Ghidra script, prior pass7 projects and Ghidra12.2/JDK25 at the configured paths; copied updated projects are included so rerun is optional. Audit includes target C, storage TSV, invariant hashes and Ghidra logs.
