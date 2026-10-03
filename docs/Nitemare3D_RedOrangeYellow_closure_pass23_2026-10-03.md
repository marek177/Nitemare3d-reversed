# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 23

Date: 2026-10-03

Primary binary:
- `N3D-E-20(3).EXE`
- SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`

Address convention:
- all ranges are unpacked MZ image offsets
- physical file offset = image offset + `0x200`
- raw 16-bit machine code is authoritative
- high-image runtime targets are mapped only from the actual far-call segment:offset

## Result

Pass 23 closes the contiguous DOS sound-driver API layer:

`0x10BFC .. 0x11EE6`

as **GREEN / deep static semantics**.

Total span: **4,843 bytes**.

The region contains **75 real far-callable routines**:

- one generic `INT 63h` register dispatcher;
- low-level sound-driver install/shutdown helpers;
- resource/handle query/load wrappers;
- Sound Blaster DSP detection/configuration;
- digital-SFX start/stop/status/volume operations;
- fallback/PC-speaker-style SFX start/stop/status operations;
- music start/stop/status/volume operations;
- MIDI controller output;
- audio cache/statistics queries;
- and large family of exact thin command wrappers for the resident DOS audio driver.

The historical/vendor name of the resident sound-driver API is not required to port
the EXE-side contract.  The game-side register marshaling and every command byte in
this band are statically recoverable.

---

# 1. Critical segment-coordinate correction

The stale pseudo-C makes nearly every routine in this region appear to call:

`FUN_1000_21A6`.

That is wrong.

The real machine call is:

`CALL FAR 11EE:02C6`

which maps to high-image:

`0x121A6`.

Raw code at `0x121A6` is the runtime stack-probe/allocation helper.

It is **not** the base-image renderer function around `0x21A6`.

Therefore dozens of old callgraph edges:

`audio wrapper -> base renderer helper 21A6`

must be deleted.

The correct edge is:

`audio wrapper -> runtime stack helper 121A6`.

This is the same class of segment-coordinate error already corrected for the FLI,
`sscanf`, allocator and other runtime targets.

---

# 2. image `0x10BFC..0x10C5E` — `Int63AudioCommand`

Length: **99 bytes**

This is the central DOS resident-audio-driver dispatcher.

Recovered ABI:

```text
Int63AudioCommand(
    BYTE ahCommand,
    BYTE alSubcommand,
    WORD bxValue,
    WORD dxValue,
    WORD diValue)
