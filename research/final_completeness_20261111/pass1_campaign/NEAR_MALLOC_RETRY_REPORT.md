# CRT: integrovaný near malloc a retry callback

Stav PARTIAL. Nový lokálny vstup **11EE:3CCF..3D0A**, image **[15BAF,15BEA)**, **59 B / 27 inštrukcií**. Jeho pôvodné ASM a CFG sú nezávisle dekódované a overené voči kanonickému image aj starému inventáru. Replay vykonáva tento vstup spolu s pôvodnými scan2168, grow21E4, finder22C1, resize2270 a v jednom callbackovom scenári aj pôvodným free3CAE. Mapa NON-CODE sa nemení.

## ABI a algoritmus

FAR vstup, request WORD [SS:BP+6]. Caller upratuje jeden WORD. BP/SI/DI sa obnovia, DX:AX nesie výsledný pointer, pri lokálne potvrdenom neúspechu je 0:0. DS ostáva DGROUP v testovanom kontrakte pôvodných callee a modelovaného DOS/callbacku; ich ľubovoľné register clobber správanie sa nepredpokladá. Flags po návrate nie sú úspechový kontrakt malloc; CF je vnútorný kontrakt helperov.

```c
farptr near_malloc(uint16_t request) {
retry:
    if (request <= 0xFFE8) {
        if (scan(root20E2, request).success) return pointer;
        if (grow(root20E2, request).success)
            if (scan(root20E2, request).success) return pointer;
    }
    if (WORD[252E] | WORD[2530]) {
        uint16_t again = FAR_CALLBACK[252E](request);
        if (again != 0) goto retry;
    }
    return FAR_NULL;
}
```

Limit je unsigned FFE8h vrátane, FFE9h a FFFFh sa k skenu vôbec nedostanú. Aj tento odmietnutý request však môže volať callback. Test callbacku používa OR oboch WORD pointera, nie len nenulový segment. Pri každom retry sa CX znovu načíta z pôvodného stack argumentu. Callback môže upraviť pamäťový stav, ale lokálny request sa automaticky nemení.

Návrat callbacku nie je obmedzený na 1: v matici FFFFh vyvolá opakovanie. Nulový callback alebo návrat0 končí AX=0 a CWD nastaví DX=0. Neukončený opakovaný nenulový callback by mohol opakovať stále; táto dávka modeluje najviac jeden nenulový návrat a potom0 a netvrdí všeobecnú termináciu ľubovoľného callbacku.

## Integračná matica

640 prípadov = 2 load bázy × 2 grow flags × 2 počiatočné tagy × 8 request × 2 výsledky DOS × 5 callback politík. Jedna počiatočná 16 B payload reťaz s tail sentinel, root20E2, quantum16 zo SS. Request0,1,16,17,128,FFE8h,FFE9h,FFFFh. Politiky: absent; návrat0; uvoľni blok a raz vráť FFFFh; povoľ grow a raz vráť FFFFh; raz vráť FFFFh bez zmeny stavu. Pri druhom callbacku sa vráti0. Scenár free používa syntetický callback stub, ktorý vykoná skutočné pôvodné free3CAE s pointerom4002h; nejde o emulovanie free jednoduchým prepisom tagu.

Modelované sú iba DOS AH4A a externá callback politika. Všetky uvedené allocator/free rutiny ostávajú pôvodné inštrukcie. Pri zmene callback stubu sa explicitne invaliduje Unicorn translation cache; test počíta skutočné vstupy do free, aby nebolo možné úspech zameniť za starý cached RETF stub. Neplatné prvé pokusy pri vývoji harnessu sa nepočítajú medzi úspešné prípady.

