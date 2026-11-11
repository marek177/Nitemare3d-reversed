# PASS1: tri sentinelové polia UI záznamov

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Rozsah **[219A0,21B3E)** má 414 B: 20 nenulových 18-bajtových položiek a tri 18-bajtové nulové sentinely. Status PARTIAL.

| FAR báza | Obraz | Počiatočné položky | Sentinel |
|---|---|---:|---|
| 20B9:0E10 | 219A0 | 6 | 21A0C..21A1E |
| 20B9:0E8E | 21A1E | 7 | 21A9C..21AAE |
| 20B9:0F1E | 21AAE | 7 | 21B2C..21B3E |

Selector v kóde F82C..F89A explicitne vyberá offsety E8Eh/E10h/F1Eh so segmentom 20B9h a vracia FAR pointer. Generický spotrebiteľ 0D29:1946, prefix EBD6..EC38, testuje BYTE +0, pri nenulovom spracuje položku a zvýši SI o 12h. Ďalší BYTE +0 je sentinelová podmienka. Zároveň číta DWORD +0Eh, WORD +0Ch a WORD +0Ah, oba WORDy zvýši o 1 a odovzdá render helperu 0D29:0096. Následné spotrebiteľské vetvy používajú BYTE +4 ako výberový guard.

Každý nenulový záznam má segmentový WORD +10h s počiatočnou hodnotou 2771h a skutočnou EXEPACK relokáciou. Spojenie s DWORD čítaním +0Eh potvrdzuje FAR16 pointer; jeho offset smeruje do default DS dát. Konkrétne textové objekty a úplný kontrakt rendereru táto dávka nepromuje. Záznamy majú počiatočný nulový sentinel všetkých 18 B, ale spotrebiteľ vyžaduje iba nulový BYTE +0. Dôkaz počiatočnej dĺžky nie je dôkaz nemennosti sentinelov ani globálnej kapacity.

```text
p = selected_array
while BYTE[p] != 0:
    render(WORD[p+0x0a]+1, WORD[p+0x0c]+1, FAR[p+0x0e], ...)
    process_item(p)
    p += 18
```

Presné významy všetkých polí, identita jednotlivých menu, prirodzené runtime mutácie a pointery do pracovných stack bufferov pri iných poliach zostávajú otvorené. Názov UI/menu je pracovná interpretácia renderovanej výberovej štruktúry, nie uzavretý herný stavový kontrakt.

## Reprodukcia a meranie

`audit_pass1_menu_records.py IMAGE PRIOR_MAP DECODER_DIR OUT` používa aj `relocations.csv` vedľa IMAGE. Kontroluje identitu, tri selector konštanty, krok spotrebiteľa, 20 relokovaných FAR polí, všetky tri nulové sentinely, intervalové SHA a presný menovateľ. Výstupy `pass1_menu_records/` obsahujú 23 slotov, ohraničené ASM a CSV/JSON mapu.

Z 414 B bolo 40 B relokovaných segmentov už PARTIAL. Čistý prírastok je **374 B z UNKNOWN**. Aktuálne **PARTIAL 46 777 B, CLASSIFIED ONLY 9 222 B, UNKNOWN 1 296 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Predchádzajúca mapa mala PARTIAL 46 403 B a UNKNOWN 1 670 B. Nové prirodzené runtime/replay prípady: 0.

DOSBox-X plán: zachytiť selector výsledok, iteráciu a mutácie sentinelov, textové pointery a súradnice pri menu prechodoch. Ďalší krok: zostávajúce UI polia, ich callbacky a textové objekty; žiadne nulové medzery sa automaticky neoznačia padding.


## Aktualizácia 13 oblastí

Nové sémantické percento všade N/A: chýba úplný inventár kontraktov/polí/vetiev. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické čísla sú orientačné.

| Oblasť | Predošlý odhad | Nové % | Nový dôkaz | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | no new resource format evidence | formát a bounds | DS:3F64 producent |
| Dátové typy a konštanty | 95 % | N/A | 414 B UI records PARTIAL; net +374 | ostatní writeri | write xrefs |
| Tabuľky a ukazovatele | 93 % | N/A | 20 FAR fields; 3 initial sentinels | resource index | caller bounds |
| Funkcie / ASM / CFG | 90 % | N/A | selector and stride-18 consumer | prirodzená dosiahnuteľnosť | UI pointer trace |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping/VGA stav | framebuffer/DAC |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | helper 04C7:1692 |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | UI text pointer and coordinate reads | renderer contract | 0D29:0096 |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | pointer restore | tabuľky po LOAD |
| Windows Win16 | 92 % | N/A | bez nového dôkazu | runtime selektory | DS callbacku |
