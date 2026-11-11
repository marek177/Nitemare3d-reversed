# PASS1: UI polia s dynamickými stack textami

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Rozsah **[21C16,21DA2)**, 396 B, obsahuje dve počiatočné polia s desiatimi 18-bajtovými položkami a nulovým sentinelom. Status PARTIAL.

| FAR báza | Obraz | Sentinel, end-exclusive |
|---|---|---|
| 20B9:1086 | 21C16 | 21CCA..21CDC |
| 20B9:114C | 21CDC | 21D90..21DA2 |

Všetkých 20 počiatočných DWORD polí +0Eh je nulových. Nejde o nevyužitý pointer priestor: na F4B1 sa explicitne nastaví prvá báza a na F4D2/F4D6 sa do +0Eh/+10h zapisuje offset lokálneho bufferu a **SS**. Druhá báza je explicitná na F5F8; rovnaké zápisy sú na F619/F61D. Segment preto nevzniká zo statickej EXEPACK relokácie, ale z runtime SS. Kód postupuje po záznamoch s krokom 12h a po lokálnych textových bufferoch s krokom 29h (41 B).

Prvá inicializácia začína textovým bufferom BP-1A2h. Desať posunov po 29h ho posunie na BP-8, ďalšia podmienka porovná pointer s adresou lokálneho indexu BP-8. Pri normálnom návrate helperov to vykoná desať iterácií, zhodných s počiatočným layoutom. Následne sa FAR báza poľa odovzdá generickému UI spotrebiteľovi na F52F..F535. Ten číta textový DWORD +0Eh a používa krok 12h so sentinelom BYTE +0.

Inicializácia zapisuje tiež WORD +2 z výsledku helpera a BYTE +5 podľa úspechu. Pri neúspechu sa do textového bufferu kopíruje náhradný statický reťazec. Tieto zápisy dokazujú mutabilitu pôvodných dátových záznamov. Druhý caller má analógový pointer setup, ale celý jeho cyklus a význam výsledkov sa v tejto dávke neoznačuje za uzavretý.

```text
record = far_array_base
text = SS:local_buffer
repeat for initial ten entries:
    record.far_text = text
    record.word2 = fill_text_or_status(index, text, ...)
    initialize_flags_and_fallback(...)
    record += 18
    text += 41
run_ui(far_array_base)
```

Po návrate callera môžu statické záznamy stále obsahovať adresy lokálnych bufferov z už neplatného rámca. Toto je otvorená lifetime otázka, nie dôkaz prirodzenej chyby: ďalší spotrebiteľ môže pred čítaním pointery znovu inicializovať. Všetky caller cesty a nepriamych spotrebiteľov treba ešte uzavrieť. Konkrétna identita menu a SAVE/LOAD slotov nie je odvodená iba z počtu desať.

## Reprodukcia a pokrytie

`audit_pass1_dynamic_ui.py IMAGE PRIOR_MAP DECODER_DIR OUT` používa `relocations.csv` vedľa IMAGE ako súčasť existujúceho workflow; nové pointery sa neopierajú o relokačné položky. Kontroluje SHA, obe explicitné bázy, runtime pointer zápisy, stride, dvadsať počiatočných nulových FAR polí, sentinely a intervalové SHA. Výstupy `pass1_dynamic_ui/` obsahujú 22 slotov, nezávislé ASM a CSV/JSON mapy.

Nových **396 B PARTIAL** bolo UNKNOWN. Aktuálne **PARTIAL 47 867 B, CLASSIFIED ONLY 9 222 B, UNKNOWN 206 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Predošlá mapa: 47 471 / 9 222 / 602 / 0 B. Žiadny nový prirodzený runtime ani replay sa nevykonal.

DOSBox-X plán: zachytiť SS a rámec callerov, jednotlivé zápisy textových pointerov, ich čítania počas UI a po návrate, následnú reinicializáciu a prípadnú reentranciu. Ďalší krok: zvyšných 206 UNKNOWN bajtov a lifetime kontrakty dynamických textov; PARTIAL nie je úplnosť PASS1.


## Aktualizácia 13 oblastí

Nové sémantické percento všade N/A: chýba úplný inventár kontraktov/polí/vetiev. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické čísla sú orientačné.

| Oblasť | Predošlý odhad | Nové % | Nový dôkaz | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | no new resource format evidence | formát a bounds | DS:3F64 producent |
| Dátové typy a konštanty | 95 % | N/A | 396 B dynamic UI records PARTIAL | ostatní writeri | write xrefs |
| Tabuľky a ukazovatele | 93 % | N/A | 20 runtime FAR text fields; 2 sentinels | resource index | caller bounds |
| Funkcie / ASM / CFG | 90 % | N/A | stack text initialization; pointer lifetime open | prirodzená dosiahnuteľnosť | UI pointer trace |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping/VGA stav | framebuffer/DAC |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | helper 04C7:1692 |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | UI text pointer and coordinate reads | renderer contract | 0D29:0096 |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | pointer restore | tabuľky po LOAD |
| Windows Win16 | 92 % | N/A | bez nového dôkazu | runtime selektory | DS callbacku |
