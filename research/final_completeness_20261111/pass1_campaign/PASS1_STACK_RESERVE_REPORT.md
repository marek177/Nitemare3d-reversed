# PASS1: runtime rezervácia zásobníka

Dávka typuje 6 B historického NON-CODE a rekonštruuje 36-bajtový runtime helper. Úroveň PARTIAL. Úspešná vetva sa vykonáva až po návrat; neúspešné vetvy iba po vstup do shared error alebo používateľskej obsluhy. Ich telá a prirodzení calleri nie sú uzavretí.

## Adresy a dôkazy

Image SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; inventár SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`. Skript overí oba vstupy a bajty každého nezávisle dekódovaného štartu.

| Položka | Image interval, koniec exclusive | Typ / initial |
|---|---|---|
| 11EE:02C6 helper | [121A6,121CA) | 36 B / 19 inštrukcií |
| DS:2156 handler | [29866,2986A) | mutable FAR16 pointer, FFFF:FFFF |
| DS:215A lower bound | [2986A,2986C) | mutable unsigned WORD, E130h |

Kanonické DS je 2771h. Handler typ dokazuje `JMP FAR DWORD PTR [2156]`; sentinel testuje iba offset WORD [2156], nie segment. Limit typ a šírku dokazuje unsigned CMP BX,[215A]. Prirodzený startup DS/SS, všetci writeri a volania zostávajú otvorené. Označenie runtime/stack helper vychádza z aritmetiky zásobníka a okolitého CRT kódu; pôvodný symbol ani presná externá knižničná signatúra sa netvrdia.

## Algoritmus a register/stack kontext

```text
input: AX = požadovaný počet bajtov, na SS:SP je FAR return IP:CS
pop CX  // return IP
pop DX  // return CS
base = SP
BX = (base - AX) & FFFF
if unsigned_subtraction_borrow == 0 and BX >= WORD[DS:215A]:
    SP = BX
    push DX; push CX
    RETF
else:
    push DX; push CX  // obnoví pôvodný návrat na pôvodnom mieste
    AX = (WORD[DS:2156] + 1) & FFFF
    if AX == 0:
        AX = 0
        JMP 11EE:00F4
    else:
        JMP FAR DWORD PTR DS:[2156]
```

Pri úspechu finálny SP je pôvodný SP+4−amount; FAR návrat sa presunie tesne pod nový SP. AX ostáva požiadavkou, CX/DX nesú rozobranú návratovú adresu a BX je nový SP. Nejde o štandardnú funkciu, ktorá zachová bežnú polohu stacku alebo vracia pointer v DX:AX. Pri amount=0 len spotrebuje pôvodný FAR return. Požiadavka sa nezaokrúhľuje; aj nepárne veľkosti sa akceptujú podľa limitu.

Na chybe ostáva pôvodný SP a pôvodný FAR return na mieste. Handler sa vyvoláva tail JMP, nie CALL; v okamihu vstupu vidí existujúci návrat na stacku. Offset FFFFh znamená shared error cestu bez ohľadu na segment. Replay pri shared 00F4 alebo custom handler vstupe zastaví a ich správanie netvrdí. Vstupné SP hodnoty v testoch nepretiekli pri dvoch úvodných POP; správanie SP blízko FFFF cez wrap sa touto maticou neuzatvára.

## Reprodukcia

`audit_replay_pass1_stack_reserve.py IMAGE INVENTORY DECODER EMULATOR OUT` vytvára ASM CSV, `data_fields.csv`, `cases.csv`, `summary.json`. Pôvodné inštrukcie sa vykonávajú bez mockovaných tiel; chybové ciele sú stop adresy. Pri load 0/1000h sa aplikujú reálne EXEPACK relokácie. SS je modelované 5000h a DS sa explicitne nastavuje.

**65936 prípadov, 0 odchýlok**: všetkých 65536 WORD požiadaviek pri load=0, entry SP=FF00h, limit=E130h, sentinel handler; ďalej 400 hranových prípadov pri oboch load bázach, štyroch SP, troch limitoch a dvoch handler offsets (FFFFh/0100h). Kontroluje sa presný cieľ, výsledný SP, DS, návratová adresa na chybe a AX=0 pri shared error vstupe. Nejde o exhaustívny súčin všetkých SS/SP/limit/pointer stavov. SHA cases `134551967be417ca4aac3f018ad63b9435fae7b25619517b73658c0881d432da`.

Presne 6 B CLASSIFIED ONLY → PARTIAL. Aktuálna mapa: **55102 B PARTIAL, 2149 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57295 B. Nezávislá kontrola overila 728 intervalov, SHA a presné členstvo bez dier/prekryvov. SHA mapy `7a41a71e5d68a84e01c6514b06c34c89bf66ceb5834cea49c687621bf6823a27`. Integrita mapy sama nedokazuje sémantickú úplnosť.

Katalóg: 82 funkčných rozsahov, 2929 inštrukcií / 7345 B, 55988 B typovaných dát celého obrazu; 55100 B historických NON-CODE dát a 2 netypované PARTIAL relokačné bajty. Controlled replay 612449 plus osobitne 65548 smerových prefixových prípadov. Prirodzené runtime testy 0. GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového %: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, preto N/A; predošlé čísla orientačné. Testové počty nie sú sémantické percentá.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | úplný inventár | zostávajúce intervaly |
| Dátové typy a konštanty | 95 % | N/A | 6 B handler/limit | startup writeri | limit inicializácia |
| Tabuľky a ukazovatele | 93 % | N/A | FAR handler sentinel offset | custom handler | writer ledger |
| Funkcie / ASM / CFG | 90 % | N/A | 36 B / 19 inštrukcií | shared error 00F4 | error closure |
| RNG | 97 % | N/A | bez nového dôkazu | ordering | DEMO trace |
| Scheduler | 96 % | N/A | CRT stack odlíšený | prirodzené callery | call graph |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | input driver | ovládač ABI |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | init režimu | VGA setup |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | health updater |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | effect producer | damage caller |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | identity | descriptor producer |
| SAVE / LOAD | 92 % | N/A | runtime stack stav oddelený | persistencia | SAVE ledger |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | CRT helper parity | Win stack helper |

## Runtime testy na vykonanie

Zachytiť prirodzené AX/SS/SP pri helper vstupe, pôvod DS:215A a všetky zápisy handler pointera. Overiť relocáciu návratu na stacku pri reálnom calleri a error cestu v izolovanom diagnostickom scenári. Nepovažovať zastavenie na handler vstupe za vykonanú obsluhu. DOSBox-X vykonanie zostáva otvorené.
