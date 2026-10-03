# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 29

Date: 2026-10-03

Primary image:
- `N3D_DOS_v2.0_IDA.EXE`
- unpacked DOS V2.0 load image

Address convention:
- addresses are unpacked MZ image offsets;
- raw 16-bit machine code is authoritative;
- CODE and DATA/TABLE bytes are counted separately.

## Result

Pass 29 resolves:

`0x17F39 .. 0x18B55`

Total span: **3,101 bytes**

Classification:

- **511 bytes executable WORX/XMS/device support -> GREEN**
- **2,590 bytes WORX TABLE/DATA/STATE -> GREEN**

This pass continues directly from pass 28'with XMS setup helper.

---

# 1. `0x17F39..0x17FDF` — `CacheCurrentDataSourceIntoXmsSlot`

Length: **167 bytes**

This routine copies the current WORX data source into an XMS-backed cache slot.

Flow:

1. call the current data-source opener/setup helper at `0x18DBA`;
2. if its returned high word is `FFFFh`, fail with `AX=FFFFh`;
3. increment the WORX/XMS slot index at the module state word corresponding to `20C4`;
4. set scratch destination to the conventional-memory buffer at offset `2249`;
5. initialize and 16-byte XMS move descriptor rooted at `21CC`;
6. copy the active XMS handle into descriptor destination-handle field;
7. load the destination XMS offset from the per-slot offset table;
8. repeatedly request up to `0x100 = 256` bytes from helper `0x18D1E`;
9. store the actual byte count into the move descriptor;
10. invoke the XMS driver with:

`AH = 0Bh`

which is **Move Extended Memory Block**;
11. advance both the per-slot XMS cursor and the descriptor destination offset;
12. continue until the read helper returns zero bytes.

The move descriptor layout is mechanically identifiable:

```text
+00 DWORD transfer length
+04 WORD  source handle = 0 for conventional memory
+06 DWORD conventional source pointer
+0A WORD  destination XMS handle
+0C DWORD destination XMS offset
```

Return on success:

- `DX = 0`
- `AX = current cache/slot index`

Return on setup failure:

- `AX = FFFFh`

This is and genuine WORX/XMS cache loader, not gameplay code.

**Status: GREEN.**

---

# 2. `0x17FE0..0x17FE6` — `ReturnZeroLong`

Length: **7 bytes**

Exact body:

```text
DX = 0
AX = 0
RET
```

This is and small callback/stub returning and 32-bit zero value.

**Status: GREEN.**

---

# 3. `0x17FE7..0x187FC` — WORX static lookup/configuration tables

Length: **2,070 bytes**

This block is non-code.

It contains multiple static tables used by the adjacent WORX audio/device routines.

Observed shapes include:

- byte control tables;
- descending WORD lookup sequences;
- fixed-size parameter records;
- register/value tables consumed by the FM-programming helper;
- additional device/audio configuration constants.

AND particularly obvious WORD table descends through values such as:

```text
0x0EF0
0x0D5A
0x0C98
0x0BE3
...
0x010D
0x00FD
0x00EF
...
0x0032
0x002F
```

These are consistent with low-level synthesis/timing/frequency lookup use, but this
pass deliberately does not assign historical vendor symbol names to each individual
sub-table.

Important conclusion:

**the entire range is DATA/TABLE, not executable code.**

**Status: TABLE/DATA GREEN.**

---

# 4. `0x187FD..0x18836` — WORX vendor signature

Length: **58 bytes**

Literal ASCII:

`WORX TOOLKIT VERSION 2.1 COPYRIGHT 1993 BY MYSTIC SOFTWARE`

This independently confirms that this module is the same WORX device/audio subsystem
whose application-facing ABI was closed in pass 23.

**Status: DATA GREEN.**

---

# 5. `0x18837..0x18A04` — WORX initialized state/defaults

Length: **462 bytes**

Mostly zero-initialized module state with and small number of fixed defaults/sentinels.

Observed values include:

- `FFFFh` sentinels;
- small mode bytes;
- small counters;
- fixed WORD/DWORD defaults.

The tail immediately before the next code entry remains state/config data.

No reliable executable control flow starts inside this interval.

**Status: DATA/STATE GREEN.**

---

# 6. `0x18A05..0x18A30` — `ConvertCStringToLengthPrefixedInPlace`

Length: **44 bytes**

Input:

- `ES:DI` points to and NUL-terminated string.

Behavior:

1. scan to terminating NUL to obtain length;
2. if length is zero, return;
3. preserve original first character;
4. write the length byte at offset `0`;
5. shift the string body one byte to the right;
6. restore the original first character at offset `1`.

Result is and Pascal-style length-prefixed byte string in the same storage.

**Status: GREEN.**

---

# 7. `0x18A31..0x18A45` — `WaitBiosTickDelta`

Length: **21 bytes**

Uses:

`INT 1Ah`

BIOS time-of-day tick service.

Flow:

1. read current tick value into `DX`;
2. add caller-supplied `BX` delta;
3. repeatedly call `INT 1Ah`;
4. return when current `DX` exceeds the target.

This is and small BIOS-tick delay helper.

No timeout/wrap handling is visible in the body.

**Status: GREEN.**

---

# 8. `0x18A46..0x18A65` — `CopyLengthPrefixedStringToInternalCString`

Length: **32 bytes**

Input:

- `ES:DI` points to and byte-length-prefixed string.

Behavior:

1. read the leading length byte;
2. copy exactly that many bytes from source+1;
3. destination is the module'with fixed internal string buffer;
4. append terminating NUL;
5. return the destination pointer in `DI`.

