# DOS 2.0: CRT TZ stav, parser a cache

## Presné NON-CODE polia

| DS | Obrazový interval, koniec exclusive | B | Doložený typ / počiatočný obsah |
|---|---|---:|---|
| 24A2 | [29BB2,29BB5) | 3 | environment key `TZ\0` |
| 24A6 | [29BB6,29BBA) | 4 | mutable signed DWORD, 28800 |
| 24AA | [29BBA,29BBC) | 2 | mutable WORD daylight indikátora, 1 |
| 24AC | [29BBC,29BC0) | 4 | mutable name buffer, `PST\0` |
| 24B0 | [29BC0,29BC4) | 4 | mutable name buffer, `PDT\0` |
| 24B4 | [29BC4,29BC6) | 2 | NEAR pointer, počiatočne 24ACh |
| 24B6 | [29BC6,29BC8) | 2 | NEAR pointer, počiatočne 24B0h |

Spolu **21 B / 7 polí**, s konkrétnymi operáciami v parseri a SHA v `data_fields.csv`. Samostatný nulový BYTE **[29BB5,29BB6)** sa nepromuje: zarovnanie/padding zatiaľ nie je doložené. Nadväzujúci RNG stav začína na 29BC8h a do tejto dávky sa nepočíta znova.

DWORD jednotku sekúnd podporujú konkrétne násobenia hodín 3600 a minút 60, plus pripočítanie sekúnd. Smer voči UTC a úplná kalendárna/DST interpretácia sa nepredpokladajú iba z názvu TZ. Pôvodné skratky sú bajty referenčného EXE, nie tvrdenie o časovom pásme používateľovho počítača.

## Štyri funkčné rozsahy

| FAR vstup | Obrazový interval, koniec exclusive | Inštrukčné B / počet |
|---|---|---:|
| 11EE:2BF4, cached init | [14AD4,14AE5) | 17 / 5 |
| 11EE:2C06, TZ parser | [14AE6,14BE0) | 248 / 102 |
| 11EE:23B4, counted near-string copy | [14294,142BC) | 40 / 24 |
| 11EE:2416, near-string long conversion | [142F6,1434E) | 87 / 48 |

Spolu **392 B / 179 inštrukcií**. CFG prieskum vynecháva nedosiahnuté bajty v obalových rozsahoch parsera a konverzie; neoznačuje ich automaticky za padding. „Near-string“ označuje argumentové pointery, nie návrat: tieto vstupy končia FAR RET. Parser navyše používa už analyzovaný low32 multiply helper 11EE:3AD8, ktorý sa nezapočítava druhýkrát.

## Parser a cache

Parser odovzdá key pointer 24A2h rutine 11EE:248A a výsledok AX používa ako near pointer v DS. Pri AX=0 alebo prvom BYTE=0 sa vráti bez zmeny TZ dát. Skutočný lookup prostredia je v tejto dávke otvorená závislosť.

Pre testované platné vstupy `ABC[sign]hours[:minutes[:seconds]][suffix]` vykoná:

```text
copy_count_3(*standard_name_pointer, input)
p = input + 3
negative = (*p == '-')
if negative: p++
offset32 = parse_long(p) * 3600 mod 2^32
skip '+' a digit znaky podľa pôvodnej slučky
if next == ':': offset32 += parse_long(minutes)*60; skip digits
if next == ':': offset32 += parse_long(seconds); skip digits
if negative: offset32 = negate32(offset32)
daylight_WORD = sign_extend8(*p)
if daylight_WORD != 0: copy_count_3(*daylight_name_pointer,p)
else: BYTE[*daylight_name_pointer] = 0
```

Daylight WORD sa **nenormalizuje na 1**: pri suffixe `DEF` uloží 68 (ASCII D). Sign extension vyplýva z CBW; high-BYTE suffixy nie sú súčasťou replay matice. Pri absent suffixe sa vymaže iba prvý BYTE názvu, nie celý buffer: z pôvodného `PDT\0` zostane `\0DT\0`. Counted copy prenáša tri bajty; pri troch nenulových znakoch sama nepridá štvrtý NUL. Ten zostáva z predchádzajúceho obsahu buffera. Všetci ďalší writeri a obsah pri chybných pointeroch nie sú uzavretí.

Cached wrapper 2BF4 číta WORD **DS:3CA8**. Pri nule zavolá parser a potom WORD inkrementuje; pri nenule ho preskočí. Cache leží mimo file-backed obrazu a nepridáva NON-CODE bajty. Riadená sekvencia potvrdila, že zmena seedovaného environment výsledku po prvom cached volaní už TZ dáta nezmení, zatiaľ čo priamy parser 2C06 ich obnoví. Prirodzená inicializácia/reset cache a celé environment správanie zostávajú otvorené.

## Kopírovanie a konverzia

Copy helper má near destination/source a WORD count, nastaví ES=DS, používa LODSB/STOSB a po zistení NUL vypĺňa zvyšok počtu nulami. Pri plnom prenose bez NUL žiadny extra terminátor nepridáva. Smer vyžaduje DF=0, ktorý v tele nenastavuje. Testovaný parser používa count=3, nie všetky možné counts alebo pointery.

Long conversion preskočí ASCII medzeru/TAB, rozpozná znamienko a akumuluje desiatkové číslice do DX:AX s 32-bitovým modulo správaním. V tejto dávke sa vykonáva pre vybrané korektné hodiny/minúty/sekundy; nevydáva sa za exhaustívnu validáciu všetkých reťazcov, overflowov, locale alebo chybných formátov. SI/DI/BP/DS a lokálny stack sú overené pri návrate parsera v modeli; pracovné registre a ES sa nepovažujú za všeobecne zachované.

## Controlled replay a reprodukcia

`audit_replay_pass1_timezone.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT` pripína SHA obrazu, overí štyri funkcie a sedem polí a aplikuje EXEPACK relokácie. Pôvodný parser, copy, long converter a multiply helper sa vykonávajú bez náhrady. **Iba environment lookup 11EE:248A je nahradený RETF/hookom**, ktorý overí key `TZ` a vráti seedovaný near pointer alebo nulu. Hostiteľské prostredie sa nemení.

Pri load bázach 0/1000h sa vykoná 120 platných kombinácií hodín (0,1,8,12,23), znamienok, minút/sekúnd a suffixu na každú bázu; absent/prázdny vstup; prvé cached volanie, preskočenie po zmene vstupu a explicitný refresh. Spolu **250 prípadov, 0 odchýlok**. Overujú sa offset, flag, presné štyri bajty oboch name bufferov, počty lookup volaní, cache a BP/SI/DI/DS/SP v modeli.

Artefakty `pass1_timezone/`: štyri ASM CSV, `data_fields.csv`, `cases.csv`, `summary.json`, nová CSV/JSON mapa, promotion summary a nezávislá partition kontrola. Nevykonáva sa pôvodný getenv, DOS environment segment ani prirodzené volanie kalendárneho subsystému. Chybné/krátke/non-ASCII TZ vstupy a všetky numerické hodnoty zostávajú otvorené.

## Pokrytie

21 B prešlo z CLASSIFIED ONLY do PARTIAL. Aktuálne **55 035 B PARTIAL, 2 216 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, presne 57 295 B. Nezávislá kontrola overila 701 intervalov, SHA, presné členstvo a nulové diery/prekryvy.

Centrálny katalóg: **70 rozsahov, 2 495 inštrukcií / 6 066 B kódu**, 55 921 B typovaných dát celého obrazu a 55 033 B historických NON-CODE dát. Rozdiel 2 B voči PARTIAL zostáva samostatná neuzavretá relokácia. Controlled replay súčet je 407 751 plus osobitne 65 548 normalizačných prefixových prípadov. Prirodzené runtime testy 0. Výsledky zostávajú PARTIAL; GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika sémantického percenta: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú; nové percentá sú N/A a predošlé orientačné.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | testovaný TZ formát v CRT | chybné formáty | parser hranice |
| Dátové typy a konštanty | 95 % | N/A | 21 B / 7 polí | pad BYTE a ďalší stav | jeho referencie |
| Tabuľky a ukazovatele | 93 % | N/A | dva near name pointery | všetci writeri | environment kontext |
| Funkcie / ASM / CFG | 90 % | N/A | 392 B / 179 inštrukcií | getenv a širší calendar | 248A |
| RNG | 97 % | N/A | bez nového RNG dôkazu | prirodzené seedy | reset caller |
| Scheduler | 96 % | N/A | CRT časový stav oddelený | herné použitie | timestamp calleri |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | call ordering | DEMO stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping | render stopa |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | AI/lifecycle | health updater |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | prirodzené vstupy | effect producer |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | asset identity | descriptor producer |
| SAVE / LOAD | 92 % | N/A | mutable CRT cache/state oddelené | prípadná väzba na timestampy | call ledger |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | CRT časová parity | Win TZ dáta |

## Runtime testy na vykonanie

Zachytiť prirodzený environment lookup, DS:3CA8 a časové dáta pred/po prvom cached volaní. Overiť, či hra časový subsystém skutočne používa a v ktorých caller scenároch. Chýbajúce/prázdne TZ skúšať v izolovanom DOS prostredí bez zmeny hostiteľských nastavení. Modelované TZ hodnoty nedokazujú používateľské časové pásmo ani úplné kalendárne správanie. DOSBox-X vykonanie zatiaľ chýba.
