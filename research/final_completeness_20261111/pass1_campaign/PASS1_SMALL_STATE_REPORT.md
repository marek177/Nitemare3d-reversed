# PASS1: malé stavové polia a NEAR ukazovatele

Táto dávka klasifikuje 19 nových bajtov pomocou 28 priamych DS operandov overených voči kanonickému DOS 2.0 obrazu. Všetkých 12 polí má stav PARTIAL. Prirodzené runtime testy ani nové DEEP VERIFIED bajty nepribudli.

Adresy nižšie sú offsety rozbaleného obrazu, koniec je exkluzívny. DS offset sa počíta od 27710h. Statické DS operandy nedokazujú prirodzený segmentový kontext každého volania. Význam vyšších úrovní je otvorený tam, kde ho uvedený konzument nepotvrdzuje.

| Začiatok | Koniec | Inicializačné bajty | Typ | Dôkaz / limit |
|---|---|---|---|---|
|278BC|278BE|0000|cached_handle_WORD|0277:008D tests zero; 00A1 writes AX; 00BC/00CE pass handle|
|27954|27955|01|one_time_init_BYTE|0277:018E tests; 0199 clears DL|
|27D88|27D89|01|one_time_gate_BYTE|0277:176A tests; 1771 clears|
|281E2|281E4|ffff|episode_cache_key_WORD|04C7:0B7D compares episode; 0B83 stores; following class 41/42 lookup|
|283AC|283AE|0000|cyclic_selector_WORD|0768:04E2 indexes FAR pointer table; 04FB increments; 04FF signed bound; 0505 resets|
|28C17|28C18|01|toggle_BYTE|083D:1504 tests; 152E XOR 1|
|28E00|28E01|00|lifecycle_latch_BYTE|0BCC:0084/00EC tests; 00E5 sets; 011B clears|
|28EF6|28EF7|00|sound_priority_BYTE_unsigned|0C2B:040B/0426 unsigned compare; 0436 writes incoming priority AL|
|297EE|297F0|f201|startup_NEAR_code_pointer|11EE:00EE assigns 01EB; 011C indirect near CALL; initial 01F2|
|29832|29834|0000|startup_mode_WORD_low_BYTE_consumed|11EE:0316 loads WORD; AL compared with 2; high-byte role unresolved|
|29888|2988A|0000|CRT_counter_WORD|11EE:0B0B increments; higher-level purpose unresolved|
|29C42|29C44|0000|optional_initializer_NEAR_pointer|11EE:00B3 loads CX; JCXZ skips; 00B9 CALL CX|

DS:17E6 je priorita: pri obsadenom zvukovom kanáli vetvy porovnávajú starú hodnotu s prichádzajúcim AL neznamienkovo. Zápis nasleduje až po prechode bránami. Nie je to dôkaz identity zvuku ani overenie WORX prehrávania. Ďalší krok je uzavrieť CFG 0C2B:03D6 a overiť poradie stop/resource/play závislostí.

DS:20DE je NEAR ukazovateľ: počiatočná hodnota 01F2h, startup zápis 01EBh a nepriamy CALL. DS:2532 je voliteľný NEAR inicializátor: nulový CX preskočí CALL CX. Ciele a celý startup zostávajú PARTIAL. DS:2122 sa načítava ako WORD, ale uvedená vetva spotrebúva AL; význam horného bajtu sa nedopĺňa hypotézou.

Susedné nulové bajty neboli povýšené na padding. Neboli analyzované celé funkcie ani pridané funkčné pokrytie. CSV direct_references uchováva adresy, pôvodné bajty a nezávislý disassembly; data_fields obsahuje hash každého intervalu. Reprodukcia: audit_pass1_small_state.py IMAGE INVENTORY DECODER OUT, potom promote_pass1_fields.py a verify_pass1_partition.py s predchádzajúcou mapou pass1_file_info.

## Meranie

19 B CLASSIFIED ONLY → PARTIAL. Aktuálne **56 930 B PARTIAL, 321 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57 295 B. Nezávislá kontrola 862 intervalov overila presné členstvo baseline a všetky hash hodnoty bez dier alebo prekryvov. Integrita mapy nedokazuje úplnú sémantiku.

SHA-256 mapy: `08c1dc3cb14cf0aaf1b133109e23db164a4a824093d5cba47ef75d0724d7bbc5`. GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 neobsahuje túto lokálnu dávku.

## Aktualizácia 13 oblastí

Nové percento = uzavreté jednotky / úplný inventár oblasti. Úplné menovatele chýbajú, preto N/A; historické orientačné percentá sa neprepočítavajú z počtu odkazov ani z integrity mapy. Pri oblastiach bez nových dôkazov sa výsledok nemení.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|bez nového dôkazu|hranice loadera|uzavrieť loader|
| Dátové typy a konštanty |95 %|N/A|19 B / 12 polí PARTIAL|321 B iba klasifikované|analyzovať zostávajúce intervaly|
| Tabuľky a ukazovatele |93 %|N/A|2 NEAR ukazovatele|startup ciele|sledovať nepriame volania|
| Funkcie / ASM / CFG |90 %|N/A|28 overených priamych operandov|celé funkcie otvorené|CFG 0C2B:03D6|
| RNG |97 %|N/A|bez nového dôkazu|prirodzené poradie|DEMO trace|
| Scheduler |96 %|N/A|bez nového dôkazu|prirodzené callery|call graph|
| DEMO a vstupy |96 %|N/A|jednorazové stavové brány|vyššia funkcia|uzavrieť konzumentov|
| Renderer / VGA |94 %|N/A|bez nového dôkazu|inicializácia VGA|setup CFG|
| GUARD / bossovia |93 %|N/A|epizódový kľúč class 41/42|celý lifecycle|health updater|
| Zbrane / projektily |92 %|N/A|zvuková priorita BYTE|skutočné audio efekty|priority dispatch replay|
| Sprity / HUD / paleta |92 %|N/A|cyklický index WORD|celý konzument|0768:04D8 CFG|
| SAVE / LOAD |92 %|N/A|cache handle WORD|účel a prirodzené I/O|0277:008A closure|
| Windows Win16 |92 %|N/A|bez nového Win dôkazu|parita týchto polí|nájsť zodpovedajúce funkcie|

## Runtime testy na vykonanie

V DOSBox-X sledovať prirodzené DS:17E6 pri prekrývaní zvukov s nižšou, rovnakou a vyššou prioritou; zaznamenať DSP aj druhú zvukovú vetvu. Sledovať epizódový kľúč 0AD2 pri prechode epizód a hodnotu 0C9C pri obehnutí rozsahu. Startup ukazovatele sledovať od načítania po ukončenie procesu. Priložený dosbox-n3d.zip bol skontrolovaný, ale jeho Linux ELF sa v tomto Windows prostredí prirodzene nespustil; tieto testy neboli vykonané. PE32 portovanie sa nevykonáva.
