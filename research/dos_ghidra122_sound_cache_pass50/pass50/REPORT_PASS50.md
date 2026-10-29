# Pass 50 — DOS sound resource cache

## Finding
Confirmed, High: six distinct supplied DOS images use a four-slot cache for resource lengths <=8192 bytes. Cache hits do not refresh the stored timestamp. This is oldest-fill selection under the tested monotonic-clock conditions, not least-recently-used access selection. Supplied 1.8/1.9 share the same executable image with embedded V1.9.

## Evidence
648 passing executions of original relocated EXE code: six images x sizes 0/8192/8193 x resource offsets +123/-123/0 x four timestamp arrangements x miss/slot0-hit/slot3-hit. Synthetic cache blocks; only the two data-transfer callees were mocked. Original selection, header reads/writes, counters and returns execute. Input hashes and exact version-specific instructions are in evidence/cache.json. Source: preserved Ghidra 12.2 instruction exports, cross-checked by execution in Unicorn 2.1.4; no new Ghidra project edits or full-game/audio run.

| Status | Claim | V1.9 location | Confidence |
|---|---|---|---|
| Confirmed | Resource table stride 6: length u16, signed source offset i32 | 1767:0698–06ac, DS:3f64 | High |
| Confirmed | Unsigned length >0x2000 returns DX:AX=0 before scanning | 1767:06a6–06b4 | High |
| Confirmed | Four far pointers; block header timestamp u32 at +0, ID u16 at +4, payload +6 | 1767:06be–06ee; DS:34f2..3501 | High |
| Confirmed | Matching ID returns payload pointer without timestamp/counter update | 1767:073e–074f | High |
| Confirmed | Miss chooses first strictly smallest timestamp below current DS:453e u32; unsigned comparison; ties retain earlier slot | 1767:06b6–06ee | High |
| Confirmed | If no timestamp is below current clock, select slot0 and increment DS:e020 dword | 1767:06f0–0706 | High |
| Confirmed | Selected nonzero old ID increments DS:e01c dword | 1767:070b–0715 | High |
| Confirmed | Positive source offset uses far transfer; zero/negative uses near transfer with negated magnitude | 1767:0720–073b,0750–076e | High |
| Confirmed | Miss stamps selected header with requested ID and current clock; returns payload pointer | 1767:0771–0788 | High |
| Inferred | Positive/negative source offsets distinguish backing stores | Transfer targets not executed here | Medium |
| Unknown | Actual asset identity, clock update cadence/wrap behavior in gameplay, transfer errors | Missing original asset/driver execution | — |

## Behavior model
```
if resource[id].length > 8192: return null
candidate = null; minimum = current_clock
for slot in slots[0:4]:
    if slot.id == id: return slot.payload
    if unsigned(slot.timestamp) < unsigned(minimum):
        candidate = slot; minimum = slot.timestamp
if candidate == null:
    candidate = slots[0]; fallback_counter++
if candidate.id != 0: replacement_counter++
transfer(candidate.payload, abs_signed_source_offset, length,
         positive_path_if_offset_gt_zero_else_other_path)
candidate.id = id
candidate.timestamp = current_clock
return candidate.payload
```
Header ID zero is treated specially only for the replacement counter; no separate empty-slot preference was observed in the instructions. Tests request ID66 with all original IDs nonzero. Signed INT_MIN negation and unusual/null cache pointers were not tested. Payload offset addition is 16-bit with no segment carry in the instruction stream; only ordinary offsets tested.

## Additional static lead
V1.9 fallback 1c27:03a2–03d9 compares resource length unsigned to 15000 (0x3a98). For lengths <=15000 it invokes far transfer 1277:008a to fixed buffer 2d0b:0000; above the threshold it skips the transfer but still returns 2d0b:0000. This is static evidence only in V1.9, not a runtime result or a claim of reachable oversized sound playback. Next test: execute this fallback across six images at 14999/15000/15001, intercept transfer, then integrate cache/fallback with dispatcher.

## Implementation-ready findings
Preserve four slots, first-tie selection, no hit timestamp refresh, strict timestamp comparison against current clock, >8192 bypass and zero-offset alternate transfer path. Do not silently replace with a conventional access-LRU cache. Backing-store semantics and error behavior remain TBD. Passing cases do not establish whole-game 1:1 parity.
