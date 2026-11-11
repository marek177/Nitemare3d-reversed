# DOS 2.0: výber zvukového ID, cyklus a tabuľka epizóda/level

Neskorší asset crosscheck v `PASS1_EPISODE_FILES_REPORT.md` zistil 11 levelov v reálnom MAP.1. Nominálna matica 3×10 nižšie preto nie je úplná doména: epizóda 1 / level 10 číta na 28CE2h hodnotu 13, prvý bajt nasledujúceho nominálneho riadka. Pôvodné intervaly a replay 30 kombinácií zostávajú historicky platné, ale neuzatvárajú všetkých 31 kombinácií odvodených z troch reálnych súborov.

## Hranice a vstupy

FAR vstup 083D:288C má obalový rozsah `[0AC5C,0AC98)`, 60 B. CFG od vstupu dosiahne **21 inštrukcií / 59 B**; bajt 083D:28A5 za nepodmieneným skokom nie je súčasťou dosiahnutých inštrukcií a automaticky sa neoznačuje za padding. Všetky priame vetvy zostávajú v rozsahu. Volanie 0C2B:0298 je externá závislosť so zatiaľ neuzavretým prehrávacím kontraktom.

Rutina nečíta argumenty callerovho zásobníka. Číta WORD DS:3CD6, DS:626A a DS:626C; špeciálna vetva číta a inkrementuje BYTE DS:15EA. SI sa v tele ukladá/obnovuje. DS/ES/SS sa explicitne neprepínajú; konečný ABI a vedľajšie účinky cez prehrávací callee nie sú uzavreté. AX sa pred volaním nastavuje na zero-extended vybrané ID, ale skutočný callee ho môže zmeniť; AX preto nie je doložená návratová hodnota pôvodnej rutiny.

```text
if word DS:3CD6 != 0:
    old = byte DS:15EA
    byte DS:15EA = (old + 1) mod 256
    id = byte DS:[15E6h + (old & 3)]
else:
    offset = (15BEh + 10*word DS:626A + word DS:626C) mod 65536
    id = byte DS:[offset]
call 0C2B:0298(zero_extend(id))
```

V špeciálnej vetve sa pôvodne nastaví iba BL, ale následné `AND BX,3` vymaže aj BH. Výber teda nezávisí od vstupnej hornej polovice BX. Počítadlo sa zvyšuje pred čítaním tabuľky, index však vzniká zo starej hodnoty. Hodnota FFh sa zmení na 00h, pričom vyberie štvrtý prvok.

## Presné dátové polia

| Pole | Obrazový interval, koniec exclusive | B | Obsah |
|---|---|---:|---|
| Nominálna matica výberu | [28CD8,28CF6) | 30 | tri riadky po 10 BYTE |
| Špeciálny cyklus DS:15E6 | [28CF6,28CFA) | 4 | 13, 8, 15, 1 desiatkovo |
| Počítadlo DS:15EA | [28CFA,28CFB) | 1 | počiatočne 0, mutable BYTE |

Riadky nominálnej matice, desiatkovo:

```text
episode 1, level 0..9: 11 10  8 4 5 6 7 8 12 11
episode 2, level 0..9: 13  2  3 4 5 6 7 8 10 11
episode 3, level 0..9: 15  2  3 4 5 6 7 8 10 11
```

Pozor na biased základňu: DS:15BE zodpovedá obrazu 28CCEh a leží v predchádzajúcom texte, nie na prvom riadku číselnej matice. Až pri epizóde 1 sa pripočíta 10. **Podmienky epizóda 1..3 a level 0..9 sú explicitný nominálny model tejto tabuľky, nie v tejto dávke uzavretá invariantná doména hry.** Telo nemá guard týchto hraníc. Napríklad epizóda 0 by čítala predchádzajúci text; to je dôsledok adresového výrazu, nie dôkaz, že tak hra prirodzene postupuje. Význam režimu DS:3CD6 ani všetky LOAD/inicializačné vetvy sa neuzatvárajú len podľa tejto podobnosti.

## Controlled replay a reprodukcia

