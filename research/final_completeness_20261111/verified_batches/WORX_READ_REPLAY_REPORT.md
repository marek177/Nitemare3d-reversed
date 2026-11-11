# WORX read312E — počty bajtov, EOF a riadené prehratie

11. 11. 2026. Stav **PARTIAL**. Nové DEEP VERIFIED 0 B. **12 controlled instruction replay prípadov**, 0 DOSBox-X testov, 0 pôvodných herných runtime stôp. Tieto kategórie sa nesmú zameniť.

## Dôkazový rozsah

Pôvodné bajty helpera CS15BF:312E–31CA, obraz `[18D1E,18DBA)`, boli porovnané s obrazom SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297` a nezávisle dekódované. 75 inštrukcií má 153 B. Tri medzery staršieho inventára 18D59,18D80,18DAE obsahujú 90 a zostávajú UNKNOWN. Celý kandidátsky rozsah má 156 B.

`replay_worx_read.py` vykonal originálne inštrukcie v Unicorn 2.1.4 UC_MODE_16. Obraz sa v emulátore nahráva s nulovou relokačnou bázou; CS=15BF. Zásobník a návratová adresa sú syntetické. INT21 má explicitný adaptér iba pre query seek 4201 a read 3F; nie je to DOS, hardvér ani spustená hra. Vstupné údaje, celé instruction traces a stav registra/FLAGS sú v `read_replay/read_replay_evidence.json`. SHA emulátora aj obrazu sú zaznamenané.

Zjednotenie vykonaných instruction starts pokrylo všetkých 75 inventarizovaných inštrukcií helpera. To nie je dôkaz všetkých kombinácií vstupov ani všetkých možných pathov. Žiadny inštrukčný krok neopustil validované hranice. Vo všetkých prípadoch sa overila rovnováha zásobníka a zachovanie BX,CX,DX,SI,DI,BP,DS,ES. Pri pamäťových prípadoch sa kontroloval aj presný obsah kopírovaných bajtov a nedotknutý zvyšok cieľa.

## Lokálny kontrakt

Vstup BX je požadovaný počet, ES:DI cieľ. CS:312D rozlišuje režim. Návrat AX je počet bajtov alebo DOS error code podľa CF; DX sa obnovuje na vstupnú hodnotu, nie na high16 počtu.

### Pamäťový režim

Pri nenulovom CS:312D sa načíta zdrojový FAR pointer z CS:3129, pripočíta low16 pozície CS:2DFF a spočíta sa low16 `size-position`. BX sa zmenší na minimum požiadavky a tohto unsigned word rozdielu. Pozícia sa zvýši, REP MOVSB vykoná kópiu a AX=BX, CF=0.

```text
available16 = (WORD(size) - WORD(position)) mod 65536
count = min(request, available16)
source_offset = (saved_offset + WORD(position)) mod 65536
WORD(position) = (WORD(position) + count) mod 65536
copy count bytes  // DF precondition remains relevant
return AX=count, CF=0
```

Nie je tu samostatné odmietnutie position>size ani úprava source segmentu pri pretečení offsetu. Platnosť stavu a rozsahu pamäte treba dokázať u producentov. Riadený replay použil DF=0, platnú pamäť a dostatočne dlhý fyzický zdrojový buffer; nepovažuje neplatný logický stav za skutočný herný vstup.

### Súborový režim

Helper si cez DOS seek query vyžiada current position a odpočíta DWORD základ slice CS:2DFF. Potom vykoná dve unsigned porovnania:

```text
if relative.high < size.high: continue
if relative.low < size.low: continue
return AX=0, CF=1
```

Táto podmienka sa líši od lexikografického DWORD `<`: pri relative.high>size.high a relative.low<size.low sa pokračuje. Následné size-relative modulo 2^32 môže mať vysoké slovo FFFF a helper neobmedzí požadovaný počet na zvyšok. Riadený príklad to demonštruje, prirodzená dosiahnuteľnosť sa netvrdí.

Ak helper pokračuje a zostávajúca veľkosť má high16=0, ohraničí požiadavku low16 zvyšku. Potom volá DOS read. Jeho AX a CF sa vrátia cez epilóg bez premeny short read na chybu. CF seek query sa pred aritmetikou výslovne netestuje; pri chybe sú výsledné AX/DX mimo kontraktu platnej file position.

## Riadené výsledky

| Prípad | Vstup / adaptér | Návrat AX,CF | Pozorovanie |
|---|---|---|---|
| memory_full | size100,pos0,request44 | 44,0 | 44 presných source bajtov |
| memory_short | size20,pos0,request44 | 20,0 | krátka kópia bez CF chyby |
| memory_eof | size20,pos20 | 0,0 | pamäťový EOF je CF=0 |
| memory_position_past_end | size20,pos21 | 44,0 | unsigned word underflow, kópia za logický koniec |
| file_full | pos0,size100,read44 | 44,0 | plný výsledok adaptéra |
| file_short | request44,read10 | 10,0 | short read sa neodmieta |
| file_eof | pos100,size100 | 0,1 | bez DOS read; odlišné od memory EOF |
| file_high_position_low_word_smaller | pos10001h,size64h | 44,0 | helper vydal read napriek logickej pozícii za slice |
| file_read_error | adaptér AX5,CF1 | 5,1 | chyba sa prenesie |
| file_seek_error_then_adapter_read | seek adaptér DX:AX=6,CF1, read10 CF0 | 10,0 | chyba query nie je lokálne stop podmienkou |
| file_clamped_to_ten_remaining | pos90,size100,request44 | 10,0 | vydaná požiadavka len10 |
| file_size_high_word | size10064h,pos0 | 44,0 | cesta s nenulovým high16 size |

Adaptér seek-error prípadu zámerne dodal konkrétne registre; ich hodnoty sa nesmú prezentovať ako garantované správanie DOS pri chybe. Adaptér nevyhodnocuje skutočný súbor ani file handle a nedokazuje dostupnosť dát na chybných pozíciách.

## Dôsledok pre predchádzajúcu WAVE dávku

File/memory audio initializátory žiadajú 44 B cez tento helper a následne čítajú polia headera. Vo viditeľnom úseku po návrate helpera nekontrolujú AX==44. Byte-backed replay helpera teraz priamo ukazuje, že AX môže byť20 alebo10 s CF=0. To dopĺňa predchádzajúci otvorený kontrakt read312E. Neznamená to, že normálne herné vzorky majú krátku hlavičku alebo že ich predchádzajúce validátory chýbajú.

Timer cesta kopíruje 44 B priamo cez REP MOVSB; tento konkrétny read helper nevolá pri jej kópii headera.

## Katalóg a 13 oblastí

Aktuálny spoločný katalóg má **13 lokálnych funkcií, 525 inštrukcií / 1 273 B, 258 B dát a 51 intervalov**. Stav všetkého lokálne analyzovaného je PARTIAL; zvyšných169 829 B je v tejto kampani neposúdených. Pôvodná mapa PASS320 a prienik s jej57 295 NON-CODE bajtmi chýbajú.

Aktualizovaná tabuľka 13 oblastí v `CAMPAIGN_CATALOG_REPORT.md` uvádza historické odhady, nové zistenia, otvorené otázky a ďalšie kroky. Nové percentá všade N/A: pred výpočtom treba uzavrieť úplný menovateľ sémantických jednotiek. Riadené replay prípady sa nezamieňajú za DOSBox-X/original-runtime ani za paritu.

## Ďalšie konkrétne brány

1. Dohľadať producentov pozície CS:2DFF a dôkaz invariantov position<=size na pamäťovej/súborovej ceste.
2. V DOSBox-X zachytiť skutočné query seek a read výsledky vrátane krátkych/error ciest, pôvodných handle a bufferov.
3. Pre WAVE callerov dokázať predchádzajúcu kontrolu dĺžky alebo zachytiť bytes-read a spotrebu headera v jednej stope.
4. Reentrancia a segmentové aliasy ostávajú otvorené; aktuálne replay používa izolovanú jednu invokáciu a DF=0. PE32 port sa nevykonáva.
