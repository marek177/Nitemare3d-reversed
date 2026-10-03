# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 23

Date: 2026-10-03

Primary binary:
- `N3D-E-20(3).EXE`
- size: 116,606 bytes
- SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`

Address convention:
- ranges below are unpacked MZ image offsets;
- physical EXE file offset = image offset + `0x200` in this unchanged-prefix region;
- raw 16-bit machine code is authoritative;
- exact vendor/library command semantics are named only where Nitemare3D call-sites prove them;
- static GREEN of the N3D-facing ABI is separate from waveform/device/runtime parity.

## Result

Pass 23 closes the complete contiguous region

`0x10BFC .. 0x11EE6`

as **GREEN / deep static ABI semantics**.

Total span: **4,843 bytes**.

- exact real function count: **75**;
- total routine bytes: **4,843**;
- inter-function padding inside the span: **0 bytes**;
- every function terminates cleanly with `RETF` before the next entry.

The key correction is that this range is not unexplained gameplay code. It is the
**Nitemare-3D -> WORX Toolkit v2.1 device/audio API wrapper layer**.

The binary itself contains the literal vendor string:

`WORX TOOLKIT VERSION 2.1 COPYRIGHT 1993 BY MYSTIC SOFTWARE`

The central wrapper at `0x10BFC` sends commands through **software interrupt 63h**.
This lets the remaining wrappers be reconstructed as an exact command ABI even when and
human-readable name for and particular vendor opcode is not yet justified.

---

# 1. `0x10BFC..0x10C5E` — `WorxInt63Command`

Length: **99 bytes**.

This is the central command thunk for the whole band.

Its five N3D-facing inputs are packed into and register structure as:

```text
AH = command/opcode byte
AL = first byte argument
BX = second WORD argument
DX = third WORD argument
DI = fourth WORD argument
```

The function then calls the generic interrupt executor at actual far target:

```text
11EE:24EA
```

which maps to image:

```text
0x143CA
```

with interrupt number:

```text
0x63
```

After the interrupt returns, the wrapper caches:

```text
DS:413E = AX
DS:4140 = BX
DS:4142 = DX
DS:3F4E = DI
```

and returns the cached AX value.

The wrapper does not explicitly seed CX or SI in its visible N3D ABI, with and portable
compatibility layer should not invent stable N3D arguments for those registers.

**Status: former opaque external helper -> GREEN.**

---

# 2. `0x143CA` generic interrupt executor — proof of the ABI

The far target used by `WorxInt63Command` is and generic real-mode interrupt helper.

It constructs executable bytes on the stack beginning with:

```text
CD <interrupt-number>
CB
```

(`INT n` followed by far return; INT 25h/26h receive their special stack handling).

It then loads from the input register record:

```text
+00 AX
+02 BX
+04 CX
+06 DX
+08 SI
+0A DI
```

executes the requested interrupt, stores the returned registers to the output record,
and writes carry/error state at `+0C`.

Therefore the call made by `0x10BFC` is mechanically:

```text
execute INT 63h with a WORX command register set
```

rather than and guessed C library call.

**Status: ABI proof GREEN.**

---

# 3. Toolkit identity

The primary executable contains the null-terminated literal at physical file offset
`0x16768`:

```text
WORX TOOLKIT VERSION 2.1 COPYRIGHT 1993 BY MYSTIC SOFTWARE
```

This matches the already recovered engine architecture in which music, digitized SFX
and joystick/device support share one third-party DOS subsystem.

For and 1:1 portable reconstruction the important boundary is therefore:

```text
N3D engine
   -> exact WORX command wrapper ABI
   -> platform/device backend
