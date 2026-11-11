# PASS1: 128 FAR allocation ukazovateľov

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Počiatočná oblasť **1BE7:0000..0200**, obraz **[1BE70,1C070)**, má 512 nulových bajtov. Typ je nominálne 128 FAR16 ukazovateľov, status PARTIAL. Susedných 16 B `[1C070,1C080)` zostáva UNKNOWN.

## Producent a spotrebiteľ

Na 7780 sa uloží vypočítaný count do DS:3504. Signed porovnanie 7783..778B obmedzí kladné hodnoty vyššie než 128 na 128. Pri count<1 sa volá game error helper, ktorého globálny non-return kontrakt zostáva otvorený. Producent nastaví DI=0 a SI=0, pri kladnom count opakovane volá CRT helper 11EE:2065 s argumentom 0C02h. Návrat AX/DX uloží do ES:[SI] a ES:[SI+2], pričom ES načíta z DS:2560. Globál v obraze 29C70 má počiatočný segment 1BE7h a skutočnú EXEPACK relokáciu.

Nulovosť pointera testuje OR oboch WORDov a pri nule volá error helper. Následne cez LES ES:[SI] načíta uložený pointer a do jeho cieľa uloží WORD 0. SI zvyšuje o 4 a DI o 1 až do count. Táto LES spotreba potvrdzuje FAR pointer interpretáciu, nie iba podobnosť dvojíc WORDov. Spotrebiteľ pri 78BF..78EB explicitne nastaví DS=1BE7h, číta položky cez LES [BX], pracuje s cieľovým WORDom a zvyšuje BX o 4 pri count DS/SS:3504.

```text
count = computed_count
if signed16(count) > 128: count = 128
if signed16(count) < 1: error_helper(...)
for i in range(count):
    pointer_table[i] = allocation_helper(0x0c02)
    if pointer_table[i] == 0: error_helper(...)
    WORD[pointer_table[i]] = 0
```

Konkrétny allocation helper a životnosť cieľov sa v tejto dávke neuzatvárajú. DS:3504 je pri default DS=2771h mimo file-backed obrazu, preto sa count bajty nepripočítavajú k PASS1. Signed clamp nie je dôkaz globálnej bezpečnosti count pri neskorších writeroch; helpery môžu meniť stav a nepriame zápisy zostávajú otvorené. Nominálna kapacita sa opiera o explicitný clamp a krok, nie o 528-bajtovú fyzickú medzeru.

## Reprodukcia a meranie

`audit_pass1_allocated_pointer_table.py IMAGE PRIOR_MAP DECODER_DIR OUT` vyžaduje `relocations.csv` vedľa IMAGE. Overuje SHA obrazu, relokáciu globálu, rozhodujúce inštrukčné bajty, počiatočné nuly, intervalové SHA a súčet. Výstupy `pass1_allocated_pointer_table/` obsahujú 128 slotov, typový rozsah, ASM a CSV/JSON mapu. Prirodzený runtime ani nový replay sa nevykonal.

Nových **512 B PARTIAL** bolo UNKNOWN. Aktuálne **PARTIAL 46 403 B, CLASSIFIED ONLY 9 222 B, UNKNOWN 1 670 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Predošlá mapa mala PARTIAL 45 891 B, UNKNOWN 2 182 B.

DOSBox-X plán: log count pred/po clamp, helper návraty, prvý/posledný pointer a jeho životnosť pri zmene úrovne či LOAD. Ďalší krok: zostávajúce statické dátové záznamy a lookup polia, bez automatického označenia nulových medzier ako padding.


## Aktualizácia 13 oblastí

Nové sémantické percento všade N/A: chýba úplný inventár kontraktov/polí/vetiev. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické čísla sú orientačné.

| Oblasť | Predošlý odhad | Nové % | Nový dôkaz | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | no new format evidence | formát a bounds | DS:3F64 producent |
| Dátové typy a konštanty | 95 % | N/A | 512 B pointer table PARTIAL | ostatní writeri | write xrefs |
| Tabuľky a ukazovatele | 93 % | N/A | 128 FAR pointer slots; LES consumer | resource index | caller bounds |
| Funkcie / ASM / CFG | 90 % | N/A | signed count clamp and producer loop | prirodzená dosiahnuteľnosť | allocation and count trace |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping/VGA stav | framebuffer/DAC |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | helper 04C7:1692 |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | resource binding | draw xrefs |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | pointer restore | tabuľky po LOAD |
| Windows Win16 | 92 % | N/A | bez nového dôkazu | runtime selektory | DS callbacku |
