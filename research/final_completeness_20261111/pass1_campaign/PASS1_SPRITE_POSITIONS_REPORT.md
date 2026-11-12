# DOS 2.0: sprite polohové tabuľky, animačný stav a clipping argumenty

## Presné dáta a funkcia

| Pole | DS | Obrazový interval, koniec exclusive | Obsah, desiatkovo |
|---|---|---|---|
| X pozície | 1406 | [28B16,28B20) | desať hodnôt 146 |
| Y pozície | 1410 | [28B20,28B2A) | 170,170,160,150,140,130,120,110,110,110 |
| Koncový index | 141A | [28B2A,28B2C) | WORD 9 |

Spolu **22 B** so samostatnými SHA a konkrétnymi čítaniami 083D:0500/050A/0554. WORD 9 je porovnávací koncový index, nie počet prvkov. Desať prvkov zodpovedá nominálnym indexom 0..9; prirodzený invariant indexu zostáva otvorený.

FAR funkcia **083D:04EC**, obalový rozsah **[088BC,089A2)**, má 230 B; prieskum CFG dosiahne **84 inštrukcií / 227 B**. Tri bajty za nepodmienenými skokmi 0545, 0553 a 058D sa do kódu nepridávajú a neoznačujú automaticky za padding. Všetky dosiahnuté inštrukcie sú byte-exact overené a nezávisle dekódované.

## Dátový tok a stavový postup

Pri BYTE DS:418F = FFh telo skočí na epilóg ešte pred čítaním tabuliek; táto vetva je staticky overená, nie súčasťou replay matice. Inak používa WORD DS:41A8 ako index do oboch tabuliek, bez maskovania alebo rozsahového guardu. Načíta X/Y do lokálov a uloží ich do WORDov DS:41AA/41AC **pred zmenou indexu alebo Y bonusom**.

Descriptor pre aktuálne volanie vzniká ako `WORD argument + 10*BYTE DS:418F`, v DS. Číta jeho BYTE +0/+1 (použité ako rozmery) a FAR DWORD +6 odovzdá blit závislosti. Úplný typ všetkých 10 B descriptora ani pôvod reálneho sprite assetu sa touto dávkou neuzatvára.

```text
old_selector = DS:418F
if old_selector == FFh: return
old_index = DS:41A8
x = X[old_index]; y = Y[old_index]
DS:41AA = x; DS:41AC = y
descriptor = base_argument + 10*old_selector
switch WORD DS:41A6:
  0:
    if BYTE DS:419A != 0: y += DS:4190 == 1 ? 6 : 3
    DS:419A = 0
  1:
    DS:41A8++
    if DS:41A8 == WORD DS:141A:
        DS:41A6 = 0
        call 083D:05D2(12)
  2:
    DS:41A8--
    if DS:41A8 == 0:
        DS:41A6 = 1
        DS:418F = BYTE DS:41A4
        DS:4190 = DS:418F == 2 ? 1 : 2
  other: no state update
h = min(descriptor.height, signed16(DS:454E - y + 1))
if h > 0: call blit(descriptor.pointer, x, y, width, height, width, h, 0, 31)
return
```

WORD aritmetika pre index a výšku je 16-bit; uvedený matematický zápis nenahrádza modulo/signed správanie pri extrémnych vstupoch. Testované sú hodnoty bez pretečenia výšky.

Pri prepnutí selektora v stave 2 zostáva lokálny descriptor odvodený od **starého selektora**, takže aktuálny blit dostane starý pointer. Nový selektor ovplyvní až nasledujúce vyhodnotenie funkcie. Rovnako aktuálne X/Y pochádzajú zo starého indexu, nie z už zmenenej DS:41A8. Toto je lokálny postup; časovanie celej hernej slučky nie je uzavreté.

## Hraničné invarianty

Syntetický vstup stav=1/index=9 zvýši index na 10 a minie rovnostný test s 9. Vstup stav=2/index=0 vytvorí FFFFh a minie test nuly. Aktuálne volanie ešte používa pôvodný platný index; ďalšie by pri nezmenenom selektore čítalo mimo nominálneho poľa. To dokladá potrebu caller/state invariantov, nie prirodzenú chybu hry.