`audit_replay_pass1_music_selector.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT` overí kanonický SHA, každú dosiahnutú inštrukciu a nominatívne polia. V každej z load báz 0 a 1000h vykoná 256 hodnôt špeciálneho počítadla a 30 nominálnych kombinácií epizóda/level, spolu **572 prípadov, 0 odchýlok**. Aplikuje reálne EXEPACK relokácie vrátane FAR call segmentu.

Závislosť 0C2B:0298 sa v emulačnej kópii nahradí jedným RETF. Hook pozoruje skutočný WORD argument na zásobníku. Testuje sa výber, inkrement, odovzdanie argumentu, lokálny stack a SI; nič z toho neoveruje samotné prehrávanie, časovanie, hardvér ani callee ABI. Druhá load báza spočiatku odhalila chýbajúce aplikovanie relokácií v testovacom prípravku; výsledný skript ich aplikuje a neúspešný pokus sa nepočíta medzi prijaté prípady.

Strojové artefakty v `pass1_music_selector/`: `instructions.csv`, `data_fields.csv`, `cases.csv`, `summary.json`, aktuálna CSV/JSON mapa a nezávislá kontrola partition. Dátové rozsahy majú SHA-256. Celý kód a dáta zostávajú PARTIAL; prirodzený runtime sa nevykonal.

Promócia z mapy `pass1_direction_fields` pridala **35 B z CLASSIFIED ONLY do PARTIAL**. Nová mapa: **54 673 B PARTIAL, 2 578 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57 295 B. Nezávislá kontrola 649 intervalov potvrdila SHA a presné členstvo bez dier alebo prekryvov.

Centrálny katalóg po pridaní rutiny: 43 funkčných rozsahov, 1 471 inštrukcií / 3 413 B kódu, 55 519 B typovaných dát celého obrazu. V historickom NON-CODE je typovaných 54 671 B; 2 PARTIAL relokačné B zostávajú bez uzavretej roly. Prijaté controlled replay prípady: 6 663; navyše samostatne 65 548 prípadov normalizačného prefixu. Prirodzené runtime testy 0. Dávka zatiaľ nie je na GitHub.

## Aktualizácia 13 oblastí

Metodika nového sémantického percenta: uzavreté jednotky / úplný inventár jednotiek oblasti. Menovatele nie sú uzavreté, preto nové percentá zostávajú N/A. Predošlé percentá sú orientačné; nové výsledky sú PARTIAL.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | podmienené indexovanie epizóda/level | prirodzené domény | inicializácia a LOAD |
| Dátové typy a konštanty | 95 % | N/A | 35 B / 3 polia | všetci writeri | counter watchpoint |
| Tabuľky a ukazovatele | 93 % | N/A | biased základňa a cyklus 4 | nepriame referencie | odvodené adresy |
| Funkcie / ASM / CFG | 90 % | N/A | 21 inštrukcií, 572 replay | callee 0298 | prehrávacia rutina |
| RNG | 97 % | N/A | výber špeciálnej vetvy je cyklus | iné zvukové výbery | ďalší caller inventár |
| Scheduler | 96 % | N/A | bez nového dôkazu | poradie udalostí | tick spotrebitelia |
| DEMO a vstupy | 96 % | N/A | režimový prepínač DS:3CD6 | význam režimu | jeho writeri |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping | spotrebitelia flagov |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | inicializátory |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | textový lifetime | SS čítania po návrate |
| SAVE / LOAD | 92 % | N/A | identifikované stavové vstupy | obnovenie počítadla a režimu | serializované rozsahy |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | ekvivalent výberu | Win xrefs |

## Runtime testy na vykonanie

Pri prirodzených prechodoch levelu zachytiť DS:3CD6/626A/626C, DS:15EA a argument 0C2B:0298. Overiť, či herné čísla epizód a levelov skutočne zodpovedajú nominálnej matici. Zaznamenať writerov režimu a počítadla vrátane SAVE/LOAD. Prehrávací callee spustiť bez náhrady až v riadnom DOS prostredí a sledovať konkrétny zdroj/kanál zvuku. Vykonanie týchto prirodzených testov zatiaľ chýba.
