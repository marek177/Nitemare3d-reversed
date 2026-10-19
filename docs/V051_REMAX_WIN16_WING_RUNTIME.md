# Nitemare 3D RE MAX v0.51 — Win16 WinG runtime laboratory closure

**Date:** 19 October 2026

## Result

The Windows 3.11 laboratory now reaches a rendered E1M1 scene in all five tested Win16 Nitemare 3-D builds:

- v1.0;
- v1.3;
- v1.6;
- v1.8;
- v1.10.

Before completing the WinG 1.0 runtime, none of the five builds displayed a Nitemare game window in the bounded headless tests. Windows 3.11 itself was already known to work because Notepad launched successfully.

## WinG fix

The laboratory copy of Windows 3.11 was supplied with the WinG 1.0 components recovered from the user-provided Microsoft package:
- WING.DLL;
- WINGDE.DLL;
- WINGDIB.DRV;
- WINGPAL.WND;
- WING32.DLL.

DVA.386 was available but was not required to reach E1M1 in the successful matrix.

For v1.10 there was an additional local DLL conflict: the game directory contained its own old WING.DLL. In the laboratory copy it was preserved under another name so that the updated system WinG could be used. No Nitemare executable or game data were patched.

## Evidence boundary

"E1M1 rendered" means the original Win16 process created its game window, proceeded through episode/difficulty selection and displayed the 3D scene with HUD.

This does **not** yet prove:
- player input parity;
- scheduler/tick equality;
- DOS-vs-Win RNG ordering;
- WinG framebuffer/palette equality;
- sprite animation parity;
- audio parity;
- full mission completion.

The first WinG calibration path may still show a video-driver warning in this emulator, and exact presentation timing remains open.

## Consequence

Win16 runtime is no longer blocked at "game window does not start." The next Win16 work can now use original runtime captures instead of being restricted to NE static analysis.

The next useful matrix is controlled movement/collision/USE/door timing plus WinG framebuffer capture across all five builds.

No proprietary Windows, WinG or Nitemare binary is added by this release.