Pri zadaných nemenných callee efektoch sú lokálne bezpečné prechody stav=1/index=0..8 a stav=2/index=1..9: prvý smer dosiahne index 9 a prejde do stavu 0, druhý dosiahne 0 a prejde do stavu 1. Helper 05D2 alebo iní writeri môžu stav ovplyvniť; ich kontrakty a LOAD/inicializácia sa zatiaľ neuzatvárajú.

## Controlled replay a reprodukcia

`audit_replay_pass1_sprite_positions.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT` vykoná pôvodné telo pre 2 selektory (0/2), 4 stavy (0..3), 10 indexov, 2 bonus flagy, 2 hodnoty DS:4190 a 3 clip limity (100/170/200), pri 2 load bázach: **1 920 prípadov, 0 odchýlok**. EXEPACK relokácie sú aplikované.

Transition helper 083D:05D2 a blit 0156:07DE sú nahradené RETF. Seedované descriptory majú rozmery 20×30 a odlišné FAR pointery; model nečíta ani nekreslí payload. Overuje sa úplných desať WORD argumentov blitu, jeho vynechanie pri nekladnej výške, argument 12 transition helpera, stavové WORDy/BYTE, uložené pôvodné súradnice, BP/SI a SP po návrate. Mock helpery tieto dáta nemenia. Prirodzené descriptory, framebuffer a renderer ABI tak zostávajú otvorené.

Artefakty `pass1_sprite_positions/`: `instructions.csv`, `data_fields.csv`, `cases.csv`, `summary.json`; ďalej mapa CSV/JSON, promotion summary a nezávislá partition kontrola. Neúspešný lineárny dekódovací pokus sa nahradil CFG prieskumom, aby sa tri nedosiahnuté bajty nezapočítali ako inštrukcie.

## Pokrytie

22 B prešlo z CLASSIFIED ONLY do PARTIAL. Aktuálne **54 977 B PARTIAL, 2 274 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, presne 57 295 B. Nezávislá kontrola 675 intervalov overila SHA, presné členstvo a nulové diery/prekryvy.

Centrálny katalóg: **54 rozsahov, 1 911 inštrukcií / 4 642 B kódu**, 55 823 B typovaných dát celého obrazu a 54 975 B historických NON-CODE dát. Rozdiel 2 B voči PARTIAL zostáva neuzavretá relokácia. Controlled replay prípady: 13 993 plus osobitne 65 548 normalizačných prefixových prípadov. Prirodzené runtime testy 0. Výsledky zostávajú PARTIAL; GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika sémantického percenta: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, nové percentá sú N/A a predošlé orientačné.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | prirodzené stavy | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 22 B / 3 polia | prirodzené indexy | writeri DS:41A8 |
| Tabuľky a ukazovatele | 93 % | N/A | 10 prvkov a descriptor stride 10 | typ všetkých descriptor polí | reálne descriptory |
| Funkcie / ASM / CFG | 90 % | N/A | 227 B / 84 inštrukcií, 1 920 prípadov | callee efekty | 05D2 a 07DE |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | old/current state postup | prirodzené poradie tickov | volacie stopy |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | pôvod stavov | prechody vstupov |
| Renderer / VGA | 94 % | N/A | výber výšky a raw blit argumenty | skutočný clipping/pixely | 07DE kontrakt |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | AI/lifecycle | inicializátory |
| Zbrane / projektily | 92 % | N/A | selektorový prechod a starý descriptor | presná gameplay identita | writeri 418F/41A4 |
| Sprity / HUD / paleta | 92 % | N/A | polohové tabuľky a animačný stav | reálne assety | descriptor producer |
| SAVE / LOAD | 92 % | N/A | otvorené indexové invarianty | stav po LOAD | serializačné rozsahy |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | animácia parity | Win ekvivalent |

## Runtime testy na vykonanie

Pri prirodzených prechodoch selektora zachytiť DS:418F/41A4/41A6/41A8, descriptory a súradnice pred/po volaní. Overiť, či nepriaznivé dvojice stav=1/index=9 a stav=2/index=0 môžu prirodzene vzniknúť, vrátane LOAD. Porovnať skutočné pixely a clipping s argumentmi blitu. Seedované nekonzistentné stavy nie sú dôkaz prirodzeného herného problému. DOSBox-X vykonanie zatiaľ chýba.
