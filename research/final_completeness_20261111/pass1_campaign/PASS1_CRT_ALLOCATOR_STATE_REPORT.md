# DOS 2.0: CRT stav pred hookmi a allocation retry callback

Neskoršie spresnenie: `PASS1_HEAP_ROOT_REPORT.md` dokladá DS:233E/2340 ako spoločný FAR tail pointer a DS:2342 ako WORD kopírovaný do headera. Zo siedmich bajtov zvyšku nižšie preto v novšej mape zostávajú iba tri. Tento report a jeho promócia 20 B zostávajú historickou dávkou.

## Z 27 B doložených 20 B

Prioritný blok `[29A3B,29A56)` sa rozdelil podľa 26 explicitných priamych DS operandov, overených bajtov a skutočných dekódovaných šírok. Doložených je **8 polí / 20 B**: dva BYTE, tri samostatné WORDy, FAR code pointer a dva FAR data pointery. Sémantické názvy nižšie odlišujú úlohu od úplnej implementácie; writeri a runtime DS zostávajú otvorené.

| DS | Interval obrazu, koniec exclusive | Typ / doložená rola |
|---|---|---|
| 232D | [29A3D,29A3E) | BYTE, CRT open cesta testuje bit 80h |
| 232E | [29A3E,29A3F) | BYTE stav načítaný do AL v CRT I/O ceste |
| 2330 | [29A40,29A42) | WORD, CRT I/O porovnáva s nulou |
| 2332 | [29A42,29A46) | FAR callback, počiatočne NULL, allocation retry vetva |
| 2336 | [29A46,29A4A) | FAR data pointer načítaný cez LDS BX; heap root rola |
| 233A | [29A4A,29A4E) | FAR data pointer cez LDS/LES, párové uloženie BX/DX |
| 2340 | [29A50,29A52) | WORD používaný pri porovnávaní heap walk segmentu |
| 2344 | [29A54,29A56) | mutable WORD, počiatočne 2000h, viacerí calleri dočasne nastavujú 0010h a obnovujú |

Počiatočne sú všetky tieto polia nulové okrem posledného WORDu 2000h. Samotné nuly neboli dôvodom typovania; rozhodujú konkrétne operandy. 2338 a 233C sú high WORDy príslušných FAR pointerov, nie ďalšie nezávisle počítané polia. Presné mená, dĺžky, počiatočné bajty a SHA sú v `data_fields.csv`.

**Zostáva 7 B CLASSIFIED ONLY**, bez promócie podľa susednosti:

| Interval | B | Poznámka |
|---|---:|---|
| [29A3B,29A3D) | 2 | nulové, konkrétna rola neuzavretá |
| [29A3F,29A40) | 1 | nulový BYTE, padding nepreukázaný |
| [29A4E,29A50) | 2 | nulové, možné nepriame štruktúrne prístupy |
| [29A52,29A54) | 2 | počiatočne 0003h; ďalší krok ES:DI odvodené prístupy |

Napríklad helper 11EE:22E2 má ES:[DI+0Ch] referenciu, ktorá môže po odvodení ES/DI objasniť posledný WORD. Táto dávka ešte neuzatvára jej celý register/OS kontext a pole automaticky nepromuje.

## Presná allocator funkcia a retry vetva

FAR **11EE:2065**, obraz **[13F45,13FDE)**, má **153 B / 71 inštrukcií**, končí RETF. Celé telo bolo porovnané s kanonickými bajtmi a nezávisle dekódované. Počet inštrukcií nie je tvrdenie, že sú uzavreté všetky heap algoritmy: telo volá ďalšie near helpery a CALL DI s heap metódami.

WORD request na SS:[BP+6] sa unsigned porovná s **FFE8h**. Hodnoty **FFE9h..FFFFh** idú priamo na failure/retry vetvu pred DS save, heap walk a OS allocation. Nižšie požiadavky môžu prejsť cez heap root/cache a alokačné helpery; tieto cesty sa v replay tejto dávky nevykonávajú.

```text
retry:
    request = WORD argument
    if request <= FFE8h:
        attempt_heap_paths_and_helpers()     # neuzavreté v tejto dávke
        if success: follow_success_epilogue() # návratový kontrakt ešte neuzavretý
    AX = 0; DX = 0
    if DWORD DS:2332 == NULL: return DX:AX
    AX = call FAR DS:2332(request)
    if AX != 0: goto retry
    return NULL
```

Pseudokód úspešnú vetvu zámerne nedefinuje ako hotový návratový kontrakt; jej presné pointer/register správanie treba uzavrieť s heap helpermi. Neúspešná vetva je presná: callback sa testuje ORom oboch WORDov pointera, dostane jeden WORD request, argument odstráni caller, AX sa interpretuje ako zero/nonzero. Nenulový výsledok nie je pointer, ale dôvod opakovania pôvodnej požiadavky. Ak callback stále vracia nenulu a nič relevantné sa nezmení, lokálna vetva môže opakovať bez pevného limitu.

