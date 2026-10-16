# WORX Toolkit 2.1 — otvorené do 1:1 po RE MAX v0.16

**Dátum:** 16.10.2026. **Platná vstupná binárna identita:** DOS N3D v2.0 unpacked MZ image SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; differential pôvodné DOS v1.9. Primárne static RE, runtime iba pri neuzavriteľných periférnych/timing častiach.

Počet auditovaných `INT63` vstupných kontraktov **41/79 nenulových**, 38 zatiaľ bez plnej zreťazenej implementácie; 3 sloty počiatočne nulové. v0.16 **nepridala žiadne úplné API entrypointy** — uzatvára nové lokálne telá.

| Priorita | Funkcia | Strojovo uzavreté do v0.16 | Presná ďalšia medzera |
|---|---|---|---|
| P0 | MIDI `3A4D/3A67/58F8` | transformácia AX, globály, 3A67 status route a pitch, 58F8 read/write 0331/0330 a 65535 poll, optional FAR 3896 | `3B5B..3CB8`, `3941`, `3E34`, FAR `CS:3896` transitive; pôvodný FLAGS/DS/IRQ + port timing |
| P0 | Stream `5F17..6149` | fill prefix, 5F3E stav hlavičky, 312E read1/read3 order, fallback 4741 STC, 6 mode dispatch, režim 08/0C lokálne | `6037` mode01, `60E8/610C` mode02, `5FF3` mode03, `6092` mode09, DOS `312E` side effects/EOF a `4741` close |
| P0 | PCM `555D..5663` | DMA poll, clear prefix, sample-byte mix, 8 slotov | komplet voice loop, refill `5863`, `5502/56F0`, 16.16 stepping, byte-exact segmentové pointery |
| P0 | XMS `5863` | 256B packet, `21CE` stale, `CS:[21C8]` indirect shell | FAR service validity/CF/AX, handles, out-of-range, runtime device/IRQ boundary |
| P1 | MIDI `44B3..45DC` | track gate, running status, 1-/2-byte events, unknown/tempo/EOT, 45F9 VLQ, index commit | zero-delta transitive reentry; replay `4265/4389`; special/error meta and live callback aliases |
| P1 | `INT08/40E7` | scheduler shell, caller/callee ordering, private-stack entry | complete flags/stack and reentrant IRQ, PCM↔MIDI timing |
| P1 | 12-build Nitemare DOS+Win16 comparison | verified fingerprint + selected original-call equivalence | all other version-specific module diffs and runtime reachability |
| P2 | `INT63 AH=00,27,28` | initial image null slots | reachable writes to slots; self-modifying code and invalid selector >51h |

**Režim uzavretia:** každá funkcia/branch vyžaduje originálny hash, opcode/CFG, read+write aliasy, registre/flags a call order; vnorené odbočky majú explicitný OPEN status. Žiadne percentá „audio parity“ neodvodzovať z jednotkových testov. Pozri `WORX21_FINDINGS_v016_SK.md`.
