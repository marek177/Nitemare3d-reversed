# Nitemare 3D — DEMO record and playback (2026-09-23)

## Range and podklady

Priamy analysis raw NE code `nite3w(10).exe` (Win16 1.10), segment 3 and 10, and check troch provided file `DEMO.1–3`. DOS v2.0 EXE slúži as sekundárny check source name mode.

| Input | Size | SHA-256 |
|---|---:|---|
| `nite3w(10).exe` | 230 400 B | `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481` |
| `DEMO.1` | 1 630 B | `50d9d333d4647831ba0786b97127a695f24ca86136c3626ad946fdf2c82ae2f7` |
| `DEMO.2` | 2 174 B | `04e9dacd18341775c72661ee57fce1cca130edb3b1616cef87c50974997f0781` |
| `DEMO.3` | 2 294 B | `ad6752da2c7da06fab62706cf0929dd10035dd990d313321e6c8c401c5b90864` |

Segment 3 starts v file on `0x15FC0`; segment 10 starts on `0x2C040`. Addresses below are segment:offset before aplikovaním NE fixupov. During call to iných segment therefore uvádzam only offset call wrapperov, nie neoverené selektory.

## Newly confirmed findings

### 1. Game zostavuje names MAP, IMG also DEMO according to numbers episodes

V `seg3:4989` sa argument episodes stores to global `0x7E52`. Routine subsequently uses same numeric value, format string `%s%d` and three prefixy:

| Prefix v segment 10 | Output buffer | Rodina file |
|---:|---:|---|
| `0x0EB8` (`map.`) | `0x7E64` | MAP |
| `0x0EC4` (`img.`) | `0x7E74` | IMG |
| `0x0ECA` (`demo.`) | `0x7E84` | DEMO |

call argumenty v this order correspond zostaveniu `prefix + episode number`; result are names as `map.1`, `img.1` and `demo.1`. Routine then opens MAP cestu and loads 514-byte header. DEMO path sa uses v separate DEMO stavovom automate.

This uzatvára question, whether is `demo.` only osamotený text v EXE: nie, code ho passes to same routines on zostavenie episode path. Name `demo.` also titulok `Nitemare-3D -- Demo Mode` sa nachádzajú v DOS v2.0 also Win16 1.10.

### 2. State machine DEMO has separate nahrávanie, playback and termination

Dispatcher during `seg3:90CE` branch according to global `0x46B8`. Telo ukazuje these state:

| Value `0x46B8` | Directly observed behavior | Confidence |
|---:|---|---|
| `1` | opens `demo` file v write mode, writes three 16-bit header words and prejde to state 2 | high |
| `2` | zaznamenáva change input state to 8-byte records | confirmed |
| `3` | opens `demo` file on read, loads three 16-bit header words and first 8-byte record, then prejde to state 4 | confirmed |
| `4` | play records according to store 32-bitového time | confirmed |
| `5` | zavrie handle and zeros status automatu | confirmed |

write branch is `seg3:90EA–9187`; play initialization is `seg3:9188–91F9`; time playback is `seg3:91FA–9249`; termination is `seg3:924A–9262`. DEMO buffer `0x7E84` sa directly passes otváracej routine during nahrávaní also play.

### 3. actual format record is structure fields, nie one 32-bit command

Previous audit zoskupil first four bytes each record as `uint32 value`. Raw Win16 code this named spresňuje: first dword contains two usage arrays and one nepoužitý byte.

| Offset record | Size | Source/target v runtime | Meaning |
|---:|---:|---|---|
| `+0` | 1 B | global `0x0108` | last/current key-event code |
| `+1` | 2 B | global `0x3756` | 16-bit mask input state |
| `+3` | 1 B | `0x3761` | automat ho during record nenastavuje and during play nekonzumuje; candidate on rezervu/padding |
| `+4` | 4 B | global time `0x53DC` | time events v runtime time základni |

write branch copies `0x0108` to `0x375E`, `0x3756` to `0x375F` and 32-bit time `0x53DC` to `0x3762`, then writes 8 bytes. Play robí opačný prevod: restores `0x0108` and `0x3756`, compares stored time `[0x3762]` with current `[0x53DC]` and loads next record, when is its time splatný.

