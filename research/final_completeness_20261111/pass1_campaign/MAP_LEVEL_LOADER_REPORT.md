# DOS 2.0: level guard, seek a 8 KiB mapový loader

## Presná funkcia

FAR vstup 0277:00EC má hranice `[0285C,028F8)`, **156 B / 51 inštrukcií**, končí RETF. Každá inštrukcia je byte-exact porovnaná s kanonickým obrazom a dodaným inventárom a nezávisle dekódovaná. Funkcia nemá vlastné argumenty na zásobníku: používa aktuálny názov DS:627C, level WORD DS:626C a počet z načítanej hlavičky DS:D30C.

```text
handle = call open(DS:627C, 8000h)
if handle == FFFFh: call error(open-format, DS:627C)
if signed16(DS:626C) >= signed16(DS:D30C):
    call error(level-range-format)
offset = 514 + sign_extend16(DS:626C) * 8192
DX:AX = call seek(handle, offset, origin=0)
if DX:AX == FFFFFFFFh: call error(seek-format, DS:627C)
AX = call read(handle, FAR 21FD:373E, 8192)
if AX != 8192: call error(read-format, DS:627C)
call close(handle)
return
```

Open/seek/close sú CRT závislosti 11EE:1C72/1BD6/1BB6, read je herný helper 0FBA:009E. Táto dávka neuzatvára ich úplnú implementáciu. Error 0FBA:000C nemá v tomto tele explicitnú koncovú vetvu; ak sa vráti, pokračuje sa za ním. Nemožno preto označiť rozsahovú kontrolu za bezpodmienečne zastavujúcu bez dôkazu kontraktu error callee.

## Guard a index 10

Kontrola používa signed `JL`, iba hornú hranicu. Pri reálnom počte 11 v MAP.1 level 10 prejde a seek sa vypočíta na **82434**. Záznam `[82434,90626)` presne končí na EOF reálneho MAP.1. To posilňuje predošlý statický crosscheck, podľa ktorého epizóda 1 / level 10 v hudobnom selectore vyberie existujúce ID 13. Stále to nie je dôkaz prirodzeného dosiahnutia tohto levelu cez celý gameplay flow.

Záporné levely tiež prejdú týmto horným guardom pri kladnom count. MOVSX ich znamienkovo rozšíri pred SHL 13. Napríklad −1 vytvorí offset **−7678** (32-bit reprezentácia FFFFE202h). Následné správanie závisí od CRT seek a chybovej cesty; nie je v tejto dávke vykonané ani vyhlásené za hernú chybu. Pre level −32768 je signed offset −268434942. `guard_boundary_model.csv` uchováva tieto výpočty pre počty 10/11 a vybrané hranice; nejde o ďalšie replay prípady.

## Cieľ a side effects

Read dostáva pevný FAR cieľ 21FD:373E a dĺžku 2000h; v nezrelokovanom obraze je to `[2570E,2770E)`. Je to ďalší konkrétny spotrebiteľ podporujúci predchádzajúcu opravu hranice mapy, ktorá mala scan-only posun o bajt. Tento rozsah sa znova nepromuje ani nezapočítava.

Rutina ukladá/obnovuje SI a vyčistí svoje argumenty externým volaniam. DS/ES/SS explicitne nemení, ale ich ABI cez callee zostáva otvorené. Názov, count a level sú mimo file-backed obrazu. Register AX na návrate môže zmeniť close; neoznačuje sa za garantovaný počet prečítaných bajtov.

## Controlled replay a reprodukcia

`audit_replay_map_level_loader.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR GAME_DIR OUT` vykoná pôvodnú rutinu pri load bázach 0 a 1000h s aplikovanými EXEPACK relokáciami. Všetkých **31 platných level záznamov** troch reálnych MAP súborov sa vykoná dvakrát: **62 prípadov, 0 odchýlok**.

Open/seek/read/close/error sú výslovne nahradené RETF a hook modelom. Open vracia handle 7, seek zaznamenáva pôvodné argumenty, read kopíruje reálny 8 KiB payload z príslušného assetu, close kontroluje handle. Error pri platnej matici nesmie byť volaný. Overuje sa poradie `open seek read close`, offset, cieľ/počet, presná zhoda payloadu a jeho SHA, lokálny stack, SI a DS. Model neoveruje pôvodné filesystem callee, fyzický disk, hardvér ani prirodzenú dosiahnuteľnosť. Chybné a záporné vstupy nie sú zahrnuté v replay matici.

Artefakty `map_level_loader_replay/`: `instructions.csv`, `cases.csv`, `guard_boundary_model.csv`, `assets.csv`, `summary.json`. Každý reálny asset má SHA; každý prijatý prípad má SHA výsledného payloadu. Po doplnení relokácií pre druhú load bázu prešiel finálny beh; neúspešný prípravný pokus sa nepočíta medzi prijaté prípady.

## Pokrytie

Centrálny katalóg po pridaní funkcie: **46 rozsahov, 1 665 inštrukcií / 3 978 B kódu**, 55 592 B typovaných dát celého obrazu. Prijaté controlled replay prípady sú 7 749, plus samostatne 65 548 prefixových prípadov. Prirodzené runtime testy zostávajú 0.

NON-CODE mapa sa nemení: **54 746 B PARTIAL, 2 505 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, presne 57 295 B. Aktuálnym zdrojom zostáva `pass1_episode_files/noncode_intervals.csv/json`, overených 660 intervalov. Názvy a už typované mapové bajty sa nepočítajú znova. Funkcia a širší loader subsystém zostávajú PARTIAL. Nová dávka zatiaľ nie je na GitHub.

## Aktualizácia 13 oblastí

Metodika sémantického percenta: uzavreté jednotky / úplný inventár jednotiek oblasti. Menovatele nie sú uzavreté, nové percentá preto zostávajú N/A a historické orientačné hodnoty sa nepovažujú za meranie tejto dávky.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | 31 reálnych payloadov cez model loadera | filesystem helpery a header význam | read helper 009E |
| Dátové typy a konštanty | 95 % | N/A | signed count/level guard | prirodzená dolná hranica | level writeri |
| Tabuľky a ukazovatele | 93 % | N/A | pevný FAR mapový cieľ | caller DS a aliasy | prirodzené watchpointy |
| Funkcie / ASM / CFG | 90 % | N/A | 156 B / 51 inštrukcií, 62 prípadov | callee kontrakty | chybové vetvy |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | poradie udalostí | tick spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | prirodzený level index | DEMO prechody |
| Renderer / VGA | 94 % | N/A | ďalší writer presnej mapovej oblasti | runtime následní spotrebitelia | render stopa |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | inicializátory |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | textový lifetime | SS čítania po návrate |
| SAVE / LOAD | 92 % | N/A | horný guard a záporný offset otvorené | hodnoty po LOAD | level invariant |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | loader parity | Win map loader |

## Runtime testy na vykonanie

Pri prirodzenom načítaní každého levelu sledovať DS:626C/D30C, file handle, seek offset, počet a FAR cieľ čítania. Osobitne level 10 epizódy 1 a hudobný selector. Zachytiť čítací helper a error callee bez náhrad. Záporné a príliš veľké indexy skúšať len ako označené kontrolované experimenty s bezpečnou kópiou dát; nedokazujú prirodzený herný stav. DOSBox-X vykonanie zatiaľ chýba.
