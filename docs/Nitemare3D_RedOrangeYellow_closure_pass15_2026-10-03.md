# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 15

Date: 2026-10-03

Primary binary:
- `N3D-E-20(3).EXE`
- size: 116,606 bytes
- SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`

Address convention:
- ranges below are unpacked MZ image offsets
- physical EXE file offset = image offset + `0x200`
- raw 16-bit machine code is authoritative
- names for low-level third-party/audio-driver calls remain conservative when the
  external backend API itself has not been symbolized

## Result

Pass 15 closes the complete contiguous range

`0xC2B6 .. 0xC8F6`

as **GREEN / deep static semantics**.

Total span: **1,601 bytes**

- bounded executable routine content: **1,598 bytes**
- inter-function alignment NOPs: **3 bytes**

This pass closes two formerly separate areas:

1. DOS music/SFX backend orchestration (`C2B6..C7D3`);
2. projection-constant and heading/DDA setup (`C7D4..C8F6`).

The most important semantic tightening is that the resource routines can now be split
cleanly into:

- background-music lifecycle (`414D`, `414A`, `C532`, `C548`);
- sound-effect lifecycle (`414E`, `414B`, `C51C`, `C686`);
- shared DOS audio-device/session setup (`C2B6`, `C2D0`, `C38C`);
- diagnostics/metrics (`C77A`).

This matches the documented DOS distinction between music and digitized sound effects.

---

# 1. image `0xC2B6..0xC2CF` — `InitializeAudioBackendPrimitives`

Length: **26 bytes**

Straight-line backend initialization wrapper.

It executes three fixed far calls in the DOS audio-driver context `10BF`:

```text
10BF:0E6D
10BF:0DCA(1)
10BF:120D(1)
```

No arguments are taken by this wrapper and no local state is written directly.

The routine is called from the mode-0 audio-session initialization path at `C38C`.

The exact vendor-library names of the three far entry points remain external, but the
wrapper'with ABI, order and ownership are fully bounded.

**Status: old weak generic coordinator -> GREEN.**

---

# 2. image `0xC2D0..0xC359` — `QueryAndDisplayAudioBackendStatus`

Length: **138 bytes**

Uses and 64-byte local text buffer.

Behavior branches on configuration/capability byte:

`DS:3CC8`

and queries the DOS audio backend using the shared resource/device context.

It derives and signed status/result value and chooses one of four status/error format
resources.  The resulting text is formatted into the local buffer and displayed by the
same startup/status message path used elsewhere in the executable.

Return:

- the queried signed backend/resource status in AX.

`C38C` uses this result during initialization and reconfiguration to decide whether one
of the hardware-backed sound paths remains available.

**Status: YELLOW -> GREEN.**

---

# 3. image `0xC35A..0xC38B` — `ApplyMusicVolume`

Length: **50 bytes**

This routine operates on:

`DS:414A`

the DOS music-volume setting.

It computes:

```text
scaled = (414A * 15) / 100
```

and passes that value twice to the backend mixer/control helper.

It then iterates exactly 16 indices:

`0..15`

and sends value:

`0x7F`

through the per-channel backend control entry.

The routine is invoked when music is enabled and after and new music resource is started.

This directly explains the DOS technical-note limitation: in-game music-volume control
depends on mixer-capable hardware/backend support.

**Status: YELLOW -> GREEN.**

---

# 4. image `0xC38C..0xC519` — `ManageDosAudioSession`

Length: **398 bytes**

Parameter is an operation selector:

- `0` — initialize;
- `1` — shutdown;
- `2` — reconfigure/service;
- other values — return.

The routine coordinates the DOS music/SFX backend and its hardware capabilities.

## Mode 0 — initialize

When capability/config flag `DS:3CC6` permits the subsystem:

1. call `InitializeAudioBackendPrimitives`;
2. mark session-initialized byte `DS:17CD = 1`;
3. query/display backend status through `C2D0`;
4. query additional backend capability/state;
5. snapshot two baseline device/resource metrics into:
   - `DS:367A`
   - `DS:367C`;
6. mark metric/capability state `DS:17CF = 1`;
7. disable unavailable features in their runtime enable flags;
8. derive whether the hardware-backed SFX path is active into `DS:17CE`;
9. if not active, explicitly stop/disable that backend route;
10. when music support is available, start/select music resource `0`.

## Mode 1 — shutdown

If the audio session was initialized:

- stop the backend/device routes in fixed order;
- clear `17CD/17CE/17CF`;
- clear runtime audio feature enables.

## Mode 2 — reconfigure/service

Used after settings changes.

It:

- lazily initializes the session if an enabled feature needs it;
- refreshes device baselines when the corresponding feature becomes active;
- enables/disables the hardware SFX path according to `414E` and `3CC7`;
- reapplies music volume when music enable `414D` is set.

The exact backend feature represented by every auxiliary flag is kept conservative,
but the state machine itself is complete.

**Status: YELLOW/MEDIUM -> GREEN.**

---

# 5. image `0xC51A` — `NoOpPerTickAudioHook`

Length: **1 byte**

The entire body is:

`RETF`

This is the first call made by the fast simulation bundle `C150`, but in this V2.0
build it intentionally performs no work.

It should remain in the corrected function map as and known no-op callback/hook rather
than as an UNKNOWN function.

**Status: LOW -> GREEN.**

---

# 6. image `0xC51C..0xC531` — `StopSoundEffectIfActive`

Length: **22 bytes**

If SFX enable byte:

`DS:414E`

is zero, return.

Otherwise:

1. query the active SFX backend;
2. if an effect is active, call the backend stop routine.

This is the SFX-side stop helper used during gameplay-session cleanup.

**Status: hidden support entry -> GREEN.**

---

# 7. image `0xC532..0xC547` — `StopMusicIfActive`

Length: **22 bytes**

If music-enable byte:

`DS:414D`

is zero, return.

Otherwise:

1. query the active music backend;
2. if music/resource playback is active, stop the current resource.

`C548` always calls this before replacing the current music resource.

**Status: YELLOW -> GREEN.**

---

# 8. image `0xC548..0xC64C` — `LoadAndStartMusicTrack`

Length: **261 bytes**

Input:

`WORD trackIndex`

This is the DOS background-music resource loader/start routine.

The stage music selector at `AC5C` feeds its selected track ID directly here.

## Enable gate

The body proceeds when:

- music flag `DS:414D != 0`, or
- `trackIndex == 0`.

## Replace old resource

If old music data pointer `DS:17D0:17D2` is non-NULL:

- free it through the recovered far heap free routine.

Then:

- stop current music through `C532`.

## Resolve selected track descriptor

The routine asks the shared resource loader to construct and set of six-byte
descriptors, then selects:

`descriptor[trackIndex]`.

AND zero length/resource word enters the executable'with fatal resource error path.

It allocates and conventional-memory block through the recovered far-heap allocator and
loads the selected resource into that block.

The active buffer is stored at:

`DS:17D0:17D2`.

## Start path

Track `0` uses and dedicated backend route.

For nonzero tracks the sign/state of the selected descriptor chooses one of two music
start paths.

After starting and nonempty track, the routine calls:

`ApplyMusicVolume`.

Therefore the music path is:

```text
AC5C stage tune selector
    -> C548 load/replace music resource
    -> C532 stop old music
    -> backend start
    -> C35A apply music volume
