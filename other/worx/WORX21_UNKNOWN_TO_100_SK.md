# WORX 2.1 — RE-MAX v0.13: presne otvorené miesta do 100 %

**Basis:** pinned unpacked N3D DOS v2.0, 16.10.2026. 41/79 nenulových INT63 API obslúh má auditované kontrakty, 38 úplné telá neuzatvorené. 3 staticky nulové položky neoznačovať za trvalo mŕtve. Ďalšie nálezy v0.13 sú subkontrakty, nie nové úplné API implementácie.

| P | Funkcia/oblasť | Čo už vieme | Presné chýbajúce dôkazy / ďalší RE krok |
|---|---|---|---|
| P0 | `44B3..45DC` MIDI track parser (`AH=2F`, IRQ08) | Vstupný index `2DC0`, aktívne stopy, delta counters `2CA2/2CA4`, dôkaz 4476 fallthrough, helper `45F9` | Všetky `FF` meta vetvy (2F/51/unknown), running status, update DI, `3A4D`, `4265`, `4389`, `466A`, možné hardvérové `DIV` trap, memo stavy; exaktný CFG/callee graph |
| P0 | `555D..5663` PCM mixer | 8 voice slots, prefix fill, sample `IMUL` + 8-bit wrap | Absolútne všetky loop/ring/stop/playlist branch, 16.16 increment, refill `5863`, `5502`, state aliasing, zvukové mem ptr, compare DMA byte stream; bytový výstup |
| P0 | `5863` XMS/EMS refill | Priamo uloží XMS argument block a volá `CS:[21C8]` | callsite, `21C8` pointer origin, transitive memory bank and XMS driver flags, error/fallback/wrap; skutočné XMS služby ako posledný krok runtime |
| P0 | `5F17` audio streaming | Nový byte-pinned prefix `2DEA=1`, `48DB` length, `48E4` 00/80 buffer fill; stream state | Dokódovať `5F17..61xx`, DOS `312E` file read return/EOF/CF, volume/rate modes, file cursor alias, error paths, 5DF2 dependent effects |
| P0 | `49BC` DMA | 49BC celý data+port contract, signed branches modelované | IRQ flags `CLI/STI`, DMA latch race v reálnom DOS emulátore, dôkaz portových údajov a sampling window; C++ `PortIO` kontrakt už pripravený |
| P1 | `3A4D`, `38A7`, `58F8` MIDI/OPL | Vstupné status/data/state a priamy call chain známe | Kompletné note/controller bank, OPL register ordering, running status, no-voice fallback, metronom |
| P1 | `4265`, `4389`, `466A`, `45F9` | `45F9` plný VLQ algoritmus; staticky známe vstupy ďalších | Čítanie streamu MZ/FAR, CMF vs MIDI parser, chybné meta dáta, far pointer alias, nested `DIV 0` faults |
| P1 | `INT 08h` `4150`, `40E7` | V0.12 audit gate, PIC, BIOS chain, SUB/SBB budget, PCM→MIDI order; v0.13 aj vstupné shell vnútorných callbackov | Presné CPU stack/flags/segmenty, IF, vnoriteľnosť prerušení, súčasnosť DSP DMA a audio bufferu, stopy IRQ oproti originálu |
| P2 | `AH=00,27,28`, `AH=52` | Nulové sloty v počiatočnom obraze; mimo tabuľky 52 alias k `20C4` | Zistiť každého writera, reachability, self-modifying dispatch, CPU efekt volania null/invalid ptr |
| P2 | ostatných 38 `INT63` handlerov | Handler pointery a priorita v `data/WORX21_ALL_82_STATUS.csv` | Recursive CFG, všetky nepriame volania, register/stack/CF/IO contract, test každého tela |

Ďalší najvyšší pomer presnosť/čas: **rozobrať `44B3..45DC` do konkrétnych udalosťových typov a `5F17` stream body, potom doplniť mixer `555D` s 5863 refill**. Pri nemožnosti uzavrieť časovanie staticky použiť dávkovo rovnaký DOSBox-X hardvér na originál vs clone a porovnať sled `(tick, CS:IP, port, AL, DMA, IRQ, PCM byte/OPL register)`.

## Akceptačná podmienka 100 %

Pri každom vstupnom bode: vlastný machine-byte dôkaz + dominator/CFG so všetkými vetvami a write/read aliasmi + zreťazený call graph + CPU flag/stack model + C++17 testy + originál/clone register/port/timing trace, len tam kde statika nestačí. Hardvérový čas, obsluha chýb a mŕtve vetvy sú súčasťou definície. Žiadne percentá audio parity nevyvodzovať z počtu rekonštruovaných selektorov.

## v0.13 nový stav tempo `FF51`

`455D..458B` a jeho priamy PIT helper `466A..469E` sú teraz strojovo kontrolované a modelované vrátane x86 16-bit `DIV` trap a `OUT` poradia. Stále však ide o subvetvu v **otvorenom** track parseri `44B3..45DC`: zostávajú všetky ostatné meta eventy, running status, OPL callback, ES far-memory a vyvolávacie podmienky. Nezvyšuje sa počet uzavretých API handlerov nad 41.
