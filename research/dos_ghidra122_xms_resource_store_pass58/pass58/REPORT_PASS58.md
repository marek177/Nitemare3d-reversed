# Pass58 — XMS resource placement and negative-offset table preparation

## Finding
Confirmed, High: resource storage uses a word counter of occupied1024-byte blocks inside an existing XMS handle. A table preparer reads eligible resources into a staging buffer, stores a rounded block span, then replaces source offsets with the negative of the returned XMS offset. Earlier duplicate detection compares both offset and length; later alias rewriting compares only the original offset.

720 original-store scenarios and108 original-table-preparer scenarios pass across six distinct supplied DOS images. Supplied1.8/1.9 are identical and are represented once. XMS driver calls and fatal-handler entry are controlled boundaries, not actual manager execution. Table-preparer scenarios additionally mock the SND transfer callee. No real asset copy, allocation lifecycle or audio is verified.

## Evidence and locations
Exact addresses, globals, hashes and instruction bytes appear in store.json. V1.9:
- store1767:029a–0355; capacity DS:3506, used-block count DS:3508;
- existing XMS handle DS:3504, scratch segment DS:255e;
- XMS wrapper1767:0804–082b, verified in pass56/57;
- resource-table preparation1767:0586–0689; record stride6, length word DS:3f64+6*ID, offset dword DS:3f66+6*ID;
- two direct store call sites1767:03e7 and1767:0620. The former is not semantically recovered here; the latter is the table preparer.

This is placement into an existing handle, not recovery of XMS AH09 handle allocation.

## Store behavior
```
blocks = ceil(length_u16 /1024)
end = (used_u16 + blocks) &0xffff
if unsigned(end) > unsigned(capacity_u16): return0xffffffff
byte_offset = int32(int16(used_u16)) *1024
move_descriptor = {
    length: blocks*1024,
    source_handle:0,
    source_offset:source_far_packed,
    destination_handle:existing_handle,
    destination_offset:byte_offset_bits
}
call original_XMS_wrapper(descriptor)
if signed16(status_DX)<0: fatal(...)
used = end
return byte_offset_bits
```
All arithmetic, descriptor fields, counter ordering and return values above are Confirmed by original instructions plus controlled execution. Fatal tests stop at entry: counter remains unchanged at that point; actual termination/nonreturn behavior is not proved. Nonnegative synthetic error statuses follow the original accepted path as in pass56.

720-case matrix: 6 images x5 lengths(0,1,1024,1025,65535) x8(used,capacity) pairs x3 driver statuses. Pairs(0,0),(0,1),(1,1),(1,2),(31,32),(32767,32768),(32768,32769),(65535,0); statuses(AX1,BL0),(AX0,BL80),(AX0,BL7f). Full descriptors, stored counter, failure-vs-return outcome, DX:AX packed result, CS/SP and DS restoration are asserted. Synthetic large-counter probes are explicitly flagged in JSON.

Edge behavior is preserved, not promoted to a gameplay bug: the capacity addition wraps at16 bits, so usedffff plus one block becomes0 and can pass capacity0. Destination offset computation sign-extends the used word before multiplication: used8000 givesfe000000h; usedffff givesfffffc00h. The table caller tests the returned packed value as signed32, so such negative results need not be accepted there even if this store completed. Reachability with actual XMS sizes remains Unknown.

## Table-preparer model and108-case verification
Controlled resource ID10 in a synthetic79-entry table; length0,1025 or8193; alias mode none, earlier matching length/offset, or later matching offset with different length3; capacity0 or4, initial used1. This gives6x3x3x2=108 scenarios. The staging pointer is6000:0206 and file offset123. The driver receives a2048-byte move to XMS offset1024 for length1025 when capacity suffices.

Confirmed behavior:
1. Length0 returns without transfer.
2. A matching earlier offset+length returns without transfer.
3. Length>8192 returns without file or XMS transfer.
4. Eligible length1025 first calls the SND routine, even when the subsequent store fails capacity checking.
5. Successful storage advances used1->3 and replaces the current record's offset123 with-1024.
6. A later record sharing offset123 is also rewritten to-1024 even with length3; its length remains3. If capacity fails, neither offset is rewritten.

Every scenario compares all474 bytes of the79-record table against an independently prepared expected table, plus the used count and exact call trace. No claim is made that the synthetic different-length aliases occur in shipped SND.DAT. The data-format constraint that shared offsets should denote compatible payloads remains to be checked against assets.

## Ghidra project update
A separate copy of pass57's runtime project has six store return interfaces corrected to an explicit32-bit result in DX:AX. Parameters are source_far packed32 at entry stack+4 and length16 at stack+8. A fresh read-only reopen verifies both argument layouts, return storage and all978448 runtime payload bytes against original-unpacker outputs. Twelve diagnostic C files cover store and table preparer. The corrected producer C now traces the returned offset into the signed guard and negative table writes. Dynamic ES scratch-memory aliases in C remain unresolved; C generation alone is not semantic proof.

The pass7 instruction export contains misleading boundary decodes inside the table preparer (for example, a standalone LEAVE where the actual raw bytes are part of XOR CX,CX). The original relocated EXE and new runtime project's C, together with108 original-code runs, establish the tested table behavior. Do not use the old textual boundary decode as the specification.

## Outcome and next test
High confidence for the tested existing-handle placement, block rounding, offset sign transformation and alias-update rules. Unknown: handle allocation/free producer, actual capacity limits, the first direct caller's resource type, real duplicate/alias constraints and full-game1:1 parity. Next: trace initialization of capacity/used/handle and validate alias lengths against actual assets before treating the synthetic arithmetic states as reachable.
