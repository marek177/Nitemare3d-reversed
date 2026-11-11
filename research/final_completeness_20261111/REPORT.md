# Final RE completeness campaign — vstupná dávka, 11. 11. 2026

Táto dávka uzatvára dohľadanie pôvodu zadania a evidenciu nedostupných vstupov. **Neuzatvára PASS 1 ani ďalšie analytické fázy. Nové binárne zistenia: 0; nové sémanticky overené bajty: 0; runtime testy: 0.**

## Overené zdroje a ich hranice

- Prečítaný strom repozitára `marek177/Nitemare3d-reversed` na commite `79e3a2a54794d5310d6348c7dd50a068efd0ee49`; odpoveď GitHub tree mala `truncated=false`. Nenašiel sa názov PASS320, PASS321 ani súbor s príponou EXE, BIN, ASM, LST alebo ZIP. Toto je kontrola názvov v tomto strome, nie dôkaz absencie obsahu vo všetkých vetvách alebo archívoch.
- GitHub vyhľadávanie 57295 a PASS 320 nevrátilo výsledky. Negatívny výsledok vyhľadávania nie je úplný obsahový audit.
- V chate „Deep audit bajtov“ (`6af32da3-6640-83eb-a3e8-40b8bc2a2661`) boli prečítané súhrny PASS 320 a 321. Odkazujú na `N3D_PASS320_INT63_COUNTER_WRAP_AUDIT.zip`, `N3D_PASS321_SERVICE49_COUNTER_LIFECYCLE.zip` a reprodukčné skripty v pôvodnom prostredí `/mnt/data`. Tieto artefakty neboli v tejto dávke otvorené.
- Chat „Pokračovanie reverznej analýzy“ (`6af47565-7030-83eb-bcdc-1c3dd6347bca`) poskytol historické odhady 13 oblastí. Nie sú meraním pokrytia.
- Používateľ dodal cestu `L:\\nite3d\\nite3\\dos\\N3D-UNFU.exe`. Dostupnosť, veľkosť, SHA-256, verzia a mapovanie na kanonický BIN zatiaľ neboli overené. Samotný názov nedokazuje DOS 2.0 ani konkrétny spôsob rozbalenia.
- Dva pokusy o lokálne čítanie zlyhali pred spustením procesu: `registered runtime ownership is missing`. Dva pokusy Node runtime skončili chybou `trusted Node process exited unexpectedly`. Nie je to dôkaz, že súbory na disku chýbajú.

Referencie v repozitári: [novembrový frontier](../../../docs/RE_NOV03_FUNCTION_CLOSURE_AND_TOOLING.md), [stav oblastí](../../../docs/RE_STATUS_AREAS_20261024_SK.md), [README](../../../README.md).

## Historická baseline — neoverená proti bajtom

| Kategória | Bajtov podľa súhrnu |
| --- | ---: |
| DEEP VERIFIED | 0 |
| PARTIAL | 72 014 |
| ALIGNMENT | 84 |
| NOP | 597 |
| EMBEDDED TABLE | 752 |
| UNASSESSED N3D | 0 |
| NON-CODE | 57 295 |
| EXTERNAL CRT/WORX | 40 618 |
| Spolu | 171 360 |

Súčet bol aritmeticky skontrolovaný. Historický počet intervalov je 1 488. Bez ich hraníc a hashov sa nesmie vytvoriť náhradná intervalová mapa ani tvrdiť jej opätovné overenie. `baseline.json` používa pri nedostupných mapách a katalógoch `null`, nie prázdny zoznam predstierajúci úplnosť.

Historických 0 DEEP VERIFIED nie je nové nezávislé meranie. Aktuálne percentá sú N/A, pretože chýbajú overené menovatele a vstupný ledger.

## Vstupná brána PASS 1

1. Získať kanonický BIN, pôvodný EXE, historický SHA-256 manifest, celú mapu PASS320/321 a ASM export.
2. Určiť adresný priestor každého offsetu: EXE file offset, load-module offset, normalizovaný BIN offset, segment:offset. Zachytiť MZ header, relokácie, load base a transformácie pri rozbalení. EXE nepovažovať automaticky za kanonický BIN.
3. Zachovať pôvodný ledger; konverziu do schémy validátora zdokumentovať vrátane pôvodných kategórií a inclusive/exclusive hraníc.
4. Overiť identitu celého obrazu, 1 488 intervalov, úplnú nadväznosť bez prekryvov a medzier, hash každého intervalu a kategóriové súčty.
5. Až potom vytvoriť NON-CODE frontu a rozdeliť intervaly podľa skutočných dátových typov.

Validátor `validate_pass320.py` je novovytvorený, **v tejto relácii nespustený**. Overuje integritu dodaného ledgeru, nepriraďuje sémantiku a nepovyšuje bajty. Vyžaduje dôveryhodný historický hash; hash práve dodaného súboru nesmie byť vydávaný za nezávislú autentifikáciu.

Príkaz po doručení a zdokumentovaní vstupov:

```text
python validate_pass320.py canonical.bin normalized_ledger.csv --expected-sha256 TRUSTED_HISTORICAL_SHA256 --out-dir integrity
```

CSV schéma: `start,end,sha256,classification`; offsety desiatkovo alebo s prefixom 0x, koniec exclusive. Kategórie sú explicitne definované v skripte. Nie je potvrdené, že pôvodný audit túto schému používa. Výstupy integrity JSON a NON-CODE CSV vzniknú až po úspešnej validácii.

## Brány sémantického uzatvorenia

Každý nový podinterval musí mať identitu obrazu, presné hranice, hash, typ/šírku/endianness, vlastníka, producentov a konzumentov, adresy xrefs, ASM s dosiahnuteľnosťou, segmentový kontext a reprodukčný postup. Hypotéza typu zostáva PARTIAL. Samotný dekódovateľný opcode, nulové bajty alebo podobnosť s knižnicou nepostačujú.

