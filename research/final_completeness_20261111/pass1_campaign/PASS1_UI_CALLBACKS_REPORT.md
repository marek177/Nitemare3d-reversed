# PASS1: UI záznamy s FAR callbackom

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Pole **20B9:1212**, obraz **[21DA2,21E0E)**, má päť nenulových 18-bajtových záznamov a nulový 18-bajtový sentinel na `[21DFC,21E0E)`, spolu 108 B. Status PARTIAL.

Každý z piatich záznamov obsahuje:

- DWORD +6: počiatočný FAR code pointer `0D29:1F62`, obrazový cieľ F1F2. Segmentový WORD +8 má skutočnú EXEPACK relokáciu.
- DWORD +0Eh: FAR textový pointer, počiatočný segment 2771h, tiež so skutočnou relokáciou na +10h.
- BYTE +0: počiatočne nenulový identifikátor; nulový v sentineli. Ostatné polia zostávajú iba čiastočne interpretované.

Na F1D7..F1DE sa explicitne odovzdá `20B9:1212` do UI spotrebiteľa `0D29:1946`. Ten používa krok 12h, nulový prvý BYTE a textový pointer +0Eh. Jeho callback vetva na ED77 testuje DWORD ES:[SI+6] proti 0; ED7F vykoná **FAR CALL ES:[SI+6]**. Nejde teda iba o relokované WORDy podobné adrese. SI/ES po navigačných helperoch môžu ukazovať na zmenenú položku; úplný navigačný a callback ABI kontrakt sa touto dávkou neuzatvára.

Počiatočný callback cieľ F1F2 má vlastný rámec a následnú prácu s globálnym stavom. Jeho úplné vedľajšie účinky, prípadné mutácie slotov a prirodzený DS sú otvorené. Kód callbacku leží mimo pôvodných NON-CODE intervalov; tento report ho nepripočítava k dátovému pokrytiu.

```text
for each initially nonzero UI record at stride 18:
    render_text(record.far_text)
    ... navigate/select ...
    if record.far_callback != 0:
        far_call(record.far_callback)
```

## Reprodukcia a meranie

`audit_pass1_ui_callbacks.py IMAGE PRIOR_MAP DECODER_DIR OUT` používa `relocations.csv` vedľa IMAGE. Overuje presné počiatočné callback adresy, oba relokované segmenty každého záznamu, sentinel, priamy caller, DWORD guard a nepriamy FAR CALL. Nezávisle dekóduje tri ohraničené okná. Výstupy `pass1_ui_callbacks/` obsahujú šesť slotov, ASM a CSV/JSON intervaly.

Z 108 B bolo 20 B segmentových relokácií už PARTIAL. Nových **88 B** pochádza z UNKNOWN. Aktuálne **PARTIAL 47 471 B, CLASSIFIED ONLY 9 222 B, UNKNOWN 602 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Predošlá mapa: 47 383 / 9 222 / 690 / 0 B. Nový prirodzený runtime ani replay sa nevykonal.

DOSBox-X plán: zachytiť ES:SI pred ED7F, skutočný cieľ, DS/SS a návrat, sledovať mutácie oboch FAR polí. Ďalší krok: zvyšných 602 UNKNOWN bajtov a kontrakt 0D29:1F62; samotný známy počiatočný pointer nedokazuje všetky runtime ciele.


## Aktualizácia 13 oblastí

Nové sémantické percento všade N/A: chýba úplný inventár kontraktov/polí/vetiev. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické čísla sú orientačné.

| Oblasť | Predošlý odhad | Nové % | Nový dôkaz | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | no new resource format evidence | formát a bounds | DS:3F64 producent |
| Dátové typy a konštanty | 95 % | N/A | 108 B callback records PARTIAL; net +88 | ostatní writeri | write xrefs |
| Tabuľky a ukazovatele | 93 % | N/A | 5 FAR code and 5 text fields; sentinel | resource index | caller bounds |
| Funkcie / ASM / CFG | 90 % | N/A | DWORD callback guard and indirect FAR CALL | prirodzená dosiahnuteľnosť | UI pointer trace |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping/VGA stav | framebuffer/DAC |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | helper 04C7:1692 |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | UI text pointer and coordinate reads | renderer contract | 0D29:0096 |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | pointer restore | tabuľky po LOAD |
| Windows Win16 | 92 % | N/A | bez nového dôkazu | runtime selektory | DS callbacku |
