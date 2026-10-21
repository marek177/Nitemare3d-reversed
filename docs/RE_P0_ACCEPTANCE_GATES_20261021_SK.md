# N3D výskumné blokery a akceptačné brány (21.10.2026)

Každý riadok je OPEN aj pri úspešnej syntetickej regresii, kým nie je splnená originál-vs-moderný kandidát brána.

| P | Oblasť | Dôkazy existujú | Potrebný nasledujúci experiment |
|---|---|---|---|
| P0 | Renderer | V078–V081, autentické U/XLAT, 42px writer | rovnaký pre-wall snapshot, 304 ownerov, 64000 indexed + 768 DAC |
| P0 | RNG + DEMO | 35 RNG draws, D02 timing | úplné seed→EOF RNG/caller/record/tick/IRQ ledger |
| P0 | Scheduler | E2M10 repeated-call statika | prirodzené multi-pass, gen/slot/writer, ABA a RNG |
| P0 | FIRE + weapons | class36, held Ctrl, fire clock | presná aktivácia/ammo a first projectile writer |
| P0 | Projectile | controlled 0→1→2→0 | natural FB–FE, damage RNG, stale-depth |
| P0 | Player/USE | V081–V086 input/strafe | tick-aligned movement, collision, USE door/secret |
| P0 | GUARD/boss | state, death vetvy | boss special transform, multi-actor a scheduler |
| P0 | SAVE/LOAD | DOS/Win16 scalar restore | prvý post-LOAD frame, RNG/cache rebinding |
| P1 | Win16 | NE fixups, WinG, clock | message-loop timing, WinG bitmap/DAC pod OS |
| P1 | Audio | bounded static recovery | emulované FIFO/tick/channel parity |
| P1 | Coverage | 31 levelov + E1M11 | deterministické reprezentatívne akcie pre všetky epizódy |

Odporúčané P0 poradie: 1. originálny post-wall-pass + indexed/DAC; 2. native wall writer a prvá divergencia, ešte bez DDA swapu; 3. originál-vs-port E1M1 tick input; 4. FIRE/USE/FB–FE; 5. E2M10 nested actor; 6. prvý frame SAVE/LOAD.

**Žiadne komerčné EXE/IMG/MAP/SND či celé RAM dumpy do verejného GitHubu.** Reproducer musí byť synthetic alebo opt-in s lokálnym originálnym súborom a kontrolou SHA256.
