# DOS 2.0 — divisor caller kontrakty a skrátenie podielu

11. 11. 2026. PARTIAL; päť nových riadených caller+callee replay prípadov. DOSBox-X/originálny runtime0, DEEP VERIFIED0 B.

## Osem lokálnych producentov AX

| Image callsite | Vstup helpera466A |
|---|---|
| 18AF6 | konstanta0952h |
| 1917A | low8(unsigned DIV16(0012:2D0Ch, CS:34B9)) |
| 19234 | rovnaký výpočet ako1917A |
| 19299 | WORD CS:2C49 |
| 192E6 | WORD CS:2C49 |
| 19A5B | konstantaFFFFh, potom zápis gate=1 |
| 19FE2 | unsigned DIV16(0012:34DCh, WORD ES:DI) |
| 1A171 | low16(10 * high16(7795 * q)), kde q je predchádzajúci DIV výsledok |

Tabuľka zachováva lokálnu provenienciu, nie globálne rozsahy. V poslednej vetve sa číta byte do DL, nuluje DH, načíta WORD do AX, vymení AL/AH a delí CS:2C5A; pôvod údajov a povolené kombinácie nie sú uzavreté. DIV16 môže chybu vyvolať už pred vstupom466A.

Na19178 a19232 je **XOR AH,AH po DIV BX**. Preto AX nie je celý podiel. Napríklad1191180/4650=256; po vynulovaní AH sa z neho stane0. Ak gate!=1, následný helper delí nulou. Konštanta v týchto dvoch vetvách je1191180 (122D0Ch); iná vetva19FE2 používa1193180 (1234DCh). Rozdiel2000 je bajtovo potvrdený a nebol potichu zjednotený.

## Úplná aritmetická doména WORD

`audit_dos_pit_callers.py` pre každý z dvoch konštantných numerátorov vyhodnotí všetkých65 536 menovateľov. Overí bajty historického inventára nezávislým dekóderom, identifikuje8 callsites a zapisuje výsledky do `dos_pit_callers/`.

| Numerátor / úprava | DIV nula | DIV overflow | platný nenulový vstup466A | platný DIV, potom AX=0 |
|---|---:|---:|---:|---:|
| 1191180, low8 | 1 | 18 | 65 482 | 35 |
| 1193180, celý WORD | 1 | 18 | 65 517 | 0 |

Zoznam35 menovateľov je v summary.json; zahŕňa4635..4653. Ide o konečný matematický priestor, nie o inventár35 chybných originálnych dát ani dôkaz vykonania týchto hodnôt. Validácia zdrojových formátov a caller dosiahnuteľnosť ostávajú otvorené.

## Gate a stavový kontrakt

V prevzatom inventári sú tri fixné CS referencie na201Eh: inicializačný zápis0 na18A7A, zápis1 na19A5E a čítanie v466A na1A25A. Zápis1 nastáva **po** pokuse nastaviť FFFFh cez466A. Ak už gate==1, tento pokus bude bypass; nie je to nepodmienené preprogramovanie časovača. Ostatné indexed/alias/external zápisy tým nie sú vylúčené.

WORD CS:2C49 má doložené tri fixné zápisy:0952h na18AF9, AX na19FE5 a AX na1A174. Dva restore callery ho čítajú bez lokálneho testu nuly. Kompletný dátový životný cyklus ani prirodzený nulový stav zatiaľ nie sú potvrdené.

## Caller+callee instruction replay

`replay_dos_pit_caller.py` vykonáva originálne bajty od1916B cez call1917A do466A. Synteticky nastavuje len WORD CS:34B9 a gate, mapuje pamäť/stack a loguje OUT/CPU interrupt. Zastaví sa na1917D alebo pri výnimke; nejde o DOS ani emuláciu časovača.

| Menovateľ | gate | Doložený výsledok |
|---:|---:|---|
| 4650 | 0 | helper dostane AX0; divide error až v helperi |
| 4650 | 1 | helper dostane AX0; bypass a návrat bez OUT |
| 11025 | 0 | helper dostane108; porty43h=34h,40h=6Ch,40h=00h |
| 0 | 0 | divide error v callerovi pred vstupom helpera |
| 18 | 0 | quotient overflow v callerovi pred vstupom helpera |

Všetkých päť assertions prešlo. Evidencia uchováva presné IP výnimiek, vstupy helpera, porty a native-library hash. Kontrolované vstupy nie sú dôkaz bug reportu pre bežné hranie.

## Pokrytie a nasledujúci krok

Táto dávka nepridáva bajtové rozsahy: centrálny katalóg zostáva1 645 B kódu/548 B dát,18 kandidátnych funkcií. Riadené replay prípady spolu23:12 read,6 PIT helper,5 PIT caller. Nové sémantické percentá N/A, PASS320 členstvo UNKNOWN.

Najbližší krok: spätne vysledovať zápis BX do CS:34B9 na190AB a platné vstupy vetiev19FE2/1A171; následne porovnať originálne resource údaje s35 aritmetickými kandidátmi. DOSBox-X test má zachytiť reálne menovatele, gate a helperAX pri týchto callsites. Bez toho nie je preukázaná prirodzená dosiahnuteľnosť delenia nulou.
