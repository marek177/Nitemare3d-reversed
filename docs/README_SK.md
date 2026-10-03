# N3W Runtime Lab 0.1.0

Natívny experimentálny nástroj pre **Windows 11 x64 (Intel/AMD)** na zber podkladov o `nite3w.exe` spustenom vo Windows 3.x pod DOSBox-X alebo cez OTVDM/winevdm.

## Začnite tu

Rozbaľte celý ZIP. Spustite `N3W_Runtime_Lab.exe`. Nie je potrebná inštalácia Pythonu, .NET ani ďalších balíkov. Program používa systémové knižnice Windows. Spustiteľný súbor nie je digitálne podpísaný. Súčasťou balíka je úplný zdrojový kód.

**Dôležité:** EXE bol skompilovaný pre Windows x64. V prostredí jeho vytvorenia nebol dostupný Windows 11, DOSBox-X s Windows 3.11 ani živý nite3w. Preto sa netvrdí, že boli overené jeho Windows API, grafické rozhranie, GPU čítače alebo spojenie so skutočným emulátorom. Prenositeľné jadro a ZIP exportér boli otestované samostatne; výsledky sú v `docs/TEST_REPORT.md`.

Pred použitím na hre vyskúšajte **`N3W_Test_Target.exe`**. Je to syntetický cieľ so známou adresou a hodnotami, nie údaje ani rekonštrukcia Nitemare 3D.

## Čo je implementované

| Oblasť | Funkcia | Hranica |
|---|---|---|
| HOST pamäť | Mapa čitateľných oblastí, hex výpis, úplné čítanie zvoleného rozsahu, A/B snímky a diff. | Jeden rozsah najviac 64 MiB. Nie atómová snímka celého procesu. |
| Scan | u8/u16/u32/u64, unsigned little-endian, každá bajtová pozícia, rozsah alebo čitateľná HOST pamäť do limitu 512 MiB. | Najviac 250 000 kandidátov; UI zobrazuje prvých 2 000. Limity a chyby sú označené. |
| Zužovanie | Zmenené, nezmenené, zvýšené, znížené, rovné novej hodnote. | Porovnáva s hodnotou z posledného scanu/filtra. Nie automatická identifikácia herného poľa. |
| Sledovanie | Do 64 adries, interval 100–10 000 ms, CSV, ručné značky udalostí. | Vzorkovanie nezachytí každý zápis do pamäte. |
| HOST CPU | Procesové vyťaženie, pracovná a súkromná pamäť, zoznam PE modulov. Odber všeobecných a segmentových registrov x64 alebo WOW64 vlákien. | Registre vlákna sa odoberajú po krátkom SuspendThread/Wow64SuspendThread a následnom ResumeThread. Nie guest CPU. Bez SIMD/FPU kontextu. |
| HOST GPU | Dostupné PDH čítače procesu: najvyťaženejšia engine inštancia, dedicated/shared pamäťové čítače. | Nie obsah VRAM, shaderov alebo hardvérových registrov. N/A nie je nula. Čítače môžu byť nepresné. |
| Obraz | BMP viditeľnej oblasti najväčšieho okna vybraného procesu. | Nie interný framebuffer. Prekrytia inými oknami sa môžu zachytiť. |
| DOSBox-X | Lokálny TCP listener pre dokumentovaný debuggerový protokol REQ / BEGIN / END. PING, BREAK, CPU, EV, RUN, HELP a povolené čítacie/debuggerové príkazy. | Potrebuje zostavu DOSBox-X s podporou `mcp_server`. Nie univerzálne rozhranie všetkých vydaní. |
| Trace | Import textového LOGCPU, CS:IP návštevy, extrakcia registrov, pozorované CALL/RET/branch následníky, voliteľná mapa funkcií. | Počty návštev nie sú časy CPU ani počty skutočných volaní; priradenie selektorov musí byť overené osobitne. |
| Export | REPORT.md, manifest.json, CSV, SHA-256, streaming ZIP; dumpy a snímky iba po výslovnom výbere. | ZIP sa nikam neodosiela. Pred zdieľaním ho treba prezrieť. |

## Prvý skúšobný záznam bez hry

1. Spustite `N3W_Test_Target.exe` a potom `N3W_Runtime_Lab.exe`.
2. V hornej lište kliknite na **Obnoviť**, vyberte `N3W_Test_Target.exe` a kliknite na **Pripojiť**.
3. Testovací cieľ zobrazuje adresu bloku. Na karte **Pamäť / dumpy** ju prepíšte do poľa **Adresa HOST (hex)**. Do dĺžky zadajte `1C` (28 bajtov).
4. Vytvorte **Snímku A**, v testovacom cieli stlačte **Zásah (-7 HP)**, potom vytvorte **Snímku B** a stlačte **Porovnať A / B**.
5. Pole zdravia na offsete `08` sa má zmeniť zo 100 na 93. Meniť sa môže aj `ticks` na offsete `18`. Tieto offsety platia iba pre syntetický testovací cieľ.
6. Na karte **Scan / sledovanie** vyberte u32 a po RESET zadajte hodnotu 100. Spustite hľadanie v rovnakom rozsahu. Po zásahu nastavte hodnotu 93 a filter „Rovné zadanej hodnote“.
7. Vyberte zostávajúceho kandidáta, pomenujte ho, pridajte sledovanie a spustite záznam. Po ďalšom zásahu by sa mala objaviť hodnota 86. Zastavte sledovanie.
8. Na karte **Export** opíšte pokus. Vytvorte ZIP. Na preverenie diffu pridajte aj binárne dumpy.

Tento test je určený na overenie skutočného behu programu na vašom Windows. Nie je to tvrdenie, že ho tvorca vykonal na Windows.

## Použitie s DOSBox-X / Windows 3.11

Spustite vašu existujúcu inštaláciu Windows 3.11 a v nej `nite3w.exe`. V nástroji pripojte HOST proces `dosbox-x.exe` (alebo iný názov vašej zostavy). Zoznam prednostne ukazuje emulátory a testovací cieľ. Pri premenovanom programe možno do výberového poľa napísať samotné PID a stlačiť Pripojiť.

Tlačidlom **Vybrať nite3w.exe** označte konkrétny súbor z disku; uloží sa jeho SHA-256, nie samotný EXE. Tento krok sám nedokazuje, že bežiaci emulátor načítal práve daný súbor. Verziu treba preveriť vo vašom prostredí.

### Novšie kompatibilné zostavy — živý guest debugger

V aktuálnej dokumentácii vývojovej vetvy DOSBox-X je opísaný miestny TCP protokol pre externé nástroje. Dostupnosť závisí od zostavy, nie iba od toho, že sa program volá DOSBox-X.

Do existujúcej sekcie `[dosbox]` konfigurácie pridajte:

```ini
mcp_server=58991
```

Nenahrádzajte tým zvyšok konfiguračného súboru. Dodaný `examples/dosbox_mcp_snippet.conf` je iba ukážka riadka, nie hotová konfigurácia Windows 3.11.

Zapnite listener v Runtime Lab a následne spustite kompatibilný DOSBox-X. Server počúva **iba na 127.0.0.1**. DOSBox-X sa pripája k nemu. Neotvárajte port na internete a nespúšťajte zároveň iný MCP server na tom istom porte.

Po úspešnom PING použite **BREAK**, **CPU stav** a **Registre EV**. **HELP** zobrazí príkazy konkrétnej zostavy. Na pokračovanie slúži **RUN**; odpoveď na RUN iba potvrdzuje prijatie, nie vykonanie nejakého počtu inštrukcií.

`LOGS 1000` znamená **4096 inštrukcií**, pretože počet je hexadecimálny. Dostupnosť LOGS/LOG/LOGL/LOGC a niektorých breakpointov závisí od debug/heavy-debug zostavy. `LOGCPU.TXT` vzniká v pracovnom priečinku emulátora, nie automaticky v priečinku Runtime Lab. Po skončení trace ho importujte cez **Import LOGCPU**. Ďalší trace môže rovnaký súbor prepísať; pred novým testom zachovajte kópiu.

Do vlastného príkazu možno zadať napríklad `EV DS`, `SELINFO` s platným runtime selektorom alebo `MEMDUMPBIN` s overeným selektorom, offsetom a dĺžkou. NE číslo segmentu z Ghidry sa nemusí rovnať runtime selektoru. V chránenom režime Win16 nepoužívajte automaticky prepočet `segment * 16 + offset`.

