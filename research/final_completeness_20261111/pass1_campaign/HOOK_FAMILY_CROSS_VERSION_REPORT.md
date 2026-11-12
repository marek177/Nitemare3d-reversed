# PASS1: neuzavretý CRT hook naprieč DOS verziami

Nová dávka rozširuje ohraničený negatívny dôkaz pre slot **DOS20 DS2356**, image `[29A66,29A6A)`. Predošlý audit overoval priame memory displacements iba v DOS20 inventári. Teraz sa hook rodina identifikuje nezávisle v každom z8 DOS štítkov (7 unikátnych obrazov) podľa7 rovnakých FAR inicializérov smerujúcich do vlastného CRT segmentu a cieľového stubu MOVAX2/JMP.

## Výsledok porovnania

|DOS|DS:začiatok rodiny|Piaty slot DS offset|Stub IP v CRT|Priame DS referencie rodiny|Raw WORD výskyty offsetu piateho slotu|
|---|---|---:|---:|---:|---:|
|10|2360:2240|2250h|02B8h|6|0|
|11|2395:2338|2348h|02C0h|6|1|
|12|239B:2334|2344h|02C0h|6|0|
|15|274A:2306|2316h|02C4h|6|0|
|17|2754:230A|231Ah|02C0h|6|1|
|18|276D:2344|2354h|02C4h|6|0|
|19|276D:2344|2354h|02C4h|6|0|
|20|2771:2346|2356h|02C0h|6|0|

V každej verzii má rodina6 explicitných neindexovaných DS referencií, po jednej na sloty0,1,2,3,5,6. **Slot index4 (piaty) nemá žiadnu**. V rozsahu displacementov rodiny sa nenašli ďalšie indexované alebo inosegmentové kandidáty v dodaných inventároch. Toto nevylučuje register pointer odvodený inde, implicitný prístup, prepísaný pointer alebo kód mimo inventára.

V DOS20 je pri úplnom raw prehľadaní celého171360B obrazu počet dvojice bajtov **56 23 nulový**. Tento silnejší, od inštrukčných hraníc nezávislý výsledok vylučuje iba explicitne zakódovanú WORD hodnotu2356h v tomto obraze, nie vypočítanú adresu/alias. Rovnako sa v historickej code doméne nenachádza dvojica58 23 pre segmentový WORD2358h; tento doplnkový prieskum nie je základom promócie.

Dve raw zhody v iných verziách sa rozlíšili cez presné hranice inštrukcií. DOS11 offset2348h vzniká na image2409h cez `48` (DECAX) + `23` (začiatok ANDAX,DX), teda naprieč dvoma inštrukciami. DOS17 offset231Ah sa vyskytuje na image85F5h v `26 C6 44 1A 23`, t. j. spojením displacement1Ah a immediate23h pri BYTE store ES:[SI+1A]. Nejde o WORD address operand231Ah. Výstup `slot4_raw_hit_context.csv` uchováva obidva prípady a ich pôvodné instruction bytes.

## Čo zostáva neuzavreté

Sedem slotov má vždy spoločný cieľ MOVAX2 a tail JMP do CRT error cesty. Počiatočný vzhľad a stabilita nepodporujú automatické typové povýšenie siedmeho slotu podľa susednosti. DOS20 segmentový WORD `[29A68,29A6A)` preto zostáva2PARTIAL bajtmi bez uzavretej typovej roly; ďalšie2B offset WORD stále nie sú týmto auditom typovo uzavreté. Dosiahnuteľnosť a runtime modifikácie slotu sa nevylúčili. Neoznačuje sa ako unused, dead, padding ani DEEP VERIFIED.

Presné autorstvo runtime knižnice/kompilátora sa týmto neidentifikuje. Cross-version rodina je štrukturálny a byte dôkaz, nie úplná CFG/behavior parita DOS ani Win16. Metadata DS/CRT a už rozbalené obrazy sú hashované; pôvodný unpack sa v tejto dávke neopakoval pre všetky verzie.

## Reprodukcia a artefakty

`audit_hook_family_versions.py VERSION_CSV ABS_DECODER OUT` používa manifest `crt_entry_gap_versions/versions.csv`, kontroluje image SHA a metadata, hľadá jedinú7-slot rodinu so správnym target stubom, nezávisle overí všetky inštrukčné bajty a dekódovanie inventárov. Potom enumeruje explicitné memory operand kandidáty aj všetky raw WORD zhody pre každý slot. Výstupy `versions.csv`, `slots.csv`(56riadkov), `reference_candidates.csv`, `slot4_raw_hit_context.csv` a summary pripínajú dôkazy. `write_hook_family_versions_report.py OUTPUTS` generuje správu a aktualizáciu13oblastí.

Overených inštrukčných začiatkov naprieč8 štítkami: **283862**; duplicitné18/19 nie sú dva nezávislé obrazy. Manifest SHA `1d571332b200d695d5a21a91422d1f83e03fe59d6755e5662b50025d8dab2968`.

## Meranie

Žiadne nové promócie, funkčné rozsahy, replay ani runtime session. Aktuálne57102PARTIAL/149CLASSIFIED ONLY/44UNKNOWN/0DEEP VERIFIED,122funkčných rozsahov a5prirodzených DOSBox scenárov zostávajú. Nové sémantické percentá N/A bez úplných menovateľov. Dávka je lokálna, nie nová GitHub publikácia.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Úplné menovatele chýbajú, preto N/A. Iniciačný runtime nie je percento gameplay completeness.

| Oblasť | Predošlý odhad | Nové % | Aktuálny dôkaz (staršie riadky zachované) | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|skutočný BSF54 B load/decode|iné BSF/role blokov|resource sloty v runtime|
| Dátové typy a konštanty |95 %|N/A|511 runtime DWORD mimo file|149 B iba klasifikované, 44 B UNKNOWN|nepriame segmentové prístupy|
| Tabuľky a ukazovatele |93 %|N/A|7-slot CRT rodina v8 DOS verziách; piaty slot otvorený|vypočítané aliasy/writeri DS2356|runtime hook watch|
| Funkcie / ASM / CFG |90 %|N/A|4 nové API/probe wrappers,88B/37inštrukcií|INT86 a ISR telá|ISR interrupt kontrakt|
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

Zachytiť všetkých7 relokovaných slotov pred/po floating-support inicializácii a sledovať prípadné writeri alebo vykonanie spoločného02C0 cieľa. Použiť memory-change breakpointy len po overení ich dostupnosti v konkrétnom heavy-debug builde; neprítomnosť zmeny nie je dôkaz neprítomnosti čítania. Hľadať register-derived prístupy aj mimo pôvodného inventára, samostatne mapovať ekvivalentWin16. Pokračovať paralelne v prirodzenej inicializačnej ceste za0476:015C.
