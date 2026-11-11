# DOS 2.0: prepínače hudby a zvuku, texty a poradie volaní

## Rozsah a lokálne správanie

Analyzované sú dve vnútorné vetvy dispatchera v segmente 06B0: vstupy 06B6 a 06FA, spoločný výstup pred 07A0. Nie sú to samostatné FAR funkcie. Overený inventár obsahuje **30 inštrukcií / 99 B** v oknách `[071B6,071FA)` a `[071FA,0721C)`; ich obalový rozsah je 102 B. Tri bajty mimo evidovaných začiatkov za nepodmienenými skokmi sa do kódu nepridávajú. Celý dispatcher ani výber týchto vetiev z používateľského vstupu sa touto dávkou neuzatvárajú.

```text
music_branch:
    if byte DS:414D != 0: call 0C2B:0282()
    byte DS:414D ^= 1
    call 0C2B:00DC(2)
    if byte DS:414D != 0: call 083D:288C()
    text = byte DS:414D != 0 ? DS:0B5F : DS:0B68
    call 0D29:0720(FAR pointer DS:text)
    jump dispatcher:07A0

sound_branch:
    byte DS:414E ^= 1
    call 0C2B:00DC(2)
    text = byte DS:414E != 0 ? DS:0B72 : DS:0B7B
    call 0D29:0720(FAR pointer DS:text)
    jump dispatcher:07A0
```

Hudobný selector 083D:288C a cieľ jeho ID 0C2B:0298 sú analyzované v predchádzajúcich dávkach. Stop závislosť 0282, účinok 00DC(2) a plné vedľajšie účinky prompt helpera sa tu nepovažujú za uzavreté. Hudobná vetva číta flag znovu po každom závislom volaní, preto poradie a text môžu závisieť aj od jeho skutočných zápisov; uvedený text nie je nemenný snapshot pred volaním.

Oba flagy sú mimo file-backed obrazu. `XOR 1` preklopí najnižší bit, nie ľubovoľnú nenulovú hodnotu na nulu. Pri počiatočných 0/1 sa vykoná bežné zapnutie/vypnutie. Pri napríklad 2 vznikne 3 a obe sú nenulové. Ak volané rutiny flag nemenia, z celého BYTE priestoru dá výsledný off text iba počiatočná hodnota 1. Invariant, že hra uchováva flagy výhradne ako 0/1, zostáva na uzavretie writerov a LOAD.

## Presné textové polia

| DS offset | Interval v obraze, koniec exclusive | B | Text |
|---|---|---:|---|
| 0B5F | [2826F,28278) | 9 | `Music on` |
| 0B68 | [28278,28282) | 10 | `Music off` |
| 0B72 | [28282,2828B) | 9 | `Sound on` |
| 0B7B | [2828B,28295) | 10 | `Sound off` |

Každý interval zahŕňa NUL, spolu **38 B**. Konštanty sú vybrané cez MOV AX a spoločný push DS; push AX; FAR CALL na 0D29:0720. Nie sú to priame PUSH-immediate call sites, preto ich predchádzajúce jednoduché skenery literalov neuzavreli. Typovanie vychádza z konkrétneho dátového toku, NUL hraníc a už analyzovaného prompt helpera; prirodzený runtime DS sa tým nedokazuje.

## Controlled replay

`audit_replay_pass1_audio_toggles.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT` overí kanonický SHA, pôvodné bajty a dekódovanie okien a štyri polia. Aplikuje reálne EXEPACK relokácie. Pri load bázach 0 a 1000h spustí každú vetvu so všetkými 256 hodnotami príslušného BYTE, spolu **1 024 prípadov, 0 odchýlok**.

Štyri závislosti 0C2B:0282, 0C2B:00DC, 083D:288C a 0D29:0720 sa v emulačnej kópii nahradia RETF. Hook zaznamenáva poradie volaní, argument 2 a skutočnú DS:offset dvojicu prompt textu. Testuje sa výsledný BYTE a návrat lokálneho SP na pôvodnú hodnotu pri dosiahnutí 07A0. Závislosti v tomto modeli nemenia flagy; test preto nepreukazuje ich skutočný vplyv, zvuk, vykreslenie promptu, vstup používateľa ani ABI celej dispatch funkcie.

`pass1_audio_toggles/branch_instructions.csv`, `data_fields.csv`, `cases.csv`, `summary.json` uchovávajú reprodukovateľné dôkazy. Vetvové okná sa nepridávajú do centrálneho katalógu ako celé funkcie.

## Pokrytie

Promócia 38 B z CLASSIFIED ONLY do PARTIAL dáva **54 715 B PARTIAL, 2 536 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57 295 B. Nezávislá kontrola 655 intervalov overila ich SHA, presné členstvo a nulové diery/prekryvy. Typované dáta v historickom NON-CODE sú 54 713 B; rozdiel 2 B voči PARTIAL zostáva neuzavretá relokácia.

Centrálny katalóg: 44 funkčných rozsahov, 1 561 inštrukcií / 3 674 B kódu; 55 561 B typovaných dát celého obrazu. Controlled replay súčet je 7 687, plus samostatne 65 548 prefixových prípadov. Prirodzené runtime testy zostávajú 0. Nové výsledky zatiaľ nie sú na GitHub.

## Aktualizácia 13 oblastí

Metodika sémantického percenta pre každú oblasť: uzavreté jednotky / úplný inventár jednotiek. Úplné menovatele chýbajú, preto nové percentá zostávajú N/A a predošlé sú orientačné. Nové výsledky majú stav PARTIAL.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | prirodzené stavy | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 38 B / 4 texty | boolean invariant flagov | ich writeri |
| Tabuľky a ukazovatele | 93 % | N/A | spoločný FAR textový argument | runtime DS | prompt stopa |
| Funkcie / ASM / CFG | 90 % | N/A | dve vetvy, 1 024 prípadov | callee efekty a celý dispatcher | 00DC a vstupný dispatch |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | doložené poradie audio závislostí | prirodzené časovanie | stop/play stopa |
| DEMO a vstupy | 96 % | N/A | lokálne audio toggle cesty | výber klávesovej vetvy | dispatcher vstup |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping | spotrebitelia flagov |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | inicializátory |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | textové vetvy a FAR prompt pointer | skutočné zobrazenie | prompt runtime |
| SAVE / LOAD | 92 % | N/A | identifikované enable flagy | normalizácia po LOAD | serializačné polia |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | UI parity | Win prepínače |

## Runtime testy na vykonanie

V prirodzenej hre prepnúť hudbu a zvuk z oboch bežných stavov. Zachytiť writerov DS:414D/414E, callee efekty, poradie stop/00DC/selector/prompt, skutočne zobrazený text a zvuk. Otestovať LOAD a inicializáciu flagov. Neboolean hodnoty sú osobitné syntetické experimenty a nemožno ich vydávať za prirodzený herný stav. DOSBox-X vykonanie zatiaľ chýba.
