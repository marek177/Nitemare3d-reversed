# Menu / Instructions / Cheats reconstruction summary

This public note records behavior and structure only. The original 22-page instruction text and captured menu images are intentionally not redistributed here.

## Main menu

Inactive game: New game, Configure game..., Load game..., Instructions, Demo, Quit.

Active game adds Save game... and Return to game.

## Configure menu

Hardware..., Cheats..., Done.

The one-episode/demo edition still exposes the Cheats command but rejects activation because the full trilogy is not present. The reconstructed `CheatSystem` preserves this edition gate.

## Cheat modes

Four original modes are represented by `CheatMode`: Omniscient, Omnipotent, Omnificent and Omnifarious. Binary anchors and recovered state effects are documented in the source and EXE notes. Confirmed reconstructed effects include mapping-power bypass, ammunition/health bypass, enemy acquisition suppression, and broad inventory grant behavior.

## Instructions flow

The original game exposes a 22-page instruction viewer. Public source keeps 22 stable page slots for menu/navigation testing while the original body text remains local reverse-engineering evidence only.
