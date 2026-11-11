# Grafické dáta: in-place obrátenie bitov

`0FBA:00D2`, obraz **[FC72,FCAB)**, je 57 B / 23 nezávisle dekódovaných inštrukcií. Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`.

FAR argument v SS:[BP+6] načíta LES DI. Rutina má tri lokálne BYTE hodnoty: vstupná maska 80h, výstupná maska 01h, akumulátor 0. Osemkrát testuje vstupný bajt, podľa bitu pridá výstupnú masku, vstupnú masku posunie doprava a výstupnú doľava. Výsledok uloží na pôvodnú adresu. FAR RET ponechá argument callerovi. Zachová SI, DI, BP, DS; ES je segment argumentu. AL je výstup, AH ostáva nezmenené. FLAGS sa nezachovávajú.

```text
reverse_byte_in_place(far_pointer):
    input_mask = 0x80
    output_mask = 1
    result = 0
    repeat 8 times:
        if BYTE[far_pointer] & input_mask: result |= output_mask
        input_mask >>= 1
        output_mask = (output_mask << 1) & 0xff
    BYTE[far_pointer] = result
```

Caller v 0D29:016A používa rutinu na každý payload bajt rozmerových položiek. Tým je transformácia grafických blokov presne identifikovaná ako bit reversal, bez tvrdenia o úplnej orientácii výsledného obrazu. Nejde o dôkaz konkrétnej fontovej identity ani renderer parity. Počiatočné príznaky načítania blokov a ich writeri zostávajú otvorení.

## Reprodukcia a replay

`replay_bitmap_bit_reverse.py IMAGE UNICORN_DIR DECODER_DIR OUT` byte-pinuje celú rutinu, nezávisle ju dekóduje a vykonáva pôvodné inštrukcie. **1 024 prípadov, 0 zlyhaní**: všetkých 256 bajtov, load segment 0/1000h a FAR offset 0033h/FFFEh. Overuje výsledok, dva susedné guard bajty, SP po FAR návrate a SI/DI/BP/DS/ES/AX. Tým nekontroluje všetky možné zápisy do pamäte ani všetky FLAGS. Nepoužíva reálny DOS runtime, prirodzené resource dáta ani game caller. Jednotlivé prípady a ASM sú v `bitmap_bit_reverse_replay/`.

`compare_bit_reverse_versions.py CANONICAL_IMAGE OLD_OUTPUT_ROOT OUT_JSON` našiel **práve jednu presnú 57-bajtovú zhodu v každom z ôsmich dostupných DOS labelov** 1.0,1.1,1.2,1.5,1.7,1.8,1.9,2.0. Ide o sedem unikátnych obrazov: 1.8 a 1.9 majú zhodný hash. Výstup uchováva hash každého obrazu a offset. Toto je bajtová/algoritmická zhoda lokálnej rutiny; nezaručuje zhodné callery, dosiahnuteľnosť ani prirodzené správanie. Win16 sa v tejto dávke neporovnával.

## Stav kampane

PASS1 byte mapa sa nemení: **39 195 B PARTIAL, 9 222 B CLASSIFIED ONLY, 8 878 B UNKNOWN, 0 B DEEP VERIFIED**. Táto rutina je mimo pôvodných NON-CODE a nepridáva tam kódové bajty. Prijatý súčet riadených replay prípadov je 2 603 (predtým 1 579); originálne runtime testy zostávajú 0. Samostatný centrálny katalóg zatiaľ rutinu nezahŕňa, jeho staršie čísla sa automaticky neprepisujú.

DOSBox-X plán: zachytiť skutočný payload pred/po transformácii a renderer čítanie, overiť počet transformácií a dosiahnutie každej položky v hraniciach bloku. Ďalší krok: renderer spotrebiteľ pointer tabuľky DS:3690 a zostávajúcich 8 878 UNKNOWN bajtov.


## Aktualizácia 13 oblastí

Nové sémantické percento všade N/A: chýba úplný inventár kontraktov/polí/vetiev. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické čísla sú orientačné.

| Oblasť | Predošlý odhad | Nové % | Nový dôkaz | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | payload bit reversal identified | formát a bounds | resource lengths |
| Dátové typy a konštanty | 95 % | N/A | no byte promotion; bit reversal proven locally | ostatní writeri | write xrefs |
| Tabuľky a ukazovatele | 93 % | N/A | 3 relocated block bases | resource index | caller bounds |
| Funkcie / ASM / CFG | 90 % | N/A | 57-byte helper; 1024 replay cases; 8 DOS labels | prirodzená dosiahnuteľnosť | DI and payload trace |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping/VGA stav | framebuffer/DAC |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | helper 04C7:1692 |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | byte bit reversal confirmed | orientation and caller integration | renderer xrefs |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | pointer restore | tabuľky po LOAD |
| Windows Win16 | 92 % | N/A | bez nového dôkazu | runtime selektory | DS callbacku |
