# PASS1: CRT stream záznamy a inkluzívny koniec

## Rozsah a typ

SHA-256 obrazu: `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Default DS=2771h. Počiatočné pole leží v DS:217A..221A, obraz `[2988A,2992A)`, 160 B. WORD DS:22BA, obraz `[299CA,299CC)`, obsahuje **2212h, adresu posledného záznamu**, nie exkluzívny koniec. Preto počet je `(2212h-217Ah)/8+1 = 20`.

Dôkaz tvorí `MOV SI,217Ah` na 12BB4, `ADD SI,8` na 12BDB a `CMP [22BAh],SI; JB exit` na 12BDE/12BE2. Prvé porovnanie predchádza spracovaniu prvého záznamu. Posledný slot pri rovnosti ešte prejde. Rozsah medzi 221Ah a 22BAh sa týmto dôkazom nepovažuje za ďalšie stream sloty.

Prvých päť záznamov má BYTE +7 postupne 0,1,2,3,4 a BYTE +6 hodnoty 01h,02h,02h,84h,02h. Zvyšných pätnásť je počiatočne nulových. Identita konkrétnych DOS štandardných zariadení nie je iba z týchto čísel uzavretá. Záznam index 3 má WORD +0 a +4 rovné 2233h; zatiaľ ich neoznačujem za úplne uzavreté buffer pointer kontrakty.

Spotrebiteľ `11EE:0BFC` používa pri nenulovom vstupnom NEAR pointeri BYTE záznamu +7 ako zero-extended argument ďalšieho helpera. Príbuzný záznam nájde transformáciou `record_offset - 217Ah + 221Ah`, v ňom testuje bit 40h. To podporuje stream/handle interpretáciu, ale neurčuje ešte úplný význam paralelnej tabuľky ani všetkých flagov.

## Iterátor 11EE:0CCC

Ohraničený kód `[12BAC,12C15)` sa nezávisle dekóduje. ABI: NEAR volanie, WORD mode v SS:[BP+4], `RET 2`; vstupy DS a počiatočný obsah tabuľky, výstup AX. Zachová SI/DI/BP; helpery môžu meniť záznamy. Volaný FAR helper je `11EE:0BFC`, argumentom je NEAR pointer na slot, caller odstráni jeho 2 B argument.

```text
si = 0x217a
successes = 0
error = 0
while unsigned(si) <= WORD_DS[0x22ba]:
    flags = BYTE_DS[si + 6]
    if mode == 1:
        if flags & 0x83:
            if helper_0bfc(si) != 0xffff: successes += 1
    elif mode == 0:
        if flags & 0x02:
            if helper_0bfc(si) == 0xffff: error = 0xffff
    si = (si + 8) & 0xffff
return successes if mode == 1 else error
```

Pseudokód zachováva pozorovanú unsigned koncovú podmienku a 16-bitové inkrementy. Neobvyklá runtime zmena end pointera môže viesť k odlišnému rozsahu alebo wraparound; nemennosť DS:22BA ani všetkých pomocných volaní nie je dokázaná. Wrapper `11EE:0CC4` vloží mode=1, zavolá NEAR 0CCC a vráti sa FAR callerovi. Iná vetva helpera 0BFC pri nulovom pointeri volá mode=0. Táto rekurzívna väzba sa neaktivuje pre počiatočné nenulové slot offsety, ale globálna reentrancia zostáva otvorená.

## Pokrytie a reprodukcia

Vstupná mapa `pass1_crt_cleanup/noncode_intervals.csv`: PARTIAL 11 841 B, CLASSIFIED ONLY 9 592 B, UNKNOWN 35 862 B. Výstup `pass1_crt_streams/`: **PARTIAL 12 003 B, CLASSIFIED ONLY 9 430 B, UNKNOWN 35 862 B, DEEP VERIFIED 0 B**. Prírastok 162 B prešiel z CLASSIFIED ONLY do PARTIAL; súčet je presne 57 295 B.

`audit_pass1_crt_streams.py IMAGE PRIOR_MAP DECODER_DIR OUT` overuje identitu obrazu, rozhodujúce kódové bajty, počiatočný end pointer, SHA vstupných intervalov a súčet partition. Produkuje 20 CSV záznamov s počiatočnými WORD a BYTE poľami, ASM, dátové polia, CSV/JSON mapu a summary. Samostatný centrálny code/data katalóg zostáva staršou snímkou; jeho čísla sa nepripočítavajú k tejto mape. Runtime testy tejto dávky: 0.

DOSBox-X plán: logovať DS:22BA a jeho writerov, breakpoint na 12BDE pre prvý/posledný slot, vstupy mode=0/1, flagy a návraty helpera 0BFC; overiť záznamy pred a po otvorení/zatvorení herných súborov. Ďalší statický krok: helper 0C4C, paralelná tabuľka DS:221A a handler na 28B0. Žiadna časť tejto dávky nedokazuje dokončenie CRT ani celej kampane.

## Aktualizácia 13 oblastí

Nové sémantické percento je všade N/A. Úplný inventár kontraktov/polí/vetiev nie je dostupný; metodika budúceho výpočtu je počet uzavretých jednotiek / úplný inventár danej oblasti. Historické percentá sú orientačné. Bajtový menovateľ PASS1 je presný, status PARTIAL však nie je sémantické uzavretie.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | mapové vstupy | mapový scan |
| Dátové typy a konštanty | 95 % | N/A | 20 stream slotov a end WORD, 162 B PARTIAL | buffer/flag kontrakty | 0C4C |
| Tabuľky a ukazovatele | 93 % | N/A | inkluzívny end pointer 2212h | runtime writeri | DS:22BA watchpoint |
| Funkcie / ASM / CFG | 90 % | N/A | 0CCC mode 0/1, RET 2, výsledok AX | 0BFC a podvolania | stream helper closure |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping/VGA stav | framebuffer/DAC |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | helper 04C7:1692 |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie/sloty | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | resource binding | draw xrefs |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | pointer restore | tabuľky po LOAD |
| Windows Win16 | 92 % | N/A | bez nového dôkazu | runtime selektory | DS callbacku |
