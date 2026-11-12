# PASS1: CRT near-heap stav a mark rutina

12 B CLASSIFIED ONLY → PARTIAL. Šesť WORD polí je doložených konkrétnymi startup zápismi alebo následnými prístupmi cez SI. Zápisy cez SS sú mapované na kandidátny počiatočný DGROUP; rovnosť segmentov pri prirodzenom behu sa touto dávkou neuzatvára. Žiadny DEEP VERIFIED.

| Image interval, koniec exkluzívny | DS/SS offset | Doložená rola |
|---|---|---|
|[297F0,297F2)|20E0|mutable_WORD_startup_shifted_limit_WORD_SS_write|
|[297F2,297F4)|20E2|mutable_WORD_startup_stack_segment_WORD_SS_write|
|[297F6,297F8)|20E6|mutable_WORD_startup_aligned_SP_WORD_SS_write|
|[297F8,297FA)|20E8|mutable_WORD_near_heap_lower_bound_WORD|
|[297FA,297FC)|20EA|mutable_WORD_near_heap_minimum_tagged_offset_WORD|
|[297FC,297FE)|20EC|mutable_WORD_startup_sentinel_SP_WORD_SS_write|

Startup 11EE:005D..0088 počíta 20E0 ako low16(SI<<4)-1, v 20E2 uloží SS, zarovná SP nadol na párnu hodnotu a uloží ho do 20E6. Po PUSH FFFEh uloží SP do 20ECh, potom po PUSH 0001h uloží SP do 20E8 a 20EAh. Počiatočný WORD 20E4=5 zostáva bez uzavretého významu; nebol povýšený ani priradený ako padding. Rovnako zostávajú otvorené ďalšie susedné polia.

## ASM a lokálny algoritmus

11EE:3CAE..3CCF, image [15B8E,15BAF), 33 B / 17 inštrukcií. FAR vstup, argument WORD v [SS:BP+6], RETF. Zachované BP/SI, BX je pracovný; stabilný návrat AX nie je definovaný. DS ukazuje na near heap kontext, SS v emulácii zostáva samostatný stack. ES ani OS sa nepoužívajú. Podmienené skoky JAE/JBE sú neznamienkové.

```c
void mark_near_block(uint16_t p) {
    if (DS.u16[0x20E8] >= p) return;
    uint16_t h = (p - 2) & 0xFFFF;
    DS.u8[h] |= 1;
    if (DS.u16[0x20EA] > h) DS.u16[0x20EA] = h;
}
```

Označenie near_heap_mark_free je pracovná interpretácia kontextu alokátora; nezávisle potvrdené sú presné operácie vyššie. Táto rutina sama nepreukazuje kompletné uvoľnenie alebo zlúčenie blokov. Nekontroluje hornú hranicu pointera, jeho platnosť ani zarovnanie. Ak p=1 a lower_bound=0, odčítanie dva dá FFFFh. Ak p<=lower_bound, nič nemení. Pri rovnakom minimálnom offsete nevykoná nový zápis WORD, ale bit hlavičky už nastavila. Aliasovanie hlavičky so stavovými poľami alebo code segmentom je mimo testovaného kontraktu.

## Reprodukcia a emulácia

2 688 prípadov = 2 load bázy × 14 pointer hodnôt × 6 hraníc × 4 minimá × 4 pôvodné hlavičkové BYTE. Pointery zahŕňajú 0,1,2,3,0100h,1FFFh,2000h,2001h,2002h,4000h,7FFFh,8000h,FFFEh,FFFFh. Hranice 0,1,2,2000h,8000h,FFFFh, minimá 0,1,2000h,FFFFh, tag 0,2,FEh,FFh. Bez stubov a OS volaní. Overené celé 12-bajtové okolie stavu, výsledný tag, SP/BP/SI a DS. Nulové odchýlky; nie je to prirodzený runtime ani celý heap lifecycle.

Reprodukcia: audit_replay_pass1_near_heap_state.py IMAGE INVENTORY DECODER EMULATOR OUT; promote_pass1_fields.py s mapou pass1_backslash_strings; verify_pass1_partition.py. Dáta: data_fields.csv, startup_and_consumer_contexts.csv, near_heap_mark_free.csv, cases.csv a summary.json. Kanonický obraz SHA-256 e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297. Iced-x86 1.21.0 a Unicorn 2.1.4.

## Meranie

**57 053 B PARTIAL, 198 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57 295 B. Nezávislá kontrola 876 intervalov potvrdila presné členstvo, všetky hash hodnoty a nulové diery/prekryvy. Integrita mapy nie je úplná sémantická verifikácia. Dva už PARTIAL relokačné bajty stále nemajú uzavretý dátový typ. Nové lokálne dôkazy ešte nie sú v poslednej publikovanej GitHub snímke; prirodzených runtime testov 0.

SHA mapy `08e3bc45c4000cd2ae1855012418358c07a65416f39b7060a3c685530a4d338d`; SHA cases `64cedd8a7f7755cc2023fa9668cf2181749e6b3fc5efc6bdbb56fa63057f01fd`.

## Aktualizácia 13 oblastí

Metodika nového %: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, preto N/A; historické percentá zostávajú orientačné. Počet testov ani integrita mapy nenahrádzajú percento sémantického uzavretia.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|bez nového dôkazu|loader hranice|map closure|
| Dátové typy a konštanty |95 %|N/A|12 B / 6 WORD polí|198 B iba klasifikované|zvyšné alias odkazy|
| Tabuľky a ukazovatele |93 %|N/A|startup SS a offset polia|DS/SS vzťah|entry segment trace|
| Funkcie / ASM / CFG |90 %|N/A|33 B / 17 inštrukcií|heap lifecycle|allocator producer|
| RNG |97 %|N/A|bez nového dôkazu|prirodzené poradie|DEMO trace|
| Scheduler |96 %|N/A|bez nového dôkazu|prirodzené callery|call graph|
| DEMO a vstupy |96 %|N/A|bez nového dôkazu|driver ABI|input closure|
| Renderer / VGA |94 %|N/A|bez nového dôkazu|setup|VGA init CFG|
| GUARD / bossovia |93 %|N/A|bez nového dôkazu|selector doména|descriptor flag 8|
| Zbrane / projektily |92 %|N/A|bez nového dôkazu|damage callery|effect producer|
| Sprity / HUD / paleta |92 %|N/A|bez nového dôkazu|identity|descriptor producer|
| SAVE / LOAD |92 %|N/A|CRT pamäťová rutina oddelená|herné I/O|stream caller trace|
| Windows Win16 |92 %|N/A|bez nového Win dôkazu|CRT parita|nájsť ekvivalent|

## Runtime testy na vykonanie

V DOSBox-X sledovať SS a DS pri startup zápisoch a pred prvým 3CAE, hodnoty 20E0..20EE a prirodzené pointer argumenty. Overiť bit hlavičky pred a po volaní a následné použitie minimálneho offsetu v alokátore. Aliasovanie a chybné pointery neskúšať vydávať za prirodzené herné stavy bez trace. Win16 parita a PE32 zostávajú mimo tejto dávky; PE32 port sa nevykonáva.
