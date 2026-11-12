# Post-VGA inicializácia: 100 samostatných BYTE s krokom 18

Nový ohraničený rozsah **0201:000A..001A**, image **[201A,202A)**, má 16 B / 6 inštrukcií. Priamy FAR caller je **0476:0128**, image4888h, bezprostredne po už runtime zachytenom VGA návrate a debug log calleri. Caller dokazuje statickú väzbu; táto dávka ešte nedokazuje jeho prirodzené vykonanie za posledným runtime breakpointom.

```asm
mov bx,50F2h
loop: mov byte ptr [bx],1
add bx,12h
cmp bx,57FAh
jb loop
retf
```

```c
// Actual instructions use inherited DS; no explicit DS initialization here.
for (uint16_t p = 0x50f2; p < 0x57fa; p += 18)
    DS_byte[p] = 1;
// BX=0x57fa; CF=0, ZF=1 from final CMP; DF unchanged.
```

Presne 100 zápisov BYTE: prvý DS:50F2, posledný DS:57E8. Na základe predpokladu DS=2771h ide o image-relative **2C802h..2CEF8h** s medzerami; posledná adresa je **2CEF8h**. Nominálny obal `[2C802,2CF0A)` má 1800 B, ale funkcia **neinicializuje ani netypuje všetkých 1800 B**. Týchto 100 bajtov je mimo file image aj historických 57295 NON-CODE bajtov. Celá rola záznamov a ostatných 17 B na slot zostáva otvorená. Názov katalógu `renderer_slot_byte_init` je pracovný názov podľa polohy v inicializačnej ceste, nie dôkaz finálnej hernej/renderer sémantiky.

CFG má vstupný MOV, loop telo MOV/ADD/CMP/JB a FAR návrat; bez callee, bez tabuľky skokov. Funkcia nemení DS/ES/SS, AX/CX/DX/SI/DI/BP. Mení BX a aritmetické flagy. Nemá vstupný stack argument a FAR návrat odstráni 4 B. ES nie je používaný. DF nie je vstupný predpoklad, keďže nejde o string inštrukciu.

## Reprodukcia a skúšky

`audit_renderer_slot_initializer.py IMAGE INVENTORY ABS_DECODER ABS_EMULATOR VERSIONS_DIR OUT` overuje SHA kanonického obrazu, presný 16 B rozsah, caller bajty, všetkých šesť dekódovaných hraníc proti inventáru. Native Unicorn replay používa 2 load bázy × 2 DF × 2 počiatočné CF × 8 obsahových vzorov = **64 prípadov, 0 odchýlok**. Memory hook overuje všetkých 100 adries, šírku a hodnotu, dump celého obalu s oboma guard bajtmi odhalí vedľajšie zápisy. Registre, SP a finálne CF/ZF/DF sú skontrolované. Žiadne callee ani OS odpovede sa nemodelujú. Ide o seeded replay, nie nový DOSBox runtime scenár.

## DOS cross-version

Presný nemaskovaný 16 B podpis má iba DOS20. Normalizácia mení výhradne dve 16-bit immediate adresy start/end, zachováva opcode, krok18, hodnotu1, JB späť aj RETF. Každá verzia má práve jedného kandidáta a nominálne 100 slotov. Osem štítkov obsahuje sedem unikátnych obrazov. Menované obrazy sa hashujú samostatne; úplná byte/CFG/behavior parita verzií z toho nevyplýva. Win16 sa touto skúškou neposudzuje.

|DOS štítok|Image začiatok|DS začiatok|DS koniec exclusive|Sloty|
|---|---:|---:|---:|---:|
|10|200Ch|4F48h|5650h|100|
|11|200Ch|504Eh|5756h|100|
|12|200Ch|504Eh|5756h|100|
|15|201Ah|501Eh|5726h|100|
|17|201Ah|5060h|5768h|100|
|18|201Ah|50F0h|57F8h|100|
|19|201Ah|50F0h|57F8h|100|
|20|201Ah|50F2h|57FAh|100|

## Meranie pokrytia

PASS1 bez zmeny: **57102 B PARTIAL,149 B CLASSIFIED ONLY,44 B UNKNOWN,0 B DEEP VERIFIED**. Katalóg sa rozširuje o jeden rozsah/6 inštrukcií/16 B; počet seeded replay prípadov rastie o64. Runtime zostáva tri uchované scenáre. Nominálny BSS obal sa nepripočítava k typovaným dátam ani k runtime reciprocal tabuľke. Nové sémantické percentá ostávajú N/A bez úplných menovateľov.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Úplné menovatele chýbajú, preto N/A. Iniciačný runtime nie je percento gameplay completeness.

| Oblasť | Predošlý odhad | Nové % | Aktuálny dôkaz (staršie riadky zachované) | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|skutočný BSF54 B load/decode|iné BSF/role blokov|resource sloty v runtime|
| Dátové typy a konštanty |95 %|N/A|511 runtime DWORD mimo file|149 B iba klasifikované, 44 B UNKNOWN|nepriame segmentové prístupy|
| Tabuľky a ukazovatele |93 %|N/A|12 lokálnych FAR konštrukcií 21FD:264E odlíšených od DS:264E|aliasy/dynamické indexy|watchpointy na 44 UNKNOWN B|
| Funkcie / ASM / CFG |90 %|N/A|nový 6-inštrukčný init, 64 replay prípadov|slot konzumenti/CFG calleri|0201 slot writeri|
| RNG |97 %|N/A|bez RNG runtime|prvý srand/rand|RNG caller trace|
| Scheduler |96 %|N/A|clock init prebehol medzi bodmi|main loop/scheduler|loop vstup|
| DEMO a vstupy |96 %|N/A|bez input/demo runtime|driver a demo|prirodzené demo|
| Renderer / VGA |94 %|N/A|statický post-VGA init 100 BYTE s krokom18|rola slotov, clipping, frame|spotrebitelia DS:50F2|
| GUARD / bossovia |93 %|N/A|bez AI runtime|map init|selector doména|
| Zbrane / projektily |92 %|N/A|bez damage runtime|effect callery|damage trace|
| Sprity / HUD / paleta |92 %|N/A|VGA init, nie vizuálna parita|paleta/sprity|resource load|
| SAVE / LOAD |92 %|N/A|BSF native file-check vrátený|SAVE/LOAD a chybové I/O|diskové scenáre|
| Windows Win16 |92 %|N/A|bez Win runtime|NE prostredie|samostatný Win16 test|

## Runtime testy na vykonanie

Pokračovať pôvodným EXE za VGA breakpointom cez 0201:000A, zachytiť DS/ES/SS a 1800 B pred/po s presným zoznamom 100 mutácií. Potom sledovať slotové writer/consumer funkcie vrátane 0201:001A a ich indexové domény; samotný krok18 neurčuje kompletný typ záznamu. Pre UNKNOWN oblasti je potrebná read/write stopa; BPM/BPLM v dodanom zdrojovom debuggeri označujú memory-change breakpointy a navyše sú podmienené C_HEAVY_DEBUG. Bez overenia konkrétneho buildu ich nemožno prezentovať ako dostupné read-watchpointy.
