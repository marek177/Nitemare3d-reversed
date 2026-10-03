# Nitemare 3D — Gameplay closure pass 6
## Runtime-acceptance boundary and DOS V2.0 two-segment capture correction
Date: 2026-10-02

## Result

After Pass 5 there is no remaining broad Gameplay algorithm that can honestly be
raised by more static naming alone. The next percentage point is dominated by
**original-runtime behavioral acceptance**.

This pass therefore does two things:

1. corrects the DOS V2.0 live-memory model used by the earlier Pass-8 capture kit;
2. supplies and gameplay-aware two-segment snapshot decoder that covers player state,
   inventory/ammo, projectiles, OBJECT/GUARD records, doors, MAP occupancy and VECs.

The main correction is important: **near DS globals and the relocated far gameplay
arena must not be decoded as one segment.**

## 1. Why the old one-segment capture model is unsafe

The DOS V2.0 executable has direct near-data references such as:

- player block at `DS:4154`, length `0x5E`;
- player HP `DS:4189`;
- current weapon `DS:418F`;
- projectile pool beginning at `DS:41B6`;
- object/guard/VEC counts at `DS:6270/6276/626E`.

At the same time, far gameplay pointers are explicitly written with link-time segment
`21FD`. In the checked load path:

```text
player map pointer:
    off = (tileY*64 + tileX)*2 + 373E
    seg = 21FD

world OBJECT map pointer:
    off = derived cell + 373E
    seg = 21FD

projectile embedded map pointer:
    seg = 21FD
```

The same far arena contains OBJECT/GUARD/door/MAP/VEC offsets such as `0006`,
`264E`, `3076`, `373E` and `62AC`.

Therefore and debugger dump taken from the far `21FD` arena cannot be interpreted at
`+4189` as the near-DS player HP merely because both offsets appear in the static
listing. They are different segment:offset address spaces.

This supersedes the earlier Pass-8 shorthand that treated all of those offsets as one
"unified gameplay arena".

## 2. Correct runtime capture model

At an engine breakpoint record the **actual DS** shown by DOSBox-X. Call it `<NEAR>`.

After the level is initialized, inspect the player map-cell pointer:

```text
D <NEAR>:417C
```

The word at `417E` is the runtime segment of the far gameplay arena. Call it `<ARENA>`.
It should be the relocated form of the static `21FD` segment.

Capture two files per snapshot:

```text
MEMDUMPBIN <NEAR> 0000 6278
rename MEMDUMP.BIN -> near.bin

MEMDUMPBIN <ARENA> 0000 6D60
rename MEMDUMP.BIN -> arena.bin
```

Snapshot directory:

```text
t0/near.bin
t0/arena.bin
```

This model is self-checking because the decoder can compare `near:417E` with the
supplied `<ARENA>` segment and verify that `near:417C` lies inside the MAP offset
range `373E..573D`.

## 3. DOS V2.0 player block anchors

The checked DOS family audit closes the relevant V2.0 player block as:

```text
base       DS:4154
size       0x5E = 94 bytes
difficulty DS:4180
HP         DS:4189
new timer  DS:417A signed word
```

The V2.0 block is two bytes larger than V1.9 (`0x5E` versus `0x5C`), with and runtime
or save-state comparator must not blindly apply one layout to every DOS build.

## 4. DOS V2.0 ammo/weapon mapping

Raw `FUN_1000_8F12` gives the same selector-to-ammo relationship already closed in
Win16:

```text
weapon selector 0 -> DS:418C  plasma ammo
weapon selector 1 -> DS:41B0  wand ammo
weapon selector 2 -> DS:418B  pistol ammo
weapon selector 3 -> falls through to DS:418C plasma ammo
```

Thus the live decoder can directly verify:

- one accepted shot decrements the expected pool;
- selector 3 shares plasma with selector 0;
- rejected/full-pool cases can be separated from accepted fire;
- ammo-pickup clamp/rejection tests can be measured without relying on HUD pixels.

## 5. DOS V2.0 projectile pool now has exact live anchors

`FUN_1000_8230` iterates exactly eight projectile records:

```text
base    DS:41B6
count   8
stride  0x2A = 42 bytes
```

