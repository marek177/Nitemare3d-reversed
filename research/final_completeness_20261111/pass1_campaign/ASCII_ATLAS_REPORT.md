# NON-CODE príprava — ASCII vzory a konflikty so stavovými dátami

11. 11. 2026. Táto dávka spracovala celý SHA-pinned obraz 171 360 B. Nejde o obnovu pôvodného PASS320 ledgeru. **Nové DEEP VERIFIED 0 B, runtime testy 0.**

## Výsledky a presná metodika

`build_ascii_candidate_atlas.py DECODER_DIR IMAGE INVENTORY OUT_DIR` bol vykonaný. Obraz: SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; historický inventár: SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`.

Vzor je maximálny beh aspoň 4 tlačiteľných ASCII bajtov 20h–7Eh bezprostredne nasledovaný NUL. Hranice a dĺžky zahŕňajú terminátor. Vyhľadanie bolo vykonané nad celým obrazom, preto je census úplný **pre toto pravidlo**, nie pre všetky skutočné reťazce: chýbajú krátke, neterminované, dĺžkovo označené, ne-ASCII a dynamické reťazce.

| Metrika | Výsledok |
|---|---:|
| Kandidátske vzory | 370 |
| Ich bajty vrátane NUL | 5 864 |
| Vzory bez prieniku so starým inštrukčným inventárom | 332 |
| Vzory s prienikom | 38 |
| Fixné CS memory referencie do vzorov | 14 |
| Historické inštrukčné záznamy overené iced-x86 | 35 648 |
| Nezhody bajtov / segmentového mapovania / hraníc | 0 |
| Únia ich inštrukčných bajtov | 92 972 |

92 972 nie je počet sémanticky overených bajtov ani dokázaných vykonateľných bajtov. Starý inventár môže mať nesprávne zvolené korene či hranice medzi kódom a dátami, aj keď každá zaznamenaná sekvencia je platnou inštrukciou. Overenie znamená iba zhodu bajtov, CS*16+IP a nezávisle dekódovanej dĺžky/platnosti. Doteraz lokálne analyzovaný kampanový katalóg preto naďalej vykazuje len 684 B inštrukcií a 214 B dát, všetko PARTIAL.

## Nové doložené nezrovnalosti

Priame xrefs vyžadujú explicitný CS segment bez base/index registra v nezávisle dekódovanej memory operande. Referencia môže smerovať dovnútra vzoru, vrátane jeho NUL; neznamená to použitie celého vzoru ako reťazca.

### ASCII0038: placeholder a príznak

Vzor `[0x187C9,0x187FD)` obsahuje 51 znakov X a NUL. Zodpovedá CS:2BD9 až 2C0D exclusive. Posledný bajt CS:2C0C je súčasne režimový príznak: kód na 18A66 doň zapisuje 1, na 18A81 zapisuje 0 a ďalšie vetvy ho testujú.

To priamo potvrdzuje, že terminátor počiatočného ASCII vzoru nemožno považovať za nemenný text. Samotných 51 X je počiatočný vzor v oblasti používanej counted-string konvertorom; účel placeholdera a deklarovaná kapacita bufferu ešte nie sú uzavreté.

### ASCII0039: copyright a chybové slovo

Vzor `[0x187FD,0x18838)` obsahuje počiatočný text `WORX TOOLKIT VERSION 2.1 COPYRIGHT 1993 BY MYSTIC SOFTWARE` a NUL. Terminátor je na CS:2C47 = image 18837. Word na CS:2C47 je pritom meniteľný error-state kandidát: 18E2C/18E44/18F16/18F33 doň zapisujú výsledok AX po DOS vetvách; 18C7E ho číta a 18C82 nuluje.

Word zasahuje terminátor vzoru a aj nasledujúci bajt mimo neho. Počiatočný copyright text je prečítateľný fakt obrazu, ale celý rozsah vrátane terminátora nesmie byť označený za nemenný ASCIIZ objekt. Toto je dôkaz potreby rozdelenia dátových intervalov podľa producentov/konzumentov.

### ASCII0042: vzor data a susedné word prístupy

Vzor `[0x1B5AC,0x1B5B1)` je `data` + NUL. Tri fixné word čítania na 191AF,1B8FC,1B97E smerujú na CS:59C0 = image 1B5B0, teda na posledný NUL a ďalší bajt mimo vzoru. Žiadna z týchto troch referencií sama osebe nepotvrdzuje spracovanie slova data ako reťazca alebo chunk identifikátora. Význam čítaného word je zatiaľ UNKNOWN.

## Artefakty a klasifikácia

- `ascii_atlas/ascii_candidates.csv`: 370 rozsahov, presné hranice, text, hash, počet prekrývajúcich sa bajtov inventára. Status CLASSIFIED_ONLY znamená **identifikovaný bajtový vzor**, nie potvrdený dátový typ.
- `ascii_atlas/fixed_cs_references.csv`: 14 nezávisle dekódovaných memory referencií vrátane presného offsetu v kandidátovi a obmedzenia rozsahu vyhľadávania.
- `ascii_atlas/decoder_conflicts.csv`: prázdna tabuľka s hlavičkou; všetkých 35 648 dodaných záznamov prešlo úzkou kontrolou.
- `ascii_atlas/summary.json` a reprodukovateľný skript zaznamenávajú pravidlo a súčty.

DS/ES dynamické referencie, MOV immediate adresy, FAR pointer aliasy a nepriame konzumenty ešte nie sú uzavreté. 332 vzorov bez konfliktu so starým inventárom preto zostáva frontou na analýzu, nie novým sémantickým pokrytím.

## Hľadanie pôvodného ledgeru

Dokončené vyhľadávanie názvov PASS320/PASS321 a byte-range/coverage artefaktov v Dokumenty/Codex a v `L:\4k Downloads` nedohľadalo originálny 1 488-intervalový ledger. Našli sa staršie katalógy a iné coverage súbory; ich názov ani počet položiek nepreukazuje identitu PASS320. Súbory v archívoch neboli týmto názvovým vyhľadávaním obsahovo vylúčené. Predchádzajúce knižničné vyhľadávanie malo neúplnú indexáciu ZIP, preto sa absencia originálu netvrdí.

## Aktualizácia 13 oblastí

Nové percentá sú všade N/A. Výpočet až po autentifikovanom inventári menovateľa: uzavreté sémantické jednotky / všetky jednotky príslušnej oblasti. Pattern census sa nesmie použiť ako sémantický čitateľ ani deliť počtom 57 295 bez známeho prieniku PASS320.

| Oblasť | Historicky | Nové potvrdenie | Neznáme/blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|
| Mapy/formáty | 99 % | žiadny nový formát uzavretý | vzor data bez konzumenta | analyzovať 3 word čítania |
| Typy/konštanty | 95 % | 370 vzorov CLASSIFIED_ONLY; meniteľné terminátory | hranice objektov a lifetime | rozdeliť ASCII0038/39 podľa xrefs |
| Tabuľky/ukazovatele | 93 % | 14 fixných CS xrefs | DS/ES aliasy a pointery | segmentový dataflow |
| Funkcie/ASM/CFG | 90 % | 35 648 boundary-valid záznamov | dosiahnuteľnosť a sémantika | konkrétne konzumenty dát |
| RNG | 97 % | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | bez nového dôkazu | tick ordering | dispatcher CFG |
| DEMO/vstupy | 96 % | bez nového dôkazu | determinizmus | párové prehratie |
| Renderer/VGA | 94 % | bez nového dôkazu | clipping/VGA stav | framebuffer + DAC |
| GUARD/bossovia | 93 % | bez nového dôkazu | prechody | stavové hrany |
| Zbrane/projektily | 92 % | bez nového dôkazu | lifecycle | collision trace |
| Sprity/HUD/paleta | 92 % | bez nového dôkazu | resource binding | draw xrefs |
| SAVE/LOAD | 92 % | bez nového dôkazu | cache po LOAD | serializácia |
| Win16 | 92 % | bez nového dôkazu | NE fixupy | identita segmentov |

## Runtime testy

Watchpointy na CS:2C0C a CS:2C47/48, zachytenie pred/po startup inicializácii a po chybách DOS služieb. Pre data vzor zaznamenať word na CS:59C0 pri všetkých troch konzumentoch. Tieto testy nie sú vykonané; umožnia odlíšiť počiatočnú reprezentáciu od živej hodnoty. PE32 port sa nevykonáva.
