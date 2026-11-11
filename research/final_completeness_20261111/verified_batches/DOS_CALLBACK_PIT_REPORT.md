# DOS 2.0 — callback setter a PIT divisor kontrakt

11. 11. 2026. PARTIAL; šesť riadených replay prípadov pôvodných inštrukcií, DOSBox-X/runtime testy0, DEEP VERIFIED0 B.

## Callback producent

`15BF:389A`, image `[1948A,19497)`, obsahuje13 B/5 inštrukcií: CLI; zápis BX do CS:3896; zápis DX do CS:3898; STI; NEAR RET. VstupDX:BX tvorí nový FAR pointer. Setter nemodifikuje vstupné general registre, ale **IF na konci nastaví na1**, neobnoví jeho vstupnú hodnotu. Dvojica zápisov je medzi CLI/STI; to nepreukazuje ochranu pred všetkými druhmi asynchrónneho zásahu.

Počiatočný pointer je0000:0000. V 82-slotovej kandidátnej tabuľke INT63 má AH=46h WORD389Ah. Je teda doložené servisné prepojenie na setter. V overenom historickom inventári nebol nájdený priamy encoded CALL na setter; nepriamy dispatcher a alias zápisy tým nie sú vylúčené. Cieľ nastavovaného callbacku ani jeho zachovanie AX zatiaľ nepoznáme.

Spotrebitelia sú potvrdení na194BC a1B50C, obaja testujú horný WORD pointera na nulu. Nenulový offset s nulovým segmentom callback nespustí. Povolené runtime hodnoty, prípadné ďalšie producenty a reentrancy ostávajú otvorené.

## Helper CS:466A

Image `[1A25A,1A28F)` =53 B/29 inštrukcií. Prvá vetva testuje CS:201E==1. Pri rovnosti okamžite RET, bez delenia, zápisov polí či portov. Každá iná hodnota pokračuje.

Na aktívnej vetve uloží AX,BX,DS, nastaví DS=CS, vnútorne uloží AX,BX,DX a vykoná:

```text
divisor = input_AX
quotient = unsigned_16_divide(DX=0, AX=FFFFh, divisor)
CS:2DB6 = quotient
CS:2DB4 = quotient
OUT 43h,34h
OUT 40h,low(input_AX)
OUT 40h,high(input_AX)
restore AX,BX,DX,DS
RET
```

Ide o nastavenie portov časovača; v tejto dávke sa neodvodzuje fyzická frekvencia ani správanie hardvéru. Kód zapisuje dve kópie celočíselného podielu65535/divisor, nie zvyšok. Pre vstup0952h z inicializácie je podiel27. Flags sa nezachovávajú. Pri gate!=1 a AX=0 nastane CPU divide error pred aktualizáciou quotient polí a portov. Globálne vylúčenie takého vstupu ešte nemáme.

Nové polia: CS:201E..2020 WORD gate (image17C0E..17C10) a CS:2DB4..2DB8 dve WORD kópie podielu (image189A4..189A8). Typy vyplývajú z čítania a zápisov; životnosť a ďalšie účely týchto polí nie sú uzavreté. Historický inventár obsahuje8 priamych callsites na helper466A, vrátane18AF6.

## Riadené replay dôkazy

`replay_dos_pit_setter.py` používa Unicorn16, celý hash-pinned obraz, syntetický stack, segmenty a registry. Pôvodné OUT inštrukcie iba zaznamenáva; neovláda zariadenie. CPU interrupt hook zaznamená divide error a zastaví vykonávanie. Nespúšťa DOS ani časovačový interrupt handler.

| gate | vstup AX | Výsledok |
|---:|---:|---|
| 0 | 1 | obe poliaFFFFh, výstupy43h=34h,40h=01h,40h=00h |
| 0 | 0952h | obe polia27, výstupy34h/52h/09h |
| 0 | FFFFh | obe polia1, výstupy34h/FFh/FFh |
| 1 | 0 | bezpečný lokálny bypass, bez portových/dátových zápisov |
| 0 | 0 | CPU interrupt0 pred portovými/dátovými zápismi |
| 2 | 0952h | rovnaká aktívna vetva ako gate0 |

Všetky assertions prešli. Pri normálnych návratoch sa overilo zachovanie AX,BX,CX,DX,SI,DI,BP,DS,ES a SP po NEAR RET. Pri divide error sa zachovanie registrov neočakáva, rutina nemá vlastný exception handler. `dos_pit_replay/evidence.json` uchováva konkrétne inštrukčné stopy, výstupy, výsledky a identitu natívnej emulačnej knižnice. Syntetická chyba nie je dôkaz prirodzenej chyby pri hraní.

## Reprodukcia, mapa a ďalší krok

Rozšírený `audit_dos_audio_lifecycle.py` vytvára aj `port_callback_setter.csv`, `pit_divisor_setter.csv`, osem nových caller hrán a6 B dátových polí. Reprodukcia replay: `python replay_dos_pit_setter.py IMAGE UNICORN_DIRECTORY OUT_DIR`.

Centrálna partition:18 kandidátnych funkčných rozsahov,724 inštrukcií/1 645 B,548 B dát,169 167 B aktuálne neposúdených,68 intervalov. Riadené replay prípady sú spolu18 (12 read+6 PIT), nie18 DOSBox-X testov. Nové percentá N/A; členstvo PASS320 UNKNOWN.

Nasleduje analýza všetkých8 callerov vstupného AX a všetkých writerov gateCS:201E. Runtime testy: watchpoint setteru/slotuAH46h, logDX:BX a následného callbackAX; loggate/divisor pri každom466A; IF pred/po setteru. Tým treba preveriť prirodzený rozsah divisor a podmienky256-iteráciovej inicializačnej slučky. Skutočný runtime test zatiaľ neprebehol.
