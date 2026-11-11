# DOS 2.0 — presná lookup tabuľka a izolácia replay nesúladu

11. 11. 2026. PARTIAL, DEEP VERIFIED0 B, pôvodný runtime0. Nová dátová dávka je nezávislá od neuzavretého emulačného problému.

## Lookup interval

CS15BF:`[33B9,34B9)` = image **[18FA9,190A9)**, presne256 B. Končí pred už identifikovaným WORD timer_base=20000 na190A9. SHA-256 rozsahu `568d7faed5be48049f590ecffafe8d19ee504e06242f2f90bdf6de457d7bc05b`.

Spotrebiteľ na19273 načíta sample BYTE do AL, na19276 nuluje AH a pripočíta33B9h. Uloží výsledok do displacement operanda lookup load na1927F. Preto index v tejto lokálnej vetve pokrýva33B9h..34B8h bez16-bitového wrapu. Lookup BYTE sa pošle na port42h a potom sa pošle nulový horný BYTE. Hranice sú odvodené z rozsahu BYTE, presných strojových bajtov a indexovej konštanty; nejde iba o vizuálny odhad tabuľky.

Počiatočné výstupy sú neklesajúce, minimum0, maximum63, celkovo50 odlišných hodnôt. Prvých11 vstupov mapuje na0, posledných27 na63. Vynechané výstupné hodnoty sa nedopočítali interpoláciou. `dos_sample_lookup/lookup.csv` zachováva všetkých256 presných vstup/výstup položiek s image adresami; histogram a vlastnosti sú v summary.json.

Skutočný matematický generátor tabuľky, jej fyzikálna odozva na zariadení a globálna runtime nemennosť nie sú potvrdené. Názov je len sample-to-output lookup, nie identifikácia konkrétneho kompresného štandardu.

Reprodukcia: `python audit_dos_sample_lookup.py IMAGE OUT_DIR`. Skript kontroluje SHA obrazu aj úplné bajtové sekvencie indexovej a výstupnej vetvy. `data_intervals.csv` bol hashovo overený pri zlúčení do centrálnej partition. Nových256 B nemá konflikt s centrálnym kódom; výsledok je1 796 B kódu,808 B dát,168 756 B aktuálne neposúdených,74 intervalov,spolu171 360 B. Členstvo pôvodného PASS320 zostáva UNKNOWN.

## Reprodukovateľné spresnenie SMC nesúladu

Rozšírený `replay_dos_sample_irq.py` má explicitné režimy `continuous` a `single_instruction` ako voliteľný štvrtý argument po troch cestách. Neprepisuje počas vykonávania očakávaný sample offset, registre ani CF. Po príprave vstupného stavu zachytáva predinštrukčné address/CF/sample-offset stopy.

Pri prvom continuous prípade:

| Hook miesto | CF | sample offset pred inštrukciou |
|---|---:|---:|
| 19260 ADD fractional accumulator | 1 | 0100h |
| prvý hook19267 ADC patchovaného displacementu | 0 | 0100h |
| druhý hook19267 | 1 | 0100h |
| 1926E nasledujúce MOV AX | 0 | 0102h |

Očakávaný lokálny model po fractional step0 /integer step1 je0101h. Zdvojený hook **nie je dôkaz dvoch dokončených CPU inštrukcií**: samotný operand sa medzi týmito hookmi nezmenil. Stopa skôr ukazuje problém opätovného vstupu/flags stavu pri self-modifying translation, ale príčina v emulátore oproti harnessu ešte nie je definitívne izolovaná.

Pri single_instruction režime s `count=1` sa beh opakovane vracia na19267 bez dokončenia celej IRQ cesty. Po64 riadených krokoch skončí diagnostickým limitom; tento limit sa eviduje, nie ako úspešný návrat. Všetky tri pripravené prípady boli odskúšané oboma režimami. Ani jeden režim sa neprijal ako nové sémantické replay potvrdenie. Predchádzajúci súčet23 prijatých read/PIT replay prípadov sa nemení.

Výstupy sú `dos_smc_continuous/evidence.json` a `dos_smc_single_instruction/evidence.json`; obsahujú verziu Unicorn2.1.4, hash natívnej DLL, vstupy, všetky kontroly a stopy. Oba behy sú ukončené, nejde o čakajúce procesy.

## Nasledujúci krok

Minimalizovať jedinú samomodifikujúcu ADC inštrukciu v nezávislom diagnostickom programe, porovnať s variantom zapisujúcim mimo prekladaného kódu a s druhým emulátorom alebo DOSBox-X. Diagnostická zmena kódu musí byť označená ako zmena experimentu, nie ako originálny handler. Originálny runtime navyše musí overiť prefetch/instruction-fetch správanie a cleanup hranicu. Statické lookup dôkazy týmto blokátorom nezanikajú; DEEP VERIFIED sa neudeľuje.
