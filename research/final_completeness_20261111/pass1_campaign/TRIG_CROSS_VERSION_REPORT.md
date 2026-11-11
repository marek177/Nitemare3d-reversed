> Updated Windows conclusion: four normalized Win16 helper bodies are now verified. See WIN110_TRIG_HELPERS_REPORT.md; the earlier raw-pattern negative result below remains only a raw-byte observation.

# Cross-version: trigonometrické tabuľky a štyri helpery

DOS 2.0 obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Porovnané DOS označenia 1.0,1.1,1.2,1.5,1.7,1.8,1.9,2.0 predstavujú **sedem unikátnych obrazov**; označenia 1.8/1.9 majú rovnaký hash. Názvy verzií sú prevzaté označenia vstupov, nie nové datovanie release.

## Bajty a funkčné telá DOS

Celý blok **546 B** (sínus 182 B, kosínus 182 B, saturovaná tangentová magnitúda 182 B) má v každom obraze práve jednu úplnú bajtovú zhodu. Tabuľky sa nenormalizovali a ich pôvodné kvantované hodnoty zostali totožné.

Štyri po sebe idúce telá sin/cos/signed-tangent-magnitude/angle-lookup boli porovnané proti DOS 2.0. **32/32 normalizovaných funkčných porovnaní** je zhodných; iba **4/32** sú raw byte-exact, všetky z referenčného obrazu. Normalizácia povoľuje iba dekóderom určené dvojbajtové dátové displacement/immediate operandy zo zoznamu canonical table-address konštánt. **91 zmenených WORDov** je adresne zaznamenaných v `operand_edits.csv`; v jednom obraze musia mať všetky rovnaký delta naprieč štyrmi funkciami.

Všetky ostatné bajty sa musia zhodovať vrátane porovnaní, znamienkových operácií a relatívnych skokov. Navyše sa kandidáti nezávisle dekódujú a kontrolujú sa relatívne začiatky/dĺžky inštrukcií a flow-control kategórie. Tým je doložená zhoda týchto lokálnych CFG/tiel pod presunom dátových adries. Nie je to len podobnosť mien či signatúr.

Umiestnenie kódovej skupiny sa vyberá až po zhode všetkých štyroch telies a jediného tabuľkového bloku. Odvodená DS báza je vypočítaná z prvej table-reference a presnej dátovej zhody; jej paragraph alignment sa kontroluje. **Toto je odvodenie, nie nezávislý startup DS dôkaz každej verzie.** Caller ABI, prirodzené vstupy a runtime dosiahnuteľnosť sa tým neuzatvárajú. Replay starších DOS verzií sa v tejto dávke nevykonal.

## Win16 1.10: presná dátová zhoda

EXE SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`. Rovnaký 546 B blok má práve jednu raw file zhodu na **file offsete 180894 (2C29Eh)**. Parsovanie NE segmentovej tabuľky potvrdilo, že celý leží vo file-backed **dátovom segmente 10**, ktorého file začiatok je 180288 a inicializovaná dĺžka 36526 B. Lokálny rozsah je **10:025E..0480** (end-exclusive).

To potvrdzuje identické počiatočné tabuľkové dáta medzi DOS a Win16. Štyri DOS kódové telá nemajú raw byte-exact zhodu v celom Win16 EXE. Táto negatívna signatúrna kontrola **nedokazuje absenciu ekvivalentných Windows algoritmov**; NE fixupy, iné adresovanie a caller kontext treba analyzovať osobitne. Windows funkčná/behaviorálna parity zostáva otvorená.

## Reprodukcia a stav

`compare_trig_versions.py IMAGE OLD_OUTPUT_ROOT DECODER_DIR WIN110_EXE OUT` reprodukuje vyššie uvedené kontroly. `trig_cross_version/versions.csv` uchováva SHA a umiestnenia, `functions.csv` raw/normalizované výsledky, `operand_edits.csv` všetkých 91 úprav a `summary.json` aj NE umiestnenie.

PASS1 mapa sa nemení: **54 164 B PARTIAL, 3 087 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**. Žiadny nový prirodzený runtime ani replay; súčet prijatých seeded prípadov zostáva 6 091. Úplnosť algoritmov alebo projektu sa nevyjadruje novým percentom z 32 lokálnych zhôd.

Ďalší krok: Win16 code xrefs na segment 10 offsety 025E/0314/03CA, NE selector kontext a štyri ekvivalentné helpery; paralelne prirodzené DOS caller kontrakty. PE32 port sa nevykonáva.


## Aktualizácia 13 oblastí

Nové sémantické percento je všade N/A: úplný inventár kontraktov/polí/vetiev chýba. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické percentá sú orientačné odhady.

| Oblasť | Predošlý odhad | Nové % | Potvrdenie | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | opravená mapa a flagy | prirodzené súbory | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 546 B tables identical across DOS labels and Win110 | 2 relokačné B bez typu | roly segmentov |
| Tabuľky a ukazovatele | 93 % | N/A | 32 normalized DOS helper comparisons | writeri/lifetime | pointer watchpointy |
| Funkcie / ASM / CFG | 90 % | N/A | 34 rozsahov, 1 150 inštrukcií | kontrakty/dosiahnuteľnosť | caller stopy |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | staršie PIT dôkazy zachované | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová DEMO stopa |
| Renderer / VGA | 94 % | N/A | bit reversal začlenený | clipping/orientácia | payload spotrebiteľ |
| GUARD / bossovia | 93 % | N/A | nominálne pole 100×26 | AI/lifecycle | inicializátory |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie/sloty | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | 60 počiatočných UI textov | textový lifetime | SS čítania po návrate |
| SAVE / LOAD | 92 % | N/A | mapové/flagové rozsahy | LOAD parity | párový stav |
| Windows Win16 | 92 % | N/A | exact 546 B table in NE segment 10 | callback DS/import ABI | Win16 code xrefs and selectors |

