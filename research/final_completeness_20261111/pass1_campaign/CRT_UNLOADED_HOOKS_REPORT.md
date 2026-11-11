# DOS 2.0: počiatočné CRT hooky a cesta R6002

## Nový dôkaz

Sedem susedných štvorbajtových slotov DS:2346, 234A, 234E, 2352, 2356, 235A a 235E obsahuje rovnakú počiatočnú dvojicu WORDov `02C0h,11EEh`. Každý segmentový WORD je skutočné EXEPACK relokačné miesto. Súhrnný file-backed rozsah je `[29A56,29A72)`, 28 B. Šesť slotov už má doložené nepriame FAR CALL spotrebitele; pri DS:2356 sa spotrebiteľ neuzatvoril.

Nová analýza cieľa ukazuje, že nejde o prázdny návratový hook:

```asm
11EE:02C0  B8 02 00    MOV AX,0002h
11EE:02C3  E9 2E FE    JMP 00F4h
```

Presná hranica tohto základného bloku je `[121A0,121A6)`, 6 B / 2 inštrukcie. Ide o tail transfer do zdieľanej CRT chybovej cesty, nie o samostatné telo ukončené RETF. Vstupné AX sa prepíše; ostatný kontrakt vyplýva zo zdieľanej cesty a jej volaní a zostáva PARTIAL.

Na 11EE:00F4 sa kód 2 uloží na zásobník. Nasleduje načítanie DS cez CS:0120, FAR volanie 11EE:05F8 (počiatočne jediný RETF), volanie 11EE:029E a potom 11EE:0545 s ponechaným chybovým argumentom. Rutina 029E volá výpis kódov FCh a FFh a podmienene hook DS:2152. Rutina 0545 volá už analyzovaný lookup 051A s WORD argumentom, určí dĺžku výsledného textu cez ES:DI a pripraví DOS zápis AH=40h, BX=2; pred zápisom môže volať ďalší NEAR hook. Úplné správanie všetkých hookov a konečná terminácia sa touto dávkou neuzatvárajú.

Pôvodná dátová tabuľka má pre kód 2 presný text `R6002\r\n- floating-point support not loaded\r\n`. Spoločný cieľ je preto staticky doložená predvolená cesta hlásenia chýbajúcej floating-point podpory. To podporuje oddelenie týchto slotov do CRT; nedokazuje použitie konkrétneho externého knižničného produktu ani to, že hra prirodzene túto cestu vykoná.

```text
unloaded_support_entry():
    AX = 2
    tail_transfer shared_runtime_error_path
```

## Otvorený siedmy slot

Audit znovu byte-exact overil a nezávisle dekódoval všetkých 35 648 začiatkov dodaného DOS inventára. Pri priamych neindexovaných pamäťových operandoch nenašiel referenciu na DS:2356. Toto je ohraničený negatívny výsledok: nepreukazuje nepoužitie, nevylučuje indexované/adresne odvodené prístupy, prepis slotu ani kód mimo inventára. Kontrolované nepriame volania sa preto nerozšírili zo šiestich na sedem.

DS:2356 zodpovedá `[29A66,29A6A)`. WORD `[29A68,29A6A)` zostáva jedinými 2 PARTIAL bajtmi bez uzavretej typovej roly v centrálnom katalógu; zhoda inicializéra a relokácie sa ukladá ako dôkaz kandidátneho FAR ukazovateľa. Klasifikácia sa nezvyšuje iba podľa susednosti.

## Reprodukcia a stav

`audit_crt_unloaded_hooks.py IMAGE INVENTORY DECODER_DIR OUT` pripína SHA-256 kanonického obrazu, overuje bajty a dekódovanie inventára, sedem relokácií, dvojinštrukčný blok, cieľ jeho skoku a pôvodné error records. Výstupy `crt_unloaded_hooks/slots.csv`, `direct_memory_refs.csv`, `instructions.csv`, `error_records.csv` a `summary.json` umožňujú výsledok zopakovať. Neoverujú dosiahnuteľnosť celého inventára.

PASS1 zostáva 54 164 B PARTIAL, 3 087 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED. Žiadny nový runtime test ani seeded replay. Nový blok je zatiaľ samostatná ASM poznámka; centrálny katalóg 40 rozsahov / 1 372 inštrukcií / 3 133 B sa touto dávkou nemení. GitHub zatiaľ neobsahuje túto dávku.

## Aktualizácia 13 oblastí

Pre každú oblasť je metodika percenta rovnaká: dôkazmi uzavreté jednotky / úplný inventár jednotiek. Úplné menovatele zatiaľ chýbajú; nové sémantické percentá sú N/A. Historické odhady nie sú meraním tejto dávky. Stav nového zistenia je PARTIAL, nie DEEP VERIFIED.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Zostávajúce neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | prirodzené serializované stavy | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | siedmy identický inicializér | jeho používanie | odvodené adresové referencie |
| Tabuľky a ukazovatele | 93 % | N/A | sedem relokácií a spoločný cieľ | writeri a nepriame prístupy | watchpoint DS:2356 |
| Funkcie / ASM / CFG | 90 % | N/A | 6 B / 2 inštrukcie tail-transfer bloku | zdieľaná terminácia | uzavrieť error-path hooky |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová DEMO stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping | payload spotrebitelia |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | inicializátory |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | textový lifetime | SS čítania po návrate |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | LOAD parity | porovnať stav |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | DS callerov | caller guardy |

## DOSBox-X testy na vykonanie

Po načítaní EXEPACK relokácií zachytiť sedem slotov a ich opravené segmenty. Nastaviť watchpointy na zápisy do `[DS:2346,DS:2362)` vrátane DS:2356 a breakpoint na načítaný ekvivalent 11EE:02C0. Pri prirodzenom zásahu zaznamenať zásobník, caller CS:IP, DS/ES/SS, error-path hooky a konečný spôsob ukončenia. Oddelene možno v kontrolovanej kópii vyvolať vstup 02C0 a sledovať text na DOS handle 2; taký test by nebol dôkaz prirodzenej hernej dosiahnuteľnosti. Zatiaľ nevykonané.
