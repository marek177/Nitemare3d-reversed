# PASS1: správca zvukového stavu

Dávka rekonštruuje DOS 2.0 funkciu 0C2B:00DC a typuje tri mutable BYTE polia. Výsledok je PARTIAL. Pôvodné WORX závislosti, prirodzený lifecycle a inicializačný mode 0 nie sú kontrolovaným replayom uzavreté.

## Hranice a ASM/CFG

Vstupný image SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; inventár SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`. Skript pripína oba vstupy, porovnáva bajty každého štartu a pomocou iced-x86 rekonštruuje CFG od 00DC po všetky návraty.

Funkcia **[0C38C,0C51A)** má span 398 B, CFG obsahuje **394 B / 127 inštrukcií**. Štyri bajty mimo CFG sa nepočítajú ako vykonané. WORD argument SS:BP+6 vyberá mode 0/1/2; iné hodnoty sa vracajú bez stavových zmien. ENTER 2, zachovanie SI, FAR RETF; caller odstraňuje WORD argument. V replays sa overuje BP/SI/DS/SP. ES, návratový AX a pracovné flags nemajú deklarovanú zachovávaciu garanciu.

| Pole, kanonický DS=2771h | Image interval | Typ / počiatočná hodnota | Dôkaz |
|---|---|---|---|
| DS:17CD | [28EDD,28EDE) | mutable BYTE / 0 | inicializačný stav: testy a zápisy 0103,018E,01B2,01DF,01F3 |
| DS:17CE | [28EDE,28EDF) | mutable BYTE / 0 | DSP-related stav: 0152/015A,019A,022E,023D,024B,0257 |
| DS:17CF | [28EDF,28EE0) | mutable BYTE / 0 | backend-related stav: 012B,01B8,01FF,021B |

Názvy sú odvodené od konzumentov a call skupín, nie od pôvodných symbolov. Žiadny z týchto bajtov nie je padding. DS:414D/414E/414F sú oddelené požadované príznaky; DS:3CC7 je ďalšia podmienka DSP vetvy. V telách sa testuje nula/nenula, preto 255 funguje ako aktívny stav a nemusí sa automaticky normalizovať na 1.

## Režimy a rekonštruované správanie

Označme aktívne BYTE stavy A=17CD, D=17CE, B=17CF a požiadavky M=414D, S=414E, X=414F.

```text
mode 1:
    if A != 0:
        call WORX 10BF:0EC2
        if D != 0: call 10BF:0EF1; call 10BF:070E
        call 10BF:006F
        A = D = B = 0
    M = S = X = 0
    return

mode 2:
    if (M or S or X) and A == 0:
        call 0C2B:0006
        call 0C2B:0298(0)
        A = 1
    if X != 0 and B == 0:
        call 10BF:05E2
        WORD[367A] = call 10BF:0646
        WORD[367C] = call 10BF:0678
        B = 1
    if S != 0 and BYTE[3CC7] != 0:
        if D == 0:
            if signed16(call 0C2B:0020) > 0: D = 1
    else if S == 0 and D != 0:
        call 10BF:070E
        D = 0
    if M != 0: call 0C2B:00AA
    return
