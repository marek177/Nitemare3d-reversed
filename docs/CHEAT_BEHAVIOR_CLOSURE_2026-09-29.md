# Cheat behavior closure — Win16 1.10 — 2026-09-29

## Coverage change

| Area | Previous working status | 2026-09-29 status |
|---|---:|---:|
| Cheat behavior | 98% | **100% for audited Win16 1.10 behavior** |
| CONFIG.SAV cheat persistence | 50% legacy estimate | **100% Win16 layout/read-write semantics** |
| Omnificent internals | ~70% legacy estimate | **95–98% static/cross-version internals** |
| Cheat binary implementation / cross-build parity | 65% legacy estimate | **90–95%** |

The 100% claim is scoped to the behavioral semantics of the four cheat modes in the audited Win16 1.10 executable. It is not a claim that the complete-trilogy validation algorithm or every DOS/older-Windows implementation detail is reconstructed.

## Exact persistent flags

CONFIG.SAV is exactly 20 bytes and is loaded into the contiguous runtime block at 1048:4BD4. The final four bytes are:

```text
CONFIG +0x10 / 4BE4  Omniscient
CONFIG +0x11 / 4BE5  Omnipotent
CONFIG +0x12 / 4BE6  Omnifarious
CONFIG +0x13 / 4BE7  Omnificent
```

The game rejects an obsolete CONFIG.SAV length instead of silently accepting a different structure. Cheat menu edits are staged; successful apply writes these flags and runs the shared grant helper. Failed complete-trilogy validation clears all four flags.

## Shared grant helper B128

B128 is reached from three important contexts:

1. player/game-state initialization;
2. USER.SAV restore;
3. successful cheat-menu apply.

This means persistent cheats are re-applied after load/init rather than behaving as a one-time menu gift.

### Omniscient

Immediate grant:
- Magic Eye / mapper power 4C42 = 100;
- Crystal Ball / mapper power 4C43 = 100.

The mapping-power drain path bypasses decrement while Omniscient remains enabled. F9/F10 remain explicit display toggles; Omniscient does not force the automap view on.

### Omnipotent

Immediate grant:
- HP 4C1D = 100;
- silver ammo 4C1F = 100;
- laser ammo 4C20 = 100;
- wand ammo 4C44 = 100;
- weapon mask 4C2A = 0x0F;
- if active weapon is 0xFF, weapon selector 0 is selected.

Runtime behavior:
- normal player-damage path returns without reducing HP;
- weapon-resource consumption succeeds without decrement while enabled.

Weapons gained while the mode is enabled are not removed merely by later disabling the flag.

### Omnifarious

Immediate grant:
- Red/Green/Blue/Yellow key mask 4C28 = 0x0F;
- Red/Yellow ID-card mask 4C29 = 0x03;
- all four weapons 4C2A = 0x0F;
- all four pentagrams 4C45 = 0x0F;
- HP and all three ammo pools = 100;
- both mapper powers = 100;
- special-use count 4C22 = 99;
- if no weapon is active, select weapon 0.

This closes the old "grant internals pending" item.

### Omnificent

Omnificent has no B128 resource grant. Its flag is consumed dynamically by GUARD AI.

The flag does **not** turn off when the player fires.

Autonomous acquisition gates:
- GUARD state 7: 4BE7 causes an early return before LOS/acquisition;
- GUARD state 8: on the branch whose saved/next state is 2, 4BE7 causes the same early return.

Already-active/scripted states are not globally frozen by this flag.

## Accepted-fire wake path

After an accepted player fire action, the firing routine calls the 64-byte selector wake cache.

This is **not a hit requirement**:
- in the hitscan branch, the wake call occurs after the target scan even if no GUARD was hit;
- in the projectile branch, it occurs after successful projectile/fire creation.

The wake call is skipped when:
- no weapon is active;
- the scripted weapon-jam path returns;
- the weapon/ammo fire gate rejects the attempt;
- projectile/fire allocation fails.

For a fresh nonzero selector, the cache marks the selector before scanning GUARDs. A GUARD wakes only when:
- strategy == 0;
- GUARD selector matches the player's current selector;
- current state is 7 or 8.

The wake transition writes:
- timer = random() % 8;
- current state = 1.

State 1 then proceeds into state 2, outside the Omnificent acquisition-suppression gate. The persistent Omnificent flag remains set.

Because the selector is marked before scanning, the wake event is one-shot for that selector until the cache is cleared/restored. Selector 0 is a no-op. The wake loop itself has no distance or LOS test.

This is the executable mechanism behind the instruction wording that monsters generally ignore the player unless the player fires.

## Remaining cheat work

No major Win16 1.10 **behavior** question remains for the four modes.

Remaining implementation/parity work is separate:

1. reconstruct the complete-trilogy validator called by cheat apply down into the BSF/registration logic;
2. compare all four cheat consumer paths byte-for-byte across DOS and older Win16 releases;
3. runtime-regression selector-0 and repeated-shot wake behavior if behavioral capture parity is required.

These remaining items do not change the recovered Win16 1.10 user-facing cheat semantics.
