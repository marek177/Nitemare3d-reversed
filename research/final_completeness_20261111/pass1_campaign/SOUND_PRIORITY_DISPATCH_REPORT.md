# Zvukový dispatcher 0C2B:03D6: CFG, ABI a priority

Stav PARTIAL. Kanonický DOS 2.0 obraz: SHA-256 e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297. Rozsah obrazu [0C686,0C779), span 243 B, 86 vykonateľných inštrukcií / 242 B. Jeden bajt preskočený CFG sa nezapočítava do kódu. Všetky inštrukcie boli nezávisle dekódované a porovnané so starším inventárom aj skutočnými bajtmi. Export: sound_priority_dispatch.csv, cfg_edges.csv, calls.csv.

## ABI a segmenty

FAR vstup 0C2B:03D6, ENTER 6, zachované BP a SI, RETF s uprataním argumentov volajúcim. [SS:BP+6] WORD resource ID, +8 WORD pan selector, +0A iba dolný BYTE priority. DS musí ukazovať na DGROUP (2771h plus load base); SS je samostatný stack segment, ES sa tu explicitne nepoužíva. Výstupná AX/DX hodnota nie je stabilný výsledkový kontrakt. Testy overujú obnovenie SP/BP/SI a DS pri zadanom kontrakte modelovaných callee; samy nedokazujú zachovanie registrov pôvodnými WORX rutinami.

## Rekonštruovaný algoritmus

```c
void sound_dispatch(uint16_t id, uint16_t pan, uint8_t priority) {
    if (DS.u8[0x414E] == 0) return;
    uint16_t entry = (uint16_t)(6 * id + 0x3F64);
    if (DS.u16[entry] == 0) return; // žiadna lokálna kontrola rozsahu ID
    bool dsp = DS.u8[0x3CC7] != 0;
    if (dsp ? dsp_busy() : other_busy()) {
        if (DS.u8[0x17E6] > priority) return; // unsigned JA
        if (dsp) dsp_stop(); else other_stop();
    }
    DS.u8[0x17E6] = priority;
    farptr p = resource_get(id);
    if (p == 0) p = resource_load(id);
    // žiadna ďalšia kontrola p; priorita je už prepísaná
    if (dsp) {
        unsigned gain = DS.u8[0x414B] * 15 / 100;
        set_gain(pan == 1 ? 0 : gain, pan == 2 ? 0 : gain);
        dsp_play(p);
    } else other_play(p);
}
```

Výpočet adresy položky je 16-bitový a môže sa pretočiť. Pravidlo priority sa uplatní iba pri nenulovom návrate busy; pri voľnom kanáli aj nižšia priorita pokračuje. Rovnaká priorita zastaví a nahradí obsadený zvuk. Prepínač DSP sa číta opakovane, takže pseudokód predpokladá stabilné pole 3CC7 počas callee; jeho mutácia alebo asynchrónny zásah sa netestovali. Pri pan=1 je prvý gain nula, pri pan=2 druhý; všetky ostatné WORD hodnoty dávajú obe vetvy. Pre BYTE volume 255 je gain 38, lokálna normalizácia na 0..100 chýba. Označenie prvý/druhý gain neurčuje fyzický ľavý/pravý kanál bez analýzy 10BF:054C.

## Volania a hranica hernej logiky / knižnice

| Cieľ | Lokálne použitie / vstup | Pozorovaný výstup |
|---|---|---|
|10BF:0F81 / 0FB3|bez stack argumentov, busy pre dve vetvy|AX nula / nenula|
|10BF:0EF1 / 0F20|stop pred nahradením|návrat ignorovaný|
|0768:0684|WORD ID|DX:AX FAR ukazovateľ|
|0C2B:039E|PUSH CS + NEAR CALL, WORD ID; efektívny FAR návrat|DX:AX fallback|
|10BF:054C|dva WORD gain argumenty|návrat ignorovaný|
|10BF:0A11 / 095B|FAR pointer offset, segment|návrat ignorovaný|

Prioritizácia a rozhodovanie o zdrojoch sú lokálnou hernou logikou. Ciele 10BF sú hranicou audio/WORX; táto dávka ich telá nevykonáva a nepriraďuje im úplný knižničný prototyp. Predchádzajúca analýza loadera 039E musí zostať samostatným dôkazom, model tu iba vracia ukazovateľ.

## Kontrolovaná emulácia

18 432 prípadov = 2 load bases × 2 enabled × 2 entry flags × 2 DSP × 2 busy × 4 staré priority × 4 nové priority × 3 resource scenáre × 4 pan × 3 volume. Priority {0,1,2,255}, pan {0,1,2,FFFF}, volume {0,100,255}; ID je vždy 2. Resource scenáre: cache hit; cache miss a úspešný fallback; oba nulové. Vykonané sú všetky 86 staticky zistené začiatky inštrukcií, nie všetky možné vstupy alebo prirodzené stavy. Overené presné poradie volaní, raw argumenty, posledná priorita a stack. Deväť callee je nahradených RETF modelmi; relokácie pochádzajú zo skutočného rozbalenia EXE. Zero failures. Nejde o prirodzené audio testy ani uzavretie null-pointer správania prehrávača.

