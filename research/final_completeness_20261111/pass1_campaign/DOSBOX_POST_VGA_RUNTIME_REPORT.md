# DOSBox-X: prirodzená post-VGA slot/resource inicializácia

Nová štvrtá zachovaná session spustila pôvodný packed DOS2 EXE a pokračovala za predchádzajúci návrat z VGA. Oproti seeded testom sa tu nemenia game registre, inštrukcie ani odpovede podvolaní. Kópie22 pôvodných vstupných súborov sú v izolovanom C:; originály boli po behu znovu hashované a zostali nezmenené. Použitý DOSBox-X aj packed EXE majú rovnaké SHA ako predchádzajúce tri scenáre.

## Presné body a dôkazy

|Kanonické miesto|Pozorované miesto|Výsledok|
|---|---|---|
|0201:000A|0A25:000A|slot initializer entry; DS=SS2F95,ES=A400|
|0476:012D|0C9A:012D|návrat slot init; BX57FA|
|0768:0024|0F8C:0024|resource mode0 entry; stack návrat0C9A:0134,arg0|
|0476:0134|0C9A:0134|resource mode0 vrátený; DS=SS2F95,ES=C3FF|

Loader základ je0824h. Slot vstupný stack obsahuje návrat0C9A:012D bez vstupných argumentov. Pred ním je všetkých1800B `[DS:50F2,DS:57FA)` nulových. Po návrate sa zmenilo **presne100B,0→1**, na offsetoch50F2+18*n,n0..99. Ostatných1700B zostalo byte-exact nezmenených. Dump pred/po a `slot_mutations.csv` uchovávajú tento dôkaz. Nepreukazuje to neprítomnosť dočasných zápisov počas slučky; tie podporuje už samostatne overené statické telo.

Po návrate resource inicializácie `[DS:34CC,DS:3504)` obsahuje **14 nenulových FAR pointerov s14 rôznymi linear adresami**. Pri každom z nich bol prečítaný presný6B header; všetky sú nulové. CSV `resource_pointer_observations.csv` uvádza slot, FAR aj linear adresu a header. Toto nie je dôkaz nulovosti celého alokovaného bloku ani úplný allocation trace. Funkcia môže vykonávať ďalšie alokácie alebo I/O, ktoré tento ohraničený bod neuzatvára. ES po návrate jeC3FF, teda nemožno rozšíriť DS=ES z niektorých starších bodov na celú init cestu.

## Nezávislá kontrola a reprodukcia

`runtime_dosbox_startup.py DOSBOX_EXE GAME_DIR IMAGE RELOC OUT WORK post_vga` vytvorí novú session. `verify_dosbox_startup_capture.py IMAGE RELOC OUT WORK` nezávisle overí celých171360 runtime image bajtov po1670 relokáciách, skoršie BSS/CRT/BSF/audio/VGA body aj všetky nové dumpy/stacks/stages. Transcript má56MEMDUMPBIN príkazov; allowlist pripúšťa iba PING,register query,code breakpointy,RUN a memory dump. Nepoužíva SR/SM na dosadenie stavu. Po poslednom bode harness ukončí svoj emulátor; jeho process return1 sa nepovažuje za pád hry ani prirodzený exit.

Každý dôkazový súbor má SHA v `independent_verification.json`; vstupné originály a kópie v `inputs.csv`, príkazy v `transcript.json`, registre v `snapshots.json`. Raw memory dumpy sú v priradenom WORK adresári. Generátor tejto správy pred zápisom znovu overuje všetky proof hash položky.

Summary SHA `91c49b499d8ba773d4ac8aa1315fd62480aec0624bcc0f38a5b5fd06d3b6ba9d`. Proof SHA `292ba6c5ffa5b29a5a0813b21e2c1c820e572172979163b0b1e628510a6e0f9c`. Slot pred SHA `09cec5a5bd8afffbb758753810a20c55ccb06a46d7bf54eda69ecd2ad645ef11`, po SHA `6e084c7e6555355d5947d30ce1c799837bdf3a991f6ef0fee24f4b78438a80fe`.

## Meranie

Prirodzené zachované DOSBox scenáre **3→4**. Scenáre majú spoločný startup prefix; nepočíta sa každý opakovaný breakpoint ako samostatný runtime test. Žiadny nový function range ani seeded replay prípad v tejto dávke. Katalóg118rozsahov a file-byte klasifikácia57102PARTIAL/149CLASSIFIED ONLY/44UNKNOWN/0DEEP VERIFIED ostávajú. Sloty aj heap sú mimo file image a PASS320 baseline. Nie je to úplná gameplay/render/audio/Win16 parita. Dávka je zatiaľ lokálna, nie nová GitHub publikácia.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Úplné menovatele chýbajú, preto N/A. Iniciačný runtime nie je percento gameplay completeness.

| Oblasť | Predošlý odhad | Nové % | Aktuálny dôkaz (staršie riadky zachované) | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|skutočný BSF54 B load/decode|iné BSF/role blokov|resource sloty v runtime|
| Dátové typy a konštanty |95 %|N/A|511 runtime DWORD mimo file|149 B iba klasifikované, 44 B UNKNOWN|nepriame segmentové prístupy|
| Tabuľky a ukazovatele |93 %|N/A|14 prirodzených FAR resource pointerov,6B hlavičky0|plný resource lifetime a obsah|resource slot consumers|
| Funkcie / ASM / CFG |90 %|N/A|prirodzený slot init a resource mode0 návrat|clipped draw a ďalšia init cesta|pokračovať za0476:0134|
| RNG |97 %|N/A|bez RNG runtime|prvý srand/rand|RNG caller trace|
| Scheduler |96 %|N/A|clock init prebehol medzi bodmi|main loop/scheduler|loop vstup|
| DEMO a vstupy |96 %|N/A|bez input/demo runtime|driver a demo|prirodzené demo|
| Renderer / VGA |94 %|N/A|mask/plane store,transparentnosť a unsigned depth|skutočné VGA registre a výstup|DOSBox frame dump|
| GUARD / bossovia |93 %|N/A|bez AI runtime|map init|selector doména|
| Zbrane / projektily |92 %|N/A|bez damage runtime|effect callery|damage trace|
| Sprity / HUD / paleta |92 %|N/A|VGA init, nie vizuálna parita|paleta/sprity|resource load|
| SAVE / LOAD |92 %|N/A|BSF native file-check vrátený|SAVE/LOAD a chybové I/O|diskové scenáre|
| Windows Win16 |92 %|N/A|bez Win runtime|NE prostredie|samostatný Win16 test|

## Runtime testy na vykonanie

Pokračovať za0476:0134 cez ďalšie inicializátory k resource dekódovaniu a prvému prirodzenému pending flush. Zachytiť pôvodné sloty/source/depth/VGA registre a porovnať štyri VRAM roviny. Pre NON-CODE44B treba stále read/write stopu nepriamych aliasov; úspech BSS inicializátora tieto intervaly neuzatvára.
