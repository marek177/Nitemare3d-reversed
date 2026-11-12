# Image cache retrieval: bounded static evidence

2026-11-12. DOS 2.0. **PARTIAL**, zero new DEEP VERIFIED bytes. This supplementary batch checks retained instruction bytes against the canonical EXE image; it does not yet independently decode, execute or add functions to the central campaign catalog. No native test was run in this batch. The supplied `L:\nite3d\dosbox-n3d.zip` remains available for runtime preparation; its presence alone is not runtime evidence.

## Reproduction and exact scope

Run `audit_image_cache_retrieval_static.py IMAGE INVENTORY OUT` with `outputs/unpack/reproduced_image.bin` and the original N3D-20 `instructions.json`. Source hashes and exact image intervals are in `image_cache_retrieval_static/summary.json`; all 122 retained starts / 338 instruction bytes match. ASM and CSV are retained alongside it. Bounds are 0768:0350..03CE and 0768:0402..04D7, end exclusive. The one-byte inventory gap at image 07B15..07B16 contains 90; this batch does not prove it is padding or unreachable by every caller.

## Confirmed instructions and reconstructed behavior

0768:0402 takes a near DS image-record pointer at BP+6. It scans ten FAR slot pointers at DS:34CC..34F4, comparing each slot's DWORD timestamp with an initially current DS:4540 timestamp using unsigned JAE. Strictly older timestamps replace the candidate; equal timestamps keep the earlier candidate. If no candidate FAR pointer was selected, it chooses the first pointer and increments DWORD DS:E00A. Slot validity/allocation is a precondition not checked here.

Each slot has a DWORD timestamp at +0, a near DS record owner at +4 and pixel storage beginning +6. If the old owner WORD is nonzero, the routine clears that record's DWORD +6 and increments the carry-propagated DWORD DS:E006. Thus replacement invalidates the previous record's cached FAR pointer.

At 0476 CMP DWORD [record+2],0 followed by **signed JLE** selects XMS for values <=0, including zero. Positive signed values call 0277:0002 with destination slot+6, DWORD file offset and WORD length 2000h. Nonpositive values are negated modulo 2^32 and passed to 0768:0350 with the same destination and length. This explains how the previous native first-image tag of zero can be consumed. No native retrieval of that record has yet been captured.

After either call, slot.owner=record, slot.timestamp=DS:4540, record.buffer=FAR(slot+6), and DX:AX returns that same FAR pointer. Dimensions are not consulted here: requested length is always **8192 bytes**. This is a proven call argument, not proof of allocation capacity, initialized trailing bytes, successful transfer or visible pixel parity.

0768:0350 rounds its WORD byte count upward to a KiB multiple and writes an XMS move descriptor at ES:[0200], where ES=WORD DS:2560. Descriptor fields: length rounded bytes; source handle DS:3506; source DWORD offset BP+0A; destination handle zero; destination FAR DWORD BP+6. It calls the already analyzed 07FE wrapper and branches to a diagnostic only when returned DX is signed negative. Therefore this caller does not itself establish successful copying for every manager failure. Diagnostic return behavior remains outside this batch.

```text
slot = strictly_oldest_before(current_tick, ten_slot_pointers)
if slot == null: slot = first_slot; fallback_count++
if slot.owner != 0: slot.owner.buffer = null; eviction_count++
if signed32(record.position_or_tag) > 0:
    file_read_into(slot.pixels, record.position_or_tag, 8192)
else:
    xms_read_into(slot.pixels, neg32(record.position_or_tag), 8192)
slot.owner = record; slot.timestamp = current_tick
record.buffer = far_pointer(slot.pixels)
return record.buffer
```

## Required runtime evidence

Capture original 0402 entry with the previously observed zero tag, selected slot and old owner; capture the complete original 0350 move descriptor and manager return; read destination bytes after return and compare the logical 8192-byte image with IMG.1[BC0A:DC0A]. Repeat with a nonzero negative XMS tag and a positive file offset. Capture all ten slot pointers and allocation bounds before drawing conclusions about 8192-byte capacity. Exercise equal timestamps, all timestamps >= current time, and owner invalidation separately. Distinguish native states from injected edge cases. Preserve original assets and capture hashes. Renderer consumption and screen parity require further evidence.

## Thirteen-area ledger update

New semantic percentages remain **N/A**: no measured semantic denominator. Historical percentages are orientation only. All thirteen remain PARTIAL. Common blocker is absent full area closure; immediate measured work below does not replace the existing campaign catalog.

|Area|Previous orientation|New measured evidence / remaining / next step|
|---|---:|---|
|Maps and formats|99%|No new map evidence; retain prior unknowns and map tests.|
|Data types and constants|95%|Slot fields +0/+4/+6 inferred from exact instructions; verify allocation bounds.|
|Tables and pointers|93%|Ten FAR pointers statically accessed; capture actual pointer array.|
|Functions/ASM/CFG|90%|122 starts byte-matched, not centrally counted; independently decode and replay.|
|RNG|97%|No new evidence; retain prior closure tasks.|
|Scheduler|96%|DS:4540 read as ordering value; producer/tick semantics still require linkage.|
|DEMO/input|96%|No new evidence; retain prior closure tasks.|
|Renderer/VGA|94%|Fixed 8192-byte retrieval call found; renderer consumer and screen output open.|
|GUARD/bosses|93%|No new evidence; retain prior closure tasks.|
|Weapons/projectiles|92%|No new evidence; retain prior closure tasks.|
|Sprites/HUD/palette|92%|Image-record buffer pointer assigned; exact downstream pixel interpretation open.|
|SAVE/LOAD|92%|No new evidence; retain prior closure tasks.|
|Windows Win16|92%|No counterpart verified in this batch; DOS conclusions not generalized.|

PASS320 map unchanged: 57,295 bytes = PARTIAL 57,118 + CLASSIFIED ONLY 149 + UNKNOWN 28; DEEP VERIFIED 0. No GitHub publication claimed for this supplementary local batch.
