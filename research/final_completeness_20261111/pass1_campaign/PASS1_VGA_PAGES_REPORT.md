# PASS1: VGA page segmenty a dve výmeny stránok

Nová dávka typuje 4 B historického NON-CODE a rekonštruuje dve celé FAR rutiny. Úroveň PARTIAL: pôvodné inštrukcie boli vykonané proti modelovanému I/O, nie proti skutočnému VGA. Prirodzené stránkové invarianty, režim displeja a časovanie zostávajú otvorené.

## Presné dáta a funkcie

Kanonický DOS 2.0 image SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; inventár SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`. Skript kontroluje identity aj bajty každého dekódovaného štartu.

| Pole pri DS=2771h | Image interval | Typ / počiatočná hodnota | Dôkaz |
|---|---|---|---|
| DS:012C | [2783C,2783E) | mutable WORD segment / A000h | načítanie, XCHG s 012E, zápis späť v oboch flip rutinách |
| DS:012E | [2783E,27840) | mutable WORD draw segment / A400h | druhá polovica výmeny, MOV ES,AX v rendererovi 0156:046C/046F |

Inventár obsahuje 19 priamych DS referencií k týmto dvom WORD. Sú v `direct_references.csv`; ich platnosť ako kanonické image dáta je podmienená DS kontextom. Operandy a presné šírky spolu s rendererovým načítaním do ES podporujú segmentový typ. Prirodzené všetky alias writeri nie sú uzavreté. Okolité DS:0129/012A a nasledujúcich osem bajtov táto dávka neklasifikuje.

| Funkcia | Image interval, koniec exclusive | CFG |
|---|---|---:|
| 0156:008E immediate | [015EE,01607) | 25 B / 12 inštrukcií |
| 0156:00A8 synchronized | [01608,01637) | 47 B / 23 inštrukcií |

Spolu 72 B / 35 inštrukcií, medzi funkciami zostáva jeden bajt mimo ich CFG. Obe používajú PUSH BP/MOV BP,SP a FAR RETF, nemajú argumenty ani volania. Synchronizovaná obsahuje dve lokálne polling slučky. Žiadna v týchto telách nemá timeout.

## Algoritmus a vedľajšie účinky

```text
immediate():
    swap WORD DS:[012C], WORD DS:[012E]
    page = WORD DS:[012C]
    out16(03D4h, 000Ch | ((((page >> 8) << 4) & FFh) << 8))
    return

synchronized():
    swap WORD DS:[012C], WORD DS:[012E]
    page = WORD DS:[012C]
    while in8(03DAh) & 01h: repeat
    CLI
    out16(03D4h, 000Ch | ((((page >> 8) << 4) & FFh) << 8))
    STI
    while (in8(03DAh) & 08h) == 0: repeat
    return
