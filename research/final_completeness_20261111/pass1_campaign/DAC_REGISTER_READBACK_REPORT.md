# DOSBox-X: skutočný readback emulovaného VGA DAC

Deviaty zachovaný runtime scenár spustil pôvodný packed DOS2 EXE až po návrat paletového loadera **0476:017C**, skutočne **0C9A:017C** pri load0824h. V tomto bode debugger iba prečítal stav emulovaného DAC príkazmi `VGA DAC` a `VGA DACPAL`. Ani jeden z nich nevykonáva game OUT alebo dosadenie registra/pamäte.

## Výsledok

**Všetkých256 RGB položiek, teda768 komponentov, je byte-exact zhodných v troch nezávisle dostupných reprezentáciách:**

1. Posledných768B pôvodnéhoGAME.PAL, každý BYTE logicky posunutý doprava2.
2. Reálny game buffer naDS4A64..4D63 v tejto session.
3. Polia RGB emulovaného DAC z read-only debugger výpisu.

DAC hlási **bits6, pel_maskFFh**. Všetky komponenty sú0..63. Výpis ďalej obsahuje state01h,write_index00h,read_indexFFh,pel_index00h; sú to pozorované hodnoty konkrétneho bodu, nie všeobecné invarianty hry. Presné256riadkové porovnanie je `dac_component_comparison.csv`.

Tým sa posilňuje predchádzajúci modeled OUT dôkaz: teraz je potvrdený aj výsledný **stav emulovaného DAC**, nie iba plánované výstupné hodnoty alebo buffer. Nie je to fyzický VGA hardvér, meranie analógového výstupu, úplná video-plane konfigurácia, vykreslený frame alebo Win16 paletová parita.

## Čo debugger číta

Referenčný zdroj `windows_runtime_probe/debug_reference.cpp` má v príkazeDACPAL slučku nad256 `vga.dac.rgb` záznamami a vypisuje ich red/green/blue polia. PríkazDAC vypisuje bitový režim a masku/indexy. Ide o čítanie interného stavu emulátora; neprebieha cez manipuláciu portového read indexu a nemení game paletu. Zhodu zdroja konkrétneho release s binárkou podopiera už uložený tool manifest; nejde o nezávislú formálnu verifikáciu celého emulátora.

VýstupDACPAL má32riadkov po8 RGB trojiciach. Verifier kontroluje postupné indexy00,08,..F8 a presne8 hodnôt v každom riadku; nedovoľuje vynechanie alebo duplicitné indexy. Výsledných768B znovu porovná s originálnym assetom a raw buffer dumpom. `dac_readback.json` navyše musí obsahovať presne rovnaké odpovede ako pôvodnýMCP transcript.

## Súbežný UNKNOWN watch a rozsah scenára

Táto session zachovala44 BYTE memory-change breakpointov odCRT0018 po main017C. Znovu nebola pozorovaná udalosť zmeny hodnoty; všetky cached baseline sú0. Hook4B má iba endpoint dumpy. Rovnaké limity ako v predchádzajúcom UNKNOWN reporte: nie je sledované čítanie, same-value zápis ani zmena/obnova v host callbacke. Žiadna promócia UNKNOWN alebo hook typu.

Spoločný init prefix sa prekrýva so staršími session. Nadväzujúci DAC readback a reálny buffer sú nové dôkazy tejto samostatnej session; každý breakpoint alebo komponent sa nepočíta ako ďalší runtime test. Hra sa po capture zastaví ukončením vlastného emulátora harnessom, nie prirodzeným exitom.

## Reprodukcia a dôkazy

`runtime_watch_dac_readback.py DOSBOX_EXE GAME_DIR IMAGE RELOCS OUT WORK` používa archivovaný `dosbox_watch_support_v1.py`, potom read-only DAC query a768B buffer dump. Pôvodné22 vstupné súbory zostávajú nezmenené. `verify_unknown_watch_capture.py IMAGE RELOCS CURRENT_MAP OUT WORK` rozpoznáDAC capture a nezávisle overí všetky jeho hodnoty, presnú44B množinu, breakpoint lifecycle, reálne relokácie a kompletne rozbalený runtime image. Povolené sú iba query/BP/RUN/dump a dve presnéVGA query; žiadne SR/SM/FM alebo port OUT príkazy.

`write_dac_readback_report.py OUTPUTS WORK` znovu overí proof hashe a vytvorí256riadkovýCSV katalóg. Summary,transcript,snapshots,watch_events,inputs,config,dac_readback aindependent proof sú v `dosbox_dac_readback_runtime/`;14 raw captures vrátane palette bufferu sú vo WORK. Predchádzajúca syntax chyba pri príprave skriptu nespustila žiadny DOSBox proces a nie je runtime scenár.

Runtime summary SHA `203096c8979108ed9d649bd71bb555be276821e3e5c93a3d584aeac92db0fd47`. Proof SHA `9af71da31cc3048a6ab114c54bc4ddbea4a287f352af626f736dae70f6740ae6`. DAC/buffer/expected768B SHA `52768cc8fc70a3242e82214ed3dbf7136fe146670ad773916ab03132ee2fd1ce`. GAME.PAL SHA `efd52442cbee3327d8cec045b31559049e8767b298c25674a557eb6e096a759f`.

## Meranie

Úspešné runtime scenáre8→9. DOS katalóg125 rozsahov, samostatný Win paletový doplnok4 rozsahy/22 replay prípadov a ostatné replay počty zostávajú. PASS1 je stále57102 B PARTIAL,149 B CLASSIFIED ONLY,44 B UNKNOWN,0 B DEEP VERIFIED. Ide o merateľnú zhodu768/768 komponentov v tomto bode, nie nové percento úplnosti renderer oblasti. Nové sémantické percentáN/A. Dávka je lokálna, zatiaľ nepublikovaná.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Úplné menovatele chýbajú, preto N/A. Iniciačný runtime nie je percento gameplay completeness.

| Oblasť | Predošlý odhad | Nové % | Aktuálny dôkaz (staršie riadky zachované) | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|32asset kópií/3varianty;WindowsPCX celý ohraničený|DOSprefix1156B a bare768 pôvod|DOSprefix spotrebitelia|
| Dátové typy a konštanty |95 %|N/A|44 UNKNOWN adries sledovaných v skutočnom DOSBox behu; bez udalosti zmeny|čítanie, rovnaké zápisy a herný loop|read/write stopa za init|
| Tabuľky a ukazovatele |93 %|N/A|hook DS2356 má rovnaký relokovaný obsah v oboch endpoint dumpoch|medzistavy a nepriame čítanie|bezpečná kalibrácia nenulového watch|
| Funkcie / ASM / CFG |90 %|N/A|loader144B/53inštrukcií a DAC37B/21|I/O chybové vetvy|read failure scenáre|
| RNG |97 %|N/A|bez RNG runtime|prvý srand/rand|RNG caller trace|
| Scheduler |96 %|N/A|clock init prebehol medzi bodmi|main loop/scheduler|loop vstup|
| DEMO a vstupy |96 %|N/A|prirodzený INT9 install a aux probeFFFFh|key IRQ/DEMO poradie/close|prvý vstupný tick|
| Renderer / VGA |94 %|N/A|768 emulovaných DAC zložiek byte-exact; bits6/maskFF|framebuffer, clipping, fyzický VGA|video roviny a prvý frame|
| GUARD / bossovia |93 %|N/A|bez AI runtime|map init|selector doména|
| Zbrane / projektily |92 %|N/A|bez damage runtime|effect callery|damage trace|
| Sprity / HUD / paleta |92 %|N/A|DOS DAC readback = runtime buffer = asset SHR2|Win OS paleta a celková obrazová parita|Win capture a paired frame|
| SAVE / LOAD |92 %|N/A|BSF native file-check vrátený|SAVE/LOAD a chybové I/O|diskové scenáre|
| Windows Win16 |92 %|N/A|Win1104funkcie/229inštrukcií,23fixupcalls,22replay|skutočnéWin16DS/API/runtime|CreatePalette/WinG trace|

## Runtime testy na vykonanie

Zachytiť sequencer/graphics-controller/video roviny a prvý prirodzený frame. Paletový readback opakovať pri fade/update cestách a porovnať s pôvodnými buffermi. Win16 CreatePalette/WinG farby sú samostatná cesta. Pre UNKNOWN44B treba rozšíriť okno do resource/map init a doplniť skutočné read/write sledovanie.
