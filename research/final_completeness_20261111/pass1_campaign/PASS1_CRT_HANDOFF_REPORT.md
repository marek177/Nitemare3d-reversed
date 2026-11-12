# PASS1: CRT návratový pointer, near hooky a stavové príznaky

Dávka spresňuje **14 B v siedmich poliach**, z toho **12 B novo CLASSIFIED ONLY → PARTIAL**; 2 B už mali starší lokálny dôkaz. Kontrolovane sa vykonávajú oddelené startup úseky a pôvodný predvolený near callback cez CRT printer. Úroveň PARTIAL, celý startup ani DOS exec sa nevykonáva.

## Vstupy a presné polia

Image SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; inventár SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`. Skript overí identity, pôvodné bajty a nezávislé dekódovanie vybraných konzumentov. Mapovanie dát používa kanonické DS=2771h.

| Pole | Image interval, koniec exclusive | Typ a dôkaz |
|---|---|---|
| DS:2149 | [29859,2985B) | mutable WORD initial 0; zápis1 pred exec INT21 a zápis0 po obnovení kontextu |
| DS:214B | [2985B,2985C) | BYTE initial 0; porovnanie s2 pred/po exec, riadi callee 05F8 |
| DS:2151 | [29861,29862) | mutable BYTE initial 0; zápis CH v020C, čítanie v stdio cleanup0826 |
| DS:215C | [2986C,29870) | mutable FAR16 pointer initial0; POP offset, POP segment, FAR JMP |
| DS:2534 | [29C44,29C46) | WORD initial0; magic D6D6 gate |
| DS:2536 | [29C46,29C48) | mutable NEAR16 pointer initial00E4; near CALL v error output a I/O kontextoch |
| DS:2538 | [29C48,29C4A) | mutable NEAR16 pointer initial00E4; near CALL v error kontexte0113 |

Žiadny z týchto pointerov sa nezamieňa za FAR tam, kde operand volá iba WORD. Obe near hodnoty smerujú v aktuálnom CRT CS na **11EE:00E4, image 11FC4h, jediný bajt C3 = RET**. Presné call sites sú v `instruction_contexts.csv`. Pôvodní writeri hook pointerov a všetky prirodzené call kontexty zostávajú otvorené.

Byte214B sa nevyhlasuje za konkrétne OS/version číslo bez writer dôkazu; presne doložený je test hodnoty2. WORD2149 sa používa ako exec-in-progress-like príznak, ale jeho všetci čitatelia a error cleanup nie sú uzavretí. Byte2151 sa nedefinuje ako celá exit politika: v020C sa uloží CH a v0826 nenulová hodnota podmieňuje ďalší cleanup callee po 0CC4. Celé tieto funkcie sa v tejto dávke nevykonávajú.

## Uložená FAR návratová adresa

Pôvodný prefix 11EE:030E/0312 vykoná:

```text
POP WORD DS:[215C]  // pôvodný return IP
POP WORD DS:[215E]  // pôvodný return CS
```

Neskorší tail 11EE:0498 vykoná `JMP FAR DWORD PTR DS:[215C]`. Stredná startup časť medzi tým v skutočnom tele vytvára argumenty a environment. Replay ju **vynecháva** a po prefixe samostatne spustí tail. Tým sa dokazuje prenos presných dvoch WORD cez uložené pole, nie celý startup algoritmus alebo jeho stack layout.

V modeli DS=SS=DGROUP, entry SP=FF00h, finálny SP po POP je FF04h. FAR JMP SP už nemení. Pôvodný tail pred0498 nastavuje DS cez SS; toto prirodzené prepojenie sa v staged modeli nepreukazuje vykonaním celého medzikódu, ale explicitne predpokladá. Cieľový kód sa nevykoná, emulácia končí na cieľovej adrese.

## Native predvolený near hook

Pre DS:2536 sa vykoná pôvodný printer0545, jeho pôvodný message lookup a pri magic D6D6 aj pôvodný RET na00E4. Hook sa nenahrádza RET stubom na inej adrese; pozorovací code hook iba počíta vstupy. DOS AH40 zostáva modelovaný a nič na hostiteľský stderr nezapisuje. Druhý near pointer2538 sa doložil staticky cez near CALL a rovnakú počiatočnú adresu; jeho úplný error caller sa nevykonal.

## Reprodukcia a výsledky

`audit_replay_pass1_crt_handoff.py IMAGE INVENTORY DECODER EMULATOR OUT` vytvára data fields, pôvodné kontexty, cases a summary. Pri load0/1000h aplikuje reálne EXEPACK relokácie.

**44 prípadov, 0 odchýlok**:

- 24 staged handoff prípadov: 2 load bázy × offsets0/1/FFFE/FFFF × segmenty1000/6000/9000; kontrola uloženého pointera, cieľových CS:IP a SP.
- 20 native hook prípadov: 2 load bázy × magic0/D6D6 × message codes0/1/FC/FF/4. Chýbajúci code4 preskočí výstup aj hook; ostatné pri D6D6 vykonajú presne jeden predvolený RET. Kontroluje sa počet hook/write volaní a RETF2 stack cleanup.

Nejde o exhaustívne všetky FAR pointery alebo vykonanie exec. SHA cases `80b95b286e9eb88e8e11806fa78b6532312feeb6b955739429679f2afc56b7eb`.

## Meranie

Netto12 B CLASSIFIED ONLY → PARTIAL. Mapa: **56881 B PARTIAL, 370 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu57295 B. Nezávislá kontrola overila852 intervalov, SHA a presné členstvo bez dier/prekryvov. SHA mapy `bf293fab5f5ddf36ca2456c707e5f2b4ba153ba2135f641c8db38ae747f7455d`. Partition integrita nie je dôkaz úplnej sémantiky.

Bounded katalóg zostáva98 funkčných rozsahov,3502 inštrukcií/8773 B; úseky a jednobajtový RET sa nepripočítavajú ako nové uzavreté funkcie. Typované dáta celého obrazu57767 B; historického NON-CODE56879 B a2 PARTIAL netypované relokačné bajty. Controlled replay777083 plus osobitne65548 smerových prefixových prípadov. Prirodzené runtime testy0. GitHub snímka52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového %: uzavreté jednotky/úplný inventár oblasti. Menovatele chýbajú, nové percentá N/A, predošlé orientačné. Staged úseky nenahrádzajú celý startup alebo termination audit.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | uložená FAR návratová forma | celý startup stack | startup closure |
| Dátové typy a konštanty | 95 % | N/A |14 B spresnené,12 B nové | zvyšné scalars | writer ledger |
| Tabuľky a ukazovatele | 93 % | N/A |2 near hooky a FAR handoff | prirodzené hook writeri | init graph |
| Funkcie / ASM / CFG | 90 % | N/A | presné POP/JMP a RET ciele | medzikód startupu |0316..0498 |
| RNG | 97 % | N/A | bez nového dôkazu | ordering | DEMO trace |
| Scheduler | 96 % | N/A | runtime stav oddelený | prirodzení calleri | trace |
| DEMO a vstupy | 96 % | N/A | startup polia oddelené | celý argv/environment | startup closure |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | init režimu | VGA setup |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | health updater |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | effect producer | damage caller |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | identity | descriptor producer |
| SAVE / LOAD | 92 % | N/A | CRT hook stav oddelený | file wrapper účinky | I/O closure |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | CRT handoff parity | Win startup |

## Runtime testy na vykonanie

Zachytiť DS/SS a návratový pointer pred030E a po0498 počas pôvodného štartu. Sledovať zápisy2534/2536/2538 a skutočné nepredvolené callbacky. Exec príznaky a CH termination flag sledovať v oddelených izolovaných scenároch až po prirodzený terminálny výsledok. DOSBox-X vykonanie a Win16 parity zostávajú otvorené.