```

The original vendor implementation does not have to be copied into the portable core;
the observable command ordering, packing, return values and engine-visible side effects
to have to be preserved.

---

# 4. Directly identified WORX command meanings

These meanings have direct N3D caller evidence, not merely opcode-shape guesses.

| WORX AH | Wrapper image | Confirmed N3D use |
|---:|---:|---|
| `01h` | `1132D` | Sound Blaster DSP auto-detection; result is reported as detected IRQ/status |
| `02h` | `1135F` | forced Sound Blaster DSP detection using configured port/IRQ |
| `04h` | `112FE` | disable/shutdown the hardware digitized-SFX/DSP route |
| `0Dh` | `11AB2` | stop current music resource when active |
| `15h` | `11B10` | stop current PC-speaker/fallback SFX before replacement |
| `1Ch` | `11BA3` | query whether PC-speaker/fallback SFX is active |
| `21h` | `1113C` | SFX two-channel mixer/control pair; fed from DOS SFX volume/pan logic |
| `22h` | `11187` | music two-channel mixer/control pair; fed from DOS music volume |
| `2Ch` | `11201` | joystick button/status query; called with indexes `0,1,2,3` |

### Sound Blaster detection evidence

`C2D0` calls command `01h` for ordinary detection.  In forced mode it calls `01h`
first, then `02h` with the explicit configured DSP port/IRQ values and selects the
startup text corresponding to success/failure.

### SFX control evidence

`C686 = PlaySoundEffect` uses:

```text
AH=1Ch  query fallback/PC-speaker activity
AH=15h  stop fallback/PC-speaker activity
AH=21h  configure two SFX mixer/control values
```

before starting the resolved SFX buffer.

### Music control evidence

`C532 = StopMusicIfActive` calls command `0Dh` after its music-active predicate.

`C35A = ApplyMusicVolume` scales `DS:414A` to `0..15` and routes the pair through
command `22h`.

### Joystick evidence

`C77A = SnapshotAudioBackendMetrics` calls command `2Ch` four times with indexes
`0..3` and stores the four returned values into its output structure.

---

# 5. Exact wrapper inventory

The table below records every real entry in the closed span.  For commands whose
higher-level meaning is not yet proven, the numeric command is intentionally retained
as the compatibility contract.

| Image range | Bytes | Exact wrapper role / WORX command |
|---|---:|---|
| `10BFC–10C5E` | 99 | central `WorxInt63Command` / INT 63h thunk |
| `10C5F–10C76` | 24 | toolkit support thunk to `15BF:2F66` |
| `10C77–10CD9` | 99 | command `1Ah`; far-pointer/named request wrapper |
| `10CDA–10D2F` | 86 | command `18h` wrapper |
| `10D30–10D97` | 104 | command `17h` + result/size helper |
| `10D98–10DC8` | 49 | command `48h` |
| `10DC9–10E8F` | 199 | composite external-resource/handle resolver |
| `10E90–10EE4` | 85 | command `49h` |
| `10EE5–10F16` | 50 | command `45h` |
| `10F17–10F48` | 50 | command `2Dh` |
| `10F49–10F77` | 47 | command `1Fh` |
| `10F78–10FA9` | 50 | command `13h`, byte argument |
| `10FAA–1102C` | 131 | composite resolver + command `39h` |
| `1102D–1105E` | 50 | command `16h`, byte argument |
| `1105F–11090` | 50 | command `38h` |
| `11091–110DB` | 75 | command `20h`, packed pair `(a<<4) | b` |
| `110DC–1110D` | 50 | command `27h` |
| `1110E–1113B` | 46 | command `28h`, WORD argument |
| `1113C–11186` | 75 | command `21h`, packed SFX mixer/control pair |
| `11187–111D1` | 75 | command `22h`, packed music mixer/control pair |
| `111D2–11200` | 47 | command `29h` |
| `11201–11235` | 53 | command `2Ch`, joystick button/status index |
| `11236–11267` | 50 | command `2Ah` |
| `11268–11299` | 50 | command `2Bh` |
| `1129A–112CB` | 50 | command `23h` |
| `112CC–112FD` | 50 | command `37h` |
| `112FE–1132C` | 47 | command `04h`, disable/shutdown digital-SFX route |
| `1132D–1135E` | 50 | command `01h`, SB DSP autodetect |
| `1135F–11391` | 51 | command `02h`, forced SB DSP detect |
| `11392–11440` | 175 | composite external-resource resolver variant |
| `11441–11488` | 72 | command `10h`, packed arguments |
| `11489–1151B` | 147 | composite resolver + command `0Fh` |
| `1151C–1154A` | 47 | command `43h`, WORD argument |
| `1154B–115A5` | 91 | command `1Bh`, far-pointer argument |
| `115A6–11600` | 91 | command `40h`, far-pointer argument |
| `11601–1165B` | 91 | command `06h`, far-pointer argument |
| `1165C–116B6` | 91 | command `3Ah`, far-pointer argument |
| `116B7–116E5` | 47 | command `44h`, WORD argument |
| `116E6–11714` | 47 | command `47h`, WORD argument |
| `11715–11769` | 85 | command `1Eh`, far-pointer argument |
| `1176A–117BE` | 85 | command `0Ch`, far-pointer argument |
| `117BF–117FD` | 63 | command `05h` wrapper |
| `117FE–1183C` | 63 | command `3Ch` wrapper |
| `1183D–1187A` | 62 | command `3Fh` wrapper |
| `1187B–118AC` | 50 | command `3Dh` wrapper |
| `118AD–118EB` | 63 | command `3Bh` wrapper |
| `118EC–11920` | 53 | command `12h`, two byte arguments |
| `11921–11958` | 56 | command `4Dh`, packed control argument |
| `11959–11987` | 47 | command `0Ah` |
| `11988–119B9` | 50 | command `0Eh` |
| `119BA–119E8` | 47 | command `1Dh`, WORD argument |
| `119E9–11A1A` | 50 | command `09h`, WORD argument |
| `11A1B–11A5C` | 66 | command `14h` wrapper |
| `11A5D–11A74` | 24 | toolkit support thunk to `15BF:2E7D` |
| `11A75–11AB1` | 61 | command `11h`, packed byte arguments |
| `11AB2–11AE0` | 47 | command `0Dh`, stop current music |
| `11AE1–11B0F` | 47 | command `07h` |
| `11B10–11B3E` | 47 | command `15h`, stop fallback/PC-speaker SFX |
| `11B3F–11B70` | 50 | command `0Bh` |
| `11B71–11BA2` | 50 | command `08h` |
| `11BA3–11BD4` | 50 | command `1Ch`, query fallback/PC-speaker SFX active |
| `11BD5–11C08` | 52 | digital-route shutdown helper then command `25h` |
| `11C09–11C37` | 47 | command `32h` |
| `11C38–11C66` | 47 | command `34h` |
| `11C67–11C98` | 50 | command `31h`, WORD+byte arguments |
| `11C99–11CCC` | 52 | command `35h`, packed mode/control arguments |
| `11CCD–11D32` | 102 | command `33h` followed by command `35h` |
| `11D33–11D98` | 102 | command `41h` followed by command `35h` |
| `11D99–11DCD` | 53 | command `36h`, byte argument |
| `11DCE–11DFC` | 47 | command `42h` |
| `11DFD–11E2B` | 47 | command `3Eh`, WORD argument |
| `11E2C–11E5A` | 47 | command `4Ah`, WORD argument |
| `11E5B–11E89` | 47 | command `4Bh`, WORD argument |
| `11E8A–11EB8` | 47 | command `4Ch`, WORD argument |
| `11EB9–11EE6` | 46 | command `51h`, WORD argument |

This inventory deliberately distinguishes **known ABI** from **known user-facing
meaning**.  AND wrapper does not remain YELLOW merely because the original vendor'with
symbol name is unavailable; its N3D-visible behavior is reconstructable exactly.

---

# 6. Why this matters for and 1:1 reconstruction

Before this pass, the DOS device/audio tail could be interpreted as dozens of unrelated
opaque external helpers.

It is now reducible to one stable model:

```text
struct WorxRegs {
    AX, BX, CX, DX, SI, DI, carry
}

