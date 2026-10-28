# Nitemare 3D – RE-MAX V068: GUARD41 terminal class, count writer census, WORLD Y-sort

**20. október 2026 — nový originálny statický audit DOS V1.2 + DOS V2.0 a spätné binárne overenie autentického V067 runtime. Nie nový DOSBox gameplay run. Nie original-vs-remake parita.**

## Original provenance

| Original | SHA-256 |
|---|---|
| DOS V1.2 `N3D-12.exe` | `f7074660ed26525d2cc5ccd16a6e5ac011f29aaf819dc8ca24ebe39f0fd793e5` |
| DOS V2.0 `N3D-UNFU.exe` | `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301` |
| Prior original V067 `long/trace-000000.n3dt` | `fb521dac30678d324bfeb75de854ed5239d98399de86e1ed4430599082f30184` |

All code addresses below are **MZ load-image offsets**, not file offsets or live CS:IP. The original MZ header is 512 bytes.

## 1. Direct actor-count writer census

| | DOS1.2 | DOS2.0 |
|---|---|---|
| GUARD count address | `DS:61D2` | `DS:6276` |
| Exact 16-bit little-endian literal occurrences in full MZ image | **26** | **26** |
| Direct reset writer (SI=0 in level constructor) | `IMG:B54C` | `IMG:B80E` |
| Direct increment writer (guard instantiation) | `IMG:B666` | `IMG:B928` |
| Direct compare-to-100 guard | `IMG:B620` | `IMG:B8E2` |
| Additional direct literal count decrements | **none found** | **none found** |

The actor stride is 26 bytes: base offset `0x264E` plus 41*26 gives GUARD41 offset `0x2A78`. The only literal near-data count writers identified are the constructor's zero and increment. **This is NOT exhaustive alias / indirect / REP MOVS-STOS / SAVE-LOAD writer proof**, and cannot alone prove that a GUARD slot is never reclaimed.

One original V067 **2,200,000-I/445,249-W** follow-up trace was scanned for writes overlapping runtime `DS:6276` (linear `0x35BC6` at DS=2F95): **0 instrumented writes**. This is bounded negative runtime evidence, not proof for all time.

## 2. Four exact state0A exclusion gates in both original DOS builds

| Function | DOS1.2 IMG | DOS2.0 IMG |
|---|---|---|
| Position-based GUARD lookup | `5F50` | `619E` |
| Filter before selected hit test | `6787` | `69D5` |
| GUARD map-event scan | `9717` | `99B1` |
| Active GUARD summary/count loop | `A733` | `A9F5` |

The corresponding `CMP GUARD+0B,0A / JE skip` machine code is **byte-identical** in both versions at every site. These gates **exclude a terminal enemy from local gameplay decisions while preserving its array record**; other callers remain unclosed.

## 3. WORLD class0F terminal helper is not an object drop

The original DOS2 CPU trace has live `WORLD+06=0x0F` and executed `IMG:86EA` (`WORLD+05 |= 1`), `IMG:86F2` (`GUARD+0B = 0A`), then the class table index `(0F-09)*2=0x0C`. It lands directly at `IMG:87D4`, the `POP SI; POP DI; LEAVE; RETF` epilogue, not at a boss morph or class-specific drop.

Equivalent original DOS1.2 locations: WORLD flags `IMG:848E`; state writer `IMG:8496`; table value `0x03F8` → epilogue `IMG:8578`. DOS2 table value `0x0404` → epilogue `IMG:87D4`. In the observed GUARD41 call, the WORLD flag remained `0B→0B`; OR bit 1 produced no change.

Both GUARD state tables map `0x0A` and `0x0B` to common dispatcher epilogue (DOS1.2 `12B2`, DOS2 `12B0`). **Only this local class0F callback is closed; indirect future item creation is not ruled out**.

## 4. NEW: `WORLD+0x32:261→260` is actually an adjacent object's sorted-Y rank

The prior V067 trace included one unattributed `WORLD+0x32` store within the broad 80-byte watched region around GUARD41's linked descriptor `2A21:1C5A`. Replaying the original CPU/W events resolves it exactly:

| DOS2 CPU ordinal | Executed code (IMG) | Actual W | Meaning |
|---:|---|---|---|
| 976560 | `B0F2`, `INC WORD ES:[SI+16]` | `2A21:1BAC`, `260→261` | first 28B WORLD object's Y-sort rank |
| 976562 | `B0F9`, `DEC WORD ES:[SI+16]` | `2A21:1C8C`, `261→260` | second, adjacent 28B WORLD object's Y-sort rank |
| 976568 | `B10B`, `MOV DWORD [BX],EAX` | `DS:DE9E`, FAR `2A21:1B96→2A21:1C76` | pointer at sorted position 260 |
| 976570 | `B111`, `MOV [BX+04],CX` | `DS:DEA2`, offset `1C76→1B96` | pointer at sorted position 261 |

Runtime `DS=2F95`, `ES=2A21`, `BX=DE9E`, `DI=0104=260`; source list is `DS:DA8E+260×4`. **The `WORLD+0x32` address is `(1C5A+1C)+16`—the +16 rank field of the NEXT 28B WORLD object**, not a field of the linked descriptor or an item drop. This paired increment/decrement plus FAR-pointer swap is a coherent positional re-sort.

Original DOS1.2 contains the same paired Y-sort opcode skeleton at `IMG:AE30/AE37`; DOS2 at `B0F2/B0F9`.

## 5. Verification and strict remaining P0

User-owned private proof `N3D_GUARD41_TERMINAL_STATIC_V068_20261020.zip`, SHA256 `44e3cef83371eb518ede90f0b61e94afd54f4326e76c2362b3d1fa3e9fc0603e`, 8 files. It includes the full standalone Python stdlib verifier, three derived CSV ledgers, JSON result, Slovak README and SHA256 manifest. No original game binaries, demo data or raw 2.2M CPU traces are redistributed in this GitHub update.

The private verifier passed both original MZ SHA-gated audits, the original V067 trace-class0F and pointer-swap witnesses, a scan of all 445249 instrumented W events for direct count changes, and **18/18 correctly rejected original-byte mutation negatives**.

**OPEN:** true transitive slot-free or drop writers through pointer aliases, block copies and LOAD; potential class-specific callbacks outside local helper; remaining game ticks and full original-vs-clean-room state/pixel/DAC/SFX parity. No global parity-percentage change.