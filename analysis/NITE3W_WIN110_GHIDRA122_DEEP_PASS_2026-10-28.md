# Nitemare 3D Win16 1.10 — hĺbkový statický prechod v Ghidre 12.2

## Výsledok a hranice

Ghidra 12.2 bola skutočne spustená v Linux headless režime s JDK 25.0.2. Otvoril som predchádzajúci projekt, vykonal čistý import toho istého Windows NE EXE, exportoval všetky evidované interné funkcie a doplnil dva prechody obnovy kandidátov. Opravil som konkrétny nepriamy skok, ktorý blokoval dekompiláciu. Výsledkom je projekt s 1 252 internými funkčnými vstupmi, ich C exportmi, disassemblážou, referenciami a registrom ďalšieho sémantického overovania.

**Úplná identifikácia všetkého neznámeho kódu nie je dokončená.** Nový funkčný vstup ani úspešná dekompilácia nie sú dôkaz správnej hranice funkcie, správneho C prototypu, významu všetkých polí alebo runtime dosiahnuteľnosti. Osem funkcií má konkrétne preskúmaný a anotovaný výrez správania; ostatné vyžadujú spojenie s predchádzajúcimi identitami a ďalšiu analýzu. Hra sa v tomto prechode nespúšťala, 1:1 parita sa netestovala.

## Identita vstupu

| Vlastnosť | Hodnota |
|---|---|
| Súbor | `nite3w - 110.exe` z predchádzajúceho overovacieho balíka |
| SHA-256 | `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481` |
| Veľkosť | 230 400 B |
| Hlavička | NE na file offsete `0x80`, 10 segmentov, alignment shift 4 |
| Kódové segmenty | NE 1–4; v tomto projekte `1000`, `1008`, `1010`, `1018` |
| Inicializované DS dáta | NE segment 10; v projekte `1048` |
| Nástroj | Ghidra 12.2, build 20261016; Java 25.0.2 |

Označenie 1.10 nadväzuje na názov a predchádzajúcu identifikáciu dodaného súboru. Všetky závery sú viazané na uvedený hash; neplatia automaticky pre Win16 1.8 ani DOS.

## Merateľné pokrytie

Porovnávam rovnakú množinu segmentov a rovnaký spôsob exportu. Starší údaj „1 588 funkcií“ z `getFunctionCount()` nie je vhodný na priame porovnanie s iterátorom `getFunctions(true)` a počtom interných vstupov.

| Metrika | Východiskový projekt | Výsledný projekt |
|---|---:|---:|
| Funkčné vstupy v štyroch kódových segmentoch | 968 | 1 252 |
| Interné funkcie s dokončenou dekompiláciou | 967 | 1 252 |
| Položky v samostatnom bloku EXTERNAL | 310 | 310 |
| Bajty definovaných inštrukcií | 126 659 | 156 385 |
| Bajty definovaných dát v kódových segmentoch | 1 681 | 1 681 |
| Neklasifikované bajty v kódových segmentoch | 41 348 | 11 622 |

Pribudlo **284 kandidátskych vstupov** a **29 726 bajtov inštrukcií**. Obe čísla zahŕňajú heuristickú obnovu, ktorá vyžaduje kontrolu. Zostávajúcich 11 622 B nemožno označiť za 11 622 B neznámeho vykonateľného kódu: rozsahy môžu obsahovať padding, tabuľky, konštanty, metadata alebo doteraz nerozpoznané inštrukcie.

| Segment | Celkom B | Inštrukcie B | Definované dáta B | Neklasifikované B |
|---|---:|---:|---:|---:|
| `1000` | 56 546 | 51 984 | 571 | 3 991 |
| `1008` | 29 694 | 28 043 | 264 | 1 387 |
| `1010` | 61 372 | 58 054 | 712 | 2 606 |
| `1018` | 22 076 | 18 304 | 134 | 3 638 |

## Konkrétne zistenia

| Status | Adresa | Zistenie a primárny dôkaz | Istota |
|---|---|---|---|
| Confirmed | `1000:03E8–03F3` | `MOV BX,SP; MOV BX,SS:[BX+4]; LDS BX,[BX]; JMP FAR [BX+7C]`. Virtuálny tail thunk na slot `+7C`; konkrétna trieda a cieľ neznáme. | High pre inštrukcie, Unknown pre identitu triedy |
| Confirmed | `1000:03F4–03FF` | Rovnaká konštrukcia, slot `+78`. | High pre statický výrez |
| Confirmed | `1000:0400–0420` | Na `0406` odovzdá handle z `object+4`, potom päť argumentových wordov; na `0418` volá import `TEXTOUT`; `RETF 0x0C`. | High pre wrapper; prototyp je predbežný |
| Confirmed | `1000:0422–045A` | `TABBEDTEXTOUT` na `044A`; `AX` a `DX` sa uložia do dvojwordového výsledku na `044F/0451`; návrat ukazuje na výsledný buffer. | High |
| Confirmed | `1000:0752–0768` | `node+0E = DS:04FE; DS:04FE = node`. Vloženie na hlavu prepojeného zoznamu; vlastníctvo ani presná trieda nie sú určené. | High pre zápisy |
| Confirmed | `1000:13AA–1481` | Záporný hook code sa reťazí cez `DEFHOOKPROC` alebo `CALLNEXTHOOKEX`. Pri správach `0x24/0x81` bez existujúcej väzby zavolá `132C`, nastaví window procedúru na `1000:137E` cez index `-4`, uloží pôvodnú procedúru, odpojí hook a nuluje `DS:0586`. | High pre vetvy a API reťazec |
| Confirmed | `1000:1482–14CB` | Registračná cesta odovzdáva hook type `4` a far callback `1000:13AA` do `SETWINDOWSHOOK` alebo `SETWINDOWSHOOKEX`; ukladá návrat na `0588/058A` a objekt na `0586`. | High |
| Confirmed / Inferred | `1000:16A6` | Nuluje zodpovedajúce aplikačné polia `+1E/+20`, uvoľní naviazaný objekt cez virtuálny slot `+30`, volá `12BE/1356` a slot `+60`. Cleanup potvrdený; označenie konkrétneho C++ deštruktora zostáva Inferred. | High pre operácie, Medium pre úlohu |
| Inferred | `1000:092C` | Inicializuje polia `+4=-1`, `+6=0`; vetví podľa flagu `0x1000`, používa lokálny buffer 260 B a handle operácie. Pravdepodobný frameworkový file-open wrapper. Presný kontrakt a trieda zostávajú otvorené. | Medium |
| Confirmed / Inferred | `1008:4E24` | Opravená osemsmerná tabuľka na `4E14` a skok na `4E7D`. Kód spracúva formátovacie špecifikátory, width, precision, `*` a length modifikátory; interpretácia ako runtime formátovací engine je silná, presný CRT názov a ABI nie sú potvrdené. | High pre tabuľku, Medium pre úplnú identitu |

Zdrojom sú bajty EXE, Ghidra listing a importné referencie vo výslednom balíku. Automaticky odhadnuté C prototypy majú chyby vo far pointeroch, segmentových registroch a parametroch. Napríklad textové symboly objavujúce sa na mieste numerických argumentov v C exporte **nepreukazujú odkaz na príbehový text**. Rozhodujúca je disassembláž a skutočná segmentová hodnota.

## Oprava `1008:4E24`

Pôvodná dekompilácia končila chybou `Bad instruction count exceeded`, s prekrývaním `1008:4591/4590` a cestami do neexistujúcej pamäte. Samotná oprava práv natívnych nástrojov problém neodstránila: zopakoval sa aj pri čistom importe.

Na `1008:4E7D` sú bajty `2E FF A7 14 4E`, teda nepriamy skok cez `CS:[BX+4E14]`. Osem wordov pred vstupom funkcie obsahuje:

`4E82, 4E8D, 4EA1, 4ED5, 4F01, 4F09, 4F32, 4F64`.

Automat na `4E59–4E7B` používa 89-bajtovú tabuľku `DS:08E2`: nízky nibble klasifikuje znak, vysoký nibble dáva ďalší stav. Pre znaky mimo `0x20..0x78` sa použije trieda 0. Triedy sú najviac 8 a stavy najviac 7, takže transition index `8*class+state` je najviac 71 a zostáva v tabuľke. Počiatočný stav je 0. Overil som všetkých **256 × 8 = 2 048** kombinácií znak/stav proti bajtom EXE; každá vedie do stavu 0–7. Tým je staticky podložený počet ôsmich cieľov.