WorxInt63Command(command, al, bx, dx, di)
    -> INT 63h
    -> cache AX/BX/DX/DI
```

and small typed wrappers around that command set.

AND portable recreation can therefore implement:

```text
N3D game code
   -> WorxCompatibilityAdapter
      -> music backend
      -> SFX backend
      -> PC-speaker compatibility path
      -> joystick backend
```

without embedding the historical WORX implementation itself.

For behavioral parity, however, the adapter must preserve:

- original command ordering;
- argument packing/truncation;
- return values visible to the engine;
- active/stop/replacement decisions;
- music/SFX enable interactions;
- Sound Blaster detection/fallback state;
- joystick query ordering.

---

# 7. What this pass does NOT claim

The following remain separate runtime-conformance questions:

- bit-identical Sound Blaster PCM output;
- PC-speaker waveform/timing parity;
- exact OPL/MIDI synthesis hardware sound;
- original interrupt latency and hardware race behavior;
- exact joystick electrical/timing characteristics;
- every vendor command'with historical public symbol name.

Those to not prevent static reconstruction of the N3D-facing command ABI.

---

# 8. Byte-map impact

New continuous GREEN span:

`0x10BFC .. 0x11EE6`

Total: **4,843 bytes**.

All **75** routines are directly bounded from raw machine code.
There are **zero** alignment/padding bytes between them.

Immediately after `0x11EE6` are **16 zero bytes**.  AND different DOS/CRT/runtime block
begins at approximately `0x11EF7`, with that later code should be classified separately
rather than merged into the WORX command layer.

---

# 9. Cumulative closure

Pass 22 cumulative since the pass-5 baseline:

`45,330 bytes`

Pass 23 adds:

`4,843 bytes`

New cumulative total:

**50,173 bytes**

of formerly RED/ORANGE/YELLOW DOS V2.0 byte-map territory explicitly promoted to
GREEN during passes 6–23.

---

# 10. Next target

The next raw region begins after the 16-byte zero gap at approximately:

`0x11EF7`

It belongs to and different low-level DOS/CRT/runtime family rather than the just-closed
WORX INT 63h API.

The next pass should therefore:

1. classify the `11EF7+` support/runtime routines;
2. mark standard compiler/CRT/DOS services separately from N3D-owned code;
3. avoid counting standard-library internals as unresolved game logic;
4. then jump to the next true N3D-owned or WORX-owned semantic block.