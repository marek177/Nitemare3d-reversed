import csv,json
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'omitted_noncode_reference_scan';s=json.loads((d/'summary.json').read_text())
text='''# PASS1: odkazy mimo starého inštrukčného inventára

Nový audit preskúmal 21 093 začiatkov na bajtoch, ktoré nepatria k žiadnej inštrukcii dodaného DOS inventára, v historickom code doméne [0,1BDA2) s vynechaním [11EE7,11EF8). Hľadal explicitné memory operandy DS/SS, ktorých displacement po hypotetickom pripočítaní DGROUP základu leží v zostávajúcom CLASSIFIED ONLY alebo UNKNOWN. Rozsah a presná vstupná mapa sú hashované v summary.json.

Výsledok: **3 raw kandidáti, 0 dokázaných nových referencií, 0 reklasifikovaných bajtov, 0 DEEP VERIFIED**. Toto nie je dôkaz absencie ďalšieho kódu alebo nepoužívania dát. Skener nezahŕňa okamžité near pointer hodnoty, CS aliasy, dynamické segmenty, register odvodené adresy ani beh mimo zadaného image doménového predpokladu. DS/SS=DGROUP je pri kandidátoch podmienka, nie dokázaný stav.

## Kandidáti a konkurenčné hranice

| Image začiatok | Raw bajty | Hypotetický operand | Posúdenie |
|---|---|---|---|
|083B5|33 9A EA 24|SS:[BP+SI+24EA]|alternatívne hranice dávajú 083B4:6A33 PUSH 33h a 083B6:9AEA24EE11 FAR CALL; prirodzený vstup otvorený|
|083CD|33 9A EA 24|SS:[BP+SI+24EA]|alternatívne hranice dávajú 083CC:6A33 PUSH 33h a 083CE:9AEA24EE11 FAR CALL; prirodzený vstup otvorený|
|1812D|00 06 32 01|DS:[0132]|platné raw dekódovanie samo nepotvrdzuje code entry alebo DS; treba doklad caller/CFG alebo dátovej štruktúry|

Prvé dva prípady sa nachádzajú v podobných sekvenciách začínajúcich 083A8 a 083C0 (MOV WORD [3F56],1/2; dve PUSH 3F56h; PUSH33h; FAR CALL; ADD SP,6; RETF). Tento konzistentný konkurenčný parse znižuje užitočnosť raw matchu ako referencie na FCB interval. Bez dôkazu entry sa však nevydáva za úplné uzavretie vykonateľného kódu týchto sekvencií. Skener preto nevytvára funkčné ani dátové promócie. Kontext každého nálezu je v raw_candidates.csv a možno ho znovu dekódovať zo skutočných bajtov.

## Reprodukcia a vstupné dôkazy

scan_omitted_noncode_references.py IMAGE MAP INVENTORY DECODER OUT. Skript overí kanonický image SHA, všetky pôvodné inventárne bajty a vylúči nový kandidát, ak prekrýva ľubovoľnú pôvodnú inštrukciu. Pre každý raw kandidát uloží pôvodné bajty, konkurenčný kontext, rozsah dotknutého zostávajúceho intervalu, operandovú šírku a segmentový predpoklad. Dekóduje iced-x861.21.0 v 16-bit režime. Nové prirodzené runtime aj controlled replay prípady sú 0.

Pri neplatných raw kandidátoch nesmie štatistická zhoda opcode alebo pekný disassembly nahradiť dôkaz dosiahnuteľnosti. Súčasne negatívny výsledok tohto konkrétneho filtra nesmie slúžiť ako dôkaz paddingu. Nulové a neodkazované intervaly zostávajú otvorené.

## Meranie

Aktuálna autoritatívna mapa pass1_startup_segments ostáva **57 069 B PARTIAL, 182 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57 295 B. Táto dávka iba rozširuje audit zdrojov referencií. Prirodzený runtime0, žiadne nové percentá. Posledná publikovaná GitHub snímka tieto lokálne dôkazy zatiaľ neobsahuje.

'''
text+=f"SHA image `{s['image_sha256']}`; SHA mapy `{s['map_sha256']}`; SHA inventára `{s['inventory_sha256']}`.\n\n"
text+='''## Aktualizácia 13 oblastí

Metodika nového %: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, preto N/A. Rozšírený vyhľadávací priestor nie je sémantická coverage.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|bez nového sémantického dôkazu|loader hranice|map closure|
| Dátové typy a konštanty |95 %|N/A|žiadna promócia z raw matchov|182 B iba klasifikované|nepriame pointery|
| Tabuľky a ukazovatele |93 %|N/A|hranice raw kandidátov zachované|DS/SS predpoklad|skutočné entry doklady|
| Funkcie / ASM / CFG |90 %|N/A|21 093 ďalších starts preskúmaných|tri nepreukázané parse|konkurenčné CFG|
| RNG |97 %|N/A|bez nového dôkazu|prirodzené poradie|DEMO trace|
| Scheduler |96 %|N/A|bez nového dôkazu|prirodzené callery|call graph|
| DEMO a vstupy |96 %|N/A|bez nového dôkazu|driver ABI|input closure|
| Renderer / VGA |94 %|N/A|0132 raw kandidát nepromovaný|mask table konzument|1812D dátový/code kontext|
| GUARD / bossovia |93 %|N/A|bez nového dôkazu|selector doména|descriptor flag8|
| Zbrane / projektily |92 %|N/A|bez nového dôkazu|damage callery|effect producer|
| Sprity / HUD / paleta |92 %|N/A|bez nového dôkazu|resource identity|resource parser|
| SAVE / LOAD |92 %|N/A|FCB raw alias bez promócie|DOS FCB konzument|argumentová cesta|
| Windows Win16 |92 %|N/A|bez nového Win dôkazu|cross-version match|Win vlastný inventár|

## Runtime testy na vykonanie

V DOSBox-X sledovať skutočný IP vstup do okolia 083A8/083C0 a prípadnú prácu s DS:0130 mask blokom. Negatívny hit bez úplného trace nie je dôkaz nepoužitia. Dátový interval 1812D najprv uzavrieť statickým kontextom alebo relokáciami, potom prípadne watchpointom; nesmie sa nasilu vykonať ako kód. PE32 sa nevytvára.
'''
(r/'OMITTED_NONCODE_REFERENCE_SCAN_REPORT.md').write_text(text,encoding='utf-8')
