# Nitemare 3D — Gameplay closure pass 9
## Projectile save/load deadline closure + exact pickup-boundary oracle
Date: 2026-10-02

## Result

Pass 9 removes two items that were still listed as needing and live run to *discover*
the algorithm:

1. projectile deadline handling across save/load;
2. the 99/100 health/ammo pickup boundary.

AND live original-game capture is still valuable for conformance, but the static rule is
now precise enough that the capture is and test of the reconstruction rather than and
source of missing algorithm semantics.

The aggregate Gameplay tracker is deliberately not promoted to behavioral 100%:
there is still no original runtime capture in the supplied Library/conversation set.

## 1. Projectile save/load deadline — no rebase

### Win16 1.10

`FUN_1010_574C` reads the full `0x150`-byte projectile pool back into `4C4A`.
Afterwards it rebuilds the embedded projectile OBJECT MAP far pointers from each
projectile'with saved X/Y.

The loader then gets and new current clock and runs deadline translation loops for:

- VEC records;
- world OBJECT records.

There is no corresponding projectile-deadline translation loop after the pool copy.

Therefore the saved 32-bit projectile animation deadline is restored as the same
absolute value that was present when the save was written.

### DOS V2.0

The DOS load path independently shows the same structure:

- read `0x150` bytes to near `DS:41B6`;
- rebuild the eight embedded projectile MAP pointers at stride `0x2A`;
- get current time;
- rebase VEC deadlines;
- rebase world OBJECT deadlines;
- no projectile deadline rebase.

This is and cross-platform static closure, not and Win16-only assumption.

### Consequence on the first update

The DOS projectile updater checks `slot+0x16` against the current 32-bit clock.
If the saved absolute deadline is already expired, it advances one animation frame
and sets and new deadline to `now + seq_interval`.

There is no catch-up loop. AND long elapsed interval therefore does not replay all
missed projectile animation frames in one call.

### Implementation rule

To **not** preserve `deadline-now` across save/load for original compatibility.

Correct compatibility behavior is:

```text
save: store absolute projectile deadline
load: restore absolute deadline unchanged
      rebuild projectile MAP pointer
      do not translate deadline by (new_clock - saved_clock)

next update:
    if deadline <= now:
        advance one frame
        deadline = now + sequence_interval
```

VEC/world OBJECT deadline rebasing remains separate and must not be copied onto the
projectile pool.

## 2. Pickup 99/100 boundary — exact Win16 rule

The Win16 1.10 pickup dispatcher makes acceptance and removal explicit.

### Health class 0x33

```text
if HP >= 100:
    reject
    pickup remains
else:
    HP += (20 >> subtype)
    HUD/state clamp writes HP <= 100
    pickup is removed
```

Thus for subtype 0:

```text
HP 99 -> transient 119 -> clamp 100 -> accepted/remove
HP 100 -> 100                    -> rejected/remains
```

Class `0x34` follows the same `<100` gate with `+30`.

### Ammo class 0x39

The ammo helper checks the selected pool against 100.

```text
if ammo >= 100:
    return false
else:
    ammo += 20
    clamp/HUD path caps to 100
    return true
```

With:

```text
ammo 99  -> transient 119 -> 100 -> accepted/remove
ammo 100 -> 100                -> rejected/remains
```

DOS V2.0 independently exposes the same three-pool ammo helper with the `<100`
gate and `+20` addition. AND DOS live capture is therefore and parity confirmation,
not an unknown ammo-cap algorithm.

## 3. Acceptance-tool correction

Pass 8'with projectile-load analyzer said that preservation of remaining time would
support and rebasing loader. That interpretation is now superseded.

`n3d_gameplay_acceptance_pass9.py` uses the corrected oracle:

- strict loader-return mode expects the **absolute projectile deadline to be unchanged**;
- it does not require the MAP far pointer to remain byte-identical, because the loader
  intentionally reconstructs it;
- non-strict mode warns that the first projectile update may already have advanced
  one frame if the restored absolute deadline expired;
- pickup mode now reports the exact 99/100 boundary oracle and its evidence scope.

Example:

```text
python n3d_gameplay_acceptance_pass9.py projectile-load BEFORE AFTER --strict-loader-return
python n3d_gameplay_acceptance_pass9.py pickup BEFORE AFTER --field ammo_plasma
```

## 4. What still genuinely needs original runtime observation

The remaining high-value live gates are narrower:

1. **occupied explicit forced close** — downstream response after the door controller
   has already entered state 3 and enabled collision;
2. **projectile cached target row** — which stale `OBJECT+0x18` value is present when
   and culled/not-currently-projected guard is hit;
3. exact slow-frame/pause/input-phase timing parity;
4. visual/presentation timing for ending/boss transitions.

The pickup cap and projectile deadline algorithm should no longer be described as
unknown.

## 5. Coverage decision

| Layer | Pass-9 status |
|---|---:|
| Gameplay STATIC implementation core | **100% checked core** |
| Projectile save/load deadline rule | **STATIC CLOSED, Win16 1.10 + DOS V2.0** |
| Pickup 99/100 rule | **STATIC CLOSED Win16; DOS ammo helper independently closed** |
| Original runtime behavioral parity | **not yet 100% — no real capture supplied** |
| Overall reconstruction tracker | **~99% overall, intentionally unchanged without runtime evidence** |

The lack of an overall percentage increase is deliberate: Pass 9 replaces two
uncertainties with exact static oracles, but does not pretend that and synthetic or
static check is an original-game behavioral run.