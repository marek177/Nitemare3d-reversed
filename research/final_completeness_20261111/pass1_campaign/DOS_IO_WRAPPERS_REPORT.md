# DOS 2.0: FAR read/write wrappery a CF/AX kontrakt

## Presné funkcie

| Vstup | Interval obrazu, koniec exclusive | B | Inštrukcie | AH pri INT 21h |
|---|---|---:|---:|---|
| 0FBA:009E | [0FC3E,0FC57) | 25 | 13 | 3Fh |
| 0FBA:00B8 | [0FC58,0FC71) | 25 | 13 | 40h |

Obe funkcie majú rovnakú lokálnu štruktúru: PUSH BP; MOV BP,SP; PUSH DS, načítanie argumentov, INT 21h, podmienené prepísanie AX, POP DS; LEAVE; RETF. Medzi rozsahmi je bajt 0FC57h; nie je súčasťou ani jednej funkcie a touto dávkou sa neklasifikuje ako padding.

Ide o tenké systémové wrappery. Nezamieňajú sa s predtým analyzovaným WORX `read_helper_312e`, ktorý má iný rozsah aj stavové správanie. Úloha read/write vyplýva z konkrétneho použitia a hodnôt AH; pôvod v konkrétnej kompilátorovej alebo externej knižnici sa iba podľa tohto vzoru nedokazuje.

## Stack, registre a výstup

Po vytvorení BP rámca sa načíta WORD handle z SS:[BP+6] do BX, FAR pointer z SS:[BP+8] cez LDS do DS:DX a WORD count z SS:[BP+0Ch] do CX. Wrapper nastaví AH na 3Fh alebo 40h a vykoná INT 21h.

```text
save BP, DS
BX = handle
DS:DX = buffer_far_pointer
CX = count
AH = 3Fh alebo 40h
INT 21h
if CF == 1: AX = FFFFh
restore DS, BP
RETF                         # argumenty odstraňuje caller
```

Pri CF=0 sa AX neprepisuje: aj nula alebo krátky počet sa vráti nezmenený. Pri CF=1 sa AX prepíše FFFFh, pôvodná chyba z AX sa stratí. CF sa lokálnou následnou vetvou/MOV/epilógom nemení. Ostatné flags zostávajú v stave po interrupte; wrapper nečíta ani nenormalizuje DF. DS a BP sa obnovia z lokálneho zásobníka. BX/CX/DX sa pred interruptom nastavia, neukladajú sa; návratové hodnoty týchto registrov a širšie vedľajšie účinky interruptu nemožno uzavrieť iba týmto telom. SI/DI nie sú explicitne zapisované wrapperom, ale ich zachovanie cez skutočný interrupt je samostatný kontrakt.

Wrapper sám nekontroluje segmentové prekročenie, maximálny count, platnosť pointera alebo handle a nevykonáva slučku na dokončenie krátkeho prenosu. V mapovom loaderi je teda samostatné porovnanie AX s 2000h rozhodujúce pre rozlíšenie plného čítania; wrapper to nezaručuje.

## Caller inventár a hranica dôkazu

`direct_far_callers.csv` obsahuje **23 byte-exact overených priamych FAR call sites** oboch wrapperov v dodanom DOS inventári, s independently decoded cieľom. Nie je to dôkaz úplnosti nepriamych callerov ani prirodzenej dosiahnuteľnosti inventára. Near aliasy alebo kód mimo inventára týmto skenom nie sú uzavreté.

Pre PASS2 je doložená hranica medzi herným loaderom a systémovým I/O wrapperom. Samotná DOS implementácia interruptu, filesystem a disk sa v tejto dávke nevykonávajú. Predchádzajúci mapový replay tieto wrappery nahrádzal celým mockom; táto dávka dopĺňa ich lokálny inštrukčný kontrakt, ale nemení pôvodný model na prirodzený DOS test.

## Controlled replay a reprodukcia

`audit_replay_dos_io_wrappers.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT` overí SHA obrazu, oba pôvodné rozsahy, každú inštrukciu a priame FAR ciele. Pre dve funkcie, dve load bázy, štyri county (0, 1, 8192, 65535), dve CF hodnoty a päť návratových AX (0, 1, 5, 8192, 65535) vykoná **160 prípadov, 0 odchýlok**.

INT 21h je explicitne zachytený a jeho výstupy sa seedia. Pred ním sa overia AH, BX, DS:DX a CX; po návrate AX/CF/DF, obnovené DS/BP, SI/DI v modeli a SP po RETF. Model ponecháva SI/DI nezmenené, takže overuje wrapperový prenos, nie skutočné zachovanie týmito interrupt službami. FAR buffer má offset FFF0h aj pri veľkom count: model sa doň neprenáša a test preto nedokazuje bezpečnosť prekročenia segmentu.

Výstupy `dos_io_wrappers_replay/`: `dos_read_wrapper.csv`, `dos_write_wrapper.csv`, `direct_far_callers.csv`, `cases.csv`, `summary.json`. Každý prípad má request count a seedované interrupt AX/CF oddelené od wrapper AX/CF. Žiadny originálny DOS/filesystem prenos nebol vykonaný.

## Pokrytie

Centrálny katalóg po pridaní oboch funkcií: **48 rozsahov, 1 691 inštrukcií / 4 028 B kódu**, 55 592 B typovaných dát. Prijaté controlled replay prípady: 7 909 plus samostatne 65 548 prefixových prípadov. Prirodzené runtime testy zostávajú 0.

NON-CODE mapa sa nemení: **54 746 B PARTIAL, 2 505 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57 295 B. Wrappery ležia mimo historických NON-CODE intervalov; ich analýza zvyšuje doloženie spotrebiteľských kontraktov, nie počet typovaných NON-CODE bajtov. Celé subsystémy zostávajú PARTIAL. Nové výsledky zatiaľ nie sú na GitHub.

## Aktualizácia 13 oblastí

Metodika nového sémantického percenta: uzavreté jednotky / úplný inventár jednotiek oblasti. Menovatele nie sú uzavreté, nové percentá sú N/A a predošlé hodnoty sú orientačné.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | wrapper vracia krátky počet bez retry | prirodzené čítanie | DOS capture |
| Dátové typy a konštanty | 95 % | N/A | handle/FAR buffer/count stack ABI | pointer bounds | caller domény |
| Tabuľky a ukazovatele | 93 % | N/A | DS:DX prenos a obnova DS | runtime segmenty | DOS stopa |
| Funkcie / ASM / CFG | 90 % | N/A | 50 B / 26 inštrukcií, 160 prípadov | interrupt kontrakt | skutočné chyby |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | I/O časovanie | prirodzené udalosti |
| DEMO a vstupy | 96 % | N/A | spoločný I/O wrapper kontrakt | DEMO parser | read caller ledger |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping | spotrebitelia flagov |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | inicializátory |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | textový lifetime | SS čítania po návrate |
| SAVE / LOAD | 92 % | N/A | read/write error AX strata, CF zachovanie | reakcie callerov | každý krátky prenos/error |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | Win I/O ABI | Win import wrappery |

## Runtime testy na vykonanie

Zachytiť vstupné parametre a flags/registers pred/po INT 21h pri reálnom čítaní a zápise. Osobitne EOF, krátky prenos, chybný handle a plný disk v izolovanom testovacom prostredí; overiť reakcie konkrétnych callerov, nie iba wrapper AX. Ak sa skúša buffer pri konci segmentu, označiť to ako syntetický experiment. DOSBox-X vykonanie zatiaľ chýba.
