# Nitemare 3D: statický rozbor všetkých funkcií

Dátum: 24. 9. 2026

## Rozsah a identita podkladov

Tento prechod pokrýva každú funkciu v aktuálnom párovacom registri Win16 1.10 a DOS v2.0. Používa Ghidra C exporty a existujúci register medziverziových zhôd. Hashy spustiteľných súborov zodpovedajú projektovým referenciám.

| Platforma | Verzia | SHA-256 EXE | Dekompilovaný export | Funkcie |
|---|---|---|---|---:|
| Win16 | NITE3W 1.10 | `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481` | `nite3w110.exe.c` | 967 |
| DOS | N3D v2.0 / N3D-E-20 | `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301` | `N3D-DOS-UNFULL-v20.exe.c` | 519 |

## Pokrytie

- Parsované telá funkcií: **1486 z 1486** položiek registra. Chýbajúce telá: **0**. Nadbytočné telá mimo registra: **0**.
- Medziverziové párovanie: **1486** funkcií: 1039 presných, 319 silných/fuzzy a 128 slabých alebo nevyriešených zhôd.
- Existujúci tracker obsahuje **65 dokončených ručných 12-bodových auditov** (65 Win16, 0 DOS). Ďalších **1293 presných/silných zhôd** je stále označených ako čakajúcich (864 Win16, 429 DOS).
- Slabých/nevyriešených 128 funkcií je zahrnutých v tomto súbore, hoci nepatria do trackera 1 358 presných/silných zhôd.
- Skenovanie priamych volaní našlo 3663 jedinečných väzieb funkcia→cieľ. Pri 500 funkciách export neukazuje priameho volajúceho. Sken nezachytáva adresované funkcie, callback tabuľky, prerušenia ani nepriame/jump-table odkazy.

## Obsah CSV pre jednotlivé funkcie

Každý riadok obsahuje funkciu zo zdrojovej platformy a jej spárovaný náprotivok, ak ho register uvádza. Číslované polia zodpovedajú existujúcemu 12-bodovému auditu:

1. Identita, presné riadky tela a SHA-256 tela.
2. Signatúra dekompilátora, názvy parametrov a deklarovaná volacia konvencia.
3. Priame dôkazy o triede alebo nepriamom dispatchi; nejasné vlastníctvo ostáva otvorené.
4. Lokálne premenné podľa dekompilátora.
5. Pomenované globálne odkazy a priradenia, plus príklady zápisov cez ukazovatele.
6. Číselné offsety ukazovateľov a indexovanie polí. Nie sú automaticky potvrdenými poľami štruktúr.
7. Hexadecimálne literály a použité identifikátory reťazcov.
8. Počty vetiev a príklady riadkov vetvenia.
9. Symbolické lokálne volania a priami volajúci.
10. Viditeľné zápisy, kandidáti externých API, nepriame volania a portové I/O.
11. Explicitné vetvy a návraty, ktoré môžu ukazovať hranice alebo chybové cesty.
12. Umiestnenie v zdroji, hash kódu, skoršia istota a stav ručného auditu.

Stĺpec `previous_summary_and_evidence` zachováva skoršiu interpretáciu funkcie a jej zaznamenanú mieru istoty. Pôvodné riadky zdroja ostávajú oddelené od navrhnutého sémantického názvu.

## Hranica interpretácie

Toto je úplný **štrukturálny statický prechod** cez všetkých 1 486 položiek registra. Zvyšných 1 421 riadkov bez dokončeného ručného auditu neoznačuje za hotové sémantické 12-bodové rozbory. V dodanom trackeri je ako plne ručne skontrolovaných označených iba 65 funkcií. CSV tento stav zachováva pri každom riadku.

DOS C export obsahuje zlúčené alebo nepresné hranice funkcií z Ghidry a niektoré zdanlivé prototypy nesedia s volaniami. Export preto umožňuje široko kontrolovať volania, konštanty, offsety a vetvenie, no pri dotknutých rutinách treba pred potvrdením presného významu skontrolovať surový assembler a relocácie/XREF. Ani jeden export nepotvrdzuje správanie počas behu hry.

## Kontrola výsledku

- Hashy binárnych súborov zodpovedajú projektovým referenciám: Win16 `12fe5168…c544481`, DOS `552d250e…d372f301`.
- Parser našiel presne 967 Win16 a 519 DOS definícií, čo zodpovedá inventáru 967 + 519.
- Každý z 1486 riadkov CSV obsahuje telo funkcie, stav párovania, zdrojové riadky a SHA-256 tela.
- Súčet zhôd sedí: 1 039 presných + 319 fuzzy = 1 358 presných/silných; po pripočítaní 128 slabých/nevyriešených vznikne 1 486.

## Zostávajúci ručný rozbor

CSV sprístupňuje dôkazy z tela každej funkcie. Zostáva ručne uzavrieť správanie, prototypy, vlastníctvo metód/callbackov, štruktúry a vedľajšie účinky podľa surového assembleru a XREF; najprv 1 293 presných/silných riadkov čakajúcich v trackeri, potom 128 slabých/nevyriešených zhôd. Pozorovania z behu hry ostávajú samostatným druhom potvrdenia.