# 18-bajtové sloty: producent a spracovanie čakajúcich položiek

Nový rozsah **0201:072C..0761**, obraz **[273C,2771)**: **53 B/22 inštrukcií**. Prejde presne 100 slotov od DS:50F2 s krokom18; flag +0 rovný nule je čakajúci, akákoľvek nenulová hodnota sa preskočí. Toto objasňuje predchádzajúci inicializátor, ktorý všetky príznaky nastavoval na1.

```c
for (uint16_t p = 0x50f2, n = 100; n; --n, p += 18) {
    if (DS_byte[p] != 0) continue;
    uint16_t resource = DS_word[p + 6];
    if (DS_dword[resource + 6] == 0)
        far_0768_04d8(resource); // external callee, not closed by this replay
    far_0156_05de(p);           // external renderer, not closed by this replay
    DS_byte[p] = 1;
}
```

Test resource pointera je bitový DWORD test rovnosti nule, nie signed pozitívnosť. Ak load helper vráti pointer stále nulový, wrapper ho znovu nekontroluje a aj tak volá renderer. Príznak nastaví na1 až po návrate renderera. Nejde o meranie úspešnosti renderera alebo potvrdený hardvérový draw.

## Producent a lokálny layout

Statický fragment **0AEA:05D6..060F** najprv overí príznak nenulový, potom nastaví +0=0, uloží DWORD z FAR argumentu SS:[BP+6] do +2, WORD resource pointer do +6 a päť WORD parametrov do +8,+Ah,+Ch,+Eh,+10h. Cesta preskakuje obsadené sloty v krokoch18; úplné hranice predchádzajúceho indexového výpočtu zostávajú otvorené. Doložené ASM je `slot_producer_context.csv`; nejde o uzavretie celého veľkého producenta.

|Offset|Šírka|Doložená rola|
|---:|---:|---|
|0|1|pending0 / skip nonzero; init1, producer0, flush1|
|1|1|UNKNOWN; tento fragment ho nečíta ani nezapisuje|
|2|4|uložený FAR object argument; úplní spotrebitelia otvorení|
|6|2|NEAR pointer do zdrojového/resource záznamu v DS|
|8,A,C,E,10|2 každý|renderer parametre, presné jednotky a celý kontrakt otvorené|

Renderer na0156:05E7 načíta slot+6 doSI a číta zdrojový záznam; začiatok tejto funkcie navyše používa +8,+Ah,+Ch,+Eh. Tým je resource pointer interpretácia viac než len podobnosť DWORD/WORD hodnôt. Samotná existencia renderera však neuzatvára clipping, mierku a VGA zápisy.

Predpokladaný default DS=2771h mapuje sloty do BSS obalu `[2C802,2CF0A)`, mimo file image `[0,29D60)`. Žiadnych 1800 B sa nepridáva k historickému PASS1 ani k file-typed počtu. Layout je samostatný PARTIAL katalóg `bss_slot_layout.csv`, nie DEEP VERIFIED. Bajt+1 zostáva výslovne UNKNOWN.

## CFG a ABI

Vstup ukladá DI/SI, SI=50F2, DI=100. Vetva skip a resource-null vetva sa zbiehajú pred krokom SI+=18, DI--, JNE. Dve priame FAR volania; žiadna jump tabuľka. Calleri odstraňujú každý jeden WORD argument. FAR návrat, bez vlastných argumentov. Wrapper obnoví SI/DI a nemení BP; AX/BX/CX/DX/ES/flags nie sú garantované cez neuzavreté callee. DS/SS sa lokálne neprepínajú a správny zdedený DS aj zachovanie potrebných registrov callee sú podmienkou kontraktu. Netvrdí sa univerzálne DS=SS=ES.

## Reprodukcia a hranice skúšky

`audit_replay_slot_flush.py IMAGE INVENTORY ABS_DECODER ABS_EMULATOR OUT` overí presný kanonický SHA, všetky53B/22inštrukcií, producentov fragment a aplikuje1670 skutočných relokácií pre dva load segmenty. Native wrapper beží s modelovanými iba dvoma externými callee cez RETF; prvý môže navyše dosadiť resource DWORD. Originálne súbory sa nemenia.

**128 prípadov,0 odchýlok**: 2load ×8layout ×4resourceDWORD(0,1,80000000h,FFFFFFFFh) ×2load-callee správania. Layouty zahŕňajú all1/all0/all2/allFF, striedanie, zmiešané a prvý/posledný čakajúci slot. Overuje sa presné poradie a argumenty každého callee, flag0 v čase draw, všetkých1800B s guard bajtmi, resource DWORD a DS/BP/SI/DI/SP. `callee_events.csv` uchováva jednotlivé udalosti. Testy nepreukazujú telá callee ani prirodzený runtime tejto cesty.

SHA cases `321cb5a39be101b1f58100d8434e7894503806b913125b99ad9432b001456ccd`. Pribúda1 funkcia/22inštrukcií/53B a128 seeded scenárov. PASS1 zostáva57102PARTIAL/149CLASSIFIED ONLY/44UNKNOWN/0DEEP VERIFIED; tri DOSBox scenáre sa nemenia. Dávka zatiaľ nie je publikovaná na GitHube.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Úplné menovatele chýbajú, preto N/A. Iniciačný runtime nie je percento gameplay completeness.

| Oblasť | Predošlý odhad | Nové % | Aktuálny dôkaz (staršie riadky zachované) | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|skutočný BSF54 B load/decode|iné BSF/role blokov|resource sloty v runtime|
| Dátové typy a konštanty |95 %|N/A|511 runtime DWORD mimo file|149 B iba klasifikované, 44 B UNKNOWN|nepriame segmentové prístupy|
| Tabuľky a ukazovatele |93 %|N/A|12 lokálnych FAR konštrukcií 21FD:264E odlíšených od DS:264E|aliasy/dynamické indexy|watchpointy na 44 UNKNOWN B|
| Funkcie / ASM / CFG |90 %|N/A|nový flush53B/22inštrukcií,128 replay prípadov|callee telá a prirodzené callery|native renderer integrácia|
| RNG |97 %|N/A|bez RNG runtime|prvý srand/rand|RNG caller trace|
| Scheduler |96 %|N/A|clock init prebehol medzi bodmi|main loop/scheduler|loop vstup|
| DEMO a vstupy |96 %|N/A|bez input/demo runtime|driver a demo|prirodzené demo|
| Renderer / VGA |94 %|N/A|slot producer→pending→renderer→done|clipping, resource decoder a výstup|0156:05DE telo|
| GUARD / bossovia |93 %|N/A|bez AI runtime|map init|selector doména|
| Zbrane / projektily |92 %|N/A|bez damage runtime|effect callery|damage trace|
| Sprity / HUD / paleta |92 %|N/A|VGA init, nie vizuálna parita|paleta/sprity|resource load|
| SAVE / LOAD |92 %|N/A|BSF native file-check vrátený|SAVE/LOAD a chybové I/O|diskové scenáre|
| Windows Win16 |92 %|N/A|bez Win runtime|NE prostredie|samostatný Win16 test|

## Runtime testy na vykonanie

Zachytiť prirodzený vstup do0201:072C, slot+0 pred/po, resource+6 a priamy renderer entry. Overiť pôvodnú DS a callee zachovanieSI/DI; porovnať VGA pamäť pred/po oddelene od flagu1. Uzavrieť indexovanie producenta a prístupy k neznámemu slot BYTE+1. Pre UNKNOWN file intervaly pokračuje samostatný read/write audit; tieto BSS sloty ich neuzatvárajú.