Použil som Ghidra `JumpTable.writeOverride`, pridal computed-jump referencie a obnovil telo funkcie podľa pribudnutých vetiev. Dekompilácia potom úspešne skončila. C export stále obsahuje varovania a predbežné typy; úspech neznamená, že každý helper alebo blok je plne pochopený.

## Postup a reprodukcia

1. Overenie hashu a NE hlavičky, otvorenie pôvodného projektu.
2. Úplný export funkcií, inštrukcií, referencií a bajtového pokrytia.
3. Čistý NE import s opravenými executable právami Linux natívnych nástrojov.
4. Prvý kandidátsky prechod: 181 prológov plus štyri výslovné adresy; 185 nových vstupov.
5. Osem doložených cieľov switch override pre `4E24`.
6. Druhý kandidátsky prechod: 99 vstupov podľa `ENTER` prológov a virtuálnych thunkov.
7. Anotácia ôsmich preskúmaných výrezov, nový úplný export a kontrola 2 048 stavových prechodov.

Skripty sú v `scripts/`. Poradie pre čistý projekt po importe: `N3DRecoverCandidates.java candidates.txt recovery.tsv`, `N3DFixFormatSwitch.java`, `N3DRecoverCandidates.java candidates2.txt recovery2.tsv`, `N3DAnnotateVerified.java`, `N3DDeepExport.java OUTPUT`, `N3DCoverage.java OUTPUT`. Použi absolútne cesty. Exportéry nemenia vstupný EXE; obnovovacie skripty menia analytickú databázu. Automatická analýza bola pri následných skriptoch vypnutá cez `-noanalysis`; žiadne skryté opakované premenovanie sa nepovažuje za dôkaz.

## Otvorené otázky a ďalší rozlišujúci test

- **284 nové kandidátske vstupy:** preveriť xrefs, koniec, near/far návrat, zdieľané bloky, thunk/vtable identitu a typy. `recovery.tsv` a `recovery2.tsv` zachovávajú pôvod kandidátov.
- **Existujúce identity:** spojiť `semantic_review_queue.tsv` s kanonickými katalógmi podľa hashu a NE segment:offset. Riadok `unknown_or_prior_identity_not_joined` znamená, že tento prechod nespojil staršiu identitu; neznamená automaticky nový objav.
- **11 622 B bez klasifikácie:** každý rozsah preveriť ako code/data/padding. Najväčší `1018:48B7–563B` má 3 461 B a obsahuje tabuľkovo pôsobiace dáta; ich presný formát zostáva Unknown. Nevykonať plošnú disassembláž tabuliek len kvôli vyššiemu počtu inštrukcií.
- **Hook:** breakpoint na `1000:13AA`, zachytiť hook code, správu, HWND, `0586/0588/058A` a starú/novú window procedúru počas vytvorenia okna. Overí runtime dosiahnuteľnosť a správnosť naviazaného objektu.
- **Formatter:** zachytiť vstupný formát, DS, callback writer a argumentový kurzor pri `4E24`; na konkrétnych formátoch porovnať výsledné bajty. Potrebné na presný ABI model.
- **Herné systémy:** tick-exact scheduler, projektily/damage, save/load prvý frame, DEMO deterministickosť a renderer zostávajú samostatné behaviorálne úlohy. Tento statický prechod ich neuzatvára.

## Obsah výstupu

- Uložený projekt `WIN110.gpr` a adresár `WIN110.rep`, vstupný EXE a hash.
- `final-results/decompiled/`: samostatný C export každého evidovaného vstupu; EXTERNAL položky sú od interného kódu oddelené v registroch.
- `functions.tsv`, `listing.tsv`, `references.tsv`, `coverage.tsv`, `undefined_ranges.tsv`.
- `semantic_review_queue.tsv`: interné funkcie, priame cally, počty dátových referencií, varovania a stav preskúmania.
- `format_state_transitions.tsv` a `verification.json`.
- Skripty obnovy, opravy, anotácie, exportu a kontrol; záznamy behov.

## Istota

**High** pre identitu EXE, vykonané Ghidra behy, počty exportovaných položiek, bajtové merania a vyššie uvedené priame inštrukčné operácie. **Medium** pre interpretácie frameworkových/CRT úloh. **Unknown** pre úplnú sémantickú obnovu, runtime dosiahnuteľnosť všetkých kandidátov a 1:1 paritu.
