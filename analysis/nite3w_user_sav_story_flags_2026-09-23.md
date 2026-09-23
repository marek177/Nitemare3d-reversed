# Win16 USER.SAV+0xC553: event and AI flags

**Date:** 2026-09-23  
**Target:** NITE3W 1.10; cross-check: NITE3W 1.8  
**Purpose:** replace the anonymous eight-byte label at USER.SAV offset 0xC553 with an evidence-based behavior map.

## Evidence boundary

The save writer and loader copy eight consecutive bytes at 0xC553 to and from DAT_1048_51A4 through DAT_1048_51AB. FUN_1010_0EF6 initializes them to 01 00 00 00 00 00 00 00 at a new-game/session setup. The same eight global addresses and corresponding initialization/read/write sites are present in the Win16 1.8 decompilation.

The operations below are directly visible in the decompiled executable. Narrative labels remain provisional where the code only selects a text pointer whose original text is not present in the decompilation. “Trigger class 0x47/0x48” means the MAP wall-class lookup values TRIGGER1/TRIGGER2, not ASCII text in the MAP plane.

## Byte map

| Save offset | Runtime byte | Directly observed behavior | Status |
|---:|---|---|---|
| 0xC553 | DAT_1048_51A4 | Bit field selected by DAT_1048_40F8. Commands 0x1E/0x1F update its selected bit while opening matching runtime door records of wall classes 0x3B/0x3C for the same selector and orientation. | Door/combo state is strongly supported; exact meaning of a set bit (completed, selected, or cached state) remains open. |
| 0xC554 | DAT_1048_51A5 | Toggled by dispatcher actions 0x20/0x21. GUARD states 0x0E/0x0F read it: when set, state 0x0E advances to 0x0F; state 0x0F repeats a timed branch through 0x10, and when clear it returns to 0x0E. | Confirmed global gate for a special GUARD behavior; actor group and design meaning remain open. |
| 0xC555 | DAT_1048_51A6 | Shared level-trigger latch/stage. Several TRIGGER1 branches set it to 1; the special-wall class 0x08 follow-up in episode 1, level index 6 advances 1 to 2. The contact-damage path for object class 0x16 also checks whether it is zero. | Confirmed state machine with values 0/1/2; exact story meaning is not recovered. |
| 0xC556 | DAT_1048_51A7 | Set to 1 by the episode 1, level index 9 TRIGGER2 branch before displaying its text event. No gameplay read was found beyond save/restore. | Confirmed one-shot event marker; text and downstream consumer remain unknown. |
| 0xC557 | DAT_1048_51A8 | Set by episode 1, level index 9 TRIGGER1. That branch sets DAT_1048_4BE8, clears DAT_1048_4BE5 and displays three text pointers. The Escape handler later checks this flag when the game is in state 7 and player health is zero. | Confirmed end-event/exit gate; the exact meaning of DAT_1048_4BE8 and the narrative text remain open. |
| 0xC558 | DAT_1048_51A9 | Set after a counter reaches a 20-call interval in the episode 2, level index 9 special collision path. The path moves the player, runs event/timer helpers and changes game state. | Confirmed persistent script marker; no direct read of this byte was found. |
| 0xC559 | DAT_1048_51AA | Set in the GUARD state-9 handler for object class 0x16 (identified as Dr. Hamerstein in the GUARD audit). The handler requests sound 0x12, displays a text pointer, resets DAT_1048_46B4, and transitions the actor out of state 9. | Confirmed class-specific event marker; not evidence by itself of a hit or kill, and no direct gameplay read was found. |
| 0xC55A | DAT_1048_51AB | Set with DAT_1048_51A6 by the episode 1, level index 6 TRIGGER1 event. While set, the renderer selects shade level 6 and zeroes floor/ceiling palette selectors; the door update helper returns early. The class-0x08 follow-up clears it while advancing DAT_1048_51A6 to 2. | Confirmed temporary presentation/world-update mode; the exact scene label is open. |

The level indices above are the zero-based values tested by the executable. For example, index 9 is the tenth level of an episode.

## Trigger dispatch recovered from FUN_1010_BFD8

