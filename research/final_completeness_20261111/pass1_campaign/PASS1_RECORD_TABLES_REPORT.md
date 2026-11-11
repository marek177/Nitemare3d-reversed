# PASS1 — tri runtime tabuľky v pôvodne nulovej FAR oblasti

11. 11. 2026. **PARTIAL**, nové DEEP VERIFIED0 B, nové runtime/replay testy0. Dávka pridáva1678 B konkrétnych tabuliek a počítadiel z pôvodného UNKNOWN priestoru; vnútorné polia záznamov nie sú všetky uzavreté.

## Segmentová proveniencia

Lookup rutiny pri image0000h,0052h a00A4h explicitne nastavujú segment21FDh. Immediate WORDy na0005h,0057h a00AAh patria do skutočného EXEPACK relocation inventára. Konštruktor18 B záznamu používa rovnaké relokované slovo na0278h. Globálna segmentová premenná pri defaultDS:2556h, image29C66h, má takisto relokované počiatočné WORD21FDh; nie je FAR pointerom sama osebe.

V nerelokovaných súradniciach je báza bloku **21FD0h**, pred default DS27710h. Pri load segmenteL treba dosadiťL+21FDh. Lookup rutiny túto bázu nezískavajú iba domnienkou o incomingDS: samy ju nastavujú. Producenti, ktorí čítajú defaultDS:2556h, majú navyše predpoklad správneho incoming defaultDS a platnej segmentovej premennej. Globálne writeri tejto premennej ešte nie sú uzavretí.

## Presné polia a rozsahy

| Objekt | Segment:offset end-exclusive | Image end-exclusive | Bajty |
|---|---|---|---:|
| count18 | 21FD:0000..0002 | 21FD0h..21FD2h | 2 |
| count14 | 21FD:0002..0004 | 21FD2h..21FD4h | 2 |
| count6 | 21FD:0004..0006 | 21FD4h..21FD6h | 2 |
| table18,64 nominálnych slotov | 21FD:3076..34F6 | 25046h..254C6h | 1152 |
| table14,32 nominálnych slotov | 21FD:34F6..36B6 | 254C6h..25686h | 448 |
| table6,12 nominálnych slotov | 21FD:36B6..36FE | 25686h..256CEh | 72 |

Všetky tieto file-backed bajty sú v kanonickom obraze nuly. Sú však referencované ako zapisované dátové štruktúry, nie potvrdený padding. Počiatočné počty sú0;108 je počet **nominálne rezervovaných slotov**, nie počet aktívnych záznamov. Tabuľky18/14 na seba nadväzujú presne, bez odhadnutej medzery.

## Dôkazy veľkosti a nominálnej kapacity

- Pri0255h je porovnanie count s40h, pri026Bh násobenie count×12h a pri026Fh pripočítanie3076h. Producent potom inkrementuje count a začína inicializovať rekord. Lookup na002Ch zvyšuje pointer o12h a používaWORD polia+4/+6 ako porovnávaný pár.
- Pri0442h je porovnanie count s20h; aritmetika0458h..0467h vytvorí count×14+34F6h. Lookup na007Eh zvyšuje pointer o0Eh a porovnávaWORD polia+8/+0Ah.
- Pri0548h je porovnanie count s0Ch;0562h..056Eh vytvorí count×6+36B6h. Lookup na00D5h zvyšuje pointer o6. WORD+0 používa ako index ďalšieho28 B záznamového priestoru; BYTE+4 producent nuluje. Význam ostatných polí ešte nie je rekonštruovaný.

Pri count>=kapacita kód volá error helper0FBA:000C a potom má pokračovanie k výpočtu adresy. **Neoverili sme, že helper nikdy nevráti riadenie.** Preto kapacity64/32/12 sú doložené nominálne rezervácie a guard hodnoty, nie globálny dôkaz bezpečného indexovania pri všetkých stavoch. Pokračovanie po chybe alebo poškodený count môže narušiť hranice; prirodzená dosiahnuteľnosť nie je potvrdená.

Časť count porovnaní používa signed vetvy. Typ počítadla je WORD so signed porovnávacou spotrebou, nie automaticky bezpodmienečne ohraničený unsigned počet. Kompletný lifecycle a všetci writeri zostávajú otvorení.

## Algoritmický kontrakt

Zjednodušený lokálny producent:

```text
if signed(count) >= nominal_capacity:
    error_helper(...)   // non-returning contract not closed
record = segment21FD:(table_base + stride*count)
count++
initialize observed record fields
```

Lookup pre18/14 B tabuľku postupuje od doloženej bázy po stride a porovnáva dveWORD hodnoty s argumentmi. Na zhode vraciaFAR adresu rekordu cezDX:AX. Na nenájdení prejde do error vetvy. Pred návratom prepneDS cezPUSH SS/POP DS, teda neobnovuje ľubovoľný pôvodnýDS; očakávaný SS/default-DS ABI treba posudzovať osobitne.

Tieto dôkazy potvrdzujú layout `record_bytes[capacity][stride]`, nie sémantický názov každého poľa ani úplnú zhodu s konkrétnym gameplay typom. Názvy `table18/14/6` sú zámerne technické, kým sa neuzavrú ďalší spotrebitelia.

## Artefakty a reprodukcia

`python audit_pass1_record_tables.py IMAGE RELOCATIONS_CSV PRIOR_PASS1_MAP ABSOLUTE_DECODER_DIRECTORY OUT_DIR` overuje hash obrazu, relokované segmentové slová, kritické guard/stride bajty, nulový počiatočný obsah a prienik s predchádzajúcou mapou.

`pass1_record_tables/` obsahuje `tables.csv`, `data_fields.csv`, `records.csv` (108 presných nominálnych záznamových hraníc), `evidence_instructions.csv` (šesť presne dekódovaných lookup/producer okien), `noncode_intervals.csv` a `.json`, `summary.json`. Inštrukčné okná nie sú potichu označené za uzavreté celé funkcie. Nulové/zarovnávacie bajty medzi staršími lookup funkciami sa do kódu nepridávali.

## Pokrytie

| Stav PASS1 | Predchádzajúca dávka | Aktuálne |
|---|---:|---:|
| PARTIAL | 306 B | **1984 B** |
| CLASSIFIED ONLY | 9649 B | 9649 B |
| UNKNOWN | 47340 B | 45662 B |
| DEEP VERIFIED | 0 B | 0 B |

Metodika:1152+448+72+6=1678 jedinečných bajtov, všetky predtýmUNKNOWN; žiadny prekryv s predchádzajúcimi relokačnými WORDmi či key-label objektmi. Nová266-intervalová mapa pokrýva presne57295 B. PARTIAL vyjadruje layout a konkrétnych producentov/spotrebiteľov; úplné field kontrakty chýbajú.

Centrálny lokálny katalóg po samostatnom zlúčení má2580 B dát a2609 B kódu;1732 B dátovej únie patrí pôvodnému NON-CODE. Tento súčet sa nesčítava s1984 B PASS1, pretože sa vrstvy prekrývajú. Prijaté controlled replay prípady zostávajú47; percentá13 oblastí N/A.

Ďalší krok: uzavrieť konkrétne polia a plnenie troch rekordových layoutov, non-returning kontrakt error helpera a bounds prirodzených count hodnôt; následne identifikovať väčší28 B priestor, na ktorý odkazuje table6. Tak sa bude zmenšovať aj zvyšná FAR nulová oblasť bez premenovania všetkých núl na padding/BSS.