- DEEP VERIFIED: úplný lokálny kontrakt podložený reprodukovateľným dôkazom; statický dôkaz môže uzatvoriť statické tvrdenie. Runtime je povinný pre tvrdenia o skutočnej dosiahnuteľnosti alebo správaní, ktoré statika nedokazuje.
- PARTIAL: identifikované použitie s otvorenými hranicami, vetvami alebo aliasmi.
- CLASSIFIED ONLY: predbežná kategória bez uzavretého významu.
- UNKNOWN: nedostupný alebo nepreskúmaný dôkaz. UNKNOWN v tejto dávke neprepisuje historický stav originálnych artefaktov.

Knižničný pôvod (CRT/WORX/game/unknown) musí byť samostatná os od úrovne overenia. EXTERNAL neznamená vyriešené.

## PASS 2–5: konkrétne ďalšie brány

- CRT/WORX: identifikovať startup a inicializáciu DS, signatúry potvrdiť relokáciami a callsites, zdokumentovať register/stack ABI a far-pointer kontrakty. Neprenášať neoverené súhrny PASS321 na status DEEP VERIFIED.
- Funkcie: oddeliť kandidátne vstupy od potvrdených hraníc; ku každej funkcii viesť CFG, FAR/NEAR hrany, nepriame ciele, DS/ES/SS, vstupy/výstupy, vedľajšie účinky a závislosti od dát. Bez ASM sa v tejto dávke nerekonštruoval pseudokód.
- Gameplay/renderer: viesť samostatné statické a runtime dôkazy. Zhodu syntetického modelu so sebou samým nepovažovať za zhodu originálu.
- Cross-version: autentifikovať každú verziu osobitne. Porovnávať raw bajty aj relokačne normalizované inštrukcie; zhodné bajty nestačia na behaviorálnu zhodu pri inom segmente alebo volajúcom kontexte. Port PE32 sa nevykonáva.

## Tabuľka 13 oblastí

Pre všetkých 13 riadkov: nové binárne zistenia sú žiadne; blokátor je nedostupný autentifikovaný obraz/úplný inventár. N/A sa nesmie nahradiť nulou. Každá metodika vyžaduje vopred uzavretý menovateľ, nemenné akceptačné brány a citovateľné dôkazy čitateľa.

| Oblasť | Historický odhad | Nové meranie | Metodika po získaní inventára | Zostáva neznáme | Najbližší krok |
| --- | ---: | --- | --- | --- | --- |
| Mapy a dátové formáty | 99 % | N/A | overené polia / inventár polí | úplnosť polí a variantov | inventár formátov a parserových vetiev |
| Dátové typy a konštanty | 95 % | N/A | sémanticky uzavreté dátové bajty / všetky dátové bajty | typy NON-CODE intervalov | importovať NON-CODE intervaly a ich xrefs |
| Tabuľky a ukazovatele | 93 % | N/A | uzavreté položky / inventár položiek | segmentové bázy a nepriame ciele | zostaviť pointer ledger s relokáciami |
| Funkcie / ASM / CFG | 90 % | N/A | funkcie so všetkými bránami / overený inventár funkcií | hranice a nepriame hrany | rekurzívna dosiahnuteľnosť z potvrdených vstupov |
| RNG a determinizmus | 97 % | N/A | uzavreté callsites / inventár callsites; runtime osobitne | poradie a spotreba RNG | zachytiť RNG pred/po každom volaní |
| Scheduler / herná slučka | 96 % | N/A | uzavreté vetvy / inventár vetiev | poradie tickov a mutácie aktérov | zachytiť vstup a všetky aktualizácie jedného ticku |
| DEMO a vstupy | 96 % | N/A | uzavreté vetvy / inventár vetiev | vzorkovanie vstupov a prehrávanie | opakovať identické DEMO z totožného stavu |
| Renderer / VGA | 94 % | N/A | uzavreté vetvy / inventár vetiev; pixely osobitne | clipping a VGA stav | zachytiť indexed framebuffer a DAC |
| GUARD AI / bossovia | 93 % | N/A | uzavreté prechody / inventár prechodov | špeciálne stavy a dosiahnuteľnosť | inventár dispatcherov a bossových prechodov |
| Zbrane / projektily | 92 % | N/A | uzavreté vetvy / inventár vetiev | kolízie a slot lifecycle | zachytiť slot pred/po kolízii a damage |
| Sprity / HUD / paleta | 92 % | N/A | uzavreté operácie / inventár operácií | resource binding a clipping | spárovať zdrojové dáta s draw callsites |
| SAVE / LOAD | 92 % | N/A | uzavreté polia / inventár polí; roundtrip osobitne | cache a prvý tick po LOAD | SAVE/LOAD stopa vrátane prvého herného ticku |
| Windows Win16 | 92 % | N/A | uzavreté funkcie / Win1.10 inventár | NE relokácie a DOS/Win odlišnosti | autentifikovať Win1.10 EXE a NE segmenty |

Bajtové, funkčné, algoritmické a runtime pokrytie vykazovať osobitne. Nepoužívať priemer týchto 13 historických odhadov ako celkové pokrytie.

## Stav výstupov

- Report, baseline JSON, 13-riadkové CSV a návrh validátora: pripravené.
- Skutočná mapa 57 295 bajtov, dátový katalóg, funkčný katalóg, nové ASM/CFG a pseudokód: nedostupné vstupy; nevytvorené.
- DOSBox-X: iba protokol plánovaných testov; žiadny test sa nespustil.
- Lokálne uložené deliverables: nevytvorené pre nedostupný lokálny runtime. Materiály sú na samostatnej vetve GitHub.
