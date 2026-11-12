# DOS 2.0: akčný dispatcher, 26/28-bajtové záznamy a otvorené poškodenie

## Funkcia a hranice

Rutina **0637:05FC**, ktorú po nenulovom gate AL volá 06B0:0B5B, má obalový rozsah **[0696C,06A6F)**, 259 B. CFG od vstupu dosiahne **87 inštrukcií / 256 B**. Tri bajty za koncovými alebo nepodmienenými vetvami sa do kódu nepridávajú. Každá dosiahnutá hranica a bajty sú porovnané s kanonickým obrazom a nezávislým dekóderom.

Je to dispatch/skenovací obal akcie, nie dôkaz celej balistiky alebo výpočtu damage. Predikát 0AEA:0CC0, record-action 04C7:1304 a alternatívny helper 07ED:000E zostávajú externé kontrakty. Interpretácia prvej vetvy ako priameho zásahu a druhej ako projektilovej vetvy je pracovná hypotéza, nie v tejto dávke uzavretá gameplay identita.

## Presný riadiaci postup

```text
if BYTE DS:418F == FFh: return
if BYTE DS:4198 != 0:
    call 0D29:2740()
    return
if WORD DS:4190 == 1:
    if AL(call 083D:0B42()) == 0: return
    i = 0; actor = FAR 21FD:264E
    if signed16(DS:6276) > 0:
        repeat:
            if DWORD actor[2] == DWORD DS:4540
               and BYTE actor[0Bh] not in {0,9,10}:
                j = signed16(WORD actor[8])
                object = FAR 21FD:WORD(6 + 28*j)
                dx = WORD((signed16(object[10h]) >> 6) - WORD DS:415E)
                dy = WORD((signed16(object[12h]) >> 6) - WORD DS:4160)
                if AL(call 0AEA:0CC0(DS:415E, DS:4160, dx, dy, 16, 1)) != 0:
                    call 04C7:1304(actor_far_pointer, object_far_pointer)
            actor.offset += 26
            i++
        while signed16(i) < signed16(current WORD DS:6276)
else if WORD DS:4190 == 2:
    if AL(call 07ED:000E()) == 0: return
else:
    return
call 04C7:08A0(zero_extend(BYTE DS:4188))
call 083D:1816()
BYTE DS:419A = 1
return
```

Zápisy/posuny v pseudokóde zachovávajú 16-bit offsety a signed SAR/porovnania. Pojmy dx/dy sú relatívne hodnoty podľa priamo doloženej aritmetiky; jednotky a plný geometrický význam predicate sa nepredpokladajú iba z delenia 64.

Po kladnom permission volaní sa spoločné záverečné efekty vykonajú aj pri nulovom alebo zápornom počte záznamov, pri samých filtrovaných záznamoch či pri všetkých nekladných predicate výsledkoch. Záverečná vetva teda lokálne nie je podmienená aspoň jedným record-action zásahom. Neznamená to automaticky spotrebu munície alebo prehratie zvuku: plné efekty oboch final helperov zostávajú otvorené.

## Typové spresnenie už klasifikovaných polí

| Záznam | Offset | Šírka | Doložená rola |
|---|---:|---:|---|
| 26 B, základňa 21FD:264E | +02h | DWORD | porovnanie rovnosti s DS:4540 |
| 26 B | +08h | WORD | signed index pri výpočte `6+28*j` |
| 26 B | +0Bh | BYTE | vylučujú sa stavy 0,9,10 |
| 28 B, základňa 21FD:0006 | +10h | WORD | signed SAR 6 a odčítanie DS:415E |
| 28 B | +12h | WORD | signed SAR 6 a odčítanie DS:4160 |

FAR základne zodpovedajú už typovaným oblastiam `[2461E,25046)` pre nominálne 100×26 a `[21FD6,2461E)` pre nominálne 350×28. Táto dávka **nedokazuje** horný limit počtu ani rozsah prepojeného indexu v prirodzenej hre. Telo nedáva explicitný guard na záporný/out-of-range j; 16-bit výpočet môže wrapnúť. Počet DS:6276 sa navyše načítava znovu po každej iterácii, takže callee zápis môže zmeniť priebeh slučky. V mock modeli sa počet nemení.

`record_field_roles.csv` pridáva päť sémantických spresnení existujúcich dát, nie nové bajty. Centrálny `campaign_catalog/record_field_refinements.csv` ich pripája s SHA zdrojového CSV. Samotný dispatcher nepoužíva health pole ani nepočíta damage hodnotu; názov record-action nepredstiera uzavretie týchto častí.

## Controlled replay a reprodukcia

`audit_replay_action_dispatch.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT` overí SHA, pôvodné inštrukcie a aplikuje EXEPACK relokácie. Pri dvoch load bázach vykoná **110 prípadov, 0 odchýlok**: disabled selektor, special flag, neaktívne modes, permission nula, alternatívny helper nula/nenula a sady záznamov s nulovým/záporným počtom, mismatch DWORDu, predicate false, stavmi 0/1/2/3/9/10/FFh a zmiešanými piatimi záznamami.

Sedem callees je výslovne nahradených RETF/hook modelom. Overuje sa úplné poradie volaní, šesť WORDov predicate argumentov, oba FAR pointery record-action, final argument z DS:4188, výsledný BYTE DS:419A a obnova BP/SI/DI/DS/SP v modeli. Mocky neimplementujú geometrickú predicate, damage, projektil ani zmeny počtu záznamov. Reálne record/object dáta sú seedované, nie zachytené z hry.

Výstupy `action_dispatch_replay/`: `instructions.csv`, `cases.csv`, `callee_trace.csv`, `record_field_roles.csv`, `summary.json`. Celý dispatcher zostáva PARTIAL z hľadiska gameplay parity. Prirodzený DOSBox-X test sa nevykonal.

## Pokrytie

NON-CODE mapa sa nemení: **54 982 B PARTIAL, 2 269 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57 295 B, aktuálna mapa v `pass1_action_gate/`. Päť rolí prekrýva už typované záznamy a nepočíta sa ako ďalšia byte coverage.

Centrálny katalóg: **56 rozsahov, 2 031 inštrukcií / 4 983 B kódu**, 55 828 B typovaných dát celého obrazu. Controlled replay súčet je 24 871 plus osobitne 65 548 normalizačných prefixových prípadov. Prirodzené runtime testy zostávajú 0. GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto novú dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového sémantického percenta: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú; nové percentá sú N/A a predošlé orientačné. Nové rolové spresnenia sú PARTIAL, nie DEEP VERIFIED.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | record DWORD filter | význam filtra | jeho produceri |
| Dátové typy a konštanty | 95 % | N/A | päť record field rolí | prirodzené domény | writeri polí |
| Tabuľky a ukazovatele | 93 % | N/A | 26→28 B prepojenie | bounds j/count | constructor/LOAD |
| Funkcie / ASM / CFG | 90 % | N/A | 256 B / 87 inštrukcií, 110 prípadov | sedem callee kontraktov | predicate a record-action |
| RNG | 97 % | N/A | dispatcher sám RNG nečíta | RNG v callee | damage výpočet |
| Scheduler | 96 % | N/A | poradie a finalizácia bez cieľa | prirodzené časovanie | call stopy |
| DEMO a vstupy | 96 % | N/A | väzba gate→dispatcher | prirodzené modes | vstupné prechody |
| Renderer / VGA | 94 % | N/A | setter DS:419A pre polohový wrapper | celý feedback efekt | prirodzený render |
| GUARD / bossovia | 93 % | N/A | filtre 0/9/10 a prepojený objekt | AI/damage algoritmus | 04C7:1304 |
| Zbrane / projektily | 92 % | N/A | dve dispatch vetvy a argumenty | geometria/projektil/damage | 0AEA:0CC0, 07ED:000E |
| Sprity / HUD / paleta | 92 % | N/A | spoločný feedback BYTE | reálny asset a pixely | descriptor producer |
| SAVE / LOAD | 92 % | N/A | mutable record count a indexy | stav po LOAD | serializačné invarianty |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | akčná parity | Win dispatcher |

## Runtime testy na vykonanie

Pri prirodzenej akcii zachytiť modes, permission, record count, DWORD filter, prepojené indexy, predicate argumenty a skutočné record-action účinky. Osobitne akciu bez cieľa a pri vylúčených stavoch. Overiť, či callee mení count alebo prepojenie, a zmerať súvisiaci feedback DS:419A. Syntetické záznamy v replay nenahrádzajú prirodzené zásahy či poškodenie. DOSBox-X vykonanie zatiaľ chýba.
