# PASS1: CRT stream buffer cache

6 B CLASSIFIED ONLY → PARTIAL, tri mutable NEAR16 ukazovatele s počiatočnou nulou. Konzument je 11EE:0B4A, image [12A2A,12A9D), 115 B / 47 inštrukcií. Pôvodné inštrukcie a ich hranice sú nezávisle overené proti kanonickému obrazu. Stav PARTIAL; žiadny DEEP VERIFIED.

| Image interval (koniec exkluzívny) | DS offset | Rozpoznaný stream |
|---|---|---|
|[299CC,299CE)|22BC|2182|
|[299CE,299D0)|22BE|218A|
|[299D0,299D2)|22C0|219A|

Názvy stdin/stdout/stderr sa k týmto trom konkrétnym väzbám nedopĺňajú bez dôkazu inicializácie a identity. Typ ukazovateľa je doložený tým, že hodnota sa kopíruje do dvoch buffer pointer polí streamu po úspešnej alokácii alebo z cache. Samotný obsah alokovaného bufferu sa tu nedereferencuje.

## ABI, CFG a pseudokód

NEAR vstup, argument stream near offset [SS:BP+4], NEAR RET. Volajúci upratuje argument. Zachová BP/SI/DI; BX/AX sú pracovné. DS musí byť DGROUP; SS je v testoch nezávislý. ES sa v tele helpera nepoužíva, register kontrakt alokátora však nie je touto dávkou uzavretý. Export CFG je cfg_edges.csv, ASM crt_stream_cache_attach.csv.

```c
uint16_t attach_cached_buffer(nearptr stream) {
    nearptr slot;
    if (stream == 0x2182) slot = 0x22BC;
    else if (stream == 0x218A) slot = 0x22BE;
    else if (stream == 0x219A) slot = 0x22C0;
    else return 0;
    nearptr aux = stream - 0x217A + 0x221A;
    if (DS.u8[stream + 6] & 0x0C) return 0;
    if (DS.u8[aux] & 1) return 0;
    uint16_t p = DS.u16[slot];
    if (p == 0) {
        p = allocator_11EE_3CCF(512); // caller spotrebuje iba AX
        if (p == 0) return 0;
        DS.u16[slot] = p;
    }
    DS.u16[stream] = p;
    DS.u16[stream + 4] = p;
    DS.u16[stream + 2] = 512;
    DS.u16[aux + 2] = 512;
    DS.u8[stream + 6] |= 2;
    DS.u8[aux] = 0x11; // prepis, nie OR
    return 1;
}
```

Cache sa pri pripojení nenuluje a nenulová hodnota sa prijíma vrátane FFFFh; pointer validitu tento helper nekontroluje. Pri blokujúcich príznakoch sa nevolá alokátor a neprepíše sa cache ani metadata. Nulový výsledok alokátora vráti 0. Aux flag sa pri úspechu prepíše na 11h, nie iba doplní bit. Pôvodný alokátor, jeho uvoľňovanie a prirodzené znovupoužitie cache zostávajú otvorené.

## Kontrolovaná emulácia

36 864 prípadov = 2 load bázy × 3 rozpoznané streamy × 256 stream flag BYTE × 4 aux flag (0,1,2,255) × 3 cache pointery (0,1234h,FFFFh) × 2 výsledky alokátora (0,5678h). Model alokátora overuje argument 512, vracia AX a odlišné DX=ABCDh, ktoré helper nespotrebuje. Žiadne pôvodné OS alokácie ani file I/O.

Overujú sa celé 8-bajtové streamové a 4-bajtové aux rozsahy, cache WORD, počet volaní, AX a SP/BP/SI/DI/DS. Dosiahnutých všetkých 47 začiatkov inštrukcií, nie všetkých možných CFG hrán: nerozpoznaný stream je zatiaľ potvrdený statickou vetvou, nie replay maticou. Nulové odchýlky. Nejde o prirodzený DOS runtime alebo celú CRT knižnicu.

Reprodukcia: audit_replay_pass1_stream_cache.py IMAGE INVENTORY DECODER EMULATOR OUT; promote_pass1_fields.py s predchádzajúcou mapou pass1_direction_vectors; verify_pass1_partition.py. Kanonický obraz SHA-256 e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297; iced-x86 1.21.0, Unicorn 2.1.4. Relokácie pochádzajú zo skutočného rozbalenia EXE.

## Meranie

**57 037 B PARTIAL, 214 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57 295 B. Nezávislá kontrola 868 intervalov potvrdila presné členstvo a všetky hash hodnoty, bez dier alebo prekryvov. Integrita partition nie je dôkaz úplnej sémantiky. Posledná publikovaná GitHub snímka zatiaľ túto lokálnu dávku neobsahuje. Prirodzených runtime testov 0.

SHA mapy `1bfa32407092fcc8ff41b88b79d19d1fc0566b924fb140c98297d9c47ca8e413`; SHA cases `3371d00583a2fe3401cc0e2d5043e11d107a9edf83bd683420f170c82dfbe765`.

## Aktualizácia 13 oblastí

Metodika nového %: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, nové percentá N/A. Predošlé hodnoty sú historické orientačné odhady, nemerajú túto dávku.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|bez nového dôkazu|loader hranice|map closure|
| Dátové typy a konštanty |95 %|N/A|6 B PARTIAL|214 B iba klasifikované|zvyšné nepriame odkazy|
| Tabuľky a ukazovatele |93 %|N/A|3 NEAR cache sloty|identita streamov|startup identifikácia|
| Funkcie / ASM / CFG |90 %|N/A|115 B / 47 inštrukcií|pôvodný alokátor|caller a allocator kontrakt|
| RNG |97 %|N/A|bez nového dôkazu|prirodzené poradie|DEMO trace|
| Scheduler |96 %|N/A|bez nového dôkazu|prirodzené callery|call graph|
| DEMO a vstupy |96 %|N/A|bez nového dôkazu|driver ABI|input closure|
| Renderer / VGA |94 %|N/A|bez nového dôkazu|setup|VGA init CFG|
| GUARD / bossovia |93 %|N/A|bez nového dôkazu|selector doména|descriptor flag 8|
| Zbrane / projektily |92 %|N/A|bez nového dôkazu|damage callery|effect producer|
| Sprity / HUD / paleta |92 %|N/A|bez nového dôkazu|identity|descriptor producer|
| SAVE / LOAD |92 %|N/A|CRT buffer helper oddelený|skutočné herné I/O|stream caller trace|
| Windows Win16 |92 %|N/A|bez nového Win dôkazu|CRT parita|nájsť ekvivalent|

## Runtime testy na vykonanie

V DOSBox-X sledovať tri cache sloty pri prvom a opakovanom pripojení bufferu, zaznamenať identitu streamov a ich uvoľnenie pri ukončení. Pri zlyhaní alokácie overiť návrat 0 a nasledujúce správanie callerov. Žiadna z týchto prirodzených runtime skúšok ešte neprebehla; PE32 sa nevytvára.