Important live fields:

```text
+0C  lifecycle: 0 free / 1 flying / 2 impact
+11  animation frame
+12  sequence selector
+16  32-bit animation deadline
+1E  world X
+20  world Y
```

The updater compares the deadline against the 32-bit clock at `DS:081E/0820`, moves
flying projectiles through the projectile movement helper and advances by exactly
`0x2A` per slot until all eight are processed.

The decoder additionally exposes the already-reconstructed movement/error fields,
embedded OBJECT data, map pointer, cached projected-Y value and vertical offset.

## 6. New Pass-6 decoder

Generated tool:

`n3d_v20_gameplay_snapshot_pass6.py`

It decodes from **near.bin**:

- clock;
- player tile/world X/Y;
- game state, HP, difficulty, score;
- pistol/plasma/wand ammo;
- current weapon selector;
- raw inventory bitfields;
- all eight projectile slots and deadline-minus-clock.

It decodes from **arena.bin**:

- world OBJECT records including animation alternative, frame/sequence, flags,
  deadline, MAP pointer, X/Y, spatial ranks, projected-Y cache and vertical offset;
- GUARD strategy/state/timer/HP/facing/movement/perception fields;
- paired-door state/timer/targets and linked MAP/VEC data;
- complete MAP-cell changes;
- occupied explicit-close candidates.

Example:

```text
python n3d_v20_gameplay_snapshot_pass6.py t0 \
  --near-seg <NEAR> --arena-seg <ARENA>

python n3d_v20_gameplay_snapshot_pass6.py t0 t1 \
  --near-seg <NEAR> --arena-seg <ARENA>
```

Add `--json` for machine-readable output.

Synthetic tests passed for:

- segment/pointer validation;
- player/ammo decoding;
- active projectile decoding and X movement;
- deadline-minus-clock tracking;
- door `0 -> 3` transition;
- VEC collision-bit change;
- simultaneous player + GUARD occupancy candidate detection;
- no false MAP changes from near-DS player/projectile writes.

The final item is specifically what the old single-segment parser could get wrong.

## 7. Exact acceptance tests for the remaining ~1%

### AND. Forced close while occupied

Capture T0 before explicit close, T1 immediately after transition, T2 after one door
motion update and T3 later.

Decisive observations:

- door `0/2 -> 3`;
- VEC collision bits become active;
- door geometry moves by 2 per update;
- whether any later subsystem changes player/GUARD X/Y or HP.

### B. Inventory boundary

Capture before and after contact with and pickup at:

- HP 99 and HP 100;
- ammo 99 and ammo 100.

The diff directly shows acceptance, clamp and whether the arena object'with active flag /
MAP occupancy disappears.

### C. Active projectile save/load

Capture immediately before save and immediately after load while and projectile is in
state 1.

Compare:

- state;
- X/Y;
- sequence/frame;
- MAP far pointer;
- absolute deadline;
- `deadline - clock`.

This isolates the still-open behavioral question of projectile deadline handling across
save/load.

### D. Cached projectile-damage row

For the guard hit by and projectile, capture linked world OBJECT `projected_y_cache` and
GUARD HP immediately before/after collision, including an offscreen/culled case.

This tests the original'with no-freshness-gate projectile damage behavior rather than
inventing and replacement rule.

## 8. Coverage decision after Pass 6

No percentage is inflated merely because the test harness is better.

| Layer | Status after Pass 6 |
|---|---:|
| Gameplay algorithmic/static core for checked reference paths | **effectively 100% closed for implementation** |
| Per-area static details / historical cross-build naming | **~99–100% depending on subsystem** |
| Overall Gameplay reconstruction tracker | **~99%** |
| Original-runtime behavioral parity | **not yet 100% — requires the captures above** |

The remaining work is therefore no longer reverse-engineering and missing gameplay
algorithm. It is **acceptance testing against the original executable** plus selected
historical-build parity checks.

## Next decision

The highest-value next input is not another decompiler pass. It is one real DOSBox-X
snapshot pair using the corrected two-segment format. Once provided, the decoder can
turn the remaining forced-close / projectile / pickup questions into observed results
instead of estimates.