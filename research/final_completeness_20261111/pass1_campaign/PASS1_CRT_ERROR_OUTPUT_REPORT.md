# PASS1: CRT výstup chyby a FAR callback

Dávka typuje 4 B historického NON-CODE a rekonštruuje dve celé CRT rutiny. Výsledok PARTIAL: pôvodné telá a vyhľadávač správ sa vykonávajú, DOS zápis a obe hook telá sú modelované. Prirodzený error/termination tok zostáva otvorený.

## Presné adresy a klasifikácia

Image SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; inventár SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`. Skript kontroluje identity, bajty každého štartu a nezávisle rekonštruuje CFG.

**DS:2152, image [29862,29866)** je mutable FAR16 pointer, pôvodne 0000:0000. `CMP WORD PTR [2154],0` testuje segment a `CALL FAR DWORD PTR [2152]` volá pointer. Nenulový offset so segmentom 0 sa preskočí. Všetci writeri a prirodzené callback telo zostávajú neuzavretí; názov callback je pracovný, nejde o pôvodný symbol.

| Funkcia | Image interval, koniec exclusive | CFG |
|---|---|---:|
| 11EE:029E callback dispatcher | [1217E,121A0) | 34 B / 16 inštrukcií |
| 11EE:0545 error output | [12425,1245B) | 54 B / 25 inštrukcií |

Spolu 88 B / 41 inštrukcií. Printer končí trojbajtovým RETF 2 na 0578; presný koniec je 057Bh, nie 0579h. Počiatočné odmietnutie skrátenej hranice dekóderom bolo opravené pred úspešným replayom. Vyhľadávač 051A, doložený staršou dávkou, sa vykonáva pôvodný a nepripočítava sa znovu ako nová funkcia.

## Algoritmus

```text
dispatcher_029E():
    error_output_0545(00FCh)
    if WORD[2154] != 0: FAR_CALL DWORD[2152]()
    error_output_0545(00FFh)
    return FAR

error_output_0545(code_WORD):
    near_text = lookup_051A(code_WORD)  // nastaví ES=DS
    if near_text != 0:
        DX = near_text
        CX = scan_length_until_NUL(ES:DX)  // REPNE SCASB, vyžaduje DF=0
        BX = 2
        if WORD[2534] == D6D6h: NEAR_CALL WORD[2536]()
        AH = 40h
        INT 21h
    return FAR, remove 2 argument bytes
```

Skutočné správy z existujúcej tabuľky: FC je presne CR/LF, FF je `run-time error ` s koncovou medzerou. Callback teda beží medzi týmito dvomi výstupmi. Samotný dispatcher hru neukončuje; po druhom volaní sa vráti. Pomenovanie ako kompletný abort by prekročilo dôkazy.

Printer pripraví DOS handle 2 a dĺžku bez NUL. Voliteľný near interceptor dostáva pracovné registre a môže ich v skutočnom tele zmeniť; replay používa prázdny RET a nezatvára jeho ABI. CF/AX po INT 21h sa explicitne nekontrolujú, preto dispatcher po modelovanej chybe zápisu pokračuje callbackom a druhým výstupom. To nie je dôkaz úspešného zápisu na reálny stderr.

Lookup používa DS tabuľku; nastaví ES=DS a printer ho neobnovuje na pôvodné ES. BP/DI/SI/DS/SP sa v modeli overujú. Pracovné AX/BX/CX/DX a flags sa nepovažujú za všeobecne zachované. DF=0 sa seedu-je; tieto telá smer samy nenastavujú. Query FFFFh a malformed message dáta sa touto dávkou netestujú.

## Reprodukcia a výsledky

`audit_replay_pass1_crt_error_output.py IMAGE INVENTORY DECODER EMULATOR OUT` vytvára dve ASM CSV, `data_fields.csv`, `cases.csv`, `summary.json`. Pri load 0/1000h aplikuje reálne EXEPACK relokácie. DOS INT 21h/AH40 hook zaznamená presný buffer/count/handle a vráti buď úspech, alebo CF=1/AX=5. FAR callback je RETF stub a near interceptor RET stub; ich vykonanie sa zaznamenáva. Pôvodné dispatcher/printer/lookup telá sa nenahrádzajú.

**104 prípadov, 0 odchýlok**: 32 dispatcher scenárov s nulovým/nenulovým segmentom, rôznymi offsetmi pri vypnutom pointeri, interceptorom on/off a DOS success/error; 72 standalone printer scenárov pre všetkých sedem existujúcich message keys a dva chýbajúce keys 4/100h, opäť obe I/O odpovede a interceptor stavy. Kontrolujú sa presné poradie callback/interceptor/write, bajty a dĺžky textov, handle 2 a návratový stack. SHA cases `e1cb37a36bb186c4247fb94836f23fe6e587cfffd8c025fc6f0b100c4f7f6687`.

Presne 4 B CLASSIFIED ONLY → PARTIAL. Mapa: **55106 B PARTIAL, 2145 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57295 B. Nezávislá kontrola potvrdila 729 intervalov, SHA a presné členstvo bez dier/prekryvov. SHA mapy `25fc1e0823f644786002fc8e2a494ff8e9c6726d6998565694e094f3de7e55c2`. Integrita mapy nie je dôkaz úplnej sémantiky.

Katalóg: 84 funkčných rozsahov, 2970 inštrukcií / 7433 B, 55992 B typovaných dát celého obrazu; 55104 B historických NON-CODE dát a 2 netypované PARTIAL relokačné bajty. Controlled replay 612553 plus osobitne 65548 smerových prefixových prípadov. Prirodzené runtime testy 0. GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového %: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, preto N/A; predošlé percentá orientačné. Replay počty nie sú sémantické percentá.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | sedem CRT message keys spotrebovaných | malformed dáta | sentinel query |
| Dátové typy a konštanty | 95 % | N/A | 4 B FAR callback | writeri | init ledger |
| Tabuľky a ukazovatele | 93 % | N/A | segment-zero disable pravidlo | callback telo | hook writer |
| Funkcie / ASM / CFG | 90 % | N/A | 88 B / 41 inštrukcií | prirodzený error tok | 00F4 closure |
| RNG | 97 % | N/A | bez nového dôkazu | ordering | DEMO trace |
| Scheduler | 96 % | N/A | CRT callback oddelený | caller kontext | runtime call graph |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | input driver | driver ABI |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | init režimu | VGA setup |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | health updater |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | effect producer | damage caller |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | identity | descriptor producer |
| SAVE / LOAD | 92 % | N/A | CRT stderr cesta oddelená | DOS I/O v hre | SAVE call ledger |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | CRT error parity | Win error helper |

## Runtime testy na vykonanie

V izolovanom chybovom scenári zachytiť skutočné 2152/2154, 2534/2536, DS/ES/DF a DOS write buffer/count/CF. Overiť caller tok pred/po 029E a skutočné callback vedľajšie účinky. Nepovažovať úspešný model DOS write za reálny I/O ani dispatcher za kompletné ukončenie procesu. DOSBox-X vykonanie zostáva otvorené.
