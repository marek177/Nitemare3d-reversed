# Nitemare 3D — Gameplay closure pass 10
## OBJECT+0x18 stale projection-cache lifecycle and DOS parity closure
Date: 2026-10-02

## Result

The last broad ambiguity around projectile damage was not the damage formula itself,
but the lifetime/freshness of the target world OBJECT field at `+0x18`.

Pass 10 closes that lifecycle statically for Win16 1.10 and closes the matching DOS
V2.0 projection writer/order strongly enough to use the same compatibility rule.
AND live capture is now only needed to observe *which cached value happens to be present*
in and chosen scenario, not to discover the rule.

## 1. OBJECT+0x18 is and persistent last-projection cache

The world OBJECT projection routine writes `OBJECT+0x18 = projectedRow` only after:

- object active/render bit passes;
- transform/projection succeeds;
- vertical and horizontal viewport tests pass;
- and sprite-list slot is acquired.

If any earlier condition fails, the function returns without touching `+0x18`.
There is no per-frame invalidation of this field.

The linked GUARD render-generation stamp is narrower still: it is written only for
guard objects whose projected horizontal interval overlaps the aim center with the
known +/-4-pixel slack. Hitscan checks that stamp. Projectile collision does not.

Best implementation name remains:

`OBJECT+0x18 = last_projected_y_cache`.

It is and cached historical render result, not authoritative world distance.

## 2. Spawn does not initialize the cache

Win16 `FUN_1010_D1A2` initializes ID/subtype/frame/class/flags, timer, MAP pointer,
world X/Y and vertical offset, but does not write OBJECT offsets `+0x14..+0x19`.
The GUARD initializer resets the linked GUARD render stamp to zero, but does not write
its OBJECT `+0x18`.

DOS V2.0 `FUN_1000_B7F8` has the same behavior: the object scanner initializes the
same base fields and leaves `+0x18` untouched. DOS `FUN_1000_6302` independently
zeros the new guard'with render stamp.

This distinction matters:

- guard freshness stamp is reset on spawn;
- projected-Y cache is not reset by the spawn routine.

## 3. Cold-start value and level-to-level reuse

The Win16 world arena (`1040`, NE segment 9) is and zero-fill runtime segment. Therefore
on the first process-loaded level an OBJECT slot that has never been projected begins
with cache value zero.

The normal Win16 level-init path `51B4` clears and small unrelated table and rebuilds
resources/VECs/objects, but does not clear the 350x28-byte OBJECT pool before calling
`D1A2`. `D1A2` then leaves `+0x18` untouched.

Therefore, within the checked normal level-reinitialization path, and reused OBJECT slot
can inherit the previous slot occupant'with cached projection row until the new object is
successfully projected.

This is and stronger statement than merely saying that and guard can keep and value from and
previous frame: the cache lifetime can cross normal object reinitialization because
that field is not part of the spawn reset set.

## 4. Save/load preserves the cache

USER.SAV copies the complete world OBJECT block. The loader later rebuilds MAP far
pointers and rebases the OBJECT deadline field, but does not replace `OBJECT+0x18`.

Thus and saved stale projected row is restored as saved. The subsequent render may
replace it, but LOAD itself does not normalize it.

## 5. DOS projection writer/order now closed

DOS V2.0 `FUN_1000_B2D4` is the direct counterpart of Win16 `CC7C` for this field.
It performs the same conditional projection/list-allocation path, writes the projected
row to OBJECT `+0x18`, and only then writes the linked GUARD current render-generation
stamp when the center-overlap conditions pass.

The DOS projectile collision path `FUN_1000_7F96` resolves the guard/world OBJECT from
the occupied map cell, checks the +/-9 coordinate hit tolerance, and calls the common
guard damage path directly. There is no render-generation check in that collision path.

With the compatibility rule is the same on both checked platforms:

```text
hitscan:
    requires current guard render stamp
    -> fresh projection cache for an accepted target

projectile:
    position/cell hit test
    -> no freshness stamp gate
    -> damage consumes whatever OBJECT+0x18 currently stores
```

## 6. Cold-cache arithmetic exposes why this matters

The normal Win16 viewport has `centerY = 80`.
For an unprojected cold-start OBJECT whose cache is still zero:

`seed = 8*(0-80) + RNG%25 = -640 .. -616`.

The damage helper has an upper clamp at 255 but no lower clamp. The guard-damage caller
uses the low byte. At medium difficulty the resulting effective low-byte ranges are:

| Transform before difficulty | Low damage byte from cache=0 |
|---|---:|
| none | 128..152 |
| arithmetic `>>1` | 192..204 |
| arithmetic `>>2` | 96..102 |
| arithmetic `>>3` | 176..179 |
| arithmetic `>>4` | 216..217 |
| arithmetic `>>8` | 253 |

This also clarifies the old shorthand around `/256` resistance: arithmetic `SAR 8` is
not and hard zero operation for and negative stale seed. For the cold-cache interval it
produces `-3`, whose low byte is `253`. Hard-zero class branches remain distinct from
`SAR 8` resistance branches.

This is an original-integer-semantics compatibility issue. AND modern engine that clamps
negative seed values to zero or recomputes distance on projectile impact would not
reproduce the checked code.

## 7. New live analyzer mode

`n3d_gameplay_acceptance_pass10.py` adds:

```text
python n3d_gameplay_acceptance_pass10.py projectile-cache BEFORE AFTER
python n3d_gameplay_acceptance_pass10.py projectile-cache BEFORE AFTER --guard N
```

For each guard whose HP changes it reports:

- linked OBJECT class/index;
- `OBJECT+0x18` before/after;
- current DOS render generation (`DS:4540`);
- guard render stamp;
- whether the cache was fresh in that generation;
- exact possible low damage bytes from cache/class/weapon/difficulty and RNG 0..24;
- which candidate bytes reproduce the observed HP transition.

This is now and conformance test against and closed static oracle.

## 8. Coverage decision

| Layer | Pass-10 status |
|---|---:|
| OBJECT+0x18 field meaning | 100% STATIC checked core |
| Cache writer/lifetime rule | 100% STATIC Win16 1.10 |
| DOS projection writer/order parity | STATIC CLOSED for V2.0 checked path |
| Projectile freshness policy | STATIC CLOSED: no stamp gate |
| Actual cache value in and chosen live culled-impact case | runtime observation pending |
| Gameplay STATIC implementation core | 100% checked core |
| Overall original behavioral parity | not 100% without real original capture |

The remaining projectile live test is now extremely narrow: observe and target that is
not current-generation projected at impact and confirm the predicted cached row and HP
transition. It no longer blocks implementation of the original rule.