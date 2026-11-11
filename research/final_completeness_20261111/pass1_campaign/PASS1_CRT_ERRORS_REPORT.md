# PASS1: preklad DOS chýb

SHA-256 obrazu `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Default DS=2771h. Nová tabuľka DS:2160..2174, obraz `[29870,29884)`, má 20 jednobajtových položiek. Bajty v desiatkovej sústave: `0,22,2,2,24,13,9,12,12,12,7,8,22,22,255,2,13,18,2,255`.

## ASM a kontrakt

Helper `11EE:05CA`, ohraničený obrazový rozsah `[124AA,124D7)`, je NEAR rutina so vstupom AX a zdedeným DS. Vždy uloží pôvodné AL do BYTE DS:2126; horný bajt susedného WORD nemení. Pri nenulovom AH presunie AH do AL a vykoná CBW bez tabuľky. Inak podľa BYTE DS:2121 vykoná normalizáciu AL a `BX=2160h; XLAT; CBW`. WORD výsledok uloží do DS:2118. AX je výsledok; BX sa na tabuľkovej vetve prepíše, na priamej AH vetve nie. Príznaky sa nezachovávajú. Zásobník netvorí lokálny rámec, končí NEAR RET.

```text
native_error_low = input_AL       # only BYTE store
if input_AH != 0:
    error = signed8(input_AH)
else:
    if dos_major >= 3 and input_AL in (32, 33): index = 5
    else: index = min(input_AL, 19)
    error = signed8(translation[index])
WORD_DS[0x2118] = error
return error
```

Položky 14 a 19 majú FFh a CBW vytvorí FFFFh. Nepovažujú sa za kladné 255. Vetvy normalizácie dokazujú index 0..19; priame AH prípady tabuľku nečítajú. Počiatočný obsah má jednoznačnú spotrebu, ale neprítomnosť runtime writerov ani prirodzený DS všetkých callerov nie sú uzavreté.

## Reprodukcia a riadený replay

`audit_pass1_crt_errors.py IMAGE PRIOR_MAP DECODER_DIR OUT` kontroluje kompletných 45 bajtov rutiny, SHA obrazu, SHA predchádzajúcich intervalov a presnú partition. Vytvára tabuľku položiek, ASM a mapy v `pass1_crt_errors/`.

`replay_crt_errors.py IMAGE UNICORN_DIR OUT` vykonáva pôvodné inštrukcie v 16-bitovom Unicorn, s nasadeným default DS a izolovaným zásobníkom. **1 532 prípadov, 0 zlyhaní**: všetkých 256 AL pri AH=0 a všetkých 255 nenulových AH pri AL=0/255, vždy pre DOS major 2 a 3. Overuje AX odvodené error pole, zachovanie horného bajtu native error a zmenu SP po RET. Ide o riadený replay pôvodných inštrukcií s dosadeným stavom, nie o DOSBox-X alebo prirodzený beh hry. Výstup `crt_error_replay/` zachováva jednotlivé prípady. Predošlých 47 prijatých replay prípadov ostáva samostatne zdokumentovaných; aktuálny súčet je 1 579. Zamietnuté SMC experimenty sa nepripočítavajú.

## Pokrytie

Nových 20 B PARTIAL pochádza z CLASSIFIED ONLY. Aktuálne **PARTIAL 12 211 B, CLASSIFIED ONLY 9 222 B, UNKNOWN 35 862 B, DEEP VERIFIED 0 B**; spolu 57 295 B. Predošlá mapa mala 12 191 / 9 242 / 35 862 / 0 B. Sémantická úplnosť CRT ani celého projektu z týchto počtov nevyplýva. Originálne runtime testy tejto dávky: 0.

DOSBox-X plán: zachytiť prirodzený DOS error, DS a vstup AX na 05CA; logovať oba error sloty a prípadné zápisy do tabuľky. Nasledujúci statický krok: úplná CF vetva zapisovacieho helpera a inicializácia/změny handle flagov.

## Aktualizácia 13 oblastí

Nové percento je všade N/A: úplný inventár kontraktov/polí/vetiev chýba. Metodika je uzavreté jednotky / úplný inventár danej oblasti, runtime parity osobitne. Historické čísla sú orientačné odhady.

| Oblasť | Predošlý odhad | Nové % | Nový dôkaz | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | mapový scan | tvorba objektov |
| Dátové typy a konštanty | 95 % | N/A | 20 B signed prekladovej tabuľky | runtime writeri | watchpoint tabuľky |
| Tabuľky a ukazovatele | 93 % | N/A | dokázaný index 0..19 | prirodzený DS | caller DS |
| Funkcie / ASM / CFG | 90 % | N/A | model 05CA a 1 532 replay prípadov | runtime integrácia | DOS error stopa |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping/VGA stav | framebuffer/DAC |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | helper 04C7:1692 |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | resource binding | draw xrefs |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | pointer restore | tabuľky po LOAD |
| Windows Win16 | 92 % | N/A | bez nového dôkazu | runtime selektory | DS callbacku |