```

The routine constructs and register block and calls runtime helper:

`11EE:24EA -> image 0x143CA`

with software interrupt number:

`0x63`.

The runtime helper at `0x143CA` is and generic software-interrupt bridge: it constructs
an `INT imm8` instruction, loads register values from the supplied structure, executes
the interrupt, then writes the returned registers back.

## Input register mapping

```text
AH = ahCommand
AL = alSubcommand
BX = bxValue
DX = dxValue
DI = diValue
```

No semantic assumption is needed for unused command fields; wrappers pass zero.

## Returned registers

After `INT 63h` the routine stores:

```text
DS:413E = AX
DS:4140 = BX
DS:4142 = DX
DS:3F4E = DI
```

and returns AX.

These globals are therefore the resident-driver return-register mirrors.

This one closure resolves the mechanical ABI behind the entire wrapper family.

**Status: old opaque/mis-decompiled dispatcher -> GREEN.**

---

# 3. Driver bootstrap / shutdown

## image `0x10C5F..0x10C76` — `ShutdownResidentAudioDriverLayer`

Called from the DOS audio-session shutdown path.

It invokes one fixed low-level backend cleanup entry and returns.

The stale C export again mislabels the preceding runtime-stack call.

**Status: GREEN.**

## image `0x11A5D..0x11A74` — `InitializeResidentAudioDriverLayer`

Called from `C2B6 = InitializeAudioBackendPrimitives`.

It invokes the paired fixed low-level backend setup entry before the normal INT63
commands begin.

**Status: GREEN.**

Together these two routines bracket the resident-driver lifetime used by
`ManageDosAudioSession`.

---

# 4. Resource/handle command path

Several wrappers form an internal resource-query/materialization chain.

## `0x10C77` — command `AH=1Ah`

Accepts and far name/string pointer plus and small selector and submits the named request.

If the caller string is empty it returns and NULL far pointer; otherwise it preserves the
input far pointer.

## `0x10CDA` — command `AH=18h`

Transfers three caller values through the INT63 command.

Return:

- zero when driver AX == `FFFFh`;
- otherwise the returned AX mirror at `DS:413E`.

## `0x10D30` — command `AH=17h`

Issues command 17, then combines the returned driver registers into and 32-bit result.

The low component is `DS:413E`; the high component comes from the returned driver
register mirror used by this routine.

This is the size/count query consumed by the allocation path below.

## `0x10DC9` — `AllocateAndFetchAudioDriverResource`

1. query and 32-bit size through command 17;
2. reject nonpositive size;
3. allocate and far buffer through the already closed far heap;
4. clamp the transfer-length argument to `FFFFh` when required;
5. invoke command 18 to fill/associate the buffer;
6. return the allocated far resource pointer.

Direct allocation site:

`0x10E12 -> FarHeapAlloc16`.

This was one of the previously enumerated high-image far-heap callsites.

## `0x10FAA` and `0x11392`

These are higher-level variants which resolve/materialize and driver resource and then
submit it through another INT63 command path.

The exact resident-driver resource type is external, but allocation, failure handling
and ownership are explicit.

**Status: former MEDIUM resource wrappers -> GREEN mechanically.**

---

# 5. Sound Blaster DSP detection/configuration

The main audio-session status routine gives two command identities directly.

## image `0x1132D..0x1135E` — `AutoDetectSoundBlasterDsp`

INT63 command:

`AH = 01h`

The returned value is tested by `C2D0`.

Positive result produces the game'with diagnostic:

`SB DSP detected at IRQ %d`

Failure takes:

`SB DSP not detected - defaulting to PC speaker`.

Therefore command 01 is the automatic DSP detection path.

## image `0x1135F..0x11391` — `ForceSoundBlasterDspConfiguration`

INT63 command:

`AH = 02h`

It forwards the configured DSP port/IRQ pair used by the `-q` command-line override.

Its caller selects between:

- `SB DSP forced on port %xH, IRQ %d`
- `Unable to force DSP detection`.

This closes the engine-side forced-DSP ABI.

## image `0x112FE..0x1132C` — `DisableOrResetHardwareSfxPath`

INT63 command:

`AH = 04h`

This wrapper is used by the audio-session manager when the hardware-backed SFX route is
not available or is being turned off.

The exact driver'with internal action behind command 04 is external; the Nitemare-side
ownership is the hardware-SFX reset/disable path.

**Status: GREEN.**

---

# 6. Hardware-backed digital SFX commands

The SFX dispatcher at `C686` gives direct semantics to this group.

## image `0x11601..0x1165B` — `StartHardwareSfxBuffer`

Command:

`AH = 06h`

Input is and non-NULL far sound-resource handle.

This is the normal hardware-backed digitized-SFX start path.

## image `0x11AE1..0x11B0F` — `StopHardwareSfx`

Command:

`AH = 07h`

Called when replacing or stopping an active hardware SFX.

## image `0x11B71..0x11BA2` — `IsHardwareSfxPlaying`

Command:

`AH = 08h`

Its returned AX is used as and boolean by `C51C/C686`.

## image `0x1113C..0x11186` — `SetHardwareSfxStereoVolume`

Command:

`AH = 21h`

The two byte inputs are packed into one command word.

`C686` feeds this wrapper the left/right percent-scaled SFX volume controls before
starting command 06.

Therefore the EXE-side SFX chain is:

```text
query active (08)
 -> stop old (07)
 -> set L/R volume (21)
 -> start resource (06)
