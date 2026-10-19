# Nitemare 3D RE MAX v0.59 — Win16 v1.10 SAVE → LOAD runtime witness

**Date:** 19 October 2026

The repaired Windows 3.11 / WinG laboratory now provides a real Win16 v1.10 E1M1 save/load witness.

Observed sequence:

1. start Win16 v1.10 and enter E1M1;
2. move forward until the view changes from the start room to the fireplace;
3. save to the first slot, producing `USER.SAV` of 55,015 bytes;
4. restart Windows and the game;
5. load the first slot;
6. observe restoration of the moved fireplace view.

The save after movement differs from a start-position save in 477 bytes at the same total size.

For the documented ROI, the loaded view compared with the saved moved view has mean channel deviation 0.94 and 98.37% exactly equal pixels. Loaded-vs-initial-start mean deviation is 55.61, strongly distinguishing the restored moved state from the original start view.

This is a **runtime persistence witness**, not byte-field closure. Exact X/Y/angle/HP/timer offsets in the Win16 save, RNG restoration, transient cache rebinding, the first post-load CPU update, and audio restoration remain open.