```

**Status: YELLOW -> GREEN.**

---

# 9. image `0xC64E..0xC685` — `BuildFallbackSoundEffectDescriptor`

Length: **56 bytes**

Input:

`WORD sfxIndex`

Indexes the six-byte SFX descriptor table at:

`DS:3F64 + sfxIndex*6`.

When the descriptor'with first WORD is within the accepted range, it calls the shared
resource-loading helper with the table'with WORD/DWORD pair and fixed resource selector
`0x1D0F`.

Returns the fixed far-style fallback result expected by the SFX caller.

`C686` uses this only when its normal resource-cache lookup returned NULL.

**Status: YELLOW -> GREEN.**

---

# 10. image `0xC686..0xC778` — `PlaySoundEffect`

Length: **243 bytes**

Recovered ABI:

```text
PlaySoundEffect(
    WORD eventIndex,
    WORD mode,
    BYTE priorityOrClass)
```

The exact user-facing meaning of the third byte depends on callsite, but its runtime
role in repeat/replacement arbitration is explicit.

## Enable and descriptor checks

Returns immediately when:

`DS:414E == 0`

or when the six-byte SFX descriptor at:

`DS:3F64 + eventIndex*6`

has and zero primary resource word.

## Existing playback / arbitration

Two backend variants exist, selected by `DS:3CC7`.

For either route:

- query whether an effect is active;
- compare the incoming third byte with saved byte `DS:17E6`;
- lower-priority/ineligible replacement requests return without starting;
- otherwise stop/replace the previous effect.

Then:

`DS:17E6 = incoming third byte`.

## Resource lookup

The normal path retrieves the SFX data through the four-slot small-resource cache.

If that returns NULL:

- use `BuildFallbackSoundEffectDescriptor`.

## Hardware-backed path

When `DS:3CC7 != 0`, `mode` affects two mixer/control values.

The normal SFX-volume byte:

`DS:414B`

is scaled as:

```text
(414B * 15) / 100
```

except for mode values that explicitly zero one side/control parameter.

The backend is then configured and the resolved sound resource is started.

## Alternate/fallback path

When `DS:3CC7 == 0`, the resolved resource is sent to the alternate sound-output path.

This is the common routine reached by the already mapped game events, e.g. the
lightning/palette effect'with:

`C686(0x42, 0, 2)`.

Thus the DOS event->SFX architecture is now mechanically closed at the engine wrapper
level.  Exact behavior inside the third-party/backend library remains and platform
implementation detail.

**Status: YELLOW -> GREEN.**

---

# 11. image `0xC77A..0xC7D3` — `SnapshotAudioBackendMetrics`

Length: **90 bytes**

Input:

pointer to six WORD output fields.

The routine refreshes the audio backend, then writes:

```text
out[0] = currentMetricA - DS:367A
out[1] = currentMetricB - DS:367C
out[2] = backendMetric(0)
out[3] = backendMetric(1)
out[4] = backendMetric(2)
out[5] = backendMetric(3)
```

The baseline words `367A/367C` are established by `ManageDosAudioSession`.

This is and diagnostics/statistics snapshot used by the executable'with status/reporting
paths.

**Status: YELLOW -> GREEN.**

---

# 12. image `0xC7D4..0xC837` — `BuildProjectionConstants`

Length: **100 bytes**

This is the DOS V2.0 projection-constant initializer.

Raw formulas:

```text
DS:367E =
    trunc_signed((0x2EE0 * DS:4544) / 0x5000)