Records sa write during change input páru (`0x0108`, `0x3756`), nie as right snapshot v each frame. If sa oba state equal posledným store value (`0x010C`, `0x3766`), writer record skips. To vysvetľuje why are time značky v file monotónne, but between nimi have nerovnomerné rozostupy.

All 760 records v `DEMO.1–3` has zero byte on offset `+3`. Its name and budúce usage remain open.

### 4. Input byte and 16-bit mask are prepojené with key dispatcherom

Routine `seg3:8C9A` branch according to key/event code, writes its byte to `0x0108` and changes individual bits wordu `0x3756`. Thereby is confirmed, that DEMO record save status input, nie ľubovoľné 32-bit game number.

Čitatelia mask confirm these effects: `0x0002` movement v direction player, `0x0004` opačný movement, `0x0008`/`0x0010` opačné direction otáčania, `0x0020` zdvojenie movement and uhlového kroku, `0x0040` vynútenie krokov on 1, `0x0080` streľba, `0x0100` modifikátor strafingu and `0x0200` hrana action podobnej USE. During combination strafing bitu with directional bitmi sa changes direction movement; named left/right and specific target USE remain partial.

Dispatcher compares also values `0x1B`, `0x20` and `0x0D`, what corresponds to Escape, Space and Enter v this branch. Other event code values neoznačujem automaticky for ASCII nor for scan codes.

## Prekontrolovaný content DEMO file

All three files have 6-byte header: three little-endian `uint16` values `10, 5, 20`. EXE confirms, that sa each writes and reads separate; their meaning so far neidentifikuje.

| File | Header | 8-byte records | Time first → posledného |
|---|---|---:|---:|
| `DEMO.1` | `10, 5, 20` | 203 | `19 → 1157` |
| `DEMO.2` | `10, 5, 20` | 271 | `35 → 2284` |
| `DEMO.3` | `10, 5, 20` | 286 | `19 → 2565` |

Equal size applies for all three: `file = 6 + 8 × count_záznamov`. Time arrays neklesajú. Their exact jednotku however cannot determine only z monotónnosti.

## Added: parametre headers and playback counter

Code initialization `seg3:D7D0–D8F4` kalibruje runtime parametre and writes header values to `0x53F6`, `0x53F8` and `0x53FA`. First two sa use as basic step movement and otáčania (`seg3:9900–993E`): mask `0x0020` their zdvojnásobí, `0x0040` sets oba steps on 1. Tretia value is directly compute as `0x53FA = 2 × 0x53F6`.

Routine `seg3:9D30–9E1E` uses `0x53FA` as limit repeated posunu object and checks medziľahlé MAP cells through helper `seg3:9B64`; result position writes to object. Thereby is confirmed substep limit for this object movement/collision branch. Whether is specific guard/object type or other aktérsku path, still needs to close. Provided headers `(10,5,20)` correspond this runtime parametrom.

During play v state 4, if following timestamp presahuje `0x53DC`, routine increments `0x53DC` o 1 on `seg3:9241`, but only when game state `0x46B6` is `8`. When is record splatný, restores input and loads next. Therefore is confirmed loop-relative playback counter; time v milisekundách on one count remains unknown.

## Open questions

1. What exact object/actor path uses `0x53FA` substep limit and what is wall-clock ekvivalent one playback counter countu? First two header arrays are movement and uhlový step; tretie is `2 × 0x53F6`.
2. Aké use names correspond dvom direction otáčania and which exact object or target vyvolá hrana `0x0200` podobná USE?
3. Is byte record `+3` rezervovaný byte, alignment padding or pozostatok iného array? All provided DEMO files ho have zero.
4. Aké are exact call path, which set DEMO state 1 and 3, and what terminate playback during reach konca file or during change game state? Status `0x46B6 == 8` allow inkrement playback countera.
5. Correspond DOS v2.0 records same layout? Win16 1.10 to dokazuje for this branch; prenos conclusion on DOS build still requires priamy compare analysis.
6. What is actual time tick? Needs to compare `0x53DC` with timer update function and confirm length playbacku run game.

## Next step

Next steps with najvyššou value are: determine aktérsku path, which uses `0x53FA` substep limit; trasovať calls začínajúce playback state 3 and its termination; compare DEMO format DOS v2.0 with Win16 1.10; and measure playback counter proti wall-clock time. Then possible use records as fixed input on simuláciu and test all 93 combination troch DEMO file with všetkými 31 finálnymi map.