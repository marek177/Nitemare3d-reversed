# PASS1: meniteľný CRT pointer do environmentového bloku

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. DWORD **DS:2144**, obraz **[29854,29858)**, počiatočne obsahuje FAR pointer **2771:2148**. Segmentový WORD má skutočnú EXEPACK relokáciu; cieľ `[29858,29859)` je NUL, teda počiatočný prázdny reťazec. Nový typový dôkaz pokrýva spolu 5 B, status PARTIAL.

## Runtime writer a spotrebiteľ

Na 121F6 sa načíta WORD DS:2122 a porovná AL s 2. Vetva rovnosti preskočí nasledujúce environmentové hľadanie. Inak 12200 načíta ES z DS:211E, 12204 potom ES z ES:[002C]. Interpretácia DS:211E ako PSP a jeho +2Ch ako environmentového segmentu zodpovedá inicializačnému kontextu; samotný tento ohraničený úsek neuzatvára všetkých writerov DS:211E.

Na 12209 sa ES uloží do segmentovej časti DS:2146. AL=0, DI=0, CX=8000h; REPNE SCASB a následný SCASB cyklus hľadajú dvojité NUL. Potom sa DI zvýši dvakrát a na 1221C uloží do offsetovej časti DS:2144. To ukazuje pointer za environmentovými reťazcami a dvojbajtovým poľom, zodpovedajúci CRT názvu/ceste programu. Konkrétna prirodzená cesta a verzionovacie podmienky sa v tejto dávke nemerali.

Na 122D2 vykoná kód `LDS SI,[2144]`; slučka LODSB/STOSB kopíruje reťazec po NUL. Toto je priamy dôkaz FAR string pointera a jeho spotreby, nezávisle od názvu symbolu. Pointer sa mení počas štartu, preto nemožno počiatočný segment 2771h zovšeobecniť na všetky runtime čítania. Skenovanie a kopírovanie predpokladajú korektný DF a platný blok; nemajú v týchto oknách uzavreté všetky hranice či error cesty.

## Reprodukcia a metriky

`audit_pass1_crt_program_pointer.py IMAGE DECODER_DIR OUT` používa `relocations.csv` vedľa IMAGE, kontroluje SHA, počiatočný pointer/NUL, relokáciu a rozhodujúce writer/consumer bajty, nezávisle dekóduje dve okná. `promote_pass1_fields.py` použije vstup `pass1_split_strings/noncode_intervals.csv`. Artefakty sú v `pass1_crt_program_pointer/`.

Segmentové 2 B už boli PARTIAL; nové **3 B** prešli z CLASSIFIED ONLY. Aktuálne **PARTIAL 49 822 B, CLASSIFIED ONLY 7 429 B, UNKNOWN 44 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Relokačné PARTIAL bajty bez typu klesli z 50 na **48 B**. Nový prirodzený runtime ani replay sa nevykonal.

DOSBox-X plán: startup DS:211E, ES:[2C], verzionovacia vetva, výsledný názov programu a DF pred skenom/kopírovaním. Ďalší krok: zostávajúce textové selectory a relokované polia; konkrétna runtime cesta sa nebude odvodzovať z počiatočného prázdneho reťazca.


## Aktualizácia 13 oblastí

Nové sémantické percento je všade N/A: úplný inventár kontraktov/polí/vetiev chýba. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické percentá sú orientačné odhady.

| Oblasť | Predošlý odhad | Nové % | Potvrdenie | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | opravená mapa a flagy | prirodzené súbory | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 159 polí/28 zdrojov; mutable CRT pointer | 48 relokačných B bez typu | roly segmentov |
| Tabuľky a ukazovatele | 93 % | N/A | LDS consumer and environment pointer writer | writeri/lifetime | pointer watchpointy |
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