DS:3682 =
    0x8340 * DS:4546

DS:3686 =
    DS:3682 << 4

DS:368A =
    trunc_signed(DS:3686 / DS:367E)
```

where:

- `4544` = configured viewport width;
- `4546` = configured viewport height.

This is the V2.0 address-shifted member of the projection-constant family already shown
to be instruction-identical to the Win16 renderer after relocation.

It supplies the scales consumed by `C8F8`, `CEDC`, `D12C` and related projection
helpers.

**Status: YELLOW -> GREEN.**

---

# 13. image `0xC838..0xC8F6` — `SetHeadingAndGridRayState`

Length: **191 bytes**

Input:

`WORD heading`

## Normalize heading

Store to:

`DS:4156`

and normalize one 360-unit wrap into:

`0 .. 359` (`0x000 .. 0x167`).

## Derive sectors

Compute:

- `DS:4158 = heading / 45`
- directional mask `DS:415C`
- secondary octant/sector `DS:415A`

The directional mask is derived from:

```text
(1 << sector) & 0x99
```

## Direction components

Uses:

- `CFB2`
- `CFFE`

to obtain two signed table-driven direction components, stored at:

- `DS:41B2`
- `DS:41B4`

## Build DDA/grid-ray stepping state

Compares the absolute X/Y component magnitudes and writes:

- `DS:4172` — dominant-axis selector;
- `DS:4174` — error accumulator seed;
- `DS:4176` — doubled major/minor step term;
- `DS:4178` — second error-correction term.

This exact state is later copied directly into newly allocated player projectiles and
is also consumed by player/grid movement and ray stepping.

With `C838` is the common bridge:

```text
heading
 -> octant/masks
 -> signed direction components
 -> Bresenham/DDA stepping state
