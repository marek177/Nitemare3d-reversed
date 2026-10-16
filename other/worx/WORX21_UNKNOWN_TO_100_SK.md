# WORX 2.1 — zostávajúce neznáme po RE MAX v0.15

**Overený základ:** doteraz 41/79 nenulových `INT63` API handlerov s auditovanými kontraktmi; ostatných 38 nenulových handlerov bez úplnej implementácie. 3 počiatočne nulové sloty sú samostatný reachability problém. **v0.15 tieto počty nemení:** v0.14 uzavrela MIDI gate/EOT a XMS/stream podkontrakty; v0.15 navyše uzavrela jedno-eventový channel/meta parser shell 44EE..4552 a priamy 3A4D prefix.

| Priorita | Oblasť | Už uzavreté v0.14 | Otvorená presná medzera |
|---|---|---|---|
| P0 | `44B3..45DC` MIDI track parser | gate, 32-bit delta, FF2F EOT, FF51/unknown meta, **44EE..4552 running/new status, nibble-length parameter read, 3A4D direct CALL, 45F9/452B commit** | zvyšok `3A4D` po `3A67`, reentry `44B4` pri nulovej delte, callback nonreturn, replay `4265/4389`, CPU flags/IRQ |
| P0 | `5863` XMS refill | 256-B call packet, indexované 4-byte resource adresy, CF carry, stale `21CE`, nepriamy `CS:[21C8]`, výsledný AX sa obnoví | úplný XMS handler, identifikácia handle/banku, jeho flags + chyby, reálny streaming/refill/DS segment, súbežnosť s IRQ |
| P0 | `5F17` streaming | fill prefix `80/00`, mode08 single-word subtraction, mode0C unsigned 32-bit saturation | `5F3E..5FBE` EOF a file-header dispatch, 312E DOS side effects, mode 01/02/03/09, shared buffer a underruns |
| P0 | `555D–5663` osemhlasový PCM mixer | DMA poll, prefix 80h pair-clear, signed IMPUL sample primitive, 8 voice slots | plná per-voice slučka, wrap, playlist `5502`, `5863` refill side effects, 16.16 phase, far source byte routing, byte-exact output stream |
| P0 | `INT08` + `40E7` | timer gate/IRQ shell + 32-bit zostatok; volanie PCM→MIDI | presné prerušenia/IF, reentrant flagy, časovanie DMA bufferu a PIC chain |
| P1 | `3A4D` MIDI/OPL | **presné bezpodmienečné zápisy 2DC4/2DC8/2DC5/2DC6**, vstup `AX/BH/BL`; 1-dátová udalosť necháva BL z indexu stopy | kompletné `3A67+` OPL/Speaker/MPU vetvy, instrument bank, reentrancy/IRQ a vedľajšie účinky v nested callee |
| P1 | Krížové verzie | 6 úsekov v0.14; v0.15 navyše 101 B channel + 34 B dispatch + meta prefix, **13 nových operandových rozdielov, inak presná zhoda** | rozšíriť na celý segment/ostatné DOS verzie a zmapovať všetky netotožné callee telá |
| P2 | Mŕtve/nepoužité/invalid | nulové sloty 00/27/28 v počiatočnom obraze; alias závislosti EOT skeneru | writer→reader a nepriamy reachability dôkaz všetkých slotov, invalid AH=52 efekt, 16-bit code/data alias |

## Ďalší RE-first postup

1. `3A67+` a `44B4` reentry: **lokálny event pipeline je uzavretý**. Teraz doplniť transitive 3A4D dispatcher, volania `58F8/3B5B/38A7`, register/flags/writer-graph a nulový delta live/reachability dôkaz.
2. `5F3E..5FBE`: všetky príkazové módy, presný DOS `312E` file-result/CF a ukončenie; synchronizovať s už hotovým mode08/0C podkontraktom.
3. `555D` a `5863`: zostaviť stateful eight-voice mixer s explicitným XMS backendom a kontrolou reálneho 16:16 `ES:DI/DS:SI` pri ukončení hlasu.
4. Vyčerpať statiku na cross-build pre DOS 1.0/1.7/1.9/2.0 pred DOSBox runtime. Originálne hostiteľské IRQ, porty a timer testovať až pri nemožnosti statického uzavretia.

Pre uzavretie 1:1 je pre každý edge potrebný EXE SHA, machine bytes + CFG/call order, alias globals, regist/flags/stack, prepis a izolovaný test. **Nie je poctivé tvrdiť 100 %, pokiaľ chýba pôvodný runtime porovnávací trace.**
