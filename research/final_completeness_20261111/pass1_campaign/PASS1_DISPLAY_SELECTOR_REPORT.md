# PASS1: demo a pentagramové zobrazovacie texty

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Päť FAR pointerov a päť textov má spolu **136 B**, status PARTIAL. Ich segmenty sú počiatočne 2771h so skutočnými EXEPACK relokáciami.

## Konkrétne cesty

Demo vetva A429..A440 pri nenulovom WORD DS:3CD6 kopíruje WORD DS:1378 do AX a DS:137A do DX, potom ich uloží do DS:3CD8/3CDA. Počiatočný text je `Nitemare-3D -- Demo Mode`.

Selector A47E..A498 číta BYTE položky +3, vykoná unsigned guard **2 <= value <= 5**, zero-extenduje BL, násobí BX štyrmi a číta DWORD **SS:[BX+0E16]**. To presne vyberá štyri počiatočné bunky **SS:0E1E,0E22,0E26,0E2A**, uložené pri počiatočnej SS báze 2771h. Ich texty sú `Pentagram of Good Health`, `Pentagram of Power`, `Pentagram of Good Sight`, `Pentagram of Knowledge`. Výsledok uloží cez explicitný SS override do SS:3CD8.

Na 8D3F..8D5E spotrebiteľ testuje oba WORDy DS:3CD8/3CDA proti nule, pri nenulovom vloží DWORD a volá renderer **0D29:03E0**. Tým je doložený vzťah statických pointerov k runtime zobrazovaciemu slotu. Ten leží pri default báze na obraze **2B3E8**, mimo súboru a NON-CODE menovateľa; nepripočítava sa ako ďalšie file-backed dáta.

**Segmentové podmienky:** selector používa SS, demo vetva a renderer DS. Rovnosť počiatočných DS/SS zo startup dôkazu nestačí na globálny dôkaz ich rovnosti pri každom prirodzenom volaní. Táto otázka zostáva otvorená. Guard presne obmedzuje lokálne čítanú hodnotu, ale neuzatvára pôvod pointera položky, prirodzenú dosiahnuteľnosť ani herné účinky pentagramov. Text Knowledge napríklad sám nedokazuje algoritmus odhalenia mapy.

## Reprodukcia a metriky

`audit_pass1_display_selector.py IMAGE DECODER_DIR OUT` používa `relocations.csv` vedľa IMAGE. Overuje SHA, všetky pointery/texty a relokácie, guard/SHL/SS read, runtime pointer zápisy a render call. Nezávisle dekóduje tri okná. `promote_pass1_fields.py` používa predchádzajúcu mapu `pass1_branched_texts/noncode_intervals.csv`. Výstupy sú v `pass1_display_selector/`.

Zo 136 B bolo 10 segmentových bajtov už PARTIAL. Nových **126 B** pochádza z CLASSIFIED ONLY. Aktuálne **PARTIAL 50 643 B, CLASSIFIED ONLY 6 608 B, UNKNOWN 44 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Predošlá mapa: 50 517 / 6 734 / 44 / 0 B. Netypované relokačné PARTIAL bajty klesli z 12 na **2 B**, jediný neuzavretý segmentový WORD slotu DS:2356. Jeho podobnosť so susednými hookmi nenahrádza spotrebiteľa. Nový prirodzený runtime ani replay sa nevykonal.

DOSBox-X plán: prirodzené SS/DS, value 2..5, zobrazovací slot pred/po zápise a text na render call. Ďalší krok: zostávajúci CRT slot a CLASSIFIED ONLY dáta, potom sémantické field/writer closure veľkých PARTIAL objektov.


## Aktualizácia 13 oblastí

Nové sémantické percento je všade N/A: úplný inventár kontraktov/polí/vetiev chýba. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické percentá sú orientačné odhady.

| Oblasť | Predošlý odhad | Nové % | Potvrdenie | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | opravená mapa a flagy | prirodzené súbory | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 208 polí/35 zdrojov; display selector | 2 relokačné B bez typu | roly segmentov |
| Tabuľky a ukazovatele | 93 % | N/A | guarded SS selector and display slot consumer | writeri/lifetime | pointer watchpointy |
| Funkcie / ASM / CFG | 90 % | N/A | 34 rozsahov, 1 150 inštrukcií | kontrakty/dosiahnuteľnosť | caller stopy |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | staršie PIT dôkazy zachované | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová DEMO stopa |
| Renderer / VGA | 94 % | N/A | bit reversal začlenený | clipping/orientácia | payload spotrebiteľ |
| GUARD / bossovia | 93 % | N/A | nominálne pole 100×26 | AI/lifecycle | inicializátory |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie/sloty | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | 60 počiatočných UI textov | textový lifetime | SS čítania po návrate |
| SAVE / LOAD | 92 % | N/A | mapové/flagové rozsahy | LOAD parity | párový stav |
| Windows Win16 | 92 % | N/A | staršie NE dôkazy zachované | callback DS/import ABI | runtime selektory |