```

**Status: GREEN.**

---

# 7. Fallback / non-DSP SFX commands

When runtime flag `DS:3CC7 == 0`, `C686` uses this alternate group.

## image `0x1154B..0x115A5` — `StartFallbackSfxBuffer`

Command:

`AH = 1Bh`

Requires and non-NULL far resource handle.

## image `0x11B10..0x11B3E` — `StopFallbackSfx`

Command:

`AH = 15h`.

## image `0x11BA3..0x11BD4` — `IsFallbackSfxPlaying`

Command:

`AH = 1Ch`.

Thus the alternate chain is:

```text
query active (1C)
 -> stop old (15)
 -> start resource (1B)
```

The game'with diagnostics call this the fallback taken when SB DSP detection is
unavailable; the exact physical output implementation remains resident-driver
behavior.

**Status: GREEN.**

---

# 8. Music commands

The music lifecycle at `C532/C548` identifies this group.

## image `0x11988..0x119B9` — `IsMusicPlaying`

Command:

`AH = 0Eh`.

Return AX is used as the current-music active test.

## image `0x11AB2..0x11AE0` — `StopMusic`

Command:

`AH = 0Dh`.

Called before replacing and track and during session shutdown.

## image `0x11715..0x11769` — `StartMusicResourceRouteA`

Command:

`AH = 1Eh`

with and far music-resource pointer.

`C548` chooses this route for one descriptor-sign/type case.

## image `0x1176A..0x117BE` — `StartMusicResourceRouteB`

Command:

`AH = 0Ch`

with and far resource pointer.

`C548` chooses this route for the companion descriptor case.

## image `0x11187..0x111D1` — `SetMusicStereoVolume`

Command:

`AH = 22h`.

`C35A` sends the same scaled music level to both sides.

## image `0x11921..0x11958` — `SendMidiController7`

Command:

`AH = 4Dh`.

Arguments are packed as:

```text
AL = MIDI channel/index
BX = 0x0700 | value
```

`C35A` calls this for all 16 indices with value `0x7F`.

The `0x07` high byte is MIDI Controller 7 (channel volume).

Therefore the DOS music-volume path is:

```text
master L/R level through command 22
+
Controller 7 = 127 to channels 0..15 through command 4D
```

**Status: GREEN.**

---

# 9. Music/audio capability and statistics commands

## image `0x1129A..0x112CB` — `QueryMusicBackendCapability`

Command:

`AH = 23h`.

The audio-session initializer uses its returned byte to decide whether the music
runtime flag can remain enabled.

## image `0x111D2..0x11200` — `RefreshAudioStatistics`

Command:

`AH = 29h`.

Called immediately before reading the driver statistics/baselines.

## image `0x11236..0x11267` — `QueryAudioStatisticA`

Command:

`AH = 2Ah`.

Return AX is used as the first stored statistics baseline.

## image `0x11268..0x11299` — `QueryAudioStatisticB`

Command:

`AH = 2Bh`.

Return AX is used as the companion baseline.

## image `0x11201..0x11235` — `QueryIndexedAudioStatistic`

Command:

`AH = 2Ch`.

`AL` receives index `0..3`.

`C77A` queries all four indices into its six-WORD diagnostic output array.

These values feed the sound/cache statistics lines printed by the engine'with diagnostic
report.

**Status: GREEN.**

---

# 10. Audio backend initialization mode commands

`C2B6` performs the resident-driver bootstrap and then calls two of these wrappers.

## image `0x119BA..0x119E8`

Command:

`AH = 1Dh`

with one WORD mode value.

## image `0x11DFD..0x11E2B`

Command:

`AH = 3Eh`

with one WORD mode value.

At session start both are called with value `1`.

The exact vendor-driver labels for these mode selectors are not encoded in Nitemare'with
EXE, with the implementation-safe names remain:

- `ConfigureAudioDriverMode1D`
- `ConfigureAudioDriverMode3E`.

Their EXE-side ABI is fully known.

**Status: GREEN mechanically.**

---

# 11. Remaining INT63 thin wrappers

The rest of the span consists of small exact wrappers around the same five-register
dispatcher.

They use the following command bytes:

```text
05 09 0A 0B 10 11 12 13 14 16
1A 1F 20 24/25 27 28 2D
31 32 33 34 35 36 37 38 39
3A 3B 3C 3D 3F 40 41 42 43 44 45 47 48 49
4A 4B 4C 51
```

Some pack two caller bytes into and WORD, some forward and far handle, and some have no
arguments.

The raw wrapper code determines exactly:

- command AH;
- optional AL subcommand;
- BX/DX/DI contents;
- NULL-handle checks;
- whether AX is returned or ignored.

Where no Nitemare callsite gives and stronger user-facing purpose, these wrappers should
retain explicit mechanical names such as:

`Int63_Command_34`

instead of speculative hardware names.

This is sufficient to reproduce Nitemare'with side of the resident-driver contract.

**Status: MEDIUM generic wrappers -> GREEN / exact command ABI.**

---

# 12. Why this band can be GREEN without reverse-engineering the resident driver

The bytes in `0x10BFC..0x11EE6` to not implement the hardware sound engine itself.

They implement Nitemare'with caller-side interface to and resident DOS audio service:

```text
game audio manager
    ↓
