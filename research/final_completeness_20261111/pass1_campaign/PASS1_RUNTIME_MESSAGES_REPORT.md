# PASS1: variabilná CRT runtime-error tabuľka

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Tabuľka **DS:2576**, obraz **[29C86,29D5E)**, má **216 B**: sedem záznamov `WORD code; ASCII text; NUL`, zakončených WORD sentinelom FFFFh.

| Kód | Začiatok záznamu | Počiatočný text / účel |
|---:|---|---|
| 0 | 29C86 | R6000, stack overflow |
| 3 | 29CA2 | R6003, integer divide by 0 |
| 9 | 29CC3 | R6009, not enough space for environment |
| 252 | 29CF1 | CR LF |
| 255 | 29CF6 | `run-time error ` |
| 2 | 29D08 | R6002, floating-point support not loaded |
| 1 | 29D37 | R6001, null pointer assignment |
| sentinel | 29D5C | WORD FFFFh |

Texty vrátane CR/LF a presné konce sú v `pass1_runtime_messages/records.csv`. Marker `<<NMSG>>` pred tabuľkou ani posledné dva FF bajty `[29D5E,29D60)` sa touto dávkou nepromujú. Dvojica nulových bajtov hneď za markerom patrí WORD kódu 0, nejde o dôkaz deväťbajtového NUL marker reťazca.

## Lookup a hraničný dopyt

Lookup **11EE:051A**, obraz **[123FA,12425)**, má WORD argument v SS:[BP+6] a vracia NEAR offset v AX; nastaví ES=DS, zachová SI/DI/BP a končí FAR RET 2. Začína LODSW kódu. Pri zhode vráti offset textu. Pri nezhode testuje kód FFFFh cez INC AX; ak nejde o sentinel, REPNE SCASB nájde NUL a pokračuje ďalším WORD záznamom. Predpokladá DF=0 a platný zdedený DS.

**Poradie kontrol je významné:** dopyt FFFFh sa zhoduje so sentinelom skôr než sa otestuje koniec. Výsledkom je **AX=264Eh**, teda adresa `[29D5E,...)` za sentinelom. Ostatné testované neznáme kódy vracajú 0. Netvrdí sa, že sa FFFFh prirodzene požaduje; ide o statický a seeded-replay potvrdený lokálny hraničný kontrakt.

Výstupný wrapper `[12425,1245B)` volá lookup, pri nenulovom AX skenuje text po NUL, nastaví BX=2 a vykoná DOS AH=40h. Má tiež podmienečný NEAR hook cez DS:2536 pri magic D6D6h. Jeho úplné hook/error/runtime kontrakty zostávajú otvorené. Dopyt FFFFh preto nemožno automaticky považovať za bezpečný textový výstup.

## Reprodukcia a metriky

`audit_pass1_runtime_messages.py IMAGE DECODER_DIR OUT` kontroluje SHA, presný poriadok siedmich kódov, NUL konce, sentinel, lookup/output bajty a nezávislé dekódovanie. `replay_runtime_message_lookup.py IMAGE UNICORN_DIR RECORDS_CSV OUT` vykonal **22 prípadov bez zlyhania**: sedem známych kódov, tri chýbajúce a FFFFh pri dvoch load segmentoch. Overuje AX a DS/ES/SI/DI/BP/SP. Ide o dosadený stav s DF=0, bez DOS output testu a bez prirodzenej dosiahnuteľnosti.

`promote_pass1_fields.py` používa predchádzajúcu mapu `pass1_io_strings/noncode_intervals.csv`. Všetkých **216 B** prešlo z CLASSIFIED ONLY do PARTIAL. Aktuálne **PARTIAL 51 089 B, CLASSIFIED ONLY 6 162 B, UNKNOWN 44 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Predošlá mapa: 50 873 / 6 378 / 44 / 0 B. Netypované relokačné PARTIAL bajty zostávajú 2 B.

Prijatý replay súčet je **2 657**, prirodzené runtime testy stále 0. Lookup je začlenený ako samostatný ohraničený funkčný rozsah; output wrapper zatiaľ iba ako ASM dôkaz, nie nový uzavretý kontrakt. DOSBox-X plán: prirodzené error kódy, DS/DF, skutočný DOS handle 2 výstup a hook. Ďalší krok: zostávajúce CRT/static údaje a caller inventár runtime chýb.


## Aktualizácia 13 oblastí

Nové sémantické percento je všade N/A: úplný inventár kontraktov/polí/vetiev chýba. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické percentá sú orientačné odhady.

| Oblasť | Predošlý odhad | Nové % | Potvrdenie | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | opravená mapa a flagy | prirodzené súbory | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 225 polí/38 zdrojov; 216 B runtime messages | 2 relokačné B bez typu | roly segmentov |
| Tabuľky a ukazovatele | 93 % | N/A | variable records, FFFF sentinel and 22 replay cases | writeri/lifetime | pointer watchpointy |
| Funkcie / ASM / CFG | 90 % | N/A | 34 rozsahov, 1 150 inštrukcií | kontrakty/dosiahnuteľnosť | caller stopy |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | staršie PIT dôkazy zachované | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová DEMO stopa |
| Renderer / VGA | 94 % | N/A | bit reversal začlenený | clipping/orientácia | payload spotrebiteľ |
| GUARD / bossovia | 93 % | N/A | nominálne pole 100×26 | AI/lifecycle | inicializátory |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie/sloty | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | 60 počiatočných UI textov | textový lifetime | SS čítania po návrate |
| SAVE / LOAD | 92 % | N/A | mapové/flagové rozsahy | LOAD parity | párový stav |
| Windows Win16 | 92 % | N/A | staršie NE dôkazy zachované | callback DS/import ABI | runtime selektory |

