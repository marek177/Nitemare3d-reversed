# Player health / enemy-to-player damage reverse-engineering report

Date: 2026-09-17

## Scope

This report tracks the next combat pass after GUARD strength, player-to-enemy damage, weapon ammo and scripted weapon-jam recovery.

## Behavioral constraints that must be reproduced

The original game has been directly tested with the following behavior:

- Player health is presented and behaves as a **0..100 percent** resource. There is no normal Doom-style health above 100%.
- At a displayed value of **0%**, further enemy hits do not simply drive the displayed health into negative values; the state behaves unusually and must be traced before assigning a death/underflow semantic.
- The Shift + `+` cheat interacts with health and is therefore a key cross-reference for finding the player-health runtime field and its clamp/set routine.
- Enemy attacks cause greater practical damage as gameplay difficulty is increased.

These are currently **BEHAVIORAL** constraints. They are not promoted to exact executable arithmetic until the corresponding receiver/setter is traced.

## Already verified combat context

Do not conflate the two damage directions.

### Player -> GUARD

Already recovered in `COMBAT_DAMAGE_RE.md`:

- `GUARD+10` is strength/HP and normally initializes to 255.
- `compute_damage` at `seg3:9FA2` generates player-to-enemy damage.
- OBJECT class x weapon transforms produce class-specific resistance/vulnerability.
- difficulty global `0x4C14` transforms this player-to-enemy damage as `0 => x2`, `1 => unchanged`, `2 => /2`.
- the same global inversely scales a GUARD timer, strongly identifying it as difficulty.

This does **not** prove that enemy-to-player damage uses the same arithmetic.

### Enemy -> player

Still to be recovered exactly:

1. player health runtime address/width/signedness;
2. damage receiver and zero/death branch;
3. hard clamp at 100 and healing/pickup saturation;
4. exact Shift + `+` cheat setter;
5. enemy attack damage producer(s), including melee/projectile distinctions;
6. difficulty transform for enemy damage;
7. invulnerability/Omnipotent interaction;
8. save/load field corresponding to health in the 94-byte USER.SAV gameplay block.

## Important implementation rule for reconstruction

Until executable evidence says otherwise, reconstructed gameplay must treat **100 as the normal hard gameplay ceiling** and must not implement Doom-style overheal. However, the unusual 0% state must not be guessed: it may be a death sentinel, cheat interaction, invulnerability edge case, or a receiver guard. Exact behavior remains TODO.

## Cross-reference targets

The next static pass should converge from multiple anchors rather than searching for an arbitrary byte equal to 100:

- Shift + `+` keyboard/cheat dispatch;
- Omnipotent global `0x4BE5`;
- HUD percent formatting / health-bar drawing;
- health pickup messages and pickup handlers;
- player death/game-over transition;
- enemy attack/projectile collision handlers;
- difficulty global `0x4C14`;
- USER.SAV writer/loader around the 94-byte compact state block at save offset `0x2035`.

A candidate player-health field is promoted only when at least two independent paths (for example HUD + damage receiver, or cheat setter + save writer) converge on the same address.

## Evidence policy

- User-observed 0..100 behavior: **BEHAVIORAL**.
- Exact runtime address, arithmetic and clamp: **TODO** until direct EXE proof.
- Higher difficulty causing greater enemy damage: **BEHAVIORAL**, consistent with the already recovered difficulty system but not yet numerically mapped for enemy-to-player damage.