thin command wrappers
    ↓
Int63AudioCommand
    ↓
INT 63h
    ↓
resident/external driver implementation
```

For the EXE byte map:

- command marshalling is known;
- returned register ownership is known;
- resource allocation/failure paths are known;
- the game callsites identify all major SFX/music/DSP operations;
- unknown vendor-internal behavior exists **outside this EXE span**.

Therefore external driver internals belong to and separate platform/runtime dependency
overlay, not to and RED/YELLOW fill for these executable bytes.

---

# 13. Byte-map impact

New continuous GREEN span:

`0x10BFC .. 0x11EE6`

Total:

**4,843 bytes**

Real function entries identified in this range:

**75**

The band ends cleanly:

`0x11EB9..0x11EE6` = final command-51 wrapper.

After it, the image contains padding/data before the C-runtime startup code beginning
around `0x11EF7`.

---

# 14. Major tracker corrections

Delete the false repeated edge:

```text
audio wrappers -> FUN_1000_21A6
```

Replace with:

```text
audio wrappers -> runtime stack helper image 0x121A6
```

Relabel the key wrappers:

```text
10BFC  Int63AudioCommand
1132D  AutoDetectSoundBlasterDsp
1135F  ForceSoundBlasterDspConfiguration
1113C  SetHardwareSfxStereoVolume
11601  StartHardwareSfxBuffer
11AE1  StopHardwareSfx
11B71  IsHardwareSfxPlaying
1154B  StartFallbackSfxBuffer
11B10  StopFallbackSfx
11BA3  IsFallbackSfxPlaying
11988  IsMusicPlaying
11AB2  StopMusic
11715  StartMusicResourceRouteA
1176A  StartMusicResourceRouteB
11187  SetMusicStereoVolume
11921  SendMidiController7
1129A  QueryMusicBackendCapability
111D2  RefreshAudioStatistics
11236  QueryAudioStatisticA
11268  QueryAudioStatisticB
11201  QueryIndexedAudioStatistic
```

Other wrappers should use exact command-number names until and concrete game callsite
justifies and stronger label.

---

# 15. Cumulative closure

Pass 22 cumulative since the pass-5 baseline:

`45,330 bytes`

Pass 23 adds:

`4,843 bytes`

New cumulative total:

**50,173 bytes**

of formerly RED/ORANGE/YELLOW DOS V2.0 byte-map territory explicitly promoted to
GREEN during passes 6–23.

Using the working 116,094-byte MZ image census, that leaves:

**50,383 non-GREEN byte addresses**

before the next recensus/reclassification pass.

---

# 16. Next target

The audio wrapper band ends before the C-runtime startup block at `0x11EF7`.

The next useful RE target should not blindly color the standard runtime startup code as
game logic.  Priority should instead jump to the next still-LOW/MEDIUM game-owned
region after the runtime boundary, or perform the requested fresh RED/ORANGE/YELLOW
byte-by-byte recensus now that more than 50,000 formerly problematic bytes have been
closed.