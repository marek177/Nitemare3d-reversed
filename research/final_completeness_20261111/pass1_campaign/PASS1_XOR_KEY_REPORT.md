# PASS1: 52-bajtový XOR kľúč a medzera starého inventára

Dávka spresňuje 63 B v troch poliach, z toho **60 B novo CLASSIFIED ONLY → PARTIAL**; trojbajtový fatal suffix už mal dôkazy v staršej klasifikácii a nezapočítava sa druhýkrát. Pôvodná XOR rutina sa vykonáva bez mockov. Ďalší 33-bajtový wrapper je novo dekódovaný statický kandidát, bez preukázaného prirodzeného vstupu. Všetko zostáva PARTIAL.

## Vstupy a adresy

Image SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; inventár SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`. Skript pripína identity a porovnáva všetky existujúce štarty. Nové štarty sú nezávisle dekódované priamo z kanonického obrazu a explicitne označené ako absent v starom inventári.

| Položka | Image interval, koniec exclusive | Dôkaz |
|---|---|---|
| SS:2045 key | [29755,29789) | 52 BYTE, presný ASCII copyright text; indexed SS read po unsigned DIV52 |
| DS:203D formát | [2974D,29755) | 8 B NUL `%s: %s` s LF; PUSH vo wrapperi 0FBA:004D |
| DS:203A fatal suffix | [2974A,2974D) | 3 B `.` + LF + NUL, PUSH 0FBA:0022 → CRT07E0 |
| XOR funkcia 0FBA:01B2..01F0 | [0FD52,0FD90) | 62 B / 29 inštrukcií, všetky v starom inventári |
| Wrapper 0FBA:0036..0057 | [0FBD6,0FBF7) | 33 B / 12 inštrukcií, všetky absent v starom inventári |

Key text je presne `Copyright 1992, David P Gray, Gray Design Associates`. Nasledujúci NUL [29789,2978A) sa do 52-bajtového kľúča nezahŕňa a touto dávkou nepromuje: rutinou sa nečíta. Úlohu kľúča dokazuje SS operand a presný modulo index, nie len ASCII čitateľnosť. SS=2771h je modelovaný kanonický kontext; XOR telo DS mení na segment vstupného bufferu.

## XOR algoritmus a vedľajšie účinky

```text
input: FAR buffer SS:BP+6, WORD count SS:BP+0A
checksum_BYTE = 0
if count != 0:
    DS:SI = input_buffer
    for i in 0..count-1:
        checksum_BYTE ^= BYTE DS:[SI]
        BYTE DS:[SI] ^= BYTE SS:[2045 + (i % 52)]
        SI = (SI + 1) & FFFF
    DS = SS
AL = checksum_BYTE
return FAR
```

Checksum je XOR **pôvodného vstupu pred zmenou**, nie transformovaného výstupu. Rovnaká operácia aplikovaná dvakrát obnoví obsah, ale druhý checksum sa počíta z ciphertextu. Garantovaný výsledok je AL; AH sa nezero-extenduje explicitne a plný AX sa nevydáva za BYTE návrat s nulovým horným bajtom.

Po nenulovom count sa DS nastaví na SS, nie na predchádzajúce DS. Pri count=0 sa tento blok preskočí a DS ostane pôvodné. SI/DI/BP a návratový stack sa v modeli zachovávajú. Pointer je 16-bitový a SI môže wrapnúť; testy s count do 4096 tento wrap neprerážajú, preto sa celá FAR-buffer doména neuzatvára.

Starý inventár má dva priame callery XOR rutiny: 0277:1B89 po čítaní/uzavretí resource bufferu a 083D:2A35 s count=36h, buffer DS:3638. Druhý porovná AL s nulou a pri nenule volá error helper. Toto je statická caller väzba; prirodzené asset bajty, checksum invariant a file formát neboli touto dávkou spustené ani overené.

## Novo nájdený wrapper

Surový WORD odkaz na 203Dh sa nachádza na image FBEEh a nepatrí žiadnemu štartu starého inventára. Dekódovanie od prologu ENTER 0Ah na FBD6h vytvorí konzistentné 33-bajtové telo končiace FAR RETF; nasledujúci NOP sa nezapočítava. Wrapper odovzdá lokálny 10-bajtový buffer do CRT 11EE:2EB4 a potom `%s: %s` s týmto bufferom a WORD argumentom BP+6 do CRT07E0.

Statický súvisiaci kontext 2EB4 používa INT21/AH2C a skladá `HH:MM:SS` s koncovým NUL, čo podporuje timestamp význam wrappera. Wrapper sa v tejto dávke nevykonáva. Starý inventár neobsahuje jeho priame volanie; prolog a platné bajty samy nepreukazujú prirodzenú reachability. Preto sa vedie ako bounded PARTIAL kandidát a nie DEEP VERIFIED funkcia.

## Reprodukcia a výsledky

`audit_replay_pass1_xor_key.py IMAGE INVENTORY DECODER EMULATOR OUT` vytvára dve ASM CSV s old-inventory príznakom, data fields, direct caller ledger, súvisiace kontexty, cases a summary. Pri load 0/1000h aplikuje reálne EXEPACK relokácie. SS je explicitne DGROUP, input buffer je iný FAR segment; žiadne telo sa nenahrádza a žiadne OS I/O sa nevykoná.

**320 prípadov, 0 odchýlok** = 2 load bázy × 10 dĺžok × 4 byte patterns × 2 počiatočné DS × 2 fázy forward/reverse. Dĺžky 0,1,2,51,52,53,104,255,256,4096. Kontroluje sa každý výsledný bajt, AL vstupného checksumu, DS špeciálne pre nulu a návratové SI/DI/BP/SP. SHA cases `ad433c856b1629b1ee86487f007ba46b915d358e9df533094dc78faa32de0bb3`. Opakovaný beh po doplnení kontextov sa nezapočítava druhýkrát.

## Meranie

Netto 60 B CLASSIFIED ONLY → PARTIAL. Mapa: **56865 B PARTIAL, 386 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57295 B. Nezávislá kontrola overila 846 intervalov, SHA a presné členstvo bez dier/prekryvov. SHA mapy `a37599997a19254587d16f043348e53cdc7b6949b240b823345dee3fcec5d16f`. Integrita mapy nie je dôkaz sémantickej úplnosti.

Katalóg: 97 bounded funkčných rozsahov vrátane explicitného kandidáta, 3405 inštrukcií / 8561 B, 57751 B typovaných dát celého obrazu; 56863 B historických NON-CODE dát a 2 PARTIAL netypované relokačné bajty. Nových 95 kódových B leží mimo historického NON-CODE, jeho code intersection zostáva 0. Controlled replay 776487 plus osobitne 65548 smerových prefixových prípadov. Prirodzené runtime testy 0. GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového %: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, nové percentá N/A, predošlé orientačné. Medzera starého inventára sa nezamieňa s nájdením kódu v historickom NON-CODE.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | opakovaný key a vstupný checksum | asset invariant | reálne resource bajty |
| Dátové typy a konštanty | 95 % | N/A | 60 B nové dôkazy, 3 B spresnenie | trailing NUL | jeho konzument |
| Tabuľky a ukazovatele | 93 % | N/A | SS key / FAR input odlíšené | SS prirodzený invariant | caller trace |
| Funkcie / ASM / CFG | 90 % | N/A | 62 B native + 33 B nový kandidát | wrapper reachability | xref mimo inventára |
| RNG | 97 % | N/A | XOR nie je RNG | prirodzené poradie RNG | DEMO trace |
| Scheduler | 96 % | N/A | timestamp wrapper odlíšený | prirodzené callery | call graph |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | driver ABI | input closure |
| Renderer / VGA | 94 % | N/A | resource codec oddelený | asset parser | load closure |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | health updater |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | effect producer | damage caller |
| Sprity / HUD / paleta | 92 % | N/A | XOR resource caller doložený | asset identity | file payload |
| SAVE / LOAD | 92 % | N/A | checksum vrstvy oddelené | serialize väzba | caller ledger |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | codec parity | Win key/helper match |

## Runtime testy na vykonanie

Zachytiť SS/DS, FAR buffer a count pri oboch prirodzených XOR calleroch, porovnať input checksum a transformované dáta so súborom. Zistiť pôvodný invariant count36 checksum=0. Wrapper najprv potvrdiť prirodzeným alebo nezávislým nepriamym xrefom; až potom overovať timestamp output. DOSBox-X vykonanie a Win16 parity zostávajú otvorené.
