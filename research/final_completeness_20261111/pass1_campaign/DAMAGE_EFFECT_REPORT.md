# DOS 2.0: typovo modifikovaný náhodný účinok a signed/low-BYTE hranica

## Presné telo a dispatch dáta

FAR funkcia **083D:01C0** má obalový rozsah **[08590,086B3)**, 291 B. Prieskum CFG vrátane všetkých 20 indexovaných jump targetov dosiahne **86 inštrukcií / 241 B**. Jump table je **083D:0206..022E, obraz [085D6,085FE), 40 B / 20 WORDov**. Zvyšných 10 B v obale sa nepovažuje automaticky za padding ani kód. Inštrukcie sú byte-exact overené a nezávisle dekódované; každý table target je zahrnutý v prieskume.

Dispatch sa používa presne pre BYTE typy **12..31**, po odčítaní 12 a unsigned teste výsledku <=19. Ostatné typy obídu table vetvy. SHA 40 B tabuľky je `c94bbd84c3b5e670812494af0e91ae9e3b78444f9f46c7b7565ffbf56e8ad2b9`. Tabuľka leží mimo historickej NON-CODE baseline; pridala 40 B dát do celého centrálneho obrazu, nie do 57 295 B NON-CODE súčtu.

## Vstupy a základný výpočet

Druhý FAR argument na SS:[BP+0Ah]/[BP+0Ch] ukazuje na 28-bajtový objekt. Telo z neho číta WORD +18h a BYTE +6. Prvý FAR argument z rozhrania callerov táto funkcia nepoužíva. Ďalšie vstupy: BYTE DS:418F (selektor), WORD DS:4180 (modifikátor), WORD DS:626A (epizóda), WORD DS:4552 a globálny RNG.

```text
delta16 = WORD(object.word18 - DS:4552)
v = signed16(WORD((delta16 << 3) + native_rand()%25))
v = type_modifier(v, object.byte6, selector, episode)
if DS:4180 == 2: v = arithmetic_shift_right(v,1)
else if DS:4180 == 0: v = signed16(WORD(v*2))
AX = v > 255 ? 255 : WORD(v)          # signed porovnanie
return FAR
```

Základný typový metric sa nedeklaruje automaticky ako vzdialenosť. Jeho prirodzený význam a rozsah závisia od producerov WORDu +18h a DS:4552. RNG návrat 0..32767 dáva zvyšok 0..24; funkcia ho spotrebuje pred type dispatchom, aj keď vetva následne vynuluje v alebo použije konštantu. Reálna callback vetva môže mať vlastné RNG efekty; v tomto teste je callback nahradený.

## Všetky typové modifikátory

`v >> n` znamená signed aritmetický posun. Čísla typov a selektorov sú desiatkové. Rozdelenie je pred globálnou úpravou DS:4180.

| Typ | Modifikácia |
|---|---|
| mimo 12..31 | v bez zmeny |
| 12,29 | v >> 3 |
| 13 | selektor 1: >>1; ostatné: >>3 |
| 14,17,20 | selektor 2: >>1; ostatné: >>3 |
| 15,16 | selektor 1: >>8; ostatné: >>1 |
| 18,19 | >>2 |
| 21 | callback 0D29:0750 s FAR textom z DS:1068; potom v=0 |
| 22 | epizóda 3: v=3; inak v=0 |
| 23 | selektor 1: >>8; ostatné: >>2 |
| 24 | selektor 1: >>8; selektor 2: >>4; ostatné: >>3 |
| 25 | v=0 |
| 26 | selektor 1: >>1; ostatné: v=0 |
| 27,28 | >>1 |
| 30 | selektor 1: v=0; ostatné: >>3 |
| 31 | selektor 1: v=0; ostatné: >>2 |

Plné identity týchto typov, bossov, zbraní a význam stavového WORDu 4180 sa neuzatvárajú len podľa multiplikátorov. `dispatch_table.csv` uchováva každý typ, pôvodnú table adresu, target a SHA WORDu.

## Orezanie a caller low BYTE

Porovnanie s 255 je signed a má iba horné orezanie. Záporné v sa neprevedie na nulu; modulo pretečenie môže vzniknúť už v počiatočnom SHL alebo finálnom zdvojení. Konkrétny prijatý prípad typ=0, selektor=0, DS:4180=1, delta=−33, rand remainder=0 vracia **AX=FEF8h (−264)**. Nie je to kladné 255 ani nula.

V overenom caller fragmente **04C7:1320..1333** sa AH vynuluje, výsledok sa uloží ako WORD a porovná s zero-extended BYTE cieľa +10h. Ten istý prípad preto caller spotrebuje ako **248**. Keď cieľový BYTE nie je väčší, pred ďalšími vetvami sa vynuluje. Nadväzujúce zásahové/úmrtné efekty, neletálna vetva a finálne health správanie celej 04C7:1304 zostávajú otvorené.

