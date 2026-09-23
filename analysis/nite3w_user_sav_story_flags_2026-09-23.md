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
| 0xC553 | DAT_1048_51A4 | Bit mask for the linked-wall state of a SECRET panel. In the supplied MAP/OBJECTS data, class 0x03 / object ID 0x62 selects channel 0. The panel requires ID-card mask bit 0, identified as the red card (object ID 0x09). Commands 0x1E/0x1F act on matching wall-pair records of classes 0x3B/0x3C. | Static selector, credential and wall-pair linkage are verified for the supplied Win16 data. The exact resulting appearance/state still needs runtime confirmation. |
| 0xC554 | DAT_1048_51A5 | Initialized to 1 and toggled by panel commands 0x20/0x21. It gates the Cannon class 0x19 (object IDs 0xCC–0xCF) state path 0x0E–0x10; the enabled path performs a perception check and can reach player damage. | Cannon binding and AI gate are verified statically; cadence, presentation and runtime effect still need measurement. |
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
- **51A4 is a SECRET-panel linked-wall bit mask, not safe/combo progress.** FUN_1010_D1A2 stores the class-relative object index in OBJECT+1; the supplied maps contain SECRET object ID 0x62 as the only class-0x03 item, so the current selector is 0. The panel checks ID-card mask bit 0 (red card, object ID 0x09); commands 0x1E/0x1F update linked class-0x3B/0x3C wall-pair records. Safe objects are a separate class-0x26 combination path. Other data builds and the exact visible wall result remain open.

## What remains unknown

1. Original text for the pointers 016E, 0172, 0176, 0182, 0186, 018A, 018E, 0196, 019A, 01C6 and 01D2, and the resources that populate them.
2. Runtime appearance/result of the linked wall-pair commands 0x1E/0x1F and whether additional SECRET channels occur in other MAP/OBJECTS builds.
3. Runtime Cannon cadence, presentation/SFX, and the player-facing labels for commands 0x20/0x21.
4. Whether 51A9 and 51AA are intentionally write-only save markers, consumed by code through an indirect path, or retained for compatibility.
5. Runtime proof of trigger placement, persistence after level changes, and behavior after loading saves with each byte independently modified.

This pass reduces the anonymous 8-byte save block to concrete call-site behavior, but it does not close the story scripts or the remaining USER.SAV anonymous blocks.
