# Nitemare 3D Win16 1.10 — Ghidra 12.2 pass 10

## Finding

Classified 51 previously undefined executable-segment bytes through explicit consumers: four status IDs, fourteen toolbar IDs, five menu-mark mask bytes and two filename suffixes. Connected all thirteen nonzero toolbar IDs to message handlers and their immediate callees using original bytes and NE selector relocations. No executable modification or runtime parity claim.

Input `nite3w - 110.exe`, 230400 bytes, SHA256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`. Ghidra 12.2 PUBLIC 20261016, JDK 25.0.2.

## Evidence

| Status | Finding | Primary evidence | Confidence |
|---|---|---|---|
| Confirmed | 01CD..01D4 is four WORD IDs: 0000,E701,E702,E703; passed with count4 into 557A | Code1 data; caller 01F2; consumer 557A | High |
| Confirmed | 01D5..01F0 is fourteen WORD IDs; passed with count14 into 5856 | Same caller; consumer 5856 | High |
| Confirmed | Consumer 5856 requests count records of six bytes; stores ID, flag, then value. ID0 -> flag1/value=this.word22+2; nonzero -> flag0/value=consecutive index | 1000:5856 body | High |
| Inferred | These are framework status-indicator and toolbar-button builders | Object initialization paths, record use and text/bitmap handling | High for role; original API names not recovered |
| Confirmed | Five bytes 06,0F,0F,0F,06 at 537C..5380 feed exactly five loop iterations | 1000:5B94..5BBC | High |
| Confirmed | 5382..5386 is `.INI` plus NUL; 5387..538B is `.HLP` plus NUL; appended during app filename initialization | 1000:5E94, LSTRCAT sites; raw bytes | High |
| Confirmed | Thirteen nonzero toolbar IDs resolve to map DS:0010 entries of signature10, then game handlers | Code1 raw map entries; NE selector relocation targets segment3 | High |
| Confirmed | Twelve handlers push a DWORD with key in low WORD and zero flags in high WORD, call 1010:8CD2, then clean four bytes | Code3 raw bodies and NE call relocations | High |
| Confirmed | Remaining ID8012 invokes 1010:0DAA | 1010:01D4, raw far call/NE relocation | High |

## Toolbar dispatch chain

Rows are in the original toolbar order. Display labels/icons and ultimate game meanings are not inferred from numeric IDs alone.

| ID | Handler | Direct effect |
|---|---|---|
| 8012 | 1010:01D4 | call 1010:0DAA |
| 800A | 1010:018E | 8CD2(key=0071,flags=0) |
| 800B | 1010:01B8 | 8CD2(key=0072,flags=0) |
| 8011 | 1010:0164 | 8CD2(key=001B,flags=0) |
| 0000 | separator | flag1; value=this.word22+2 |
| 8006 | 1010:012C | 8CD2(key=0031,flags=0) |
| 8007 | 1010:013A | 8CD2(key=0032,flags=0) |
| 8008 | 1010:0148 | 8CD2(key=0033,flags=0) |
| 8009 | 1010:0156 | 8CD2(key=0034,flags=0) |
| 800D | 1010:019C | 8CD2(key=0073,flags=0) |
| 800C | 1010:01AA | 8CD2(key=0074,flags=0) |
| 800E | 1010:0180 | 8CD2(key=0078,flags=0) |
| 800F | 1010:0172 | 8CD2(key=0079,flags=0) |
| 8010 | 1010:01C6 | 8CD2(key=0009,flags=0) |

Nonzero image indices are 0..12; the separator does not increment that counter. This joins the previously recovered keyboard path to the toolbar's literal ID ordering. Availability, enabled state and actual user-triggered delivery remain runtime questions.

## Menu-mark buffer model

1000:5B0C reads GETMENUCHECKMARKDIMENSIONS, caps each dimension at32 using signed comparisons, and does not clamp a minimum. It fills a 128-byte stack buffer with FF, using the near memset from pass9 (DF=0 precondition). For the modeled positive dimensions:

    width = min(input_width,32)
    height = min(input_height,32)
    stride_bytes = 2 * ((width+15) >> 4)
    shift = min(trunc_toward_zero((width-4)/2),12)
    first_offset = ((height-6) arithmetic_shift_right 1) * stride_bytes
    for i in 0..4:
        value = NOT16(mask[i] << shift)
        buffer[first_offset+i*stride_bytes] = HIGH8(value)
        buffer[first_offset+i*stride_bytes+1] = LOW8(value)

The high byte is stored before the low byte, despite the x86 host's usual little-endian WORD representation. The code calls CREATEBITMAP(width,height,1,1,SS:buffer). If its returned AX is zero, it calls LOADBITMAP with instance0/resource7FE3. Result is stored DS:45A4. This establishes the buffer construction and fallback call, not GDI pixel interpretation, glyph appearance or runtime API success.

The status consumer allocates ten-byte records, loads text for nonzero IDs and computes extent; a zero first ID gets record byte+3 OR9 and a width based on screen width/4. E701/E702/E703 human labels are left unassigned in this pass.

## Validation

- Original binary hash and exact mask-construction loop checked.
- 3599 dimension pairs, width4..64 and height6..64, compared between literal and separately expressed buffer models. All128 bytes compared, including untouched FF bytes.
- All thirteen command map records checked against raw WORD fields and segment3 NE selector fixups; every wrapper checked against original opcodes and call selector fixups.
- Ghidra defined exactly51 bytes, annotated three consumers, completed full native export and saved the project. No new function entries were created.

| Segment | Instruction bytes | Defined data bytes | Undefined bytes |
|---|---:|---:|---:|
| 1000 | 53731 | 2463 | 352 |
| 1008 | 28814 | 623 | 257 |
| 1010 | 59156 | 1602 | 614 |
| 1018 | 18304 | 3594 | 178 |
| Total | 160005 | 8282 | 1401 |

Internal function entries remain1551, all1551 native decompilations completed;310 EXTERNAL-block entries are tracked separately. Completion does not certify signatures, full semantics or runtime parity. Undefined bytes fell1452 ->1401 solely through the five evidenced data regions. Bytes01F1 and5381 remain undefined; they were not swept into an array or called proven padding.

## Unknowns and next test

For actual menu pixels, record the runtime dimensions and compare the complete128-byte source buffer plus resulting GDI bitmap; exercise CREATEBITMAP failure to verify fallback behavior. Width below4, height below6, negative signed dimensions and resulting stack accesses are outside the safe fixture domain; no invalid-dimension safety is claimed. For toolbar reachability, break at the thirteen handlers and capture the WM_COMMAND routing and enabled states. Remaining1401 undefined bytes, the prefix before shared numeric tail and pass7 opaque metadata schema remain unresolved.

## Implementation-ready findings and confidence

Use the exact ID order, separator policy, record sizes, zero flags forwarded to key handling, five mask bytes and byte-store order. Preserve literal suffix casing. High confidence for these bounded static operations; runtime rendering, API ABI, dynamic command state and whole-game parity remain unverified.
