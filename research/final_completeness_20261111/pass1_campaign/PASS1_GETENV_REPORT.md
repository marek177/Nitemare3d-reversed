# PASS1: CRT argumentové polia a pôvodný getenv

Dávka typuje 6 B a rekonštruuje tri FAR rutiny s near dátovými argumentmi. Pridáva aj priame prepojenie pôvodného environment lookupu na už analyzovaný TZ parser bez mockov. Úroveň PARTIAL: DOS startup konštrukcia prostredia a prirodzené environment dáta zostávajú otvorené.

## Vstupy a presné hranice

Image SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; inventár SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`. Skript pripína identity, porovnáva pôvodné bajty každého štartu a nezávisle dekóduje CFG.

| Pole pri DS=2771h | Image interval, koniec exclusive | Typ / dôkaz |
|---|---|---|
| DS:213E | [2984E,29850) | mutable WORD initial 0, argument count role; zápis DI v 03D1, push pred main call |
| DS:2140 | [29850,29852) | mutable NEAR16 pointer initial 0, argv-like vektor; zápis SP-derived AX v 03E4, push pred main |
| DS:2142 | [29852,29854) | mutable NEAR16 pointer initial 0, null-terminated near environment vector; zápis 04DC a iterácia v getenv |

Startup kontext v `startup_contexts.csv` ukazuje SS→DS pred argumentovou konštrukciou a odovzdanie 2142/2140/213E pred FAR main-like call 0476:0326. Ide o lokálne statické doloženie rolí, nie vykonanie celého startup parsera alebo uzavretie argc/argv edge cases. Environment near-pointer typ je navyše priamo spotrebovaný pôvodným getenv.

| Funkcia | Image interval | CFG |
|---|---|---:|
| 11EE:2398 strlen-near | [14278,14293) | 27 B / 15 inštrukcií |
| 11EE:23DC strncmp-near | [142BC,142F6) | 58 B / 32 inštrukcií |
| 11EE:248A getenv-near | [1436A,143CA) | 95 B / 42 inštrukcií |

Getenv span má 96 B, jeden bajt mimo CFG sa nepočíta. Spolu 180 B / 89 inštrukcií. Všetky majú FAR návrat s caller argument cleanup. Near suffix označuje dátové pointery, nie NEAR return. Getenv zachováva BP/SI/DI/DS v modeli, vracia AX near hodnotový pointer alebo 0. Helpers používajú ES=DS; pôvodné ES sa neobnovuje. DF=0 je predpoklad, nie lokálne nastavenie týchto tiel.

## Algoritmus getenv

```text
vector = WORD DS:[2142]
if vector == 0 or key_near == 0: return 0
n = strlen(key_near)
while WORD DS:[vector] != 0:
    entry = WORD DS:[vector]
    if strlen(entry) > n and BYTE DS:[entry+n] == '=':
        if strncmp(entry,key_near,n) == 0:
            return (entry+n+1) & FFFF
    vector = (vector+2) & FFFF
return 0
```

Vyhľadávanie je case-sensitive, prvá zhoda vyhráva. `TZ=` vracia nenulový pointer na koncový NUL, zatiaľ čo chýbajúce TZ vracia 0. Záznam `TZ` bez rovná sa sa odmietne. Prázdny key môže nájsť záznam začínajúci `=`. Key obsahujúci `=` sa automaticky neodmietne: napríklad key `A=B` nájde entry `A=B=V`. Tieto výsledky opisujú konkrétnu implementáciu, nie požiadavky moderného hostiteľského getenv.

Strlen používa REPNE SCASB s CX=FFFF. Strncmp najprv obmedzene hľadá NUL v prvom argumente, potom REPE CMPSB a vytvorí výsledok z unsigned BYTE porovnania. V tejto dávke sa cez getenv potvrdzuje najmä rovnosť/nerovnosť; úplná všetkých string/count doména a orientácia všetkých nenulových výsledkov zostávajú otvorené. Neplatné alebo neukončené near pointery sa netestujú.

## Reprodukcia a native TZ prepojenie

`audit_replay_pass1_getenv.py IMAGE INVENTORY DECODER EMULATOR OUT` vytvára tri ASM CSV, startup kontexty, `data_fields.csv`, `cases.csv`, `summary.json`. Pri load 0/1000h aplikuje reálne EXEPACK relokácie. Environment vector aj NUL ASCII/BYTE stringy sú explicitne seedované v DS; hostiteľské prostredie sa nečíta ani nemení. **Žiadne telo sa nenahrádza hookom alebo RET stubom.**

**320 prípadov, 0 odchýlok** = 308 getenv prípadov (2 load bázy × 11 tabuliek × 14 query hodnôt) + 12 TZ integration prípadov. Zahrnuté sú null vector, prázdny vector, null/prázdny key, prázdne hodnoty, duplicity, case rozdiely, chýbajúce `=`, embedded `=` a high BYTE 80h. Kontroluje sa presný near pointer, nie iba textová zhoda.

TZ integrácia vykonáva originálny parser 2C06, getenv, strlen, strncmp, copy, atol a multiply z reálneho obrazu. Pre absent TZ, inú premennú, prázdne TZ a lowercase `tz` zostanú (28800,1); `TZ=ABC3DEF` dá (10800,68), `TZ=XYZ-5GHI` dá (−18000,71). Táto dávka odstraňuje mockovanú lookup medzeru pre týchto šesť scenárov, ale nepreukazuje pôvodný DOS environment block, všetky TZ formáty alebo prirodzené použitie hry. Starších 250 mock-getenv TZ prípadov sa nevyhlasuje spätne za native lookup testy.

SHA cases `a5e3ab1a3a37bc082820ab9510106fc2eb9a2db1fc36a80da0d2bba166b9fd0a`. Opakovanie behu po doplnení startup kontextov sa do súčtu nezapočítava druhýkrát.

## Meranie

Presne 6 B CLASSIFIED ONLY → PARTIAL. Mapa: **55250 B PARTIAL, 2001 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57295 B. Nezávislá kontrola overila 760 intervalov, SHA a presné členstvo bez dier/prekryvov. SHA mapy `f5317788f93a607f99498a07c7db1a7364b4f18c49b9544e7d8804b01566d7f0`. Partition integrita nie je dôkaz úplnej sémantiky.

Katalóg: 89 funkčných rozsahov, 3135 inštrukcií / 7802 B, 56136 B typovaných dát celého obrazu; 55248 B historických NON-CODE dát a 2 netypované PARTIAL relokačné bajty. Controlled replay 614175 plus osobitne 65548 smerových prefixových prípadov. Prirodzené runtime testy 0. GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového %: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, nové percentá N/A, predošlé orientačné. Replay počty nie sú sémantické percentá.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | near env vector spotreba | DOS block konštrukcia | startup env parser |
| Dátové typy a konštanty | 95 % | N/A | 6 B / 3 WORD polia | argc/argv edge cases | startup closure |
| Tabuľky a ukazovatele | 93 % | N/A | near pointer list po 2 B | neplatné pointery | allocator kontext |
| Funkcie / ASM / CFG | 90 % | N/A | 180 B / 89 inštrukcií | helper úplné domény | strncmp boundaries |
| RNG | 97 % | N/A | bez nového dôkazu | ordering | DEMO trace |
| Scheduler | 96 % | N/A | native TZ lookup prepojenie | herné použitie času | caller graph |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | driver ABI | input closure |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | init režimu | VGA setup |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | health updater |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | effect producer | damage caller |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | identity | descriptor producer |
| SAVE / LOAD | 92 % | N/A | CRT environment oddelený | persistencia | SAVE ledger |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | getenv parity | Win CRT helper |

## Runtime testy na vykonanie

Zachytiť DS/SS, 213E/2140/2142 a výsledný near vector po pôvodnom startup parsovaní. Overiť reálne getenv query hry a prirodzené TZ caller scenáre bez zmeny hostiteľského prostredia. Skontrolovať startup DF a platnosť near pointerov. DOSBox-X vykonanie a Win16 parity zostávajú otvorené.