```

Keď mode 1 dostane A=0 a D/B nenulové, podriadené D/B zostanú zachované, hoci M/S/X sa nulujú. Keď mode 2 dostane S nenulové, 3CC7=0 a D nenulové, DSP stav D sa tiež nevynuluje: vypínacia vetva je viazaná na S=0. Ide o správanie pri seedovanom stave; prirodzená dosiahnuteľnosť týchto kombinácií nie je potvrdená.

Mode 0 je staticky rekonštruovaný v ASM CSV: pri 3CC6=0 nuluje M/S/X a vracia sa. Inak volá init, zapisuje A=1, probe 0020 do SI, zisťuje AL cez 10BF:06AA, volá backend 05E2/0646/0678 a nastavuje B=1. Nulový výsledok 06AA vypne M; nekladný signed SI nuluje 3CC7. D je potom nastavené na 1 práve pri S!=0 a 3CC7!=0, inak 0 s volaním 070E. Nenulový výsledok 06AA vyvolá resource 0298(0); spoločný záver podmienečne volá volume 00AA. Táto vetva sa v tejto dávke nevykonala; statické dekódovanie nie je runtime overenie jej závislostí.

## Knižničná hranica a reprodukcia

`audit_replay_pass1_audio_state.py IMAGE INVENTORY DECODER EMULATOR OUT` vytvára `audio_state_manager.csv`, `data_fields.csv`, `cases.csv`, `summary.json`. Replays aplikujú skutočné EXEPACK relokácie pri load bázach 0/1000h. Telo managera je pôvodné; jedenásť cieľov závislostí je nahradených RETF/hookmi. Resource hook overuje WORD argument 0. Probe vracia −1/0/1; dva getter hooky vracajú CAFE/BEEF; ostatné nemenia stav. Presné target offsets sú v summary. Úplné WORX ABI, zariadenia, prerušenia a možné callback zmeny globálneho stavu sa tým nepotvrdzujú.

**10212 prípadov, 0 odchýlok**: pre každú load bázu 27 kombinácií M/S/X × 27 kombinácií A/D/B, pričom jednotlivé BYTE hodnoty sú 0/1/255. Mode 1 sa vykoná raz a mode 2 so šiestimi kombináciami 3CC7 z {0,1} a signed probe z {−1,0,1}; navyše tri neplatné modes 3/255/FFFF. Kontroluje sa presné poradie závislostí, výsledný stav, požiadavky, oba getter outputs a DS/BP/SI/SP. Počiatočný chybný pokus mal nesprávnu adresu mockovaného 070E a skončil CPU výnimkou; adresa bola opravená na image 112FE, finálny uvedený výsledok pochádza výhradne z úspešného behu.

Presne **3 B CLASSIFIED ONLY → PARTIAL**. Aktuálna mapa: **55071 B PARTIAL, 2180 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57295 B. Nezávislá kontrola overila 712 intervalov, SHA a presné členstvo bez dier/prekryvov. SHA mapy `1cece8eb421492091d9dd86178d5a4dc8b45883e48968f2cc43a28297eb600a5`. Integrita mapy nie je nezávislý dôkaz sémantickej úplnosti.

Nové controlled replays sa pripočítavajú raz: súčet 510111 plus osobitne 65548 normalizačných prefixových prípadov. Prirodzené runtime testy 0. GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového % je uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú; nové percentá preto N/A a predošlé čísla orientačné. Testové počty nenahrádzajú sémantické pokrytie.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | úplný inventár | zostávajúce intervaly |
| Dátové typy a konštanty | 95 % | N/A | 3 mutable BYTE stavy | alias writeri | write ledger |
| Tabuľky a ukazovatele | 93 % | N/A | stav oddelený od požiadaviek | getter výstupy | WORX ABI |
| Funkcie / ASM / CFG | 90 % | N/A | 394 B / 127 inštrukcií | mode 0 replay | seed 06AA/init |
| RNG | 97 % | N/A | bez nového dôkazu | prirodzené poradie | DEMO stopa |
| Scheduler | 96 % | N/A | zvukový lifecycle oddelený | timing IRQ | WORX interrupt graph |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | prirodzené prepínače | zaznamenať nastavenia |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping | render stopa |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | health updater |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | sound effects callee | 10BF:0EF1 |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | asset identity | descriptor producer |
| SAVE / LOAD | 92 % | N/A | mutable audio state oddelený | persistencia | SAVE ledger |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | audio parity | Win lifecycle match |

## Runtime testy na vykonanie

Zaznamenať mode 0/1/2 a A/D/B/M/S/X pri štarte, vypnutí/zapnutí music/sound a ukončení. Overiť skutočné výsledky probe/06AA/getterov a vedľajšie účinky WORX. Osobitne zachytiť prirodzené invarianty A=0 ⇒ D/B=0 a S≠0 s 3CC7=0; syntetický replay nedokazuje dosiahnuteľnosť porušených invariantov. Porovnať Win16 backend lifecycle. Pôvodný DOSBox-X beh zostáva nevykonaný.
