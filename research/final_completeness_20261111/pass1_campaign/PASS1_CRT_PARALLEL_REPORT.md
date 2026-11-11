# PASS1: paralelné CRT záznamy a flush bufferu

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Adresy sú nerelokované, konce intervalov exkluzívne. Výsledok je statický PARTIAL, bez runtime testu.

## Párovanie tabuliek

Počiatočné stream pole DS:217A..221A obsahuje 20 slotov po 8 B podľa predchádzajúceho dôkazu inkluzívneho end pointera. Kód na 12B03/12B07 transformuje stream pointer na `stream_offset - 217Ah + 221Ah`. Kód 12B4F/12B53 používa rovnakú transformáciu na čítanie bitu 01h. Zachováva teda relatívny offset aj krok 8. Zodpovedajúca počiatočná paralelná oblasť je DS:221A..22BA, obraz `[2992A,299CA)`, **160 B**. Neodvodzuje sa iba z medzery medzi tabuľkami.

Potvrdené sú spotreby BYTE paralelného slotu +0: bit 01h povoľuje jednu cestu flushu a bit 40h povoľuje následný helper v 0BFC. Ďalší pozorovaný kód 1274D číta WORD +2 paralelného slotu. Úplný typ všetkých ôsmich bajtov ani všetci writeri nie sú uzavretí. Klasifikácia celého nominálneho slotu PARTIAL znamená známy vzťah a krok, nie dokázanú sémantiku každého poľa.

## Buffer flush 11EE:0C4C

Rozsah `[12B2C,12BA3)` je súvislý, nezávisle dekódovaný a končí NEAR RET. Argument je NEAR stream pointer v SS:[BP+4]. DS je zdedený; rozsah slot indexu sa v helperi nekontroluje. Výstup AX je 0 alebo FFFFh. SI/DI/BP sa obnovujú. Vstupné stream polia +0 a +4 majú bufferovú aritmetiku, +6 obsahuje flagy, +7 sa zero-extenduje ako handle argument zapisovacieho helpera `11EE:1EFE`.

```text
result = 0
flags = stream.byte6
if (flags & 3) == 2:
    if (flags & 8) or (paired.byte0 & 1):
        pending = signed16(stream.word0 - stream.word4)
        if pending > 0:
            actual = write_helper(stream.byte7, stream.word4, pending)
            if actual != pending:
                stream.byte6 |= 0x20
                result = 0xffff
            elif stream.byte6 & 0x80:
                stream.byte6 &= 0xfd
stream.word0 = stream.word4
stream.word2 = 0
return result
```

Reset word0/word2 sa vykoná aj pri preskočení zapisovacej vetvy. Test pending je signed `JLE`, rozdiel je 16-bitový. Úspech sa posudzuje rovnosťou počtu bajtov, nie priamo CF helpera. Názov flush vyplýva z tohto bufferového algoritmu; konkrétnu CRT značku/verziu knižnice neidentifikujem.

Wrapper 0BFC pri nenulovom pointeri volá tento NEAR helper; pri jeho nenulovom výsledku vráti FFFFh. Pri úspechu môže podľa bitu 40h paralelného slotu volať `11EE:28B0` s handle. Význam a úplný kontrakt tohto podvolania zostáva otvorený. Priradenie wrappera ku konkrétnej štandardnej C API funkcii nie je týmto dôkazom uzavreté.

## Meranie

Pribudlo 160 B PARTIAL z CLASSIFIED ONLY. Aktuálna mapa `pass1_crt_parallel/noncode_intervals.csv` a JSON: **PARTIAL 12 163 B, CLASSIFIED ONLY 9 270 B, UNKNOWN 35 862 B, DEEP VERIFIED 0 B**. Súčet je presne 57 295 B. Predchádzajúca mapa mala 12 003 / 9 430 / 35 862 / 0 B. Nové sémantické percento sa nepočíta.

Reprodukcia: `audit_pass1_crt_parallel.py IMAGE PRIOR_MAP DECODER_DIR OUT`. Kontroluje SHA obrazu a vstupných intervalov, inkluzívny end pointer, mapovacie a bufferové inštrukčné bajty; dekóduje dva ohraničené helpery a vypíše 20 počiatočných paralelných slotov. Výstupy obsahujú ASM, dátové polia, sloty, CSV/JSON mapu a summary. Centrálna code/data partition je samostatná staršia snímka.

DOSBox-X plán: sledovať slot a paralelný slot pri otvorení/čítaní/zápise herného súboru, testovať pending=0, krátky zápis a plný zápis, logovať flag 20h a reset pointera aj pri chybe. Ďalší krok: `11EE:1EFE` a `11EE:28B0`, writeri paralelných flagov a runtime rozsah end pointera.

## Aktualizácia 13 oblastí

Metodika percenta: uzavreté jednotky / úplný inventár kontraktov, polí alebo vetiev danej oblasti; runtime parity osobitne. Menovatele nie sú úplné, preto nové percento všade N/A. Historické odhady nie sú nameraná baseline.

| Oblasť | Predošlý odhad | Nové % | Nový dôkaz | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | mapový scan | tvorba objektov |
| Dátové typy a konštanty | 95 % | N/A | 160 B paralelných slotov PARTIAL | všetky polia | writeri flagov |
| Tabuľky a ukazovatele | 93 % | N/A | párovanie so stream poľom | runtime rozsah | DS:22BA writeri |
| Funkcie / ASM / CFG | 90 % | N/A | buffer flush a chyba short write | zapisovací helper | 11EE:1EFE |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping/VGA stav | framebuffer/DAC |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | helper 04C7:1692 |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | resource binding | draw xrefs |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | pointer restore | tabuľky po LOAD |
| Windows Win16 | 92 % | N/A | bez nového dôkazu | runtime selektory | DS callbacku |
