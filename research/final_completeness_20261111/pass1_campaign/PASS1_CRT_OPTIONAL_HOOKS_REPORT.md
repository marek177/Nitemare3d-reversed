# PASS1: voliteľné CRT hooky a registerové parametre

Dávka staticky typuje **12 B v troch poliach**. Úroveň PARTIAL: presné operandové šírky a konkrétni konzumenti sú doložení, vyššia sémantika callbacku a celý startup/termination tok zostávajú otvorené. Nové runtime ani replay prípady 0.

## Vstupy a presné adresy

Image SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; inventár SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`. `audit_pass1_crt_optional_hooks.py IMAGE INVENTORY DECODER OUT` kontroluje identity, nulové počiatočné bajty polí, konkrétne operandové bajty a nezávisle dekóduje 52 kontextových inštrukcií. Kanonické mapovanie používa DS=2771h.

| Pole | Image interval, koniec exclusive | Presne doložený typ |
|---|---|---|
| DS:2546/2548 | [29C56,29C5A) | dvojica WORD initial0, načítaná do AX/DX pred callbackom s BX=0 |
| DS:254A/254C | [29C5A,29C5E) | dvojica WORD initial0, načítaná do AX/DX pred rovnakým callbackom s BX=3 |
| DS:2552 | [29C62,29C66) | mutable FAR16 pointer initial0:0, segment-zero gate a FAR JMP |

Obe dvojice majú spolu 32 bitov, ale samostatné WORD čítania do DX:AX samy nedokazujú, či ide o integer DWORD, FAR pointer alebo dva nezávislé parametre. Preto konečný strojový typ ostáva WORD pair s explicitne otvorenou vyššou sémantikou. FAR pointer typ2552 naopak priamo dokazuje `JMP FAR DWORD PTR [2552]`.

## Callback argumenty

V 11EE:013B sa číta segmentová polovica už skôr doloženého callbacku2542 a pri nule sa blok preskočí. Z PSP-context segmentu211E sa načíta ES a jeho environment-like WORD na002Ch do SI. Potom:

```text
AX = WORD[2546]; DX = WORD[2548]; BX = 0
FAR_CALL DWORD[2542]
ak prvé volanie nevyvolá chybovú vetvu:
    AX = WORD[254A]; DX = WORD[254C]; BX = 3
    FAR_CALL DWORD[2542]
```

Konkrétne bajty prvého výsledkového CF vetvenia a error cieľa zostávajú v CSV. Obidve volania používajú registerové parametre, nie tieto hodnoty na zásobníku. Pomenovanie akcií0/3 je presná hodnota BX; nevyvodzuje sa automaticky konkrétna externá knižničná operácia. Pôvodný callback, jeho vedľajšie účinky a writeri oboch dvojíc neboli vykonaní ani uzavretí.

## Voliteľný tail pointer

11EE:397A načíta WORD[2554] do CX a JCXZ vedie na fallback. Pri nenulovom segmente sa vykoná FAR JMP [2552]. Nie je to CALL a táto vetva nevytvorí novú návratovú adresu. Offset0 so segmentom nenulovým preto nie je null podľa tohto testu.

Fallback nastaví AX=FFFFh, WORD[2118]=16h a skočí na spoločný tail05B7. Ten závisí aj od prenesených flags a stack/BP kontextu; samotný krátky úsek preto nepredstavuje uzavretú samostatnú FAR funkciu. Táto dávka nepovažuje výsledok za úplne overenú exec/CRT chybu.

DS:2552 sa zároveň v startup/cleanup kontextoch objavuje ako hranica SI/DI rozsahov. To sa zaznamenáva, ale nevydáva za dôkaz ďalších neexistujúcich položiek tabuľky alebo celého callback-array layoutu. Dátová klasifikácia stojí na presnom FAR operandovom použití tohto poľa.

## Artefakty a meranie

`data_fields.csv` obsahuje tri intervaly s SHA. `instruction_contexts.csv` presné pôvodné bajty a dekódovanie konzumentov. `summary.json` uvádza rozsah, neuzavreté časti a nulový runtime prírastok. Kontexty sa nepridávajú ako nové úplné funkcie.

12 B CLASSIFIED ONLY → PARTIAL. Mapa: **56893 B PARTIAL, 358 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu57295 B. Nezávislá kontrola overila853 intervalov, SHA a presné členstvo bez dier/prekryvov. SHA mapy `3af4b298d55b6c5abb1bab1325e6a13b6f4a44ad07ba37d39314d275992d1e76`. Partition integrita nie je dôkaz sémantickej úplnosti.

Katalóg zostáva98 bounded funkčných rozsahov,3502 inštrukcií/8773 B. Typované dáta celého obrazu57779 B; historického NON-CODE56891 B a2 PARTIAL netypované relokačné bajty. Controlled replay zostáva777083 plus osobitne65548 smerových prefixových prípadov. Prirodzené runtime testy0. GitHub snímka52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového %: uzavreté jednotky/úplný inventár oblasti. Menovatele chýbajú, nové percentá N/A, predošlé orientačné. Typovanie registerovej dvojice nie je uzavretie externej knižnice.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového formátového dôkazu | úplný inventár | zvyšné intervaly |
| Dátové typy a konštanty | 95 % | N/A |12 B /3 polia | vyšší typ WORD pairs | writer audit |
| Tabuľky a ukazovatele | 93 % | N/A | FAR tail pointer dokázaný | callback-array hranice | cleanup ledger |
| Funkcie / ASM / CFG | 90 % | N/A |52 kontextových inštrukcií | celé caller funkcie | startup closure |
| RNG | 97 % | N/A | bez nového dôkazu | ordering | DEMO trace |
| Scheduler | 96 % | N/A | voliteľné CRT hooky oddelené | prirodzené callery | call graph |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | driver ABI | input closure |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | init režimu | VGA setup |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | health updater |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | effect producer | damage caller |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | identity | descriptor producer |
| SAVE / LOAD | 92 % | N/A | runtime hook stav oddelený | persistencia | SAVE ledger |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | CRT parity | Win hook match |

## Runtime testy na vykonanie

Zachytiť writerov2542/2546/254A a skutočné registerové argumenty callbacku pri BX0/3. Osobitne sledovať2552/2554 a prenesený stack/flags kontext pri tail dispatchi/fallbacku. Bez toho nepriraďovať dvojiciam pointerovú alebo integer sémantiku. DOSBox-X vykonanie a Win16 parity zostávajú otvorené.