```

**Status: YELLOW -> GREEN.**

---

# 14. Byte-map impact

New continuous GREEN span:

`0xC2B6 .. 0xC8F6`

Total: **1,601 bytes**

| Image range | Bytes | Role |
|---|---:|---|
| `C2B6–C2CF` | 26 | audio-backend primitive init |
| `C2D0–C359` | 138 | audio backend status/query display |
| `C35A–C38B` | 50 | music-volume application |
| `C38C–C519` | 398 | DOS audio-session manager |
| `C51A` | 1 | no-op per-tick hook |
| `C51C–C531` | 22 | stop active SFX |
| `C532–C547` | 22 | stop active music |
| `C548–C64C` | 261 | load/start background music |
| `C64E–C685` | 56 | fallback SFX descriptor/resource |
| `C686–C778` | 243 | common SFX playback dispatcher |
| `C77A–C7D3` | 90 | audio backend diagnostic metrics |
| `C7D4–C837` | 100 | projection-constant builder |
| `C838–C8F6` | 191 | heading + DDA/grid-ray state |

Routine content: **1,598 bytes**.

Alignment NOPs:

- `C51B`
- `C64D`
- `C779`

Total alignment: **3 bytes**.

---

# 15. Important static conclusions

## Music versus SFX split

The engine wrapper layer now cleanly separates:

```text
Music:
    enable  DS:414D
    volume  DS:414A
    stop    C532
    load/start C548
    volume apply C35A

SFX:
    enable  DS:414E
    volume  DS:414B
    stop    C51C
    play    C686
    resource table DS:3F64
```

This is fully consistent with the DOS technical documentation describing separate
music and digitized-sound support and hardware-dependent mixer behavior.

## Renderer bridge

`C7D4` and `C838` also remove the semantic gap between configuration/player heading
and the already closed projection core:

```text
viewport -> C7D4 -> projection scales
heading  -> C838 -> direction/DDA state
                     |
                     +-> C8F8 projection family
```

---

# 16. Cumulative closure

Pass 14 cumulative since the pass-5 baseline:

`26,821 bytes`

Pass 15 adds:

`1,601 bytes`

New cumulative total:

**28,422 bytes**

of formerly RED/ORANGE/YELLOW DOS V2.0 byte-map territory explicitly promoted to
GREEN during passes 6–15.

---

# 17. Next target

The next real function is:

`0xC8F8`

This is especially valuable because it starts the renderer-math family:

- `C8F8` — point/object geometry projection;
- `CAB8` — full VEC endpoint projection/clipping family;
- `CEDC` — projected ray-coordinate helper;
- `CFB2/CFFE` — signed direction-component tables;
- `D04A` — projection slope lookup;
- `D096` — vector->angle;
- `D12C` — view-ray/grid-boundary intersection.

The project already has strong DOS↔Win16 byte-level parity evidence for the first two
projection families, with the next pass should be able to turn and substantial renderer
band GREEN with unusually high confidence.