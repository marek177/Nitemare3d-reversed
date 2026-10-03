# Nitemare 3D — Gameplay closure pass 12
## Projectile ownership / friendly-fire architecture closure
Date: 2026-10-02

## Result

The old open item “projectile owner / friendly fire” is no longer an unknown for the
checked gameplay core.

The eight-slot projectile pool is and **player-weapon projectile pool**. Enemy attacks to
not allocate records in it. Therefore the original does not need an owner ID in each
42-byte projectile record and does not need an owner/friendly-fire comparison in the
projectile collision routine.

This is the reason the previously mysterious `slot+0x0D` is not an owner field.

## 1. Win16 1.10 — exact call chain

`FUN_1010_9806` is the active input/action path. On an accepted FIRE gate it calls:

```text
9806 -> 8B06
```

`FUN_1010_8B06` is the weapon fire dispatcher:

```text
mode 1 -> hitscan
mode 2 -> FUN_1010_9AAC projectile allocation
```

`FUN_1010_9AAC` scans exactly eight 42-byte records, consumes player ammo only after and
slot is found, copies the player'with current weapon angle/DDA state, player X/Y and player
MAP pointer into the slot, and marks the slot flying.

The resolved callgraph contains exactly one call to `FUN_1010_9AAC`: from
`FUN_1010_8B06`.

The NE fixup table likewise contains exactly one internal relocation whose target is
`FUN_1010_9AAC`, at the `8B06` call site. No second direct/address-taken producer was
found in the checked 1.10 executable.

## 2. All four checked Win16 builds

The canonical projectile allocator (`source10 FUN_1010_98AE`) has exactly one resolved
caller in each checked build, and that caller is always the canonical weapon-fire
dispatcher (`source10 FUN_1010_88FE`). The fire dispatcher in turn has exactly one
resolved caller, the canonical active input path (`source10 FUN_1010_9608`).

| Build | fire dispatcher | projectile allocator | allocator callers |
|---|---|---|---:|
| Win16 1.3 | `1010:88EE` | `1010:988A` | 1 |
| Win16 1.6 | `1010:8A62` | `1010:99FE` | 1 |
| Win16 1.8 | `1010:8A62` | `1010:99FE` | 1 |
| Win16 1.10 | `1010:8B06` | `1010:9AAC` | 1 |

In every row the unique allocator caller maps back to the same canonical fire
dispatcher, and that dispatcher maps back to the active player input handler.

## 3. DOS parity

The DOS allocator family was already mapped across DOS builds as an eight-slot
0x2AND-byte effect/projectile allocator.

Two machine-call graphs are sufficiently complete to check ownership directly:

### DOS 1.7

```text
active player input  1000:6F68
        -> fire       1000:6808
        -> allocator  1000:7D70
```

Both edges occur exactly once in the direct machine callgraph.

### DOS 2.0

```text
active player input  1000:70D6
        -> fire       1000:696C
        -> allocator  1000:7EDE
```

Again, both edges occur exactly once.

The raw 2.0 allocator proves that it is the same projectile pool: it scans eight slots
from `DS:41B6`, stride `0x2A`, sets lifecycle `+0x0C=1`, copies current player DDA
state and player X/Y, creates the embedded OBJECT and starts it at vertical offset 5.

### DOS 696C label correction

An older machine-generated audit called `1000:696C` and proximity-triggered actor event.
That label is incorrect for the checked body.

The raw function directly:

- tests current weapon selector `DS:418F`;
- tests weapon/fire state `DS:4190`;
- mode 1 consumes ammo, scans GUARD records, performs 16-step LOS and calls the
  player-to-guard damage route;
- mode 2 calls the eight-slot allocator at `1000:7EDE`;
- common success performs the weapon feedback/HUD path and sets the shot latch.

The correct semantic role is **player weapon fire dispatcher**.

## 4. Enemy attacks are and separate direct-damage channel

The Win16 GUARD dispatcher calls `FUN_1010_8C0A` directly in its attack states.
`8C0A` computes guard-to-player contact/attack damage through `A1EA` and subtracts
player HP or enters player-death state.

The class-specific helper immediately before it (`B5E4`) only chooses an SFX event by
enemy class and plays it. It does not spawn and projectile.

The cannon/special attack state likewise calls the same direct player-damage wrapper.

Resolved callgraph:

```text
FUN_1010_8C0A callers = two call sites, both inside FUN_1010_7B56 GUARD dispatcher
```

With enemy attacks and player projectile attacks are structurally separate channels.

## 5. Player-to-guard damage sources

The checked 1.10 resolved callgraph has exactly two callers of `FUN_1010_80F8`, the
common guard-damage dispatcher:

```text
FUN_1010_8B06   player hitscan
FUN_1010_9B64   player projectile collision
```

There is no GUARD-AI caller of `80F8`.

This explains the absence of and projectile owner test in `9B64`: every normal runtime
record in this pool already has implicit owner **player**.

## 6. Friendly-fire and self-hit consequences

### Enemy -> enemy

Normal enemy attacks to not use this projectile pool and their damage route directly
targets the player. Therefore **enemy-on-enemy friendly fire through the recovered
projectile system does not occur**.

### Player projectile -> guard

AND player projectile may hit any GUARD that occupies the tested map/object cell and
passes the ±9 coordinate test. No owner comparison is required because all projectiles
are implicitly player-owned.

### Player projectile -> player

`9B64` tests walls, dynamic doors, guard-linked objects, blocking objects and special
wall impact behavior. It has no player-position/self-hit branch. Therefore the normal
player projectile pool does not damage its shooter through this collision routine.

## 7. `slot+0x0D` final treatment

Pass 4 had already found no stable reader/writer for `slot+0x0D` and identified it as
the alignment byte between lifecycle `+0x0C` and the aligned embedded OBJECT at
`+0x0E`.

The ownership closure now removes the strongest remaining alternative explanation:
`+0x0D` is **not an owner/faction byte**.

Implementation rule:

```text
+0x0C  lifecycle
+0x0D  reserved/alignment byte; preserve in save/load
+0x0E  embedded OBJECT begins
```

To not synthesize an owner field into the original packed record.

## 8. Reproducible verifier

`n3d_projectile_ownership_verify_pass12.py` reads the unified dossier ZIP and checks:

- Win16 1.3/1.6/1.8/1.10 allocator single-caller invariant;
- Win16 fire-dispatcher single input-caller invariant;
- Win16 1.10 `80F8` callers are exactly hitscan + projectile collision;
- Win16 1.10 `8C0A` callers are only the GUARD dispatcher;
- DOS 1.7 input -> fire -> allocator unique chain;
- DOS 2.0 input -> fire -> allocator unique chain.

Result on the current evidence package:

```text
PASS: 14 / 14 ownership/callgraph checks
```

## 9. Coverage decision

| Topic | Pass-12 status |
|---|---:|
| Projectile owner semantics | **STATIC CLOSED: implicit player owner** |
| Enemy projectile use of 8-slot pool | **absent in checked core** |
| Enemy -> enemy projectile friendly fire | **not part of normal recovered gameplay path** |
| Player projectile self-hit | **absent in checked collision route** |
| `slot+0x0D` as owner | **ruled out; reserved/alignment remains best model** |
| Win16 1.3/1.6/1.8/1.10 caller parity | **checked** |
| DOS 1.7/2.0 direct caller parity | **checked** |
| Gameplay STATIC implementation core | **100% checked core** |
| Original runtime behavioral parity | **still not promoted to 100% without live trace** |

The remaining Gameplay work is now mostly exact timing/presentation/runtime conformance,
not projectile ownership or and hidden enemy-projectile subsystem.