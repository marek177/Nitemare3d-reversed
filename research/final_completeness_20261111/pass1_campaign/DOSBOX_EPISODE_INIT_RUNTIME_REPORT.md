# DOSBox-X: prirodzený výber epizódy a príprava názvov dát

Šiesty zachovaný scenár pôvodného packed DOS2 EXE pokračoval po input init cez **0D29:2696** a prípravu epizódy0277:0336 až po návrat **0476:0174**. Pôvodné registre, game kód ani odpovede volaní sa nedosadzujú. Skoršie startup/BSF/VGA/input body sú znovu overené ako spoločný prefix, nie ako nové samostatné testy.

## Skutočný priebeh

|Kanonický bod|Zachytený výsledok|
|---|---|
|0D29:2696|DS=SS2F95; návrat0C9A:016E|
|0D29:26AE|pôvodný formatter vytvoril `map.1` v lokálnom16B buffere DS:E7E6|
|11EE:3990|near filenameE7E6,arg4; návrat154D:26BC|
|0D29:26BC|AX0 z pôvodného access wrappera|
|0D29:26CA|BSFmode1 vrátil FAR2F95:363B|
|0476:016E|AX1 z episode probe|
|0277:0336|návrat0C9A:0174,WORD episode1|
|0476:0174|DS626A=1; buffery627C/628C/629C obsahujúmap.1/img.1/demo.1|

Lokálny filename offset je nezávisle vypočítaný zo vstupnéhoSP−18 podľa ENTER16 a uloženiaBP; verifier ho porovnáva s reálnym stack argumentom access. Nie je odvodený len z harness summary. BSF pointer ukazuje na flag v pôvodnom decoded headeri. Tento capture potvrdzuje bežnú existujúcu epizódu1; ešte neuzatvára neúspešný scan, unregistered vetvu alebo caller výsledku7.

## Čo skutočne robí access wrapper

Nový ohraničený ASM kontext **11EE:3990..39AF** je v `access_wrapper_context.csv`, nezávisle byte-exact overený proti kanonickému obrazu a inventáru. NačítanieDXfilename nasleduje **AX4300h;INT21h**. Pri carry skočí na zdieľaný normalizátor05A2. Pri úspechu kontroluje iba bit2h druhého argumentu; ak je bit nastavený aCL atribút bit1h je nenulový, vytvoríAX0D00h,STC a znovu prejde normalizátorom. Inak ponechá úspech.

```text
query_attributes(filename) via AX4300h/INT21
if DOS carry: tail common_result
if (mode & 2) != 0 and (CL & 1) != 0:
    AX=0D00h; carry=1
tail common_result

common_result at05A2:
    if carry: branch error path05B9   // full error mapping not closed here
    AX=0; restore SP/BP; FAR return
```

Pri skutočnom argumente **4** sa bit2h netestuje ako zapnutý. Úspešný probe teda v tejto implementácii nepotvrdzuje skutočné otvorenie/čítanie mapy ani platnosť jej obsahu. Prirodzený capture overil výsledokAX0, nie každú atribútovú a chybovú vetvu wrappera. Táto krátka závislosť sa zatiaľ nepridáva ako uzavretá celá funkcia do katalógu, pretože zdieľaná error tail cesta nie je v dávke vykonaná.

## Reprodukcia

`runtime_dosbox_startup.py DOSBOX_EXE GAME_DIR IMAGE RELOC OUT WORK episode_init` a `verify_dosbox_startup_capture.py IMAGE RELOC OUT WORK`. Verifier preverí74MEMDUMPBIN príkazov,1670relokácií a celých171360B runtime obrazu, všetky skoršie registre/stacks/headers aj6 nových raw dumpov. Nové súbory sú episode_probe_stack,episode_filename,episode_access_stack,episode_prepare_stack,episode_global,episode_asset_names. Hashované sú spolu s transcript,snapshots,inputs aconfig v independent_verification.json. Raw memory je vo WORK, nie v GitHube.

`write_episode_init_runtime_report.py OUTPUTS WORK INVENTORY ABS_DECODER` znovu overí všetky capture proof hash položky a ASM závislosť. Originálne22 vstupné súbory zostali po behu nezmenené. Harness ukončí svojDOSBox po poslednom bode; nejde o prirodzený exit hry. Skutočná grafika/zvuk aWin16 zostávajú mimo tejto skúšky.

Summary SHA `e3fd475acad1450b55e657e31c8088d2d8ec0e628cf6f3993f8fa5bdbcf00b15`; proof SHA `19f9e204adf2fb77f8f521f19d45a4917d9dc541a3539068986b9efebc00a720`.

## Meranie

Prirodzené zachované scenáre5→6. Žiadna nová funkcia ani seeded replay v tejto dávke; katalóg zostáva123rozsahov. PASS1 bez zmeny57102PARTIAL/149CLASSIFIED ONLY/44UNKNOWN/0DEEP VERIFIED. Nové near filename aepisode globals sú BSS/stack, nie nové file-backed promócie. Lokálna dávka zatiaľ nie je súčasťou publikovanej päť-scenárovej snímky2ced761cb0bf1eece24a224e92c05636058ab0ae. Nové percentá N/A bez úplných menovateľov.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Úplné menovatele chýbajú, preto N/A. Iniciačný runtime nie je percento gameplay completeness.

| Oblasť | Predošlý odhad | Nové % | Aktuálny dôkaz (staršie riadky zachované) | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|prirodzený map.1 probe a názvy map/img/demo.1|platnosť obsahu a iné scenáre|map/resource skutočné čítanie|
| Dátové typy a konštanty |95 %|N/A|511 runtime DWORD mimo file|149 B iba klasifikované, 44 B UNKNOWN|nepriame segmentové prístupy|
| Tabuľky a ukazovatele |93 %|N/A|7-slot CRT rodina v8 DOS verziách; piaty slot otvorený|vypočítané aliasy/writeri DS2356|runtime hook watch|
| Funkcie / ASM / CFG |90 %|N/A|prirodzené2696→access→BSF1→0336|caller výsledku7 a ďalšia init|0476:0174 pokračovanie|
| RNG |97 %|N/A|bez RNG runtime|prvý srand/rand|RNG caller trace|
| Scheduler |96 %|N/A|clock init prebehol medzi bodmi|main loop/scheduler|loop vstup|
| DEMO a vstupy |96 %|N/A|prirodzený INT9 install a aux probeFFFFh|key IRQ/DEMO poradie/close|prvý vstupný tick|
| Renderer / VGA |94 %|N/A|mask/plane store,transparentnosť a unsigned depth|skutočné VGA registre a výstup|DOSBox frame dump|
| GUARD / bossovia |93 %|N/A|bez AI runtime|map init|selector doména|
| Zbrane / projektily |92 %|N/A|bez damage runtime|effect callery|damage trace|
| Sprity / HUD / paleta |92 %|N/A|VGA init, nie vizuálna parita|paleta/sprity|resource load|
| SAVE / LOAD |92 %|N/A|BSF native file-check vrátený|SAVE/LOAD a chybové I/O|diskové scenáre|
| Windows Win16 |92 %|N/A|DOS8štítkov/7obrazov krížovo overených; Win bez zmeny|WinNE prostredie a algoritmické mapovanie|Win hook rodina|

## Runtime testy na vykonanie

Pokračovať za0476:0174 do čítania palety0277:02A6 a resource/game init; zachytiť skutočné file offsety a počty, nie iba existenciu. V oddelených pracovných kópiách overiť chýbajúceepizódy, atribútové chyby a spracovanie výsledku7. RNGreset0D29:271C zostáva neskorší prirodzený bod, nie časový seed v tejto vetve. PASS1 UNKNOWN44B stále vyžaduje priamy read/write alias dôkaz.
