# Recovered USE dispatch code (2026-09-22)

`src/game/RecoveredUseDispatch.hpp` implements the directly observed decision
layer in the Win16 NITE3W 1.10 `FUN_1010_19d6` path. `useRoute` accepts wall
property, wall class and object class as separate values, preserving their
priority. It routes door (`wall property 0x08`), level exits (`09/0A`), warp
(`0D–2C`), panel (`object 03`), special walls and interactive objects.

`doorUseGate` models the observed class ranges `33–38` (colour key), `39–3A`
(ID card), and `3B–3C` (remote only). It tests the bit selected by runtime
object byte `+01` against the appropriate mask. An index outside the eight
representable bits is returned as `InvalidKeyIndex`; this is a defensive
reconstruction result, not a documented original-game error message. The
routine does not consume keys or cards.

`warpFamily`, `colourWarpUnlocked` and `otherSidePortalUnlocked` represent
the five observed WARP ranges, the four colour-key gates and the one-way
`WARP_S1` portal requiring four pentagrams. `WARP_S2` does not offer a return
teleport. The reserved `25–2C` range is classified but has no invented effect.

Evidence: `Nitemare3D_unknowns_audit_2026-09-21.md` (version 21), sections
“Hlavný USE dispatcher”, “USE dispatcher — doplnené priame writery”, “Presné
rozsahy WARP tried” and “WARP_S1/S2”. A direct reconstruction of the handler
side effects, wall animation timing, remote group selection and teleport
orientation still requires the relevant assembler and runtime observations.

Build and run the focused check with:

```sh
cmake -S . -B build -DN3D_ENABLE_SDL3=OFF
cmake --build build --target n3d_recovered_use_dispatch_test
./build/n3d_recovered_use_dispatch_test
```
