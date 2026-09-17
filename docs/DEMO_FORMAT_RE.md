# DEMO.1-3 format / attract-mode reverse engineering

Date: 2026-09-17

## Data comparison

Three supplied original demo streams were compared byte-for-byte.

| file | size | SHA-256 | header | 8-byte records | final timestamp |
|---|---:|---|---|---:|---:|
| DEMO.1 | 1630 | `50d9d333d4647831ba0786b97127a695f24ca86136c3626ad946fdf2c82ae2f7` | `0A 00 05 00 14 00` | 203 | 1157 |
| DEMO.2 | 2174 | `04e9dacd18341775c72661ee57fce1cca130edb3b1616cef87c50974997f0781` | `0A 00 05 00 14 00` | 271 | 2284 |
| DEMO.3 | 2294 | `ad6752da2c7da06fab62706cf0929dd10035dd990d313321e6c8c401c5b90864` | `0A 00 05 00 14 00` | 286 | 2565 |

All three have exactly the same 6-byte header: three little-endian words `(10, 5, 20)`. After the header, every remaining byte divides exactly into 8-byte records. **VERIFIED_DATA**.

The second dword of every 8-byte record is monotonically non-decreasing and is used by the executable as a playback timestamp. **VERIFIED_DATA / VERIFIED_EXE**.

## MAP container correlation

The supplied MAP files have a common 514-byte container/header region followed by 8192-byte level payloads:

- `MAP.1`: 90,626 bytes = 514 + 11 x 8192 -> 11 levels.
- `MAP.2`: 82,434 bytes = 514 + 10 x 8192 -> 10 levels.
- `MAP.3`: 82,434 bytes = 514 + 10 x 8192 -> 10 levels.

A direct E1M3 versus E1M11 payload comparison produced a very important result: **all 4096 bytes at even positions are identical**. Only 17 odd-position bytes differ. In the established 2-byte-per-cell map representation this means that the complete first byte/plane of every map cell is identical between E1M3 and E1M11, while only 17 second-byte/object-state entries differ. **VERIFIED_DATA**.

Therefore the statement that E1M3 and E1M11 are the same map is substantially correct at the structural/geometry level: E1M11 is an E1M3-derived duplicate with a very small set of object/entity differences rather than an independently designed level.

This is highly relevant to DEMO.1. The cleanest current model is that DEMO.1 was recorded against the E1M3 geometry (or its E1M11 demo duplicate), and E1M11 exists specifically as a stable demo copy with altered object population/state. **INFERRED**, supported by exact geometry-plane equality and behavioral playback compatibility.

## Episode-2 / Episode-3 demo hypothesis

Behavioral substitution tests show:

- DEMO.1 renamed/used as the normal demo stream fits E1M11.
- DEMO.2 forced into the DEMO.1 slot does not fit E1M11: recorded commands collide with the wrong geometry and produce aimless turning/shooting.
- DEMO.3 forced into the DEMO.1 slot behaves likewise and does not fit E1M11.
- The HUD/map remains E1M11 during these substitutions, proving that changing the stream does not itself select a map. **BEHAVIORAL**.

Because the EXE constructs `MAP.N`, `IMG.N`, and `DEMO.N` from the same resource-set number, a strong candidate is:

- `DEMO.1` -> Episode 1 demo geometry, apparently E1M3/E1M11.
- `DEMO.2` -> a map in `MAP.2`, with **E2M3 a high-value candidate**.
- `DEMO.3` -> a map in `MAP.3`, with **E3M3 a high-value candidate**.

The specific E2M3/E3M3 assignments are currently **INFERRED/TODO**, not yet VERIFIED_DATA. MAP.2 and MAP.3 contain only ten final level payloads, so there is no physical E2M11/E3M11 payload in the supplied final containers. If development once used hidden/test E2M11/E3M11 copies analogous to E1M11, those payloads are absent from these final MAP files and cannot be asserted without another build or residual evidence.

A particularly plausible development history to test is: each episode's demo was recorded on its M3 map; Episode 1 later received a duplicated M3 geometry as hidden E1M11 for attract playback, while DEMO.2/3 remained unused residual recordings. This model explains both the E1M3/E1M11 geometry identity and why DEMO.2/3 do not fit the final attract map. It remains **INFERRED** until trajectory/map matching or EXE caller evidence confirms it.

## EXE filename construction

The episode/resource setup routine stores its numeric argument in global `0x7E52`, then constructs three names with `%s%d`:

- `map.` + N -> `map.N`
- `img.` + N -> `img.N`
- `demo.` + N -> `demo.N`

