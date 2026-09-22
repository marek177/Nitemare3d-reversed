# Remote door command reconstruction

`src/game/RemoteDoorRuntime.hpp` models the confirmed record-level path for
Win16 NITE3W 1.10 menu commands `0x1E` and `0x1F`:

- Match class `0x3B/0x3C` and `object+1 == selected group`.
- Open command: select door state `1/3`, write `door+0x14 = 1`, transition to
  state `2` and request SFX `0x25` unless global `0x51AB` blocks transitions.
- Close command: select state `0/2`, write `door+0x14 = 1`, transition to state
  `3`, request SFX `0x26` and clear `door+0x14` unless blocked.
- Toggle the group's bit in `0x51A4` after the loop even if no door changes.

`RemoteDoor` is a logical view; it is **not** a packed declaration of the
original 22-byte record. `openSounds` and `closeSounds` count requests for
the audio layer; this module does not play sound. The caller must separately
handle neighboring-record propagation, the full door animation tick, and
the ID-card gate on the CONTROL wall. `group >= 16` is rejected to keep the
16-bit reconstruction mask within bounds; its original runtime behavior is
not established. The global blocker may still leave the caller's `+0x14`
write, as seen in the Win16 call ordering.

Evidence: current `Nitemare3D_unknowns_audit_2026-09-21.md`, sections
“Deviaty”, “Desiaty” and “Jedenásty auditný prechod”, including raw segment
offsets `seg4:2ACB–2B40` and `seg3:188A–1A21`. The names *open* and *close*
are inferred from the observed state transitions. Unlike `TRIGGER1/2`,
this command path originates from the class-`03` CONTROL wall and card menu.

Focused build:

```sh
cmake -S . -B build -DN3D_ENABLE_SDL3=OFF
cmake --build build --target n3d_remote_door_runtime_test
./build/n3d_remote_door_runtime_test
```
