# Menu / Instructions / Cheats reconstruction summary

This public note records behavior and structure only. The original 22-page instruction text and captured menu images are intentionally not redistributed here.

## Main menu

Inactive game: New game, Configure game..., Load game..., Instructions, Demo, Quit.

Active game adds Save game... and Return to game.

## Configure menu

Hardware..., Cheats..., Done.

The one-episode/demo edition still exposes the Cheats command but rejects activation because the full trilogy is not present. The reconstructed `CheatSystem` preserves this edition gate.

## Cheat modes

Four original modes are represented by `CheatMode`: Omniscient, Omnipotent, Omnificent and Omnifarious.

The Win16 1.10 effects are now statically closed:

- **Omniscient** keeps both mapper-power resources from draining and immediately restores them to 100 when the grant helper runs.
- **Omnipotent** supplies all four weapons, keeps weapon resources from being consumed, prevents normal player damage, and immediately restores HP/ammo to 100.
- **Omnifarious** grants the full collectible-access set: weapons, ammo, HP, keys, ID cards, pentagrams, mapper powers and special-use count 99.
- **Omnificent** does not globally freeze enemies. It suppresses autonomous acquisition in GUARD state 7 and the relevant state-8 branch. An accepted player fire action separately wakes eligible strategy-0 guards in the player's saved selector group into state 1; the global Omnificent flag remains enabled.

This distinction matters for a faithful reconstruction: the original instruction wording "unless you fire at them" is implemented by a saved, one-shot guard wake cache rather than by disabling Omnificent.

## Instructions flow

The original game exposes a 22-page instruction viewer. Public source keeps 22 stable page slots for menu/navigation testing while the original body text remains local reverse-engineering evidence only.
