# Audio dáta a ohraničené funkcie medzi verziami

11. 11. 2026. PARTIAL, nové DEEP VERIFIED0 B, runtime testy0. Presné porovnanie skutočných EXE v hash-pinned archíve, nie prevzatie textových ASM názvov.

## Rozsah a identita vstupov

`compare_dos_audio_regions.py` používa archív `N3D_ALL_VERSIONS_ASM.zip`, SHA-256 `b0e8b4d81cfbce9dcab4ee432aee6320080c35f6181fec8c585d4b7970a2bdb3`. Pre každý DOS label overí packed EXE hash, znovu vykoná statické EXEPACK rozbalenie s roundtrip kontrolou a overí výsledný image hash podľa predchádzajúcej vstupnej dávky. Osem labelov1.0,1.1,1.2,1.5,1.7,1.8,1.9,2.0 predstavuje sedem jedinečných EXE;1.8 a1.9 sú v dodanom archíve identické. Label nie je nezávislé datovanie vydania.

## Lookup tabuľka

Všetkých osem obrazov obsahuje presne rovnakých256 B na zodpovedajúcej pozícii knižnice. SHA-256 `568d7faed5be48049f590ecffafe8d19ee504e06242f2f90bdf6de457d7bc05b`. Zodpovedá to28/28 párových zhodám tejto tabuľky. Susedný počiatočný timer_base je20000 vo všetkých ôsmich labeloch. `audio_cross_version/tables.csv` obsahuje presné image hranice a hodnoty pre každý build.

Ide o zhodu dodaných inicializačných dát, nie dôkaz nemennosti počas behu ani rovnakej prirodzenej playback cesty.

## Štyri kódové úseky

Porovnané rozsahy vzhľadom na library base a delta0/4:

| Úsek | DOS2.0 CS offset | Dĺžka | Inštrukcie |
|---|---|---:|---:|
| sample_irq | 3651h | 145 B | 59 |
| pit_divisor_setter | 466Ah | 53 B | 29 |
| callback_setter | 389Ah | 13 B | 5 |
| timer_base_setter | 34BBh | 6 B | 2 |

112 porovnaní =4 úseky ×28 build párov. Bez transformácie je zhodných48/112; po explicitnej normalizácii112/112. Porovnáva sa celý bajtový úsek, nie iba opcode podpis.

Normalizácia má dve pravidlá: od fixného16-bitového CS memory displacementu odpočíta build delta; pre konkrétny sample_irq ADD AX,lookup_base prevedie33B9h+delta na33B9h. Každá z76 vykonaných zmien je v `normalization_patches.csv`, vrátane pôvodnej/novej hodnoty a pozície. Delta0 verzie sa nemenia. Relatívne skoky a CALL displacements sa nemenia, pretože porovnávaný lokálny layout má spoločný posun.

**Výnimka je presná a sémanticky podložená:** sample_irq displacement pri region offset40h patrí runtime patchovanému CS load, nie statickému build pointeru. Musí zostať5555h. Parser overuje vlastnícku inštrukciu na region offset3Eh a sentinel5555h. Prvý pokus s nerozlíšením tohto poľa vytvoril16 falošných rozdielov; po oprave sa neprezentujú ako verzionálna odchýlka. Ostatné immediate5555h zostávajú takisto nezmenené.

Zhodné inštrukčné sekvencie a relatívne vetvy podporujú rovnakú lokálnu statickú štruktúru týchto úsekov. **Neuzatvárajú** ich callerov, pointerové ciele, externé implementácie ani runtime správanie. Nepreukazuje sa tým celé WORX parity ani gameplay parity.

## Win1.10

Overený Win EXE hash `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`. Presná256 B tabuľka sa hľadala v každom zo šiestich súborom podložených NE segmentov1,2,3,4,7,10, spolu211 916 B payloadu. Výsledok:0 presných výskytov. Veľkosti a file offsety skenovaných segmentov sú v summary.json, prázdny result CSV má hlavičku.

Táto negatívna kontrola nevylučuje výpočet tabuľky pri behu, transformované dáta, resources mimo skúmaných payloadov ani iné Windows audio rozhranie. DOS tabuľka sa Win16 adresám nepriradila. Žiadne percento Win16 parity z toho nevzniká.

## Reprodukcia a pokračovanie

`python compare_dos_audio_regions.py ASM_ZIP DOS_BUILDS_CSV ABSOLUTE_DECODER_DIRECTORY OUT_DIR`. Výstupy `tables.csv`, `regions.csv`, `normalization_patches.csv`, `pairs.csv`, `win110_exact_matches.csv`, `summary.json` zachovávajú hranice, raw aj normalized SHA a všetky porovnania.

Centrálny DOS2 katalóg sa nemení:1 796 B kódu/808 B dát. Nové percentá N/A; chýba pôvodný PASS320 ledger. Ďalší krok: mapovať konkrétnych callerov týchto úsekov medzi verziami a vo Win16 sledovať skutočné audio importy a buffer formát. Runtime pôvodného sample_irq ostáva otvorený aj pre známy emulačný SMC nesúlad.
