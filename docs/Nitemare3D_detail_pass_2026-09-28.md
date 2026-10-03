# Nitemare 3D — detailný priechod, 28. 9. 2026

## Vstupy a rozsah

Kontrolovaný export `nite3w110.exe.c` (Win16 v1.10), správa `Nitemare3D_cross_version_function_matching_report.md` a staršia správa `NITEMARE3D_SAVE_LIBRARIES_IDA_REPORT.md`. Ide o statický priechod dvoma funkciami, bez nového debuggerového testu. Názvy Ghidry nie sú názvy pôvodného zdrojového kódu.

## Oprava východiskového počítania

Starší párovací report skutočne eviduje 493/514/526/519 extrahovaných tiel pre DOS 1.0/1.7/1.8/2.0 a 959/965/965/967 pre Win16 1.3/1.6/1.8/1.10. Súčet je 5 908 tiel. Používateľská tabuľka uvádza približne 8 135 *odhadovaných* funkčných záznamov. Tieto dve veličiny nemajú rovnakú metodiku; 2 120 „zostáva“ preto nie je overený menný zoznam. Párovací report označuje 90 DOS 2.0 a 38 Win16 1.10 funkcií ako slabé/bez viacverziovej zhody; ani to neznamená automaticky, že všetky ostatné sú detailne vysvetlené.

## Win16 v1.10 `FUN_1010_574c`: obnova uloženého stavu

**Potvrdené z exportu:** Funkcia má parametre index slotu a názov súboru. Otvára súbor (`FUN_1010_5260`, potom `FUN_1008_54d4`), posunie sa na `index * 0xD6E7`, číta štvorbajtovú dĺžku a vyžaduje hodnotu `0xD6E7`. Potom preskočí `0x29` bajtov (názov slotu), číta dve dvojbajtové polia a štvrobajtový čas, blok mapy `0x2000` a globálny blok `0x5E`. Nasledujú ďalšie čítania, rekonštrukcia odvodených ukazovateľov a časovačov, a zatvorenie súboru. Pri chybe volá `FUN_1018_3118`; po koncovom čítaní porovná dve načítané polia s `DAT_1048_7e52` a `DAT_1048_7e54`.

**Pozor na poškodený dekompilát:** Štyri volania `FUN_1018_31c4()` a ďalšie volania `FUN_1008_5798()` nemajú vypísané argumenty. Čítanie štvorbajtového času a následné `CONCAT22(uVar6,uStack_a)` strácajú spoľahlivú provenienciu horného slova. Preto nemožno z C exportu samého potvrdiť všetky podbloky ani presný vzorec úpravy časovačov. Segmentovo relatívne adresy typu `0x6d66`, `0x9dd6` tiež vyžadujú overenie v raw disassembly. Súčasný model: uložené časy menšie než uložený referenčný čas sa nulujú; ostatné sa upravujú o rozdiel aktuálneho a uloženého času. Tento model je **silná inferencia**, presná 32-bitová aritmetika je otvorená.

**Presný nasledujúci test:** V IDA/Ghidra skontrolovať assembly pri `1010:574C`, všetky call sites `1008:5798` a `1018:31C4`, vstupné `DS/ES`, a každú dvojicu push argumentov. Urobiť kontrolovaný save/load s časovačom pred a po načítaní a porovnať zmenené štyri bajty príslušného záznamu.

## Win16 v1.10 `FUN_1010_5b96`: dekódovanie obrázka

**Potvrdené z exportu:** Funkcia skúša otvoriť vstup cez `FUN_1008_3ea4`. Ak otvorenie zlyhá, vracia `0`; ak uspeje, načíta hlavičku `0x80` bajtov. Kontroluje prvý bajt na `10`, potom dve rozdielové hodnoty (`199`, `0x13F`) v hlavičke. Následne číta bajty a pri horných dvoch bitoch `11` interpretuje spodných šesť bitov ako dĺžku opakovania nasledujúceho bajtu. Inak vloží jediný literál. Výstup zhromažďuje po `320` bajtoch a každý hotový riadok odovzdá `FUN_1010_41a2`. Končí po `200` riadkoch, zatvára vstup a vracia `1`.

**Inferencia:** Je to PCX-kompatibilné RLE pre 8-bitový obrázok 320 × 200. Samotná kontrola dvoch rozmerov používa v dekompiláte `&&`; teda odmietne hlavičku až keď sú *obe* rozdielové hodnoty nesprávne. Potvrdenie tejto podmienky aj reakcie na skrátený súbor vyžaduje assembly a test na modifikovaných vstupoch.

**Presný nasledujúci test:** V assembly overiť `AND`/`OR` vetvenie a obsluhu EOF v `FUN_1008_3ebe`. Pripraviť štyri hlavičky: správna, chybná iba šírka, chybná iba výška, chybné oboje; zvlášť skrátiť RLE dáta pred 200. riadkom.

## Poradie ďalšieho priechodu

1. `FUN_1010_574c`: doplniť chýbajúce argumenty z assembly a presný časový vzorec.
2. `FUN_1010_5b96` a podobná `FUN_1010_5d72`: porovnať obrázok zo samostatného súboru so sekciou v agregáte.
3. DOS `FUN_1000_0AEA`, `FUN_1000_4A86` a zlúčený blok `FUN_2000_9364`: opraviť hranice a až potom počítať funkcie.
4. Vytvoriť menný stavový register pre všetky exportované telá; rozlišovať identifikované, základne opísané, hlboko overené a poškodenú dekompiláciu.

## Istota

Vysoká pre priamo zobrazené podmienky a konštanty oboch Win16 funkcií; stredná pre ich sémantické označenie; nízka pre presné poradie vnútorných čítaní a časovú aritmetiku tam, kde C export stratil argumenty.