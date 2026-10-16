# Nitemare 3-D — RE MAX NEXT v0.57: geometria, pohyblivé steny, GUARD damage a stavový automat zásahu

**Dátum:** 16. 10. 2026. **Metóda:** striktne read-only statické RE originálnych bajtov, cross-build porovnanie, explicitné modelové predpoklady a syntetické testy. **Bez originálneho gameplay CPU trace.** Označenie `v0.57` patrí tomuto lokálnemu balíku; nie je vyjadrením GitHub release.

## A. Originálne vstupy a hranice dôkazu

| Build | Originál (nie je pribalený) | Dĺžka | SHA-256 | Adresovanie |
|---|---|---:|---|---|
| DOS 2.0 | Unpacked headerless MZ load image | 171 360 | `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297` | `IMG:xxxxx` = bajt v load image |
| Win16 1.10 | Raw NE EXE | 230 400 | `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481` | `NE3:xxxx` = offset logického segmentu 3 |
| Win16 alternatívny | Raw NE EXE | 230 224 | `144e96bb649c5463d440c343ad982ed8e5f143e788c9af08bbb890fcd1b3db22` | `NE3:xxxx` |

Pozor: `IMG:` nie je runtime breakpoint pri dosboxovej relokácii. `NE3:` nie je loaded Win16 selector. Cross-build porovnania sú ohraničené presne týmito tromi hashmi. Počet syntetických testov nemožno previesť na percento originálnej gameplay parity.

## B. Geometry/LOS: originálne 354 B, vo všetkých troch buildoch

| Build | Funkčný vstup | Koniec lokálneho tela |
|---|---|---|
| DOS 2.0 | `IMG:BB60` | `IMG:BCC1` (RETF) |
| Win16 1.10 | `NE3:D50A` | `NE3:D66B` |
| Win16 alt | `NE3:D45C` | `NE3:D5BD` |

- 354/354 bajtov prešlo sha-gated porovnaním. DOS vs Win16 1.10: **338 bajtov rovnakých a 16 rozdielnych operandových bajtov** (mapová báza, property tabuľky, pointer a dva FAR ciele); všetky ostatné inštrukcie a Jcc ostávajú totožné.
- Win16 1.10 vs alternatívny build: po maske vyššie uvedených operandových polí je celé telo rovnaké.
- Sign krokov je **+1 iba ak delta > 0; inak −1**, aj pri nulovej delte. Koniec je 16-bitový `start+delta` s wrapom.
- Rieši dominantnú os pomocou `abs(deltaY) < abs(deltaX)` so znamienkovým 16-bitovým porovnaním; error je `2*minor − major`. Pohyb dominantnej osi prebehne vždy, pohyb vedľajšej osi iba keď pred aktualizáciou `error>=0`.
- `maxSteps <= 0` (signed word) vracia neúspech. Inak v každom kroku **najprv pohne X/Y a porovná oba koordináty s cieľom**. **Pri dosiahnutí cieľa vráti `AL=1` ešte pred testom mapových vlastností cieľovej bunky.**
- Ak cieľ v limite nebol dosiahnutý, nastane `AL=0`, nie „prázdna cesta => úspech“.

### Lokálne mapové rozhodnutie, každý medzikrok

```
if (wallFlags & 0x02) {
    if (wallFlags & 0x04) return false;
    if (wallFlags & 0x08) {
        moving_wall_record = Find18ByteRecordForMapCell(...);
        if (!MovingWallStateAllowed(moving_wall_record)) return false;
    }
}
if (checkObject != 0) {
    if ((objectFlags & 0x02) && !(objectFlags & 0x20)) return false;
}
// pokračuje ďalším Bresenham-like krokom, ak limit ešte dovolí
```

Nie je správne nahradiť to všeobecným `raycast` testom všetkých buniek vrátane poslednej ani vynechať nulové delta prípady. Normálne herné vzdialenosti sú menšie ako 32768; vlastnosti 16-bitového signed overflow a čítania mimo 64×64 mapy pri patologických vstupoch ešte vyžadujú reachability dôkaz.

### Vstupy od 3 priamych DOS volajúcich

| CALL site v originálnom DOS 2.0 | Maxsteps | Kontrola OBJECT | Použitie |
|---|---:|---|---|
| `IMG:01A5` | premenná dĺžka z `CX` | `0` | jedna selekčná/viditeľnostná rutina |
| `IMG:542D` | `8` | `1`, len pri splnenej vetve predchádzajúceho argumentu | GUARD LOS rozhodnutie |
| `IMG:6A1B` | `16` | `1` | zameriavanie GUARD v weapon/action state=1 |

Pri `IMG:542D` je objektový argument odvodený z `WORD [BP+0E] == 1`, nie natvrdo zapnutý. Pri `IMG:01A5` nie je dokončené priradenie konkrétneho herného účelu všetkým volajúcim rámcom; lokálna podpisová sémantika je preukázaná. **Tri výskyty je úplný census danej priamej FAR inštrukcie v DOS 2.0 image, nie úplný census nepriamych volaní.**

## C. Nové: DOS pohyblivá stena má stavový gate 0/4 a samostatnú chybovú vetvu

V predchádzajúcich reportoch boli na `IMG:BC6E` a `IMG:BC78` v LOS význame neúplné transitive callee. Priamo kontrolovaný originál má:

1. `IMG:BC6E` → `CALL FAR 0000:0000` (**IMG:0000**), lookup v poli 18 B záznamov.
2. Prvá funkcia načíta count z `21FD:0000`, štartuje na `21FD:3076`, iteruje stride `0x12`, porovnáva mapový `offset` a `segment` s WORD `record+04/+06`. **Vráti prvý zhodný pointer v DX:AX**.
3. `IMG:BC78` → `CALL FAR 0000:01E0` (**IMG:01E0**), číta WORD `record+08` a vracia AL=1 **iba ak** `state==0` alebo `state==4`.
4. Ak sa lookup neskončí zhodou, `IMG:0044` volá `0FBA:000C` s kódom `0x42`; jeho telo je `IMG:FBAC`, volá runtime `11EE:01EB` s exit status `1`; v normálnej exit vetve je `IMG:1214A` `MOV AH,4Ch; INT 21h`.

**Statické uzavretie:** pri existujúcom matching 18B recorde je presné miestne rozhodnutie o priechodnosti `state in {0,4}`. Pri chýbajúcom recorde je jasná diagnostická a DOS exit cesta, nie obyčajný `false` bez vedľajších účinkov. Kompletné cleanup callbacky/runtime návratnosť veľmi špeciálnych exit hookov a rovnaký Win16 vnorený mechanizmus **nie sú uzavreté**. Hra nebola spustená.

## D. Damage scalar: 20 pôvodných tried a precízna aritmetika

| Build | Funkčný vstup | Lokálne telo |
|---|---|---:|
| DOS v2.0 | `IMG:8590` | 291 B |
| Win16 1.10 | `NE3:9FA2` | 291 B |
| Win16 alt | `NE3:9EF4` | 291 B |

Celých 291 B má po maske **18 explicitne deklarovaných operandových okien** rovnaké inštrukcie naprieč tromi buildmi. DOS vs Win16 má 78 odlišných bajtov vrátane 20 relokovaných WORD cieľov v skokovej tabuľke; nie sú to 78 odlišné logické rozhodnutia. Všetkých 20 skokových cieľov pre triedy `0x0C..0x1F` je dekódovaných z originálneho CS-relative `JMP WORD PTR CS:[...]` a kontrolovaných proti nezávislým buildom.

1. Bez vstupného class gate načíta `OBJECT+0x18`, odčíta `DS:4552` (Win16 zodpovedajúca `DS:53EE`), posunie výsledok doľava o tri bity (`×8`, 16-bit wrap).
2. **Bezpodmienečne** volá zdieľané RNG, nasleduje `CWD; IDIV 25`, do hodnoty pripočíta signed remainder `0..24` (RNG návrat má 15-bitovú nezápornú doménu).
3. Podľa `OBJECT+06` triedy vykoná vetvu uvedenú nižšie.
4. Difficulty `0`: `SI*=2` s 16-bit wrapom; difficulty `2`: signed `SAR SI,1`; pri ostatných hodnotách lokálne ponechá SI.
5. `CMP AX,00FFh; JLE return` (signed), inak `AX=00FFh`. **Žiadna dolná nula**. Nadriadený `IMG:5F74` následne vykoná `SUB AH,AH`: používa iba low8-bit výsledku (nie celý signed AX).

| Trieda `OBJECT+06` | Vetva pred obtiažnosťou (`S` je raw SI po RNG) |
|---|---|
| `0C`, `1D` | `S SAR 3` |
| `0D` | selektor byte `DS:418F == 1` → `SAR 1`, inak `SAR 3` |
| `0E`, `11`, `14` | selektor `==2` → `SAR 1`, inak `SAR 3` |
| `0F`, `10` | selektor `==1` → `SAR 8`, inak `SAR 1` |
| `12`, `13` | `SAR 2` |
| `15` | najprv FAR callback s argumentom z `DS:1068`, potom `S=0` |
| `16` | ak `DS:626A == 3` → `S=3`, inak `S=0` |
| `17` | selektor `==1` → `SAR 8`, inak `SAR 2` |
| `18` | selektor `==1` → `SAR 8`, `==2` → `SAR 4`, inak `SAR 3` |
| `19` | `S=0` |
| `1A` | selektor `==1` → `SAR 1`, inak `S=0` |
| `1B`, `1C` | `SAR 1` |
| `1E` | selektor `==1` → `S=0`, inak `SAR 3` |
| `1F` | selektor `==1` → `S=0`, inak `SAR 2` |
| mimo `0C..1F` | v tomto dispatcheri sa SI pred difficulty nezmení |

Špecificky trieda `0x15` **nepreskakuje RNG ani FAR callback**, aj keď výsledná číselná škoda je nula. Taktiež trieda `0x16` nepoužíva bežnú damage aritmetiku po triedovom dispatchi; do difficulty vstupuje konštanta 0 alebo 3.

**Syntetická odchýlka, NIE retail bug dôkaz:** ak `OBJECT+18 – reference == -1`, RNG remainder=0, class `0C`, difficulty=1, potom `SI=-8 → SAR3=-1 → AX=FFFFh → low byte FFh (255)`. Dosiahnuteľnosť takýchto reálnych depth hodnôt v hernom ticku ešte nemáme.

## E. Zásahový wrapper: úvodné vetvy a 19-state dispatch

Pôvodný DOS `IMG:5F74` (Win16 `NE3:80F8`, alt `NE3:8054`) spotrebuje nízky bajt damage scalaru:

```
damage = byte(DamageScalar(guard,object))
if (guard.HP <= damage) {
    guard.HP = 0
    // death helpers, score, SFX, world-object and drop/map changes
    // presné nested účinky OPEN
} else if (damage == 0) {
    return  // bez lokálneho HP/pain writeru v tejto vetve
} else {
    if (guard.state == 7) call_special_pre_hit(...)
    guard.HP -= damage
    guard.pain_timer_at_12 = 8
    if (guard.strategy_at_0A == 2) special_strategy_2(...)
    else if (guard.strategy_at_0A == 4) return
    else route_by_state_03_to_15(...)
}
```

V 19-prvkovej WORD tabuľke pre `GUARD.state = 3..21` sú **iba tri cieľové kategórie**:

- `3`, `4`, `11`: okamžitý návrat z lokálneho stavu (po HP/timer writeroch).
- `7`, `8`, `21`: špeciálna animačná vetva s ďalšími FAR volaniami.
- `5`, `6`, `9`, `10`, `12..20`: vetva s prednastavením GUARD state `21` (0x15) a ďalšími side effects.

Pri stavoch mimo rozsahu 3..21 prejde lokálny dispatcher do predvolenej vetvy state 21. **To neznamená**, že taký stav je prirodzene dosiahnuteľný alebo že finálne vyhodnotenie všetkých FAR helperov je uzavreté. V hazardnom symbolickom prípade GUARD HP=0 a damage=0 je vykonaná lethal vetva `HP <= damage`; prirodzená dosiahnuteľnosť je OPEN.

DOS image obsahuje **dve priame** FAR volania tohto hit wrappera: `IMG:6A2F` (weapon-state1 GUARD scan) a `IMG:8125` (ďalšia kolízna/hit vetva). Ide o lokálny direct-call census, nie úplný transitive graf.

## F. Dôsledky pre 1:1 implementáciu

- Nespájať všetkých 3 volajúcich geometrie do jediného `bool HasLineOfSight()` bez parametrov `max_steps` a `checkObject`.
- Cieľová bunka sa netestuje ako bežná medzibunka; blokovanie koncového objektu sa rozhoduje už v iných vrstvách.
- Special WALL bit 0x08 vedie k vyhľadaniu záznamu a testu jeho stavu; pri chybe lookup nemožno bez dôkazu pokračovať tichým `return false`.
- Damage scalar používa cached `OBJECT+18` a jeden RNG odber **pred** triedovým dispatchom; výsledok má iba horný signed clamp.
- Pri GUARD hit wrapperi treba zachovať poradie `damage producer → lethal/nonlethal gate → HP/pain/state helpers`; volané helpery môžu mať vlastné vedľajšie účinky.
- Porovnanie automatických originálnych CPU logov ešte nebolo vykonané, preto sa **celková behavior/timing/render parita nezvyšuje**.

## G. Reprodukcia a kvalita kontroly

```
py verify_v057.py --dos20 "C:\\N3D\\N3D_REMAX_EXEPACK_UNPACKED_RAW_20261014.bin" --win110 "C:\\N3D\\nite3w_110.exe" --winalt "C:\\N3D\\nite3w_alt.exe" --out evidence_v057.json
py -m unittest discover -s tests -p test_v057.py -v
c++ -std=c++17 -Wall -Wextra -pedantic tests/test_cpp_v057.cpp -o test_v057
```

Verifikátor **pred každým offsetom vyžaduje správny SHA-256 a dĺžku**; kontroluje celé telá 354B/291B proti odlišným buildom, 20 class table entry, 19 state entry, explicitné opcode witnesses aj DOS nested lookup/exit proof. Kód verifikátora a oba modely sú bez pôvodných autorských game bináriek.

Testy: **41 Python unit testov** (syntetické modelové vstupy), samostatný **C++17** test pre geometriu, damage, hit vetvy a moving-wall výsledok; class matrix 1656 symbolických konfigurácií. **Testy nezakladajú tvrdenie, že bola spustená pôvodná Nitemare 3D.**

### Otvorená hranica po v0.57

1. Presné Win16 ekvivalenty dvoch DOS nested moving-wall funkcií, full writer census `18B record+08`, celá fallback/error runtime cleanup cesta.
2. Všetci producenti `OBJECT+18` a `DS:4552`, dosiahnuteľnosť záporných medzihodnôt a efekty render/visibility na damage a RNG.
3. Celé transitive FAR callee class `0x15`, špeciálny `DS:626A==3` branch, score/drop/morph, GUARD state 21 a strategy 2/4.
4. Weapon state1 precondition helper a dynamická multi-GUARD scan reachability.
5. Všetky verziové rozdiely vo Win16, DOS1.x a original LOAD/scheduler IRQ chronológia; pixel/timing runtime ak statika nemôže viac rozhodnúť.

Strojovo čitateľný prioritný zoznam: `UNKNOWN_FRONTIER_v057.csv`. Výstupne modelové matice majú `data_type=synthetic_input`. GitHub nebol upravený.