The routine reads the current wall class through the 256-entry wall-ID-to-class table, then gates event branches on episode, level index and class. The movement/collision path checks the wall property bit 0x40 before entering this trigger dispatcher.

| Episode | Level index | Wall class | Handler/effect |
|---:|---:|---:|---|
| 1 | 6 | 0x47 / TRIGGER1 | If DAT_1048_51A6 is zero, run FUN_1010_BEF4: event preparation, set 51A6=1 and 51AB=1, then show the text pointer at DAT_1048_016E. |
| 1 | 8 | 0x47 / TRIGGER1 | Set the auxiliary DAT_1048_4C2E event byte if clear; request sound 0x44. |
| 1 | 8 | 0x48 / TRIGGER2 | If the auxiliary 4C2E byte is set, clear it and request sound 0x44. The 4C2E byte lies inside the 94-byte saved gameplay/global block. |
| 1 | 9 | 0x47 / TRIGGER1 | If 51A6 is zero, run FUN_1010_BF20: set 51A6=1 and 51A8=1, set 4BE8=1, clear 4BE5 and display three text pointers. |
| 1 | 9 | 0x48 / TRIGGER2 | If 51A7 is zero, run FUN_1010_BF70: set 51A7=1 and display the text pointer at DAT_1048_018E. |
| 2 | 9 | 0x47 / TRIGGER1 | If 51A6 is zero, run FUN_1010_BFA4: set 51A6=1 and display the text pointer at DAT_1048_019A. |
| 3 | 0 | 0x47 / TRIGGER1 | If 51A6 is zero, run FUN_1010_BFBE: set 51A6=1 and display the text pointer at DAT_1048_01D2. |
| 3 | 9 | 0x47 / TRIGGER1 | If 51A6 is zero, run FUN_1010_BF8A: set 51A6=1 and display the text pointer at DAT_1048_01C6. |

This matrix closes the dispatch conditions and byte writes for the listed branches. It does not identify the original text, prove that every corresponding trigger is placed in every MAP build, or assign a story name to shared latch 51A6.

## Less-obvious cross-links

- **51A6 changes one damage branch.** In FUN_1010_A1EA, class 0x16 receives damage 33 when the episode is not 3 and 51A6 is zero; otherwise it falls through to damage 100 before difficulty scaling. The flag is therefore not only a dialogue latch.
- **51AB changes more than color.** FUN_1010_C5E2 selects shade mode 6 and clears floor/ceiling selectors when the flag is set. FUN_1010_188A exits before its normal door operation while the flag remains set.
- **51A9 is reached from object collision.** FUN_1010_9B64 calls FUN_1010_C356 when the object-property table has bit 0x40. C356 only enters the timed helper for episode 2, level index 9; C2B8 increments its counter and sets 51A9 on the 20-call event path.
- **51AA marks a GUARD state transition.** The caller is the state-9 branch in FUN_1010_7B56, not the projectile hit routine. Its sound/message side effect is class-specific to 0x16.
- **51A4 selector is not safely nameable as “level.”** FUN_1018_21D8 copies byte +1 of a selected record into DAT_1048_40F8. The safe-door dispatcher uses that selector for both its bit shift and record filter. The code proves a selector-keyed door state, but the original field meaning and valid selector range need data/runtime confirmation.

## What remains unknown

1. Original text for the pointers 016E, 0172, 0176, 0182, 0186, 018A, 018E, 0196, 019A, 01C6 and 01D2, and the resources that populate them.
2. Exact interpretation and valid range of the selector used by 51A4; whether the bit records a solved combination, an open pair or a UI/cache state.
3. Which GUARD classes reach the 0x0E–0x10 special branch controlled by 51A5, and what the map action commands 0x20/0x21 mean to the player.
4. Whether 51A9 and 51AA are intentionally write-only save markers, consumed by code through an indirect path, or retained for compatibility.
5. Runtime proof of trigger placement, persistence after level changes, and behavior after loading saves with each byte independently modified.

This pass reduces the anonymous 8-byte save block to concrete call-site behavior, but it does not close the story scripts or the remaining USER.SAV anonymous blocks.
