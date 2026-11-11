# PASS1: 104 adresne doložených error formátov

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`, historický inventár SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`. V tomto inventári bolo overených **104 priamych call sites 0FBA:000C**, každé s bezprostredne predchádzajúcim konštantným PUSH formátového offseta. Ide o 104 samostatných formátových objektov, spolu **2 535 B** vrátane NUL. Status PARTIAL.

## Metodika a ochrana pred falošnými xrefs

Voľné hľadanie PUSH čísel dávalo aj náhodné zhody: napríklad numerický argument 400h náhodne smeruje doprostred iného textu. Taká zhoda sa nepreberá. Nový skript vyžaduje presný FAR CALL opcode/target 0FBA:000C, bezprostrednú fyzickú susednosť posledného PUSH, jeho konštantný operand, zhodu pôvodných bajtov a nezávislé dekódovanie oboch inštrukcií.

Už analyzovaný error helper má prvý argument formátu v SS:[BP+6], ktorý odovzdáva formátovaciemu helperu. Posledný PUSH pred FAR CALL je teda konkrétny formátový argument, nie ľubovoľný číselný parameter. Jeho mapovanie do file-backed DS používa zdedený default DS predpoklad; prirodzený DS všetkých 104 ciest nie je uzavretý. Skript overuje skutočný NUL a celý ASCII obsah vrátane riadiacich CR/LF/TAB, ak sú prítomné.

Presné texty, adresy, konce, PUSH/CALL bajty a CS:IP sú v `pass1_error_formats/format_references.csv`; typy a SHA v `data_fields.csv`. Príklady zahŕňajú limity objektov/segmentov, chýbajúce obrázky či sekvencie, neplatné rozmery, I/O a pamäťové diagnostiky. Konkrétna diagnostika nie je dôkaz úspešného prirodzeného vykonania príslušnej chybovej vetvy.

Všetkých 104 nájdených call sites splnilo zvolený susedný konštantný vzor; vynechaných podľa tejto podmienky bolo 0. To sa týka **použitého inventára**, nie dôkazu absencie ďalších call sites v nevykatalogizovanom či nepriamo volanom kóde. Formátovacie konverzie, vararg typy, error non-return kontrakt a všetci writeri textov zostávajú otvorení.

## Reprodukcia a metriky

`audit_pass1_error_formats.py IMAGE INVENTORY DECODER_DIR OUT` vytvára source-pinned typový katalóg a 104 caller dôkazov. `promote_pass1_fields.py` používa predchádzajúcu mapu `pass1_runtime_messages/noncode_intervals.csv`. Výstupy sú v `pass1_error_formats/`; centrálny katalóg počíta prekryvy ako úniu.

Z 2 535 B bolo **176 B už PARTIAL**. Čistý prírastok **2 359 B** pochádza z CLASSIFIED ONLY. Aktuálne **PARTIAL 53 448 B, CLASSIFIED ONLY 3 803 B, UNKNOWN 44 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Predošlá mapa: 51 089 / 6 162 / 44 / 0 B. Netypované relokačné PARTIAL bajty zostávajú 2 B. Nový prirodzený runtime ani replay sa nevykonal; 104 statických call sites nie je 104 runtime testov.

DOSBox-X plán: vybrané dosiahnuteľné error vetvy, skutočný DS, formát/varargs a ukončenie procesu. Ďalší krok: zvyšné CLASSIFIED ONLY názvy súborov, parametre formátov, statické tabuľky a runtime segmentové kontrakty. Celková úplnosť sa neodvodzuje z počtu diagnostických textov.


## Aktualizácia 13 oblastí

Nové sémantické percento je všade N/A: úplný inventár kontraktov/polí/vetiev chýba. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické percentá sú orientačné odhady.

| Oblasť | Predošlý odhad | Nové % | Potvrdenie | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | opravená mapa a flagy | prirodzené súbory | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 329 polí/39 zdrojov; 104 error formats | 2 relokačné B bez typu | roly segmentov |
| Tabuľky a ukazovatele | 93 % | N/A | 104 source-pinned format PUSH/CALL pairs | writeri/lifetime | pointer watchpointy |
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

