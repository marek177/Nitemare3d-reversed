# Heap pass16 — reuse, split, deferred coalescing and failed-growth recovery

## Finding
Confirmed across six distinct supplied DOS images: released far blocks are reused by the original allocator; a smaller request splits a free block; adjacent released blocks can be merged by a later allocation. Free itself only marks the block, as established in pass15. Failed DOS heap growth preserves the tested live block and permits later recovery from newly freed adjacent space.

## Evidence
180 stateful sequences passed:5 initial sizes16,32,64,128,512 x6 scenarios x6 images. These comprise600 original allocator calls and240 original far-free calls (840 total), with240 simulated DOS allocation requests. Original heap initialization, linked heap search, free-marker processing, splitting, merging and wrapper return paths execute. Only DOS INT21 AH48 allocation is hooked. Initial heap/list globals and failure callback are0; segment min/max globals are0. First new segment5000, later new segments spaced by0100; the tested block sizes remain within those mapped allocations. DOS failure returns carry/error8.

Every sequence first allocates A(size a) then B(size2). It asserts A=5000:0016, B=A+a+2, puts5aa5 in B and frees A. Cases:

| Scenario | Additional operations | Verified result |
|---|---|---|
| Smaller reuse | allocate a/2 | Same pointer A, no new DOS request |
| Equal reuse | allocate a | Same pointer A, no new DOS request |
| Too large with B live | allocate a+2 | New segment5100, one new DOS request |
| Adjacent merge | free B, allocate a+2 | Same pointer A, no new DOS request |
| Split | allocate a/2-2, then a/2 | First at A, second at A+a/2, no new DOS request |
| Failed growth/recover | force DOS failure, allocate a+2 ->null; free B; allocate a+2 | Later allocation at A with no further DOS request, even though provider still fails |

For all cases where B stays allocated, its5aa5 canary remains intact. In failed-growth/recovery, B's canary is checked before freeing B. Every original call checks DS restoration, far return and SP restoration. Call-by-call pointers and DOS request count/paragraphs are in evidence/allocator_reuse.json, with EXE SHA256 and per-build allocator addresses.

The growth provider allocates fresh zero-mapped test memory and does not emulate DOS memory-manager fragmentation or process blocks. Assertions are specific to these constructed sequences and sizes; they do not establish a universal allocation-placement policy for arbitrary heap histories.

## Behavior model
Allocation payload lengths in these even-size tests are followed by a2-byte next-block header. Releasing A makes its payload reusable; keeping B active prevents merging through B. When B is also free, a request that cannot fit in A alone succeeds at A, demonstrating deferred coalescing during allocation. Splitting A returns the first portion and preserves a second free portion whose subsequent allocation lands at the predicted offset. A failed growth request does not prevent that later reuse.

This extends the BSF ownership chain: pass15's mode4 consumer releases its original buffer through the same far-free routine. The heap sequences verify that the marked space can subsequently be reused; they do not execute the complete UI/BSF lifecycle in one game run.

## Ghidra12.2 changes
Updated copies of all six pass14 projects are saved under pass16/projects. The free routine receives analyst name `ReleaseFarBlock`, a dword argument at entrySP+4 and a void analytical return because callers consume no defined return value. Original behavior is unchanged; the label is not claimed as a source symbol. Allocator comments now distinguish verified existing-heap scenarios from untested arbitrary histories and failure-handler callbacks.

Each project hashes all instruction addresses/bytes and function entrypoints before/after metadata edits; hashes must match. Allocator/free targeted stock decompilations complete for all6 builds (12 C exports). No functions or candidate seeds are deleted and no global decompiler success-count increase is claimed.

## Confidence and open questions
Confirmed/High for these deterministic heap sequences, original routines and simulated DOS contract. Unknown: general allocation ordering across many heaps, all odd/zero-size sequences, double-free/invalid pointers, failure callback retry, heap compaction/release to DOS, and real process memory behavior. Full renderer/gameplay/timing1:1 parity remains open. Supplied1.8/1.9 remain one identical image.

## Reproduce
`/usr/bin/python3 scripts/verify_allocator_reuse.py` with Unicorn. Inputs include pass7 specs/instruction exports and pass15 recovered far-free entries. `python scripts/run_pass16_types.py` applies the included Ghidra script to copies of pass14 projects with Ghidra12.2/JDK25 at configured paths. Updated projects, target C, storage TSV, hashes and logs are archived. Next: generic BSF text-consumer parsing and ownership for modes3/5, then arbitrary-heap/failure-handler cases only where relevant to game callers.