Heap cached FAR pointer na DS:233A sa v úspešnej časti párovo ukladá z BX/DX po obnovení DS. To podporuje jeho typ, ale nie invariant životnosti, správnosti celého linked heapu alebo bezpečnosti všetkých veľkostí. Názov heap root/cache je funkčná rola z miestnych dátových tokov, nie potvrdenie konkrétnej CRT distribúcie.

## Controlled replay a reprodukcia

`audit_replay_pass1_crt_allocator_state.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT` pripína SHA obrazu, overí osem polí podľa konkrétnych operandov a celé allocator telo. Pri dvoch load bázach vykoná všetkých 23 odmietaných requestov a tri callback režimy: NULL pointer, callback vracajúci 0 a callback vracajúci postupne 1/0. Spolu **138 prípadov, 0 odchýlok**.

Jediná vykonaná externá závislosť je výslovne seedovaný FAR callback s RETF. Overuje sa jeho WORD argument a počet volaní, návrat AX=DX=0 a BP/SI/DI/DS/SP. Žiadny heap traversal, úspešná alokácia ani INT 21h sa nevykoná. Test teda nesimuluje bežné vyčerpanie reálneho heapu a nepreukazuje prirodzenú dostupnosť reject requestov v hre. Stav DS je seedovaný na referenčný DGROUP.

Výstupy `pass1_crt_allocator_state/`: `consumer_instructions.csv` (26 pamäťových operandov), `allocator_instructions.csv`, `data_fields.csv`, `cases.csv`, `summary.json`, nová CSV/JSON mapa a nezávislá partition kontrola. Numericky zhodné branch targety boli pri tvorbe finálneho spotrebiteľského zoznamu vylúčené explicitnou kontrolou pamäťového operand kind; nie sú to dátové čítania.

## Pokrytie a aktualizovaný zvyšok

20 B prešlo z CLASSIFIED ONLY do PARTIAL. Aktuálne **55 006 B PARTIAL, 2 245 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, presne 57 295 B. Nezávislá kontrola 691 intervalov potvrdila SHA a presné členstvo bez dier/prekryvov.

Nový nižšie klasifikovaný zvyšok je v `remaining_after_allocator/`: **95 intervalov / 2 289 B**. Vyšší počet intervalov oproti predchádzajúcim 92 neznamená viac neznámych bajtov; pôvodný 27 B blok sa rozdelil na polia a štyri zvyšky. Starý `remaining_noncode/` zostáva historicky reprodukovateľný voči starej mape.

Centrálny katalóg: **63 rozsahov, 2 238 inštrukcií / 5 501 B kódu**, 55 892 B typovaných dát celého obrazu a 55 004 B historických NON-CODE dát. Rozdiel 2 B voči PARTIAL zostáva samostatná neuzavretá relokácia. Controlled replay súčet je 276 441 plus osobitne 65 548 normalizačných prefixových prípadov. Prirodzené runtime testy zostávajú 0. Výsledky sú PARTIAL; GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika sémantického percenta: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú; nové percentá sú N/A a predošlé orientačné.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | prirodzené stavy | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 20 B / 8 CRT polí | 7 B fokus zvyšku | odvodené ES:DI |
| Tabuľky a ukazovatele | 93 % | N/A | callback a dva FAR heap pointery | lifetime/heap invarianty | heap helpery |
| Funkcie / ASM / CFG | 90 % | N/A | 153 B / 71 inštrukcií, 138 prípadov | alokačné vetvy | 2168/21E4/22E2 |
| RNG | 97 % | N/A | bez nového dôkazu | prirodzené seedy | reset caller |
| Scheduler | 96 % | N/A | bez nového dôkazu | poradie udalostí | tick stopy |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | call ordering | DEMO stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping | render stopa |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | AI/lifecycle | health updater |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | prirodzené vstupy | effect producer |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | asset identity | descriptor producer |
| SAVE / LOAD | 92 % | N/A | heap stav oddelený od herných dát | pointer reset/obnova | serializačné invarianty |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | allocator parity | Win heap kontext |

## Runtime testy na vykonanie

Pri prirodzenom resource load zachytiť request, DS a root/cache pointery, callback slot a skutočný návrat allocatora. Vyčerpanie heapu skúšať osobitne v izolovanom testovacom prostredí, s pôvodnými heap/OS helpermi. Pre nepriame polia zachytiť ES/DI a kompletné šírky operácií; ich typ neodvodzovať iba z počiatočných núl alebo hodnoty 3. DOSBox-X vykonanie zatiaľ chýba.
