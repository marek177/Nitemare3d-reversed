# PASS1: CRT XOR kontrola prvých 66 B DGROUP

Dávka typuje **66 B** ako presnú kontrolovanú BYTE oblasť a rekonštruuje runtime kontrolu 11EE:02EA. Pôvodná kontrola, callback dispatcher, error printer a message lookup sa vykonávajú spoločne. Modelovaný je iba DOS zápis AH40; voliteľné callbacky sú vypnuté. Úroveň PARTIAL, nie pôvodný DOSBox-X runtime dôkaz.

## Presné hranice a klasifikácia

Image SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; inventár SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`. Skript overí obe identity, každý pôvodný inštrukčný štart a presný XOR kontrolovanej oblasti.

- Dáta **DS:0000..0042, image [27710,27752)**: BYTE array 66, pôvodný XOR=55h.
- Funkcia **11EE:02EA..030E, image [121CA,121EE)**: 36 B / 19 inštrukcií.

Oblasť obsahuje úvodné nuly a CRT copyright text. Jej typovanie je založené na presne ohraničenom implicitnom LODSB čítaní všetkých 66 B, nie na samotnej ASCII pozorovateľnosti alebo tvrdení, že úvodné nuly sú padding. Copyright sa nevyhlasuje za samostatne tlačený reťazec. DS=2771h sa v modeli explicitne nastavuje; všetky prirodzené alias zápisy a startup/caller kontext ostávajú otvorené.

## Algoritmus a návratová hodnota

```text
save SI
SI = 0
CX = 0042h
AH = 0
CLD
repeat 66 times:
    AL = BYTE DS:[SI++]
    AH ^= AL
AH ^= 55h
if AH != 0:
    call 11EE:029E()
    call 11EE:0545(1)
    AX = 1
restore SI
return FAR
```

Nezhoda vyvolá pôvodný dispatcher, ktorý vypíše CR/LF a `run-time error `, potom printer code 1 vypíše `R6001` a `null pointer assignment`. V helperi nie je samostatné ukončenie procesu; celá termination cesta sa tým neuzatvára. Tieto texty sa v replayi získajú cez pôvodný vyhľadávač z pôvodných dát, nie z náhrady formattera.

Čistá vetva **explicitne nenastavuje AX=0**. AH po porovnaní je 0 a AL zostáva posledným načítaným bajtom. V pôvodnom obraze je posledný bajt 0, preto bežne vráti 0. Pri XOR-zachovávajúcej mutácii posledného bajtu na 80h vráti AX=0080h bez diagnostiky. Nie je správne bez podmienky opísať návrat ako striktne boolean 0/1.

XOR kontrola deteguje každú jednotlivú skutočnú zmenu bajtu v tejto oblasti, ale dve rovnaké XOR zmeny sa môžu vyrušiť. Nejde o univerzálny detektor zápisu cez nulový pointer ani dôkaz jeho príčiny. Pole bolo seedované modelom; prirodzený chybný zápis hry nebol reprodukovaný.

## Reprodukcia a výsledky

`audit_replay_pass1_null_guard.py IMAGE INVENTORY DECODER EMULATOR OUT` vytvára ASM CSV, `data_fields.csv`, `cases.csv`, `summary.json`. Pri load 0/1000h aplikuje reálne EXEPACK relokácie. Kontrolovaná oblasť sa pred každým prípadom explicitne nastaví. Dispatcher callback DS:2152=0 a interceptor magic DS:2534=0; ich skutočné telá nie sú súčasťou tejto skúšky.

DOS INT21/AH40 hook kontroluje handle 2, zachytí presný DS:DX/CX buffer a vráti count s CF=0. Žiadny hostiteľský súbor alebo konzola sa neprepisuje. Všetky ostatné vykonané inštrukcie, vrátane error lookupu a string scanov, zostávajú pôvodné. Kontrola sama vykoná CLD; DF po návrate preto nie je zachovaný.

**17428 prípadov, 0 odchýlok**:

- Load 0: 66 pozícií × všetkých 256 BYTE hodnôt = 16896 prípadov, vrátane 66 nezmenených prípadov.
- Load 1000h: 66 × 8 jednotlivých bitových zmien = 528 prípadov.
- Po dva XOR-cancellation scenáre na každú load bázu = 4 prípady, vrátane zmeny posledného bajtu.

Kontrolujú sa presné tri DOS write buffery alebo ich absencia, AX a návratové DS/BP/SI/DI/SP. Štandardný čistý vstup, všetky jednotlivé bajtové mutácie a zvolené párové mutácie nepredstavujú exhaustívny audit 256^66 kombinácií. SHA cases `4a8003e167a59d255361c254d5b9870e2b3b737f9c7ceed48307721e43822bd4`.

## Meranie

66 B CLASSIFIED ONLY → PARTIAL. Mapa: **56793 B PARTIAL, 458 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57295 B. Nezávislá kontrola overila 837 intervalov, SHA a presné členstvo bez dier/prekryvov. SHA mapy `6ebb1c7e19762e425955a4745544f97539d3c5d34fcc1cac3967654212694b63`. Partition integrita sama nepreukazuje sémantickú úplnosť.

Katalóg: 91 funkčných rozsahov, 3254 inštrukcií / 8161 B, 57679 B typovaných dát celého obrazu; 56791 B historických NON-CODE dát a 2 PARTIAL netypované relokačné bajty. Controlled replay 697151 plus osobitne 65548 smerových prefixových prípadov. Staršie dispatcher/printer funkcie sa nepripočítavajú znovu ako nové kódové bajty. Prirodzené runtime testy 0. GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového %: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, nové percentá N/A, predošlé orientačné. Počet mutácií ani integrita mapy nenahrádzajú sémantické pokrytie celej oblasti.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | presná XOR doména | prirodzené startup DS | startup trace |
| Dátové typy a konštanty | 95 % | N/A | 66 B, expected XOR55h | všetci writeri | write ledger |
| Tabuľky a ukazovatele | 93 % | N/A | nulové prefixy sú kontrolované dáta | alias segmenty | DS kontext |
| Funkcie / ASM / CFG | 90 % | N/A | 36 B / 19 inštrukcií | prirodzení calleri | 02EA call graph |
| RNG | 97 % | N/A | bez nového dôkazu | ordering | DEMO trace |
| Scheduler | 96 % | N/A | CRT kontrola oddelená | frekvencia kontroly | caller trace |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | driver ABI | input closure |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | init režimu | VGA setup |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | health updater |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | effect producer | damage caller |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | identity | descriptor producer |
| SAVE / LOAD | 92 % | N/A | CRT integrity stav oddelený | persistencia | SAVE ledger |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | null guard parity | Win CRT helper |

## Runtime testy na vykonanie

Zachytiť DS, kontrolovaných 66 B a skutočné callery počas prirodzeného behu/ukončenia. Error scenáre robiť v oddelenej diagnostickej kópii a sledovať callback/termination tok až po terminálny výsledok. Nezamieňať checksum mismatch so zistenou príčinou zápisu. DOSBox-X vykonanie a Win16 parity zostávajú otvorené.
