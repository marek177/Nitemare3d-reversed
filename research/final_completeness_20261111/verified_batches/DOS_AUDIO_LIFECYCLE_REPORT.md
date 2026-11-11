# DOS 2.0 — audio lifecycle a portový helper

11. 11. 2026. **PARTIAL**, runtime testy0, DEEP VERIFIED0 B. Nové dôkazy odlišujú volanie inicializácie knižnice od volania jej INT63 servisov.

## Hranice a callerovia

| Kandidát | Image end-exclusive | Inštrukcie / B | Priame encoded callsites v inventári |
|---|---|---:|---:|
| audio_install | 18A6D..18B0B | 83 /158 | 1 |
| audio_uninstall | 18B56..18BBF | 58 /105 | 1 |
| port388_write | 19497..194C2 | 24 /43 | 35 |

Názvy sú analytické, nie pôvodné symboly. Caller inicializácie je image11A6A: FAR CALL15BF:2E7D; caller ukončenia image10C6C: FAR CALL15BF:2F66. Tieto priame hrany sú bajtovo potvrdené, ale ich prirodzená runtime dosiahnuteľnosť nie je tým uzavretá. Katalóg35 helper callerov je viazaný na prevzatý inventár, nie globálny dôkaz úplnosti.

## Inicializácia a ukončenie

Inicializačný kandidát ukladá AX,BX,CX,DX,BP,DI,SI,DS,ES, nastaví DS=CS, CLI a CLD. Nuluje CS:201E a CS:2C0C. Uloží a nainštaluje vektor63h podľa predchádzajúcej dávky. Do FAR pointera CS:3EE1 uloží offset40E1h a CS; jeho ďalší kontrakt ostáva otvorený.

Po portovej slučke uloží pôvodný vektor08h do CS:000A/000C a nastaví nový handlerCS:4150. Nasleduje AX=0952h, callCS:466A a zápis0952h do CS:2C49. Význam helpera466A sa v tejto dávke nepomenúva. Koniec symetricky obnoví uložené registre, vykoná STI a RETF. IF sa teda lokálne bezpodmienečne povoľuje, neobnovuje zo vstupných FLAGS; DF na konci závisí aj od helperov/callbackov.

Ukončenie začína CLD/CLI, uloží rovnaké registre, DS=CS a volá lokálne helpery4741,3E77,37C4,3E67,335B. Ich vnútorné kontrakty zostávajú otvorené. Obnoví vektory08h aj63h. Ak CS:21C6 nie je FFFFh, zavolá uložený XMS entry s AH=0Ah a DX=handle; výsledok AX lokálne nevyhodnotí. Obnoví registre, STI, RETF. Životnosť handle po návrate a vylúčenie opakovanej deinicializácie nie sú uzavreté.

## Portový kontrakt a slučka

Helper19497 ukladá AX,BX,CX,DX. Nastaví DX=0388h a vykoná OUT DX,AL; nasleduje6 iterácií IN AL,DX. Potom DX zvýši na0389h, vymení AH/AL a vykoná OUT DX,AL. Nasleduje35 iterácií po dvoch IN, teda70 čítaní dátového portu. Pred návratom obnoví DX,CX,BX,AX.

**Obnova registrov je pred voliteľným callbackom.** Po nej testuje CS:3898, pri nenule FAR CALLCS:[3896], až potom RET. Bez callbacku zachová AX/BX/CX/DX; s callbackom závisia konečné hodnoty od jeho neuzavretého ABI. FLAGS nezachováva. Toto sú potvrdené portové operácie; správnosť časovania na konkrétnom zvukovom zariadení nie je runtime overená.

Inicializačná slučka začína AX=0, volá helper, inkrementuje **AH** a opakuje pri AH!=0. Ak callback nie je aktívny alebo zachová AX, vznikne256 volaní s AL=0 a AH=0..255. Podľa vyššie uvedeného poradia OUT je prvá hodnota na388h stále0 a druhá na389h postupne0..255. **Nie je to dôkaz vymazania256 registrov** ani volanie256 INT63 servisov. Ďalšie samostatné volanie má AX=2001h, teda388h dostane1 a389h dostane20h za rovnakého vstupného kontraktu.

Ak callback zmení AH/AL, presný počet iterácií a hodnoty sa môžu zmeniť. Statická prítomnosť INC AH sama osebe nepreukazuje256 opakovaní pre všetky runtime konfigurácie.

## Dáta, CFG a reprodukcia

Nové4 B FAR callbacku sú CS:3896..389A = image19486..1948A. Horné WORD pointera je zároveň guard. Ďalšie4 B uloženého predchádzajúceho vektora08h sú CS:000A..000E = image15BFA..15BFE. Pole pre starý vektor63 je už v predchádzajúcej dávke a nepripočítalo sa znovu.

`audit_dos_audio_lifecycle.py IMAGE HISTORICAL_INSTRUCTIONS ABSOLUTE_DECODER_DIRECTORY OUT_DIR` overuje hash obrazu, dekóduje celé uvedené kandidátne rozsahy a kontroluje konečné RET/RETF hranice. `dos_audio_lifecycle/` obsahuje tri inštrukčné CSV, `control_edges.csv`, `direct_callers.csv`, `data_intervals.csv` a `summary.json`. Priame control hrany sú oddelené od nevyriešeného callbacku. CFG zatiaľ neuzatvára externé návraty, runtime dosiahnuteľnosť ani vnútorné helpery.

Po nezávislom zlúčení má centrálny katalóg16 kandidátnych funkčných rozsahov,690 inštrukcií/1 579 B a542 dátových B, bez konfliktu. Úplná partition má64 intervalov a169 239 B aktuálne neposúdených. Predchádzajúce43 inštrukcií inštalačných/restore fragmentov sa nepripočítali ako samostatné funkcie; ich bajty sú zahrnuté v celých lifecycle rozsahoch tam, kde sa prekrývajú. Zostávajúci near-exit restore fragment zostáva osobitným dôkazom mimo centrálneho function code count.

## Nasledujúci konkrétny krok

V DOSBox-X sledovať FAR call11A6A, IVT08/63 po inštalácii, AX na vstupe/výstupe portového helpera, stav CS:3896 callbacku a IF/DF pred/po lifecycle. Rozlíšiť priamu inicializáciu od prvého vstupu INT63 a od service49. Staticky pokračovať producentmi pointeraCS:3896 a helperomCS:466A. Tieto testy zatiaľ neprebehli; pôvodný PASS320 ledger stále chýba, sémantické percentá zostávajú N/A.