Reprodukcia: audit_replay_sound_priority.py IMAGE INVENTORY DECODER EMULATOR OUT. Výstup cases.csv uchováva vstupy a očakávané/overené poradie; hash v summary.json. Iced-x86 1.21.0 a Unicorn 2.1.4. Žiadne zmeny pôvodného EXE ani PE32 port.

## Meranie a otvorené otázky

PASS1 mapa sa nemení: 56 930 B PARTIAL, 321 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED. Zvuková priorita 17E6 bola už typovaná predchádzajúcou dávkou. Pribúda jeden funkčný rozsah a 18 432 kontrolovaných prípadov; prirodzené runtime testy zostávajú 0. GitHub publikácia zatiaľ tieto nové lokálne dôkazy neobsahuje. Otvorené: správnosť ID od callerov, runtime inicializácia tabuľky 3F64, pôvodné WORX ABI a zachovanie registrov, null-pointer účinok a DOS/Win16 ekvivalencia.

SHA-256 cases.csv: `678e01f133649dd29d6fe48179745c59232c7070e99a219774d4cbedb5c69934`.

Preskočený bajt je image 0C721h = 90h, CS:IP 0C2B:0471. Zostáva mimo vykonateľnej množiny tohto CFG; samotná hodnota NOP nedokazuje padding. Aktualizovaný centrálny katalóg obsahuje 99 rozsahov, 3588 inštrukcií / 9015 B a 796045 kontrolovaných replay prípadov plus osobitný smerový prefixový súbor. Nový audit zostávajúcej mapy (remaining_after_small_state) eviduje 80 intervalov / 365 B: 321 CLASSIFIED ONLY a 44 UNKNOWN. Zo starého inventára už nemajú priame absolútne DS operandy; zostáva 41 immediate kandidátov a 3 indexed-base kandidáti. Toto nie je dôkaz absencie dynamických alebo aliasovaných referencií.

## Aktualizácia 13 oblastí

Nové percento = uzavreté jednotky / úplný inventár oblasti. Úplné menovatele chýbajú, preto N/A; historické orientačné percentá sa neprepočítavajú z počtu odkazov ani z integrity mapy. Pri oblastiach bez nových dôkazov sa výsledok nemení.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|bez nového dôkazu|hranice loadera|uzavrieť loader|
| Dátové typy a konštanty |95 %|N/A|bez novej byte reklasifikácie|321 B iba klasifikované|analyzovať zostávajúce intervaly|
| Tabuľky a ukazovatele |93 %|N/A|2 NEAR ukazovatele|startup ciele|sledovať nepriame volania|
| Funkcie / ASM / CFG |90 %|N/A|86 inštrukcií / 242 B dispatchera|9 závislostí modelovaných|uzavrieť pôvodné callee|
| RNG |97 %|N/A|bez nového dôkazu|prirodzené poradie|DEMO trace|
| Scheduler |96 %|N/A|bez nového dôkazu|prirodzené callery|call graph|
| DEMO a vstupy |96 %|N/A|jednorazové stavové brány|vyššia funkcia|uzavrieť konzumentov|
| Renderer / VGA |94 %|N/A|bez nového dôkazu|inicializácia VGA|setup CFG|
| GUARD / bossovia |93 %|N/A|epizódový kľúč class 41/42|celý lifecycle|health updater|
| Zbrane / projektily |92 %|N/A|pravidlá priority a fallbacku, 18 432 prípadov|pôvodné WORX prehrávanie|callee null-pointer správanie|
| Sprity / HUD / paleta |92 %|N/A|cyklický index WORD|celý konzument|0768:04D8 CFG|
| SAVE / LOAD |92 %|N/A|cache handle WORD|účel a prirodzené I/O|0277:008A closure|
| Windows Win16 |92 %|N/A|bez nového Win dôkazu|parita týchto polí|nájsť zodpovedajúce funkcie|

## Runtime testy na vykonanie

V DOSBox-X zachytiť prirodzené vstupy dispatchera a obsah 3F64+6*ID; sledovať obsadený kanál pri nižšej, rovnakej a vyššej priorite pre obe audio vetvy. Overiť fyzický význam argumentov 054C a zachovanie DS/SI pôvodnými callee. Pri zlyhaní resource load najprv sledovať následný pointer bez tvrdenia o páde. Testy nulového pointera vykonať v izolovanom behu so zachovaným pôvodným EXE. Win16 porovnať podľa call graph a dátového toku, nie iba rovnakého textu funkcie.
