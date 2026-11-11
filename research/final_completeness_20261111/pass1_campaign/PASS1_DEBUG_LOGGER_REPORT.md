# DOS 2.0: debug logger, jeho CFG a 253 B dát

## Doložená funkcia

FAR rutina 0476:0078 má presné hranice `[047D8,0482D)`, 85 B / 30 inštrukcií, končí LEAVE; RETF. Nezávislý dekóder overil všetky jej bajty a všetky priame vetvy smerujú na hranice inštrukcií v tomto rozsahu. `cfg_edges.csv` obsahuje inštrukčné hrany; pokračovanie za CALL platí pod podmienkou návratu callee. Žiadna jump table sa v tomto tele nenachádza.

Vstup: DS musí ukazovať na príslušné herné dáta; FAR stack layout dáva formátový near pointer na SS:[BP+6] a ďalšie argumenty od SS:[BP+8]. Rutina nemení DS/ES/SS explicitnými inštrukciami; ich správanie cez callee sa neuzatvára. BP sa obnoví, argumenty odstraňuje caller. AX/FLAGS a ďalšie registre cez CRT volania nemajú touto dávkou uzavretý ABI kontrakt.

```text
debug_log(format, ...):
    if byte DS:3CD0 == 0: return
    mode = (word DS:082C == 0) ? DS:082E : DS:0830
    AX = call 11EE:06E6(DS:0832, mode)
    word DS:082C = AX
    if AX == 0:
        call 0FBA:000C(DS:0846, DS:083C)
        # ak sa chybová rutina vráti, vykonávanie pokračuje
    call 11EE:2822(word DS:082C, format, &SS:[BP+8])
    call 11EE:05FA(word DS:082C)
    return
```

Počiatočný WORD DS:082C je nula; DS:082E obsahuje `w`, DS:0830 `a`, DS:0832 `debug.txt`, každý reťazec má NUL terminátor. Po každom open volaní sa výsledok uloží na DS:082C a po poslednom volaní sa tu nevynuluje. Pri konvenčnom CRT význame módov teda prvý úspešný open volí zápis a ďalšie append; presná realizácia a návraty CRT callee zostávajú závislosti na uzavretie. Volanie 05FA sa tu eviduje ako finalizačná závislosť, jeho úplný close/flush kontrakt sa nepredpokladá iba podľa podobnosti.

DS:3CD0 je mimo file-backed obrazu; tejto runtime premennej sa nepripisujú NON-CODE bajty. Pri nulovom príznaku telo nevykoná žiadne externé volanie ani zápis do herných dát; vykoná však stack prolog/epilog. Pri zapnutom príznaku zahŕňa vedľajšie účinky otvorenie/výpis/finalizáciu cez CRT a zmenu DS:082C. Zlyhanie open nemá v tomto tele návratovú vetvu: ak sa error callee vráti, nulový výsledok sa ďalej odovzdá formátovacej rutine.

## Caller a dátový katalóg

Inventár obsahuje 17 priamych volaní: 9 pomocou PUSH CS + NEAR CALL zo segmentu 0476 a 8 FAR CALL z iných segmentov. Pri 16 je bezprostredne odovzdaný konštantný WORD formátu; pri 0C2B:009D sa odovzdáva AX odvodené od SS lokálneho bufferu. Tento dynamický reťazec sa nepromuje na statické dáta. Úplnosť nepriamych callerov a runtime DS callerov nie je preukázaná.

`data_fields.csv` má 20 polí / 253 B: 16 presných NUL-ukončených formátových reťazcov, dva mode reťazce, názov súboru a dvojbajtový uložený výsledok. Každé pole má vlastné hranice a SHA-256. `callers.csv` pripája konkrétny call site, bajty argumentu a text; `instructions.csv` celé telo. Chybové reťazce DS:083C a DS:0846 už boli evidované predchádzajúcimi dávkami a tu sa nezapočítavajú znova.

Všetkých 253 B prešlo z CLASSIFIED ONLY do PARTIAL na základe konkrétnych spotrebiteľov. Nová mapa: **54 417 B PARTIAL, 2 834 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**. Nezávislá kontrola 629 intervalov potvrdila všetky intervalové SHA, presné členstvo baseline 57 295 B a nulové diery či prekryvy. Integrita mapy sama nepotvrdzuje úplnú sémantiku.

Centrálny katalóg po regenerácii: 41 rozsahov, 1 402 inštrukcií / 3 218 B kódu; 55 263 B typovaných dát celého obrazu. Typované dáta v historickom NON-CODE: 54 415 B; rozdiel 2 B voči PARTIAL zostáva relokačný WORD otvoreného slotu DS:2356. Typový katalóg má 376 polí zo 43 zdrojov. Seeded replay zostáva 6 091, prirodzené runtime testy 0.

## Reprodukcia

1. `audit_pass1_debug_logger.py IMAGE INVENTORY DECODER_DIR OUT` overí kanonický SHA obrazu, telo, lokálne CFG hrany, priame call targets a NUL hranice literalov.
2. `promote_pass1_fields.py IMAGE pass1_tangent/noncode_intervals.csv pass1_debug_logger/data_fields.csv pass1_debug_logger` reprodukuje novú mapu.
3. `verify_pass1_partition.py IMAGE pass1_debug_logger/noncode_intervals.csv OUT_JSON` vykoná nezávislú kontrolu partition.
4. `independent_decode_and_catalog.py ABS_DECODER_DIR OUTPUTS_DIR` regeneruje centrálny katalóg s novou rutinou a dátami.

Skripty a výstupy sú lokálne; táto dávka zatiaľ nie je publikovaná na GitHub. Runtime test: v izolovanej hernej kópii zachytiť nulový/nenulový DS:3CD0, návraty všetkých troch CRT callee a životnosť DS:082C; overiť prvý zápis a druhé pripojenie k `debug.txt`. Zvlášť kontrolovať zlyhanie open. Testy zatiaľ nevykonané.

## Aktualizácia 13 oblastí

Metodika každého nového sémantického percenta: uzavreté jednotky / úplný inventár jednotiek oblasti. Menovatele nie sú uzavreté; nové percentá sú N/A. Staré hodnoty sú orientačné. Nové dôkazy majú stav PARTIAL.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | prirodzené stavy | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 253 B / 20 polí | runtime hodnoty | logger watchpointy |
| Tabuľky a ukazovatele | 93 % | N/A | uložený open výsledok a varargs pointer | SS/DS konvencia callee | CRT 2822 vstup |
| Funkcie / ASM / CFG | 90 % | N/A | 85 B / 30 inštrukcií a 17 callerov | CRT kontrakty | 06E6/2822/05FA |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová DEMO stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping | payload spotrebitelia |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | inicializátory |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | textový lifetime | SS čítania po návrate |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | LOAD parity | porovnať stav |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | DS callerov | caller guardy |
