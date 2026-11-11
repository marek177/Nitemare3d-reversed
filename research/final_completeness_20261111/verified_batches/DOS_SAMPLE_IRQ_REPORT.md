# DOS 2.0 — samomodifikujúci sample IRQ handler

11. 11. 2026. **PARTIAL**. Nový handler image `[19241,192D2)`:145 B/59 inštrukcií, dva IRET konce. Nové DEEP VERIFIED0 B, originálny runtime0. Pokusy o nový replay neboli prijaté ako sémantické potvrdenie.

## Operandy ako dátová vrstva

`audit_dos_sample_irq.py` kontroluje identitu obrazu a pre každé pole používa encoded constant offsets nezávislého dekódera. Nasledujúce WORD polia patria **do inštrukcií**:

| CS offset / image | Úloha | Vlastník |
|---|---|---|
| 366C /1925C | end offset | immediate CMP na19257 |
| 3675 /19265 | fractional step | immediate ADD na19260 |
| 367C /1926C | integer step | immediate ADC na19267 |
| 367F /1926F | sample segment | immediate MOV AX na1926E |
| 3684 /19274 | sample offset | displacement MOV AL na19273 |
| 3691 /19281 | lookup address | displacement CS MOV AL na1927F |

Všetky majú v kanonickom obraze5555h, ale doložené fixné CS zápisy ich menia. Šesť polí /12 B sa eviduje v `operand_overlays.csv`, **nepripočítava sa k disjunktným DATA bajtom**. Samostatný fractional accumulator CS:364F..3651 = image1923F..19241 je2 B mimo handler kódu. Počiatočná hodnota0. Štrnásť fixných pamäťových referencií je v `fixed_cs_xrefs.csv`; indexed/alias zápisy nie sú globálne vylúčené.

## Statický algoritmus

Handler uloží AX,DS a nastaví DS=CS. Od DWORD CS:2C4B/2C4D odčíta64; výsledný borrow pripočíta do BYTE CS:2C53. Potom porovná aktuálny sample offset s end offset; pri offset>=end prejde do cleanup vetvy19290.

Na normálnej vetve pripočíta fractional step do samostatného WORD accumulátora. Carry prenesie cez ADC spolu s integer step do **vlastného displacement operanda** sample offset. Nastaví DS na patchovaný sample segment, načíta BYTE z patchovaného offsetu a vytvorí lookup adresu33B9h+unsigned_sample. Tú uloží do ďalšieho vlastného displacement operanda a načíta lookup BYTE cez CS.

Následne OUT42h=lookup_byte, OUT42h=0, OUT20h=20h; obnoví DS,AX a IRET. Kontrola konca predchádza posunu offsetu a načítaniu. Staticky teda neobsahuje druhý bounds test po integer/carry kroku. Skutočné limity vstupov, prípadné sentinel bajty a prirodzený presah bufferu ešte nie sú potvrdené.

Cleanup uloží DI, obnovuje časovač cez466A s CS:2C49, upraví port61h, zapisuje uložený WORD na42h, nuluje active flagCS:2DCA, obnovuje predchádzajúci vektor08h cez INT21 a končí EOI/IRET. Presný DOS/interrupt reentrancy kontrakt zostáva otvorený. Úplný FLAGS/segmentový kontrakt nie je uzavretý, pretože cleanup volá externé služby a ďalší helper.

## Neprijaté replay pokusy

`replay_dos_sample_irq.py` pripravil tri syntetické normálne IRQ stavy s patchovanými operandmi a konvenčným IRET frame. Zaznamenal návrat a portové výstupy, ale sémantické assertions sa nezhodovali. Pri prvom prípade offset0100h, integer step1 a fractional step0 bol očakávaný patchovaný offset0101h; pozorovaný bol0102h a iná lookup adresa.

Ide o konkrétny **rozpor replay s lokálnym statickým modelom**. Možnou príčinou je translation-cache/self-modifying správanie Unicorn alebo chyba harnessu; príčina nie je izolovaná. Rozpor sa nesmie prezentovať ako správanie originálneho procesora ani ako potvrdený dvojnásobný krok hry. Všetky tri pokusy majú accepted_cases=0; súčty23 predchádzajúcich riadených replay prípadov sa nemenia. Evidencia zachováva očakávané aj pozorované polia, kontroly, vstupy a hash natívnej knižnice v `dos_sample_irq_replay/evidence.json`.

Najbližší reprodukčný krok je kontrola jedného ADC a následného instruction fetch v režime jednotlivých inštrukcií, prípadne druhým emulátorom; nesmie sa manuálne vnútiť očakávaný offset a potom tvrdiť úspešný replay. Originálny DOSBox-X test má navyše overiť skutočne patchovaný kód a CPU/prefetch model.

## Katalóg a ďalšia práca

Reprodukcia statiky: `python audit_dos_sample_irq.py IMAGE HISTORICAL_INSTRUCTIONS ABSOLUTE_DECODER_DIRECTORY OUT_DIR`. Reprodukcia otvoreného replay problému: `python replay_dos_sample_irq.py IMAGE UNICORN_DIRECTORY OUT_DIR`.

Po nezávislom zlúčení:20 kandidátnych rozsahov,785 inštrukcií/1 796 B,552 B disjunktných dát,169 012 B v tejto kampani neposúdených,73 intervalov. Dvanásť overlay bajtov je zahrnutých v kóde a nemení dátovú úniu. Pôvodné PASS320 členstvo UNKNOWN, nové percentá N/A.

Ďalšia statická práca: uzavrieť spotrebu fixed-point krokov pri všetkých init vetvách, bounds a umiestnenie sample-to-output lookup tabuľky. Runtime: logovať patchované operandy, prvé a posledné čítanie sample bufferu, port42h, countdown borrow a cleanup vetvu. Žiadny z týchto výsledkov zatiaľ nie je originálny runtime dôkaz.