Príkazy meniace registre alebo pamäť (`SR`, `SM`, `SMV`) a príkazy portových zápisov sa cez tento nástroj nepovoľujú. BREAK, RUN, breakpointy a LOG však **ovplyvňujú vykonávanie a časovanie**, hoci nástroj nevolá WriteProcessMemory.

### Staršia zostava bez protokolu

Použite debugger DOSBox-X priamo (v podporovaných zostavách štandardne Alt+Pause), skontrolujte HELP a uložte krátky trace alebo dump. Importujte `LOGCPU.TXT`, text CPU/EV alebo `MEMDUMP.BIN`. Na A/B porovnanie importujte dva raw dumpy rovnakého rozsahu tlačidlami Import súboru A/B. Bez metadát sa ich adresy zobrazujú iba ako súborové offsety.

## Použitie cez OTVDM / winevdm

Pripojte konkrétny proces `otvdm.exe`, `otvdmw.exe` alebo `winevdm.exe`, v ktorom beží hra. HOST mapa, scan, snímky, sledovanie, moduly a štatistiky používajú rovnaké API ako pri DOSBox-X.

**Živý DOSBox bridge s OTVDM nekomunikuje.** Pri OTVDM táto verzia nevie automaticky získať ani namapovať vnútorné registre emulovaného Win16 CPU. Zaznamenané HOST registre patria emulátoru. Existujúce debug logy možno zachovať cez Import CPU textu; automatická analýza je určená hlavne pre rozpoznateľné CS:IP riadky typu LOGCPU, nie ľubovoľný formát OTVDM.

## Kde sú výsledky

Relácie sa ukladajú do:

```text
%LOCALAPPDATA%\N3WRuntimeLab\sessions\<čas_a_identifikátor>
```

`events.csv` obsahuje ručné značky a hlásenia, `watch.csv` časové vzorky hodnôt a `metrics.csv` štatistiky. Ďalšie súbory majú časové a sériové označenia. `scan_coverage*.csv` uvádza rozsahy skutočne čítaných blokov a úspech čítania. A/B `.bin` má sprievodný JSON s adresou, dĺžkou a hashom.

Pri exporte sa vytvorí `EXPORT_CONTENTS.csv`, ktorý uvádza obsah, hash a dôvod prípadného vynechania binárneho súboru. ZIP používa štandardný formát bez kompresie; nedokáže vytvárať ZIP64 a má bezpečnostný limit približne 2 GiB. Dlhé testy rozdeľte na menšie relácie.

## Čo tento program zámerne netvrdí

Neskenuje fyzickú RAM celého počítača. Nekopíruje automaticky kompletný procesový minidump. Nečíta obsah GPU VRAM ani hardvérové registre grafiky. Nezachytáva všetky vstupy z klávesnice. Nevykonáva automatickú dekompiláciu. Neurčuje automaticky názvy alebo význam všetkých funkcií a nekalkuluje percento dokončenosti reverznej analýzy.

Snímka počas behu nie je atómová; rozdiel hodnoty nehovorí sám o sebe, ktorá inštrukcia ho spôsobila. Preto sa majú HOST dáta kombinovať s osobitne overeným guest debuggerovým trace.

## Bezpečnosť a oprávnenia

Program neobsahuje driver, injekciu DLL, skryté služby, prácu so vzdialenými procesmi ani automatické nahrávanie súborov. Na pamäť používa bežné čítacie oprávnenia. Pri odmietnutí prístupu skontrolujte proces a jeho oprávnenia; neobchádzajte ochranu systému.

Obsah procesu emulátora môže obsahovať aj cesty, dokumenty alebo iné súkromné údaje. Aj textové logy môžu byť citlivé. Pred zdieľaním ZIP prezrite. EXE je nepodpísaný; prípadné bezpečnostné upozornenie posudzujte podľa pôvodu, zdrojového kódu a overeného hash súboru, nie automatickým vypínaním ochrany.

## Zdrojový kód a zostavenie

Kód je v `src/` (C11, natívne Win32 API). S dostupným LLVM a Pythonom na vývojovom počítači:

```text
python build_llvm.py
```

Python je potrebný iba na tento build skript a vývojové testy, **nie na spustenie hotového programu**. Nástroj nevyžaduje pre zber dát pripojenie na internet. Windows a Nitemare 3D nie sú súčasťou balíka. Podrobnosti: `docs/ARCHITECTURE.md`, `docs/FUNCTION_MAP.md`, `docs/SOURCES.md`.