# WORX — meniteľná 44-bajtová RIFF/WAVE hlavička

11. 11. 2026. Stav **PARTIAL**. Nové DEEP VERIFIED 0 B; runtime testy 0. Predchádzajúci ASCII kandidát `data` sa v tejto dávke zasadzuje do konkrétneho dátového objektu a jeho konzumentov.

## Rozsah a dôkazy

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Blok `[0x1B588,0x1B5B4)` zodpovedá CS:5998–59C4 pri CS=15BF a má 44 B. Počiatočný hash bloku: `5869e8fce27216ac7f6278e56b0e81ee92a6581fff41d17d3d8135d51be9249a`.

V pôvodných bajtoch sú markery RIFF na +0, WAVE na +8, fmt-space na +12 a data na +36. Všetky počiatočné číselné polia sú nulové, preto nejde o dôkaz platnej hrateľnej WAVE vzorky; ide o mutable blok/šablónu pred jeho naplnením.

Rozloženie je v súlade s jednoduchou RIFF/WAVE hlavičkou s 16-bajtovým fmt payloadom. Názvy zatiaľ nepoužívaných polí sú **odvodené z formátu**, nie potvrdené všetkými hernými konzumentmi. RIFF identifikátory a úloha fmt/data sú opísané v [Microsoft RIFF dokumentácii](https://learn.microsoft.com/en-us/windows/win32/xaudio2/resource-interchange-file-format--riff-); pomenovanie číselných audio polí vychádza z [WAVEFORMATEX](https://learn.microsoft.com/en-us/previous-versions/windows/desktop/ee419019%28v%3Dvs.85%29).

## Katalóg polí

| Relatívny offset | B | Typ/rola | Sila dôkazu |
|---:|---:|---|---|
| 0 | 4 | RIFF marker | počiatočné bajty |
| 4 | 4 | RIFF size DWORD LE | formátom odvodené |
| 8 | 4 | WAVE marker | počiatočné bajty |
| 12 | 4 | fmt-space marker | počiatočné bajty |
| 16 | 4 | fmt size DWORD LE | formátom odvodené |
| 20 | 2 | format tag WORD LE | formátom odvodené |
| 22 | 2 | channels WORD LE | formátom odvodené |
| 24 | 4 | samples/sec DWORD LE | názov z formátu; lokálne sa číta iba dolný WORD |
| 28 | 4 | avg bytes/sec DWORD LE | formátom odvodené |
| 32 | 2 | block align WORD LE | formátom odvodené |
| 34 | 2 | bits/sample WORD LE | formátom odvodené |
| 36 | 4 | data marker | počiatočné bajty; nie ASCIIZ |
| 40 | 4 | data size DWORD LE | dve cesty čítajú obe slová, timer cesta iba dolné |

Presné image/CS hranice, počiatočné bajty, hash a stav každého poľa sú v `wave_header/header_fields.csv`.

## Tri lokálne cesty

Skript `audit_wave_header.py` overil staršie ASM záznamy proti obrazu a každú inštrukciu nezávisle dekódoval iced-x86 1.21.0 v 16-bit režime. V troch rozsahoch bolo spolu **146 inštrukcií / 436 B**, bez medzier inventára. Hranice ostávajú kandidátske lokálne funkčné hranice; neznamenajú úplný audit všetkých vstupov.

### 15BF:3597, image 19187–1923F

Rutina používa CLI, testuje stav CS:2DCA a na aktívnej ceste volá helper36E2 a normalizáciu4630. Potom nastaví CX=44 a kopíruje z normalizovaného ES:DI do CS:5998 pomocou explicitného CLD/REP MOVSB. Toto je priamo doložený producent celého 44-bajtového bloku, vrátane markerov.

Po kópii DI označuje zdroj bezprostredne za 44-bajtovou hlavičkou. Na 191AF sa načíta **WORD** CS:59C0 (header+40), pripočíta k DI a uloží sa do CS:366C. Číta sa aj **WORD** CS:59B0 (header+24) a vykonávajú sa DIV operácie s CS:34B9. Následne sa nastavuje INT08 a časovačové porty.

Doložený lokálny rozdiel: táto cesta pri uvedenom výpočte konca používa iba low16 veľkosti dát. Neznamená to ešte, že všetky vstupy sú limitované na 64 KiB, ani že veľké vzorky spôsobujú chybu; treba uzavrieť vstupné podmienky, pointer reprezentáciu a ďalšie konzumenty.

### 15BF:5CF6, image 1B8E6–1B95F

Rutina zavolá helper4741, nastaví BX=0, volá31CA a vetví podľa CF. Nastaví cieľ CS:5998 a žiada 44 B cez helper312E. Potom skopíruje WORD CS:59C0 do CS:48DF a WORD CS:59C2 do CS:48E1, teda zachová oba 16-bitové komponenty veľkosti. Dolný WORD CS:59B0 používa ako deliteľa pri výpočte z DX:AX=000F:4240, čo je 1 000 000.

Vo viditeľnej lokálnej sekvencii medzi návratom čítania hlavičky a používaním polí nie je potvrdenie presného počtu prečítaných bajtov ani porovnanie všetkých markerov. Validáciu v helperi312E či pred volaním zatiaľ nemožno vylúčiť.

### 15BF:5D6F, image 1B95F–1B9E2

Táto cesta číta WORD ES:[DI+28h] (teda +40), pripočíta 44 do BX a volá31CA; používa tak iba dolné slovo veľkosti pri zostavení parametra celkového rozsahu. Potom opäť žiada 44 B do hlavičky a kopíruje oba WORD veľkosti do CS:48DF/48E1. Nasleduje podobný výpočet z 1 000 000 / low16 sample rate a nastavenie audio stavu.

Názvy file/memory/timer v katalógu sú pracovné identifikácie podľa lokálneho správania, nie obnovené pôvodné symboly ani dôkaz konkrétneho hardvérového backendu.

## Spresnenie kandidáta ASCII0042

Reťazcový vzor data+NUL začínal na 1B5AC. Štyri písmená tvoria marker na header+36. NUL na 1B5B0 je počiatočný nízky bajt DWORD veľkosti na header+40. Predchádzajúce tri referencie teda nesmerujú na ASCIIZ terminátor objektu data, ale na číselné pole nasledujúce po FourCC. Je to priamo doložený príklad nesprávnej hranice objektu pri samotnej heuristike printable+NUL.

## Reprodukcia a stav celej dávky

`audit_wave_header.py DECODER_DIR IMAGE INVENTORY OUT_DIR` vytvára tri pôvodné a tri nezávisle dekódované ASM CSV, 13 poľový katalóg, 8 fixných CS xrefs a JSON dôkazy. Bulk copy/read producenti sú dokumentovaní osobitne; 8 priamych xrefs nepredstavuje všetky zápisy do bloku.

Po prepočítaní spoločného katalógu má kampaň **12 lokálnych funkčných rozsahov, 450 inštrukcií / 1 120 B a 258 B dát**, všetko PARTIAL. Úplná pracovná partition má 45 intervalov a 169 982 B označených ako v tejto kampani neposúdené. Nejde o prepis historického auditu.

Aktualizovaná tabuľka všetkých 13 oblastí je v `CAMPAIGN_CATALOG_REPORT.md`. Nové percentá zostávajú N/A, pretože úplné menovatele a originálny PASS320 ledger chýbajú. Táto dávka pridáva dôkazy dátovým typom, formátom a funkciám; ostatné oblasti nemajú nový behaviorálny výsledok.

## Otvorené brány a runtime testy DOSBox-X

1. Zachytiť skutočné 44-bajtové vstupné hlavičky a bytes-read výsledky helpera312E; potvrdiť validáciu markerov, format tag, kanálov a bits/sample.
2. Porovnať cesty pri veľkosti dát FFFFh/10000h a pri sample rate s nenulovým high16. Označiť generované hraničné vstupy ako fault injection, nie dosiahnuté herné správanie.
3. Uzavrieť životnosť CS:5998 a prípadnú reentranciu so zvukovými callbackmi; kópia celej hlavičky prepisuje pôvodné markery.
4. Overiť, či pred vstupom existuje parser variabilných RIFF chunks. Lokálny pevný offset44 nie je sám osebe dôkazom všeobecnej WAVE podpory.

Žiadny z týchto runtime testov sa zatiaľ nevykonal. PE32 port sa nevykonáva.