`consumer_context.csv` pripína tento fragment a začiatok vetvy 13D8; ide o statický dôkaz, nie replay celého health updatera. Šiesty riadok centrálneho `record_field_refinements.csv` spresňuje +10h v 26-bajtovom recorde. Záporné metric vstupy a pretečenia v matici sú syntetické; ich prirodzená herná dostupnosť nie je potvrdená a nevyhlasuje sa z nich chyba hry.

## Controlled replay a reprodukcia

`audit_replay_damage_effect.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT` vykonáva pôvodnú celú funkciu a pôvodný RNG vrátane multiply helpera. Len callback 0D29:0750 pre typ 21 je nahradený RETF. EXEPACK relokácie sa aplikujú pri dvoch load bázach.

Hlavná matica: typy 0,11,12..31,32,255; selektory 0..3; control 0/1/2; epizóda 1; raw delta −4096,−33,−1,0,1,32,4095,4096; všetkých 25 RNG zvyškov. Pridáva sa vetva typu 22 pre epizódy 2/3, vybrané delta a control hodnoty. Pre každý zvyšok sa použije seed, ktorého skutočný native RNG krok tento zvyšok vytvorí.

Spolu **116 100 prípadov, 0 odchýlok** voči explicitnému 16-bit modelu. Overuje sa AX, aktualizovaný skutočný RNG DWORD, počet callbackov a návratové BP/SI/DI/DS/SP v modeli. Matica obsahuje 45 512 záporných WORD výsledkov a 4 800 mock callback volaní; nie sú to počty prirodzených herných udalostí ani sémantické percentá. Nie sú exhaustívne všetky WORD metric vstupy, selektory a control hodnoty. Nepokryté control hodnoty majú staticky spoločnú nezmenenú vetvu, ktorú tento test osobitne neseeduje.

Artefakty `damage_effect_replay/`: `instructions.csv`, `dispatch_table.csv`, `cases.csv`, `consumer_context.csv`, `consumer_field_roles.csv`, `summary.json`. SHA-256 finálneho case dumpu: `14225766bbeecb39af4d3b96b5f904d86a464bacf23fb733457d08aa4713c20c`. Opakovaný beh po doplnení statického consumer dôkazu mal rovnaký SHA; nepripočítava sa druhýkrát.

## Pokrytie

NON-CODE mapa zostáva **54 986 B PARTIAL, 2 265 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, presne 57 295 B, v `pass1_rng/`. Nových 40 B dispatch dát je mimo baseline a nemení jej súčet.

Centrálny katalóg: **62 rozsahov, 2 167 inštrukcií / 5 348 B kódu**, **55 872 B typovaných dát celého obrazu**, šesť record field spresnení. Controlled replay súčet je 276 303 plus samostatne 65 548 normalizačných prefixových prípadov. Prirodzené runtime testy 0. Celý damage/health/caller subsystém zostáva PARTIAL. GitHub commit 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika sémantického percenta: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú; nové percentá sú N/A a predošlé orientačné.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | typový BYTE a metric WORD spotreba | producer význam | object constructor |
| Dátové typy a konštanty | 95 % | N/A | low BYTE consumer a signed hodnoty | prirodzené metric rozsahy | writeri +18h/4552 |
| Tabuľky a ukazovatele | 93 % | N/A | 20 WORD dispatch tabuľka, 40 B | typové identity | producer typov |
| Funkcie / ASM / CFG | 90 % | N/A | 241 B / 86 inštrukcií | callback a celí calleri | health updater |
| RNG | 97 % | N/A | všetkých 25 zvyškov s native RNG | callback RNG efekty | prirodzené stopy |
| Scheduler | 96 % | N/A | bez nového časového dôkazu | poradie akcií | tick stopa |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | seed/call ordering | DEMO stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping | render stopa |
| GUARD / bossovia | 93 % | N/A | typové modifikátory a target scalar | smrtiace/neletálne vetvy | 04C7:1304 zvyšok |
| Zbrane / projektily | 92 % | N/A | úplná lokálna effect aritmetika | prirodzené vstupy a identity | upstream metric |
| Sprity / HUD / paleta | 92 % | N/A | callback vetva typu 21 | reálny text/pixely | 0D29:0750 |
| SAVE / LOAD | 92 % | N/A | metric/counter stavové väzby | invarianty po LOAD | serializačné rozsahy |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | effect parity | Win typový dispatch |

## Runtime testy na vykonanie

Pri prirodzenom zásahu zachytiť object +6/+18h, DS:4552/418F/4180/626A, RNG stav a návrat AX. Sledovať následný low BYTE a cieľový BYTE +10h až do smrtiacej/neletálnej vetvy. Overiť rozsahy raw delta a či v prirodzenom behu vôbec vznikajú záporné/pretečené výsledky. Typ 21 zachytiť bez mock callbacka vrátane prípadných ďalších RNG spotrieb. DOSBox-X vykonanie zatiaľ chýba.