```

Presne sa vysiela WORD cez OUT DX,AX na 03D4h: AL=0Ch a AH je spracovaný high BYTE nového segmentu. Telo samo nevykonáva samostatný zápis registra 0Dh. Pre segment A000h vzniká WORD 000Ch, pre A400h 400Ch. Dolný BYTE segmentu sa ignoruje; z horného BYTE zostanú po SHL AH,4 iba pôvodné spodné štyri bity. Ľubovoľné seedované segmenty preto nie sú všeobecne platné stránky.

Rutiny najprv vymenia globálne WORD a až potom vykonajú I/O. V synchronized je dokonca prvá polling slučka pred CLI. Po OUT nasleduje nepodmienené STI, teda pôvodný IF sa neobnovuje: pri vstupe IF=0 sa rutina vráti s IF=1. Immediate IF nemení. BP/DS/SP sa v modeli kontrolujú; AX/CX/DX a pri synchronized aj BX sú pracovné. Netvrdí sa zachovanie ostatných flags.

Register index 0Ch a status port 03DAh zodpovedajú VGA stránkovému ovládaniu; táto dávka potvrdzuje presné inštrukcie a hodnoty portov. Skutočná viditeľná stránka závisí od predchádzajúceho VGA režimu, nízkej adresnej časti a hardvérovej interpretácie WORD I/O, ktoré neboli týmto modelom vykonané. Preto sa nezamieňa úspešný hook s pozorovaným obrazom.

## Reprodukcia a výsledky

`audit_replay_pass1_vga_pages.py IMAGE INVENTORY DECODER EMULATOR OUT` vytvára dve ASM CSV, `direct_references.csv`, `data_fields.csv`, `cases.csv`, `summary.json`. Používa pôvodné celé funkcie, EXEPACK relokácie a load bázy 0/1000h. IN/OUT sú modelované hookmi: IN poskytuje explicitné sekvencie; OUT zaznamenáva port, šírku, hodnotu a IF. Nevykonávajú sa žiadne hostiteľské hardvérové porty.

**8192 prípadov, 0 odchýlok**: pre každú load bázu všetkých 256 horných BYTE nového page segmentu, dolný BYTE 00/FF a vstupný IF=0/1. Immediate má jeden scenár bez IN. Synchronized má sekvencie 00,08; 01,00,00,08; 01,01,00,00,00,08, ktoré pokrývajú čakanie v oboch slučkách. Predchádzajúci segment je seedovaný ako bitový doplnok druhého, aby výmena bola nezameniteľná. Kontrolujú sa oba výsledné WORD, presné portové výstupy, spotrebovanie všetkých vstupov, IF počas OUT aj po návrate a DS/BP/SP. Nejde o exhaustívny test všetkých dvojíc segmentov alebo všetkých I/O sekvencií.

Presne 4 B CLASSIFIED ONLY → PARTIAL. Aktuálna mapa: **55075 B PARTIAL, 2176 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57295 B. Nezávislá kontrola potvrdila 715 intervalov, ich SHA, presné členstvo a nulové diery/prekryvy. SHA mapy `b0ed4ef42aa5fbd5986580e10bb7d7b49d73c3d6cc3bf9b72f0290d08c3c02ab`. Integrita intervalov nie je dôkaz úplnej sémantiky.

Centrálny katalóg: 78 funkčných rozsahov, 2761 inštrukcií / 6903 B, 55961 B typovaných dát celého obrazu, 55073 B historických NON-CODE dát a 2 PARTIAL netypované relokačné bajty. Controlled replay súčet 531425 plus osobitne 65548 smerových normalizačných prefixových prípadov. Prirodzené runtime testy 0. GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového %: uzavreté jednotky / úplný inventár oblasti. Úplné menovatele chýbajú, preto N/A; predošlé čísla sú orientačné. Testové počty a integrita mapy nenahrádzajú sémantické percentá.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | úplný inventár | zostávajúce intervaly |
| Dátové typy a konštanty | 95 % | N/A | 4 B segmentové WORD | alias writeri | úplný page ledger |
| Tabuľky a ukazovatele | 93 % | N/A | A000/A400 page segmenty | prirodzené invarianty | init režimu |
| Funkcie / ASM / CFG | 90 % | N/A | 72 B / 35 inštrukcií | caller interrupt kontext | flip calleri |
| RNG | 97 % | N/A | bez nového dôkazu | prirodzené poradie | DEMO stopa |
| Scheduler | 96 % | N/A | synchronized nepodmienene STI | IF callerov | zachytiť vstupný IF |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | prirodzené ordering | runtime stopa |
| Renderer / VGA | 94 % | N/A | swap a presné IN/OUT hodnoty | skutočný VGA model | CRTC/runtime trace |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | health updater |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | effect producer | damage caller |
| Sprity / HUD / paleta | 92 % | N/A | draw ES z 012E | framebuffer layout | režim init |
| SAVE / LOAD | 92 % | N/A | mutable page state oddelený | persistencia | SAVE ledger |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | backend parity | Win present match |

## Runtime testy na vykonanie

Zachytiť hodnoty DS:012C/012E, IF a presné portové zápisy pri oboch flipoch; korelovať s viditeľnou stránkou. Overiť inicializáciu CRTC 0Ch/0Dh a VGA addressing režimu. Skontrolovať polling pri štandardnej aj oneskorenej emulácii a callerov vstupný IF. Nekonečné čakacie sekvencie nie sú súčasťou úspešných replayov. DOSBox-X hardvérové časovanie a Win16 present parity zostávajú otvorené.
