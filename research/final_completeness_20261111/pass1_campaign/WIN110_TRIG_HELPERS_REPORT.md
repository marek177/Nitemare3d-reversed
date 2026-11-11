# Win16 1.10: štyri ekvivalentné lokálne trig helpery

EXE SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`. NE autodata segment je **10**; predtým potvrdené tabuľky ležia v 10:025E..0480. V kódovom segmente **3** sú štyri helpery s nasledujúcimi presnými hranicami (end-exclusive):

| Funkcia | Win16 rozsah | Bajty |
|---|---|---:|
| sínus | 3:ECAC..ECF8 | 76 |
| kosínus | 3:ECF8..ED44 | 76 |
| tangentová magnitúda | 3:ED44..ED90 | 76 |
| celočíselný angle lookup | 3:ED90..EE25 | 149 |

## Dôkaz ekvivalencie a segmentové obmedzenie

Všetky štyri telá sa zhodujú s DOS 2.0 po presne evidovanej zmene **13 dátových operand WORDov**, vždy delta **-5514 = -158Ah**. Žiadne iné kódové bajty sa neignorujú. Relatívne vetvy, porovnania, delenie, NEG, prahy a stack operácie sú zhodné. Kandidáti sa znovu nezávisle dekódujú so zhodnými hranicami/dĺžkami a flow-control kategóriami. Celý dátový blok 546 B je byte-exact zhodný.

To podporuje lokálnu algoritmickú a CFG parity vrátane neštandardného znamienka tangentovej magnitúdy v Q2, lookup indexu 91 a nulového vektora ->90. Je to podmienené rovnakým platným vstupným stavom a DS namapovaným na príslušné autodata. **NE deklarácia autodata=10 sama nedokazuje prirodzený runtime DS každého callera.** Reálne selektory, prology callerov, NE fixup volania a behaviorálna parity celej hry zostávajú otvorené. Žiadny Windows runtime replay sa tu nevykonal.

## Oprava hranice DOS funkcie

Cross-version kontrola odhalila, že starší rozsah angle lookup `[D096,D12C)` zahŕňal aj trailing 90h za RETF. Vo Win16 zodpovedajúci bajt je 00h. Správny doložený rozsah je **[D096,D12B), 149 B / 62 inštrukcií**. Bajt D12Bh sa z funkčného katalógu odstránil; neoznačuje sa tým automaticky ako padding. Starší 150 B / 63 výkaz bol o jeden bajt/inštrukciu širší. Po oprave znovu prešlo všetkých **1 274** pôvodných seeded prípadov. Nepripočítavajú sa znova ako nové prípady.

## Reprodukcia a artefakty

Aktualizovaný `compare_trig_versions.py IMAGE OLD_OUTPUT_ROOT DECODER_DIR WIN110_EXE OUT` prehľadá všetky file-backed NE kódové segmenty, vyžaduje jedinú súvislú štvoricu kandidátov, rovnaký operand delta odvodený z presnej tabuľky a zhodné zvyšné bajty. `trig_cross_version/win110_functions.csv` obsahuje adresy/file offsety/SHA, `win110_operand_edits.csv` všetkých 13 úprav. DOS výsledky zostávajú 32 normalizovaných zhôd a 91 recorded úprav pri ôsmich označeniach/siedmich unikátnych obrazoch.

`audit_replay_angle_lookup.py` a centrálny katalóg boli regenerované s opravenou hranicou. PASS1 byte mapa zostáva **54 164 B PARTIAL, 3 087 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**. Replay súčet zostáva 6 091, prirodzený runtime 0. Nové Windows helpery sa vedú v samostatnom NE katalógu, nepripočítavajú sa k DOS funkčným rozsahom.

Ďalší krok: NE fixup caller inventár na 3:ECAC/ECF8/ED44/ED90, runtime DS guard a vstupy. Súbory v `L:\nite3d` a `L:\nite3d\dos` zostávajú primárnym miestnym zdrojom; nevyžaduje sa PE32 port.


## Aktualizácia 13 oblastí

Nové sémantické percento je všade N/A: úplný inventár kontraktov/polí/vetiev chýba. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické percentá sú orientačné odhady.

| Oblasť | Predošlý odhad | Nové % | Potvrdenie | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | opravená mapa a flagy | prirodzené súbory | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 546 B tables identical across DOS labels and Win110 | 2 relokačné B bez typu | roly segmentov |
| Tabuľky a ukazovatele | 93 % | N/A | 4 normalized Win16 helpers; angle boundary corrected | writeri/lifetime | pointer watchpointy |
| Funkcie / ASM / CFG | 90 % | N/A | 34 rozsahov, 1 150 inštrukcií | kontrakty/dosiahnuteľnosť | caller stopy |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | staršie PIT dôkazy zachované | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová DEMO stopa |
| Renderer / VGA | 94 % | N/A | bit reversal začlenený | clipping/orientácia | payload spotrebiteľ |
| GUARD / bossovia | 93 % | N/A | nominálne pole 100×26 | AI/lifecycle | inicializátory |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie/sloty | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | 60 počiatočných UI textov | textový lifetime | SS čítania po návrate |
| SAVE / LOAD | 92 % | N/A | mapové/flagové rozsahy | LOAD parity | párový stav |
| Windows Win16 | 92 % | N/A | 4 code helpers plus exact 546 B autodata table | callback DS/import ABI | Win16 code xrefs and selectors |