The generated demo filename buffer is at `0x7E84`. **VERIFIED_EXE**.

This means DEMO.1/2/3 are structurally associated with the same numeric resource/episode selector used for MAP.N and IMG.N. The menu attract-mode behavior observed by testing nevertheless enters E1M11 and, when the files are removed, specifically fails opening `demo.1`; therefore the normal menu demo path appears to force/select resource set 1. Exact caller is still to be fully named. **BEHAVIORAL + PARTIAL EXE**.

## Demo playback/record state machine

A state machine is driven by word global `0x46B8` around `seg3:90CE..9266`.

### Playback setup

State 3 (`0x46B8 == 3`) opens the filename in `0x7E84` for reading. Failure reaches the existing fatal-error path using `Error opening file %s`.

It then reads:

1. 2 bytes -> global `0x53F6`
2. 2 bytes -> global `0x53F8`
3. 2 bytes -> global `0x53FA`
4. 8 bytes -> current demo record buffer at `0x375E`

and changes state to 4. **VERIFIED_EXE**.

### Playback record layout

The 8-byte current record at `0x375E` is consumed as follows:

- `+0`: byte copied to runtime input/control byte `0x0108`
- `+1`: word copied to runtime value `0x3756`
- `+3`: byte is zero in all 760 supplied records; exact semantic/padding status remains PARTIAL
- `+4`: dword timestamp copied/compared through `0x3762`

The executable compares the current tick/time dword `0x53DC` against record timestamp `0x3762`. Once the record is due it applies the recorded control fields and reads the next 8-byte record. **VERIFIED_EXE**.

A conservative packed representation is therefore:

```cpp
struct DemoRecord {
    uint8_t  control;
    uint16_t value;
    uint8_t  reserved_or_padding; // zero in supplied DEMO.1-3
    uint32_t timestamp;
};
static_assert(sizeof(DemoRecord) == 8);
```

The semantic names of `control` and `value` remain PARTIAL until the runtime input handler is fully cross-referenced. Do not yet rename `value` to angle/direction without proof.

### Recording path

State 1 opens/creates the same `demo.N` filename for recording and writes the three 16-bit header globals. State 2 records 8-byte input/timestamp records. Thus the executable contains both a demo recorder and player. **VERIFIED_EXE**.

## Command-line switch

The command-line parser accepts single-letter `-x` switches from `b` through `w`. The `-r` case executes:

```asm
mov word ptr [0x46B8], 1
```

State 1 is the demo-record setup state described above. Therefore:

**`NITE3W.EXE -r` enables demo recording. VERIFIED_EXE.**

No command-line case in this parser directly sets `0x46B8 = 3`, so no direct `-playdemo`/demo-playback command-line switch has yet been found. Playback state 3 is entered elsewhere, consistent with the observed menu attract/demo launcher. **VERIFIED_EXE for parser; TODO for exact menu caller**.

Important: `-r` is a recorder switch, not a proven command to play an existing demo.

## Behavioral observations

- Menu demo plays E1M11; HUD visibly reports Level 1:11. **BEHAVIORAL**.
- E1M11 is not reached through normal Episode 1 progression. **BEHAVIORAL**.
- A key press aborts demo playback and returns from attract mode. **BEHAVIORAL**.
- Selected menu episode does not change the observed attract demo; freeware/shareware testing behaves the same. **BEHAVIORAL**.
- MIDI music can change between repeated demo launches. MIDI selection is therefore not yet assumed to be stored in DEMO.1. **BEHAVIORAL**.
- Removing the demo files causes `Error opening file demo.1`. **BEHAVIORAL**, consistent with the recovered filename/open path.

## Next tests / trajectory matching

The highest-value next pass is no longer merely file substitution. Decode `control`/`value` into exact player commands and replay each stream against candidate map collision geometry.

For each candidate level score:

1. whether the demo start position/direction is valid;
2. number of movement commands that collide with walls;
3. use/open commands that coincide with doors or interactive cells;
4. firing events whose rays have plausible targets/guards;
5. duration before trajectory diverges or becomes trapped;
6. endpoint and any level/event interaction.

Run DEMO.1 against all E1 maps as a calibration set: E1M3 and E1M11 should score near the top because their geometry plane is byte-identical. Then run DEMO.2 against all ten MAP.2 levels and DEMO.3 against all ten MAP.3 levels. A clear minimum-collision candidate would provide strong evidence for the original recording map.

Also trace the menu caller that sets `0x46B8 = 3`, end-of-file handling, keyboard abort, and MIDI selection independently.
