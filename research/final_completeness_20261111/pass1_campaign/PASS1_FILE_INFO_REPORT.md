# PASS1: CRT file-info prefix a uložený interrupt vector

Dávka typuje **18 B v dvoch poliach** a vykonáva pôvodný lokálny dekódovací úsek file-info príznakov. Úroveň PARTIAL: celé environment scan/copy, encoder, DOS vektory a prirodzený startup zostávajú otvorené. Žiadny skutočný interrupt vector sa nemení.

## Vstupy a adresy

Image SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; inventár SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`. Skript overí identity, presné bajty polí aj všetky zachované kontextové inštrukcie nezávislým dekóderom. Kanonické dáta mapuje cez DS=2771h.

| Pole | Image interval, koniec exclusive | Typ / dôkaz |
|---|---|---|
| DS:20FC | [2980C,2981A) | NUL ASCII `_C_FILE_INFO=`: 13 payload BYTE + NUL |
| DS:210A | [2981A,2981E) | mutable FAR16 pointer initial0:0: uloženie BX/ES a neskoršie LDS DX |

Samostatný WORD pred prefixom a zvyšné nulové susedstvá sa touto dávkou nepretypujú. Uložený FAR pointer patrí inému účelu než environment prefix, hoci sú susedné.

## Prefix a príznaky súborov

11EE:017F nastaví CX=13 a SI=20FC, potom porovná prefix s environment textom cez REPE CMPSB. Pri zhode sa prepne zdrojový DS a cieľový ES, nastaví sa SI na suffix za prefixom a DI=212Ah. Pôvodné príznakové BYTE sa dekódujú po dvojiciach znakov.

```text
while true:
    high = next_byte() - 'A'
    if unsigned_borrow: stop
    high = (high << 4) & FF
    low = next_byte() - 'A'
    if unsigned_borrow: stop
    BYTE ES:[DI++] = high | low
DS = SS
```

Pre normálne znaky A..P ide o high/low nibble kódovanie všetkých 256 BYTE hodnôt. Parser však nemá horný test P; `QA` vytvorí0, `AZ`25 a iné vyššie znaky môžu vytvárať nekanonické hodnoty. Pri nedokončenej dvojici sa neuloží jej BYTE. V samotnom úseku nie je count limit výstupu. Tieto syntetické vstupy nie sú dôkazom prirodzene vytvoreného poškodeného prostredia ani konkrétneho herného exploitu.

Statický encoder kontext3355..339B kopíruje rovnaký prefix a číta BYTE príznaky z212A; vysoký/nízky nibble prevádza do A-based znakov. Ďalší environment-copy kontext04EF..0518 rozpoznáva špeciálny prefix a upravuje vektorové zaradenie. Celé tieto funkcie sa tu nevykonávajú; presné bajty sú v `instruction_contexts.csv`.

## Uložený vector0

11EE:0122 nastaví AX=3500h a zavolá INT21. Následne uloží BX do210A a ES do210C. Restore kontext027F používa LDS DX,[210A], AX=2500h a INT21, potom obnoví DS. To identifikuje FAR segment:offset uloženého DOS vector0 kontextu. Skutočné OS odpovede a celý lifecycle sa nevykonávajú; dátový typ stojí aj na explicitnom FAR LDS operande.

## Reprodukcia a výsledky

`audit_replay_pass1_file_info.py IMAGE INVENTORY DECODER EMULATOR OUT` vytvára data fields, kontexty, `decode_prefix.csv`, cases a summary. Pôvodný prefix **11EE:0194..01B3, image [12074,12093)** má31 B/20 inštrukcií. Replay začína po nájdení prefixu, s explicitným suffixom, DF=0 a SS=DGROUP. Nevykonáva environment scan, DOS INT alebo callback. Úsek nemá segmentové relokačné operandy; CS/segmenty sa pri load0/1000h nastavia explicitne.

**530 prípadov,0 odchýlok** = 2 load bázy × (256 samostatných kódovaní + jeden vektor všetkých256 BYTE +8 nekanonických/ukončovacích scenárov). Overuje sa celý dekódovaný rozsah, dva nezmenené guard BYTE, DS=ES=DGROUP a SP. Test256 výstupov dokazuje len vykonanie seedovaného úseku bez lokálneho limitu; nepovažuje sa za prirodzený počet handles. SHA cases `69bc983640ce12655906be468fce7895fefaf9f73fdf9049d0451bf6dcc5b830`.

## Meranie

18 B CLASSIFIED ONLY → PARTIAL. Mapa: **56911 B PARTIAL,340 B CLASSIFIED ONLY,44 B UNKNOWN,0 B DEEP VERIFIED**, spolu57295 B. Nezávislá kontrola overila856 intervalov,SHA a presné členstvo bez dier/prekryvov. SHA mapy `55c48f88f63912789f25836a8e6101b9c35e439e6eb096018511ee4e25d3b64a`. Partition integrita nie je dôkaz sémantickej úplnosti.

Bounded katalóg zostáva98 funkčných rozsahov,3502 inštrukcií/8773 B; prefix sa nepočíta ako celá funkcia. Typované dáta celého obrazu57797 B; historického NON-CODE56909 B a2 PARTIAL netypované relokačné bajty. Controlled replay777613 plus osobitne65548 smerových prefixových prípadov. Prirodzené runtime testy0. GitHub snímka52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového %: uzavreté jednotky/úplný inventár oblasti. Menovatele chýbajú, nové percentá N/A,predošlé orientačné. Byte codec testy nenahrádzajú celý startup alebo DOS I/O.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|A..P nibble kódovanie|celý encoder/scan|startup env closure|
| Dátové typy a konštanty |95 %|N/A|18 B/2 polia|nulové susedstvá|zvyšné intervaly|
| Tabuľky a ukazovatele |93 %|N/A|FAR vector0 pointer|skutočné OS hodnoty|runtime vector trace|
| Funkcie / ASM / CFG |90 %|N/A|31 B/20 prefixových inštrukcií|celý startup|0194 call kontext|
| RNG |97 %|N/A|bez nového dôkazu|ordering|DEMO trace|
| Scheduler |96 %|N/A|runtime vector stav oddelený|prirodzené callery|call graph|
| DEMO a vstupy |96 %|N/A|environment input odlíšený|driver ABI|input closure|
| Renderer / VGA |94 %|N/A|bez nového dôkazu|init režimu|VGA setup|
| GUARD / bossovia |93 %|N/A|bez nového dôkazu|lifecycle|health updater|
| Zbrane / projektily |92 %|N/A|bez nového dôkazu|effect producer|damage caller|
| Sprity / HUD / paleta |92 %|N/A|bez nového dôkazu|identity|descriptor producer|
| SAVE / LOAD |92 %|N/A|CRT file príznaky oddelené|herné použitie|wrapper closure|
| Windows Win16 |92 %|N/A|bez nového Win dôkazu|CRT env parity|Win helper match|

## Runtime testy na vykonanie

Zachytiť pôvodné prostredie a príznaky212A pred/po decode, overiť skutočný count limit z okolitého procesu. Encoder a vektorové vynechanie overiť samostatne. Vector0 save/restore sledovať v izolovanom DOS behu až po prirodzené ukončenie. Hostiteľské prostredie ani vektory nemení tento audit. DOSBox-X vykonanie a Win16 parity zostávajú otvorené.