222 prípadov skončilo alokáciou, 360 vstúpilo do callbacku, pôvodné free sa vykonalo162-krát. Overené DX:AX, požadovaná veľkosť allocation hlavičky, presné DOS paragraph argumenty/počty, callback argument/počet, flags, guard BYTE a zachovanie pôvodného živého 16 B payload pri alokácii za ním. Overuje sa SP/BP/SI/DI/DS. Nulové odchýlky. Predchádzajúce scan/grow reporty majú samostatné detailné memory modely; tento integračný test neporovnáva každý bajt ľubovoľného dlhého heapu.

## Limity a reprodukcia

Nie je to dôkaz celého životného cyklu CRT pamäte: chýbajú ľubovoľné dlhé sekvencie alloc/free, poškodené reťaze, prirodzený DOS memory pressure, všetky callback implementácie, ľubovoľné flag bity a Win16 parita. Pôvodná hra sa v DOSBox-X nespúšťa; natural runtime0. Priame hraničné požiadavky sú seedované, nie prirodzene potvrdené herné požiadavky.

Reprodukcia: audit_replay_near_malloc.py IMAGE INVENTORY DECODER EMULATOR OUT. Kanonický image SHA e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297, iced-x861.21.0/Unicorn2.1.4; skutočné EXEPACK relokácie. Exporty near_malloc_retry.csv, cfg_edges.csv, cases.csv a summary.json. Kontext súvisiacich funkcií je v NEAR_HEAP_SCAN_REPORT.md, NEAR_HEAP_GROW_REPORT.md, PASS1_NEAR_HEAP_FLAGS_REPORT.md a PASS1_NEAR_HEAP_STATE_REPORT.md.

## Meranie

PASS1 ostáva **57 102 B PARTIAL, 149 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**. Nový funkčný rozsah a 640 integračných prípadov nenahrádzajú percento celej CRT/hry. Táto nová lokálna dávka ešte nie je v publikovanej analytickej snímke ba27379dd28c9a689d15233b0fd7017867f50114.

SHA cases `9734a2955ce7ac7a1c3657afb761a8b060e50211385d0930eb3cd7de95b1964a`.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, preto N/A; historické orientačné hodnoty sa nemenia z test count ani integrity mapy.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|bez nového dôkazu|loader hranice|map closure|
| Dátové typy a konštanty |95 %|N/A|bez novej promócie|149 B iba klasifikované|susedné alias polia|
| Tabuľky a ukazovatele |93 %|N/A|retry FAR callback kontrakt|prirodzená callback inštalácia|pointer writer audit|
| Funkcie / ASM / CFG |90 %|N/A|59 B /27 inštrukcií,640integrácií|celý lifecycle|dlhé alloc/free sekvencie|
| RNG |97 %|N/A|bez nového dôkazu|prirodzené poradie|DEMO trace|
| Scheduler |96 %|N/A|bez nového dôkazu|prirodzené callery|call graph|
| DEMO a vstupy |96 %|N/A|bez nového dôkazu|driver ABI|input closure|
| Renderer / VGA |94 %|N/A|bez nového dôkazu|setup|VGA init CFG|
| GUARD / bossovia |93 %|N/A|bez nového dôkazu|selector doména|descriptor flag8|
| Zbrane / projektily |92 %|N/A|bez nového dôkazu|damage callery|effect producer|
| Sprity / HUD / paleta |92 %|N/A|bez nového dôkazu|resource identity|resource parser|
| SAVE / LOAD |92 %|N/A|CRT memory oddelená|prirodzené I/O|stream trace|
| Windows Win16 |92 %|N/A|bez nového Win dôkazu|iný heap model|Win kontrakt|

## Runtime testy na vykonanie

V DOSBox-X sledovať prirodzené requesty do3CCF a zapisovateľnosť callbacku252E/2530. Pri nedostatku pamäte zaznamenať plnú scan/grow/retry cestu, návratDX:AX a následné použitie pointera callerom. Sledovať dlhé reálne alokačné sekvencie a free vrátane zachovania živých payloadov. Prirodzené runtime0 a PE32 sa nevytvára.