This is the inverse bridge used by the WORX resource/device layer.

**Status: GREEN.**

---

# 9. `0x18A66..0x18A6C` — `SetWorxStringModeFlag`

Length: **7 bytes**

Stores:

`1`

into one WORX module state byte and returns.

Exact higher-level label for that flag is not established, but the setter semantics
are complete.

**Status: GREEN.**

---

# 10. `0x18A6D..0x18B0A` — `InitializeWorxToolkitInterruptsAndTimer`

Length: **158 bytes**

This is and major WORX initialization entry.

## INT 63h

The routine obtains the previous software interrupt `63h` vector using:

```text
INT 21h
AH = 35h
AL = 63h
```

and stores the old handler.

It then installs the WORX handler with:

```text
INT 21h
AH = 25h
AL = 63h
DS:DX = WORX INT63 handler
```

This is the same software API consumed by the `WorxInt63Command` wrapper from pass 23.

## Internal device initialization

The routine then runs and fixed register-initialization sweep through helper `0x19497`,
including:

- and complete 8-bit register-selector pass;
- one fixed `AX=2001h` device write.

These calls belong to the low-level audio/device backend.

## INT 08h timer hook

The function obtains the old timer IRQ vector:

`INT 08h`

and saves it.

It then installs the WORX timer handler through DOS `AH=25h`.

Finally it calls an internal timer/rate helper with fixed value:

`0x0952`

and caches that value in WORX state.

Interrupts are disabled while the vectors and state are changed and re-enabled before
the far return.

Therefore the exact architecture is:

```text
save old INT63
install WORX INT63 API
initialize audio/device registers
save old INT08
install WORX timer hook
configure WORX timer rate/state
```

**Status: GREEN.**

---

# 11. `0x18B0B..0x18B4E` — `ProgramWorxFmVoiceFromTables`

Length: **68 bytes**

This helper programs and set of low-level audio registers from internal WORX tables.

It performs five iterations.

For each iteration it:

1. reads one register selector from and static table;
2. derives one device register address from and per-voice table and and channel offset;
3. writes through common helper `0x19497`;
4. repeats for and second selector/table pair;
5. advances the device-register group by `0x20`, with one wrap case.

After the loop it selects one WORD from another table using the caller-supplied
voice/index value, swaps its bytes, and sends that final value through `0x19497`.

The surrounding hardware routines and table layout show that this belongs to the
WORX FM/synthesis backend.

Exact original vendor function name is unknown.

**Status: GREEN.**

---

# 12. `0x18B4F..0x18B55` — `ReturnWorxMagicSignature`

Length: **7 bytes**

Exact return:

```text
AX = 1234h
DX = 5678h
RET
```

Combined 32-bit marker:

`0x56781234`

This is and fixed WORX signature/probe value.

**Status: GREEN.**

---

# Byte-map impact

Resolved span:

`0x17F39 .. 0x18B55`

Total:

**3,101 bytes**

| Range | Bytes | Classification |
|---|---:|---|
| `17F39–17FDF` | 167 | XMS cache-loader code |
| `17FE0–17FE6` | 7 | zero-return callback |
| `17FE7–187FC` | 2,070 | WORX static tables |
| `187FD–18836` | 58 | WORX vendor signature |
| `18837–18A04` | 462 | WORX state/default data |
| `18A05–18A30` | 44 | C-string -> length-prefixed string |
| `18A31–18A45` | 21 | BIOS tick delay |
| `18A46–18A65` | 32 | length-prefixed -> internal C string |
| `18A66–18A6C` | 7 | WORX state flag setter |
| `18A6D–18B0A` | 158 | INT63 + INT08 WORX initialization |
| `18B0B–18B4E` | 68 | FM/device table programming |
| `18B4F–18B55` | 7 | fixed WORX signature return |

Totals:

- **CODE GREEN added: 511 bytes**
- **DATA/TABLE/STATE GREEN added: 2,590 bytes**

---

# Closure metrics

Pass 28 executable GREEN cumulative:

`65,897 bytes`

Pass 29 adds executable code:

`511 bytes`

New executable GREEN cumulative:

**66,408 bytes**

Pass 28 DATA/TABLE/STATE GREEN:

`8,917 bytes`

Pass 29 adds:

`2,590 bytes`

Tracked DATA/TABLE/STATE GREEN from passes 28–29:

**11,507 bytes**

To not combine this data total with executable-function closure percentages.

---

# Important architectural consequence

The XMS code is now connected directly to the embedded WORX subsystem:

```text
WORX data source
      ↓
18D1E buffered/source read
      ↓
17F39 chunk loader
      ↓
16-byte XMS move descriptor
      ↓
XMS AH=0Bh
      ↓
WORX XMS cache slot
```

and WORX startup is:

```text
18A6D
  ├─ install INT63 API
  ├─ initialize device/FM state
  ├─ install INT08 timer hook
  └─ configure toolkit timer state
```

This substantially reduces the remaining uncertainty around why Nitemare 3D'with DOS
audio/device support, XMS usage and software INT63 interface occur in the same
third-party module.

---

# Next target

Continue at:

`0x18B56`

The next function is and matching WORX shutdown/cleanup path.

Its raw body already shows:

- subsystem cleanup calls;
- restoration of the previous `INT 08h` vector;
- restoration of the previous `INT 63h` vector;
- XMS function `AH=0Ah` to free the active XMS handle;
- final interrupt-state restoration.

With the next pass should close the WORX shutdown, device-detection and remaining
low-level hardware helpers beginning at `0x18B56`.