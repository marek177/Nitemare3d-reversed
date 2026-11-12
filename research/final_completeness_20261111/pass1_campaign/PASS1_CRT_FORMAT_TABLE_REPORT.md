# DOS 2.0: zdieľaná znaková a prechodová tabuľka CRT formátovača

## Presné NON-CODE dáta a spotreba

Blok **DS:22CA..2323, obraz `[299DA,29A33)`, 89 B** má doložené použitie cez dve inštrukcie XLAT so spoločnou základňou BX=22CAh. Prvý lookup používa spodný nibble ako triedu znaku, druhý horný nibble ako nový stav. Nie je to sekvencia ASM ani obyčajný text. Nasledujúci reťazec `(null)` do tohto rozsahu nepatrí a touto dávkou sa nepromuje.

Prvých **72 B** má dvojitú rolu: low4 pre znaky a high4 pre 9×8 prechodov. Zvyšných 17 B má v tejto ceste doloženú low4 klasifikáciu; jeho high4 sa pri tomto prvom lookup maskuje a touto dávkou sa mu nepripisuje samostatný význam. Celý blok má stav PARTIAL, nie DEEP VERIFIED.

Klasifikácia pokrýva znaky 20h..78h inclusive. SUB AL,20h sa vykonáva modulo 256; následné unsigned porovnanie s 58h dá pre všetky ostatné vstupné BYTE triedu 0. Platný prvý lookup teda nikdy neprekročí 89 B. Všetky získané triedy sú 0..8.

| Trieda | Konkrétne znaky mimo triedy 0 |
|---:|---|
| 1 | `%` |
| 2 | `.` |
| 3 | `*` |
| 4 | `0` |
| 5 | `1`..`9` |
| 6 | medzera, `#`, `+`, `-` |
| 7 | `F`, `L`, `N`, `h`, `l` |
| 8 | `E`, `G`, `X`, `c`, `d`, `e`, `f`, `g`, `i`, `n`, `o`, `p`, `s`, `u`, `x` |

Trieda 0 zahŕňa zvyšné pokryté znaky aj všetky znaky mimo rozsahu. Názvy stavov a úplná sémantika jednotlivých formátovacích špecifikátorov sa neodvodzujú iba podľa tejto triedovej podobnosti.

## Lokálny algoritmus a dispatch

Pôvodný blok **11EE:1676..169F**, obraz `[13556,1357F)`, má 41 B / 19 dekódovaných inštrukcií vrátane záverečného nepriameho JMP. Vstupný znak je v AL, starý stav v BYTE SS:[BP-5].

```text
index = BYTE(character - 20h)
class = index <= 58h ? TABLE[index] & 0Fh : 0
transition_index = BYTE(class*8 + old_state)
new_state = TABLE[transition_index] >> 4
SS:[BP-5] = new_state
AX = sign_extend8(new_state)
BX = AX*2
jump WORD CS:[1638h + BX]
```

Pre old_state 0..7 je transition_index presne v 0..71; všetkých 72 horných nibblov dáva new_state 0..7. Zachytené okolie obsahuje inicializáciu lokálneho stavového BYTE na nulu. Toto podporuje lokálnu uzavretosť prechodu, ale neuzatvára aliasované stack zápisy a všetky účinky handlerov/callee celej funkcie.

CS dispatch tabuľka je **11EE:1638..1648**, obraz `[13518,13528)`, 8 WORDov. Stavové ciele 0..7 sú **169F, 16AA, 16BE, 16F2, 171E, 1726, 174F, 1781** v segmente 11EE. Všetky ciele majú byte-exact overenú inštrukčnú hranicu v inventári a nezávisle dekódovanú prvú inštrukciu. Celé telá handlerov ani ich prirodzená dosiahnuteľnosť sa tým nepotvrdzujú. Dispatch dáta sú mimo historickej NON-CODE baseline a v tejto dávke sa nepridávajú do jej mapy.

## Controlled replay a reprodukcia

`audit_replay_pass1_crt_format_table.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT` overuje identitu obrazu, bajty prefixu, rozsah tried, prechodov a dispatch target hranice. Spustí pôvodné inštrukcie pre **256 znakov × 8 starých stavov × 2 load bázy = 4 096 prípadov**, bez odchýlok.

Vykonávanie sa zastaví pred 11EE:169A, teda pred nepriamym JMP. Overuje sa uložený stav, AX a BX; handler sa nevykonáva. Seedované DS a SS/BP sú súčasťou modelu. Test nie je prirodzené volanie printf, nevykonáva celý formátovač, produkciu textu, varargs ABI ani DOS I/O.

Strojové výstupy v `pass1_crt_format_table/`: `prefix_instructions.csv`, `table_bytes.csv` (každý bajt a oba nibbly), `dispatch_targets.csv`, `data_fields.csv`, `cases.csv`, `summary.json`. CSV/JSON mapa a nezávislá kontrola partition sú v rovnakom adresári.

## Pokrytie a hranice tvrdenia

Všetkých 89 B prešlo z CLASSIFIED ONLY do PARTIAL. Aktuálne: **54 835 B PARTIAL, 2 416 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57 295 B. Nezávislá kontrola overila 662 intervalov, SHA, presné členstvo a nulové diery/prekryvy.

Centrálny katalóg zostáva 48 úplnejších funkčných rozsahov / 1 691 inštrukcií / 4 028 B kódu; tento neuzavretý prefix sa nepridáva ako celá funkcia. Typované dáta celého obrazu: **55 681 B**; typované historické NON-CODE dáta: **54 833 B**. Rozdiel 2 B oproti PARTIAL zostáva neuzavretý relokačný WORD.

Controlled replay súčet je 12 005, vrátane tejto výslovne prefixovej dávky; navyše sa samostatne vedie 65 548 prípadov normalizačného prefixu. Prirodzené runtime testy zostávajú 0. Najnovšia overená GitHub snímka je commit 52924ebf849dd79d15af9d7c164b8304f50cae87; túto novú dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika sémantického percenta pre každú oblasť: uzavreté jednotky / úplný inventár jednotiek. Menovatele chýbajú; nové percentá sú N/A a predošlé orientačné. Nová tabuľka a širší formátovač zostávajú PARTIAL.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | prirodzené stavy | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 89 B s presnou nibble rolou | okolie tabuľky | susedný null text |
| Tabuľky a ukazovatele | 93 % | N/A | 9×8 DFA a 8 dispatch cieľov | handler kontrakty | osem handlerov |
| Funkcie / ASM / CFG | 90 % | N/A | prefix a nepriama dispatch väzba | celé telo formátovača | vetvy od 169F |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | prirodzené poradie | tick stopy |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová DEMO stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping | render stopa |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | AI/lifecycle | inicializátory |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | CRT textový parser oddelený | skutočný výstup | formátovacie callery |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | parity | serializačné stopy |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | CRT parser parity | Win tabuľka a XLAT |

## Runtime testy na vykonanie

Zachytiť prirodzené formátovacie volanie, DS, SS/BP, znak, starý/nový stav a cieľ nepriameho JMP. Porovnať výstup pri šírke, presnosti, príznakoch a typových špecifikátoroch s konkrétnymi handlermi. Syntetické prechádzanie stavov ani nepodporované formáty sa nepočítajú ako prirodzené herné pokrytie. DOSBox-X vykonanie zatiaľ chýba.
