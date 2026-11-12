# DOS 2.0: pôvodný RNG, seed, násobenie a väzba na výpočet účinku

## Presný file-backed stav

**DS:24B8, obraz `[29BC8,29BCC)`, 4 B** je mutable DWORD RNG stav, počiatočne `01 00 00 00`. Rutiny seed/rand explicitne zapisujú jeho low/high WORDy; nejde o pointer ani padding. `data_fields.csv` pripína rozsah a SHA. Prirodzené ďalšie zdroje seedov, alias writeri, serializácia a časovanie RNG volaní zostávajú otvorené.

## Presné funkcie a oddelenie vrstiev

| Funkcia | CS:IP | Interval obrazu, koniec exclusive | B / inštrukcie |
|---|---|---|---:|
| WORD seed | 11EE:31E6 | [150C6,150D7) | 17 / 7 |
| CRT RNG | 11EE:31F8 | [150D8,15100) | 40 / 14 |
| low32 multiply helper | 11EE:3AD8 | [159B8,159EA) | 50 / 23 |
| Herný rand wrapper | 0FBA:01A0 | [0FD40,0FD46) | 6 / 2 |
| Herný fixed-seed wrapper | 0FBA:01A6 | [0FD46,0FD51) | 11 / 4 |

Spolu **124 B / 50 inštrukcií**. Každé celé telo je byte-exact overené a nezávisle dekódované. Medzery medzi funkciami sa k nim nepripočítavajú. „CRT“ a „compiler helper“ tu pomenúvajú úlohu oddelenú od herných wrapperov; totožnosť konkrétnej verzie knižnice/kompilátora sa nepovyšuje iba podľa signatúry algoritmu.

## Algoritmus a ABI

```text
srand_word(seed_WORD):
    state.low16 = seed_WORD
    state.high16 = 0
    return FAR                  # argument odstraňuje caller

rand():
    state = (state * 214013 + 2531011) mod 2^32
    AX = (state >> 16) & 7FFFh
    return FAR

game_rand(): return rand()
game_fixed_seed(): srand_word(1)
```

Násobiteľ je z okamžitých WORDov 0003h:43FDh, prírastok z 0026h:9EC3h. Výstup je preto vždy **0..32767**. Z file počiatočného stavu 1 vychádza ďalší stav 2745024 a návrat 41; zo seed 0 vychádza stav 2531011 a návrat 38. Toto sú vypočítané a replay overené príklady, nie pozorovanie prirodzeného prvého RNG volania hry.

Multiply helper dostane štyri WORDy `A.low,A.high,B.low,B.high`, vracia DX:AX a končí **RETF 8**, teda odstráni vlastných 8 B argumentov. Ak sú oba horné WORDy nulové, použije kratšiu vetvu; inak skladá low32 výsledok z 16-bitových MUL. Algebraický tvar je low=`A.low*B.low mod 65536`, high=`high16(A.low*B.low)+A.high*B.low+A.low*B.high mod 65536`. High×high príspevok je mimo low32 a neukladá sa.

Rand ani jeho herný wrapper neprijímajú explicitný argument. Seed helper prijíma WORD, zatiaľ čo fixed wrapper sám pushne 1 a odstráni argument po návrate. RNG používa DS stav; nemení DS/ES explicitne. BP/SI/DI/DS a lokálny SP sú overené v riadenom modeli; pracovné AX/CX/DX/FLAGS sa nepovažujú za zachované. Multiply helper navyše v samostatnej matici zachová BX.

## Väzba na výpočet účinku a calleri

Prefix 083D:01C0..01EA získa WORD druhého FAR objektu na +18h, odčíta DS:4552 a výsledok posunie v 16-bit SI doľava o 3. Potom zavolá game_rand, vykoná signed IDIV 25 a pripočíta zvyšok DX do SI. Keďže skutočný RNG vracia nezáporné AX, zvyšok je **0..24**. Prefix sa dá zapísať `SI = WORD(WORD(object_word18 - DS:4552)*8 + rand()%25)`.

Celé následné rozdelenie podľa BYTE objektu +6, selektora, epizódy a ďalšieho stavového WORDu ešte nie je uzavreté. Tento prefix sa nepridáva do funkčného katalógu ako celá damage rutina a nevydáva sa za finálny damage vzorec.

`direct_far_callers.csv` obsahuje byte-exact overené priame FAR referencie na päť uvedených funkcií v dodanom inventári. Medzi nimi je 22 priamych volaní game_rand a reset wrapper z **0D29:271C**. Úplný inventár nepriamych/alias volaní, prirodzená udalosť resetu a poradie spotreby náhodných hodnôt zostávajú otvorené. Statická reset väzba sama nedokazuje deterministický DEMO/replay celej hry.

## Controlled replay a reprodukcia

`audit_replay_pass1_rng.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT` vykoná pôvodné seed/rand/multiply/wrapper inštrukcie, s EXEPACK relokáciami pri load bázach 0 a 1000h a **bez mock callees**:

- Všetkých 65 536 WORD seedov: seed funkcia musí uložiť celý DWORD so zero high WORD, potom sa overí prvý RNG krok.
- Šestnásť ďalších 32-bitových seedovaných stavov vrátane 7FFFFFFFh/80000000h/FFFFFFFFh: 128 nadväzujúcich krokov z každého stavu.
- Samostatná 9×9 operandová matica multiply helpera: obe jeho vetvy, low32 výsledok, BX a RETF 8 cleanup.
- Fixed-seed wrapper musí prepísať FFFFFFFFh na 1.

Spolu **135 332 prípadov**, z toho **135 168 RNG návratov**, **162 samostatných násobení** a **2 fixed reset prípady**, bez odchýlok. Reprezentatívne 32-bitové sekvencie ani 81 násobkov nie sú exhaustívne prejdenie všetkých 2^32 stavov alebo všetkých párov operandov; všeobecný modulo vzorec je podložený aj pôvodnými inštrukciami. Test neoveruje prirodzený seed ani call schedule.

Výstupy `pass1_rng/`: päť funkčných ASM CSV, `damage_rng_prefix.csv`, `direct_far_callers.csv`, `data_fields.csv`, `cases.csv`, `summary.json`. SHA-256 finálneho `cases.csv`: `dfda84ff2f3dfc97bd50345e3c2598fcb268786d145a7c9d12854c72d24a2c40`. Staršie behy pred pridaním samostatnej multiply matice sa nezapočítavajú znova. Pôvodné DOS/runtime testy zostávajú 0.

## Pokrytie

4 B stavu prešli z CLASSIFIED ONLY do PARTIAL. Aktuálna mapa: **54 986 B PARTIAL, 2 265 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57 295 B. Nezávislá kontrola overila 680 intervalov, ich SHA, presné členstvo a nulové diery/prekryvy.

Centrálny katalóg: **61 rozsahov, 2 081 inštrukcií / 5 107 B kódu**, 55 832 B typovaných dát celého obrazu, 54 984 B historických NON-CODE dát. Rozdiel 2 B voči PARTIAL zostáva neuzavretý relokačný WORD. Controlled replay súčet: 160 203 plus osobitne 65 548 normalizačných prefixových prípadov. Počet testov nie je sémantické percento. Širší RNG/DEMO/damage kontext zostáva PARTIAL. GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového sémantického percenta: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú; nové percentá sú N/A a predošlé orientačné.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | prirodzené stavy | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 4 B LCG stav a presné konštanty | všetci writeri | alias/LOAD zápisy |
| Tabuľky a ukazovatele | 93 % | N/A | seed/reset state väzba | nepriamy caller inventár | úplný call ledger |
| Funkcie / ASM / CFG | 90 % | N/A | päť funkcií, 124 B / 50 inštrukcií | prirodzené kontrakty | seed caller |
| RNG | 97 % | N/A | presný LCG, output range, WORD seed doména | časovanie a seed zdroje | 0D29:271C kontext |
| Scheduler | 96 % | N/A | RNG call sites identifikované | poradie spotreby | tick/RNG stopy |
| DEMO a vstupy | 96 % | N/A | fixed seed 1 wrapper | prirodzená reset udalosť | DEMO call ordering |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping | render stopa |
| GUARD / bossovia | 93 % | N/A | zdroj random zložky účinku | stavové multiplikátory | 083D:01C0 zvyšok |
| Zbrane / projektily | 92 % | N/A | rand%25 rozsah 0..24 v prefixe | finálny damage | dispatch 20 typov |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | asset identity | descriptor producer |
| SAVE / LOAD | 92 % | N/A | file-backed mutable RNG DWORD | uloženie/obnova | serializačné rozsahy |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | RNG/seed parity | Win LCG a calleri |

## Runtime testy na vykonanie

Zachytiť prirodzené seed/reset volania, prvé RNG stavy a presné poradie callerov pri novej hre, DEMO a LOAD. Porovnať rovnaký seed v dvoch prirodzených behoch a určiť prvého odlišného spotrebiteľa; samotná zhoda LCG nestačí na deterministický gameplay. Pri zásahu sledovať RNG návrat, remainder a následné typové modifikácie až k zápisu cieľového stavu. DOSBox-X vykonanie zatiaľ chýba.
