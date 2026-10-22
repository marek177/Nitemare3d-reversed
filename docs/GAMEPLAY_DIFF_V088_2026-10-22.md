# V088: original DOS2 ↔ remake gameplay first-divergence gate

**Scope:** diagnostics and contract tests only. No claim of achieved 1:1 behavior.

The new `tools/n3d_gameplay_diff.py` compares ordered state snapshots, reports the earliest divergence, detects sample omissions, malformed or truncated captures, invalid input masks, backwards ticks and bad CSV headers. `src/re/N3DGameplayTrace.hpp` provides opt-in C++20 capture serialization. The converter does not hook the actual game loop; callers must supply tick-aligned observations. The isolated Python/C++ CI suite uses only synthetic fixtures.

Exact CSV field order:

```csv
sample,tick,x,y,direction,input_mask,hp,ammo,weapon,object_count,guard_count,projectile_count,render_count
0,58,1440,3616,0,0,100,50,1,3,2,0,10
```

`sample` starts at 0 and increments by one. `tick` is a **real engine tick**, not host wall-clock elapsed time. `direction` is [0,359], expressed in **degrees**; any original angular encoding must be converted through separately verified math. `input_mask` is a uint16 (decimal or hexadecimal); DOS2 FIRE=0x80, ALT=0x100, USE=0x200, and unclassified bits must be retained. All columns are mandatory.

Envelope JSON, for each CSV:

```json
{"schema":"n3d.gameplay-state.v1","kind":"original","build":"dos-v2.0","capture_id":"E1M1-probe","begin":"tick_58","end":"tick_100","closed":true,"row_count":101,"csv_sha256":"ACTUAL_SHA256"}
```

For the candidate, use `kind: remake` and a build identifier. Envelopes must share capture_id/begin/end. Byte hash and actual row count are checked. Using an envelope does not demonstrate the program that actually produced the CSV.

```bash
python3 tools/n3d_gameplay_diff.py original.csv remake.csv \
  --original-manifest original.json --remake-manifest remake.json \
  --output report.json
```

Exit 0: matching snapshots and metadata-consistent captures. Exit 1: first difference, or equal data without matching capture envelopes. Exit 2: invalid CSV or metadata. `parity_proven=false` and `original_runtime_verified=false` remain deliberately false even for exit 0: actual executable provenance, atomic capture boundary, RNG call ordering, wall/sprite framebuffer and VGA DAC parity require **separate** independent evidence.

**All-in-One next pass:** capture original DOS2 KEYSTATE → movement/rotation → player XY commit at an instruction-ordered boundary; instrument the same point in reconstructed C++; run comparator; use static RE on its first divergence; correct the responsible code, compile Linux, and rerun with identical deterministic input. Extend with distinct event trace schemas for scheduler/RNG/projectiles and 320×200 framebuffer + 768 DAC, rather than asserting they are covered by this state-only comparator. No original proprietary executable/data is included.
