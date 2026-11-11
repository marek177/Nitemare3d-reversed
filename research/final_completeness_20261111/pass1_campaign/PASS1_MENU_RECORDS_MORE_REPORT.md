# PASS1: ďalšie tri priamo volané UI polia

Nový dôkaz nad obrazom SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297` pokrýva **[21B3E,21C16), 216 B**. Tri počiatočné polia majú vždy tri nenulové položky po 18 B a jeden 18-bajtový nulový sentinel. Nepreberá sa iba podobnosť dát: všetky tri majú priame argumenty do už analyzovaného spotrebiteľa `0D29:1946`.

| FAR pointer | Obrazový začiatok | Caller / konštanta | Nulový sentinel, end-exclusive |
|---|---|---|---|
| 20B9:0FAE | 21B3E | F905..F90C | 21B74..21B86 |
| 20B9:0FF6 | 21B86 | FA70..FA77 | 21BBC..21BCE |
| 20B9:103E | 21BCE | F44F..F456 | 21C04..21C16 |

Spotrebiteľ prefix EBD6..EC38 testuje BYTE +0, číta FAR pointer +0Eh a súradnicové WORDy +0Ah/+0Ch, postupuje po 12h a končí na nulovom BYTE +0. Každá z deviatich nenulových položiek má segmentový WORD +10h počiatočne 2771h so skutočnou EXEPACK relokáciou. Sentinely majú počiatočne nulových všetkých 18 B; runtime podmienka vyžaduje iba prvý BYTE. Plný algoritmus spotrebiteľa a nepriame mutácie zostávajú otvorené, rovnako presná identita jednotlivých menu.

V callerovi poľa FAE sa pred spustením menu skenujú položky rovnakým krokom a môže sa meniť BYTE +5. Preto tieto objekty nemožno považovať za nemenné konštanty iba preto, že sú prítomné v počiatočnom obraze. Výsledok je PARTIAL, bez novej DEEP VERIFIED klasifikácie.

## Reprodukcia a pokrytie

`audit_pass1_menu_records_more.py IMAGE PRIOR_MAP DECODER_DIR OUT` používa `relocations.csv` vedľa IMAGE. Overuje tri priame caller konštanty, spotrebiteľské bajty, deväť relokovaných FAR polí, tri počiatočné sentinely, identitu obrazu a intervalové SHA. Nezávisle dekóduje spotrebiteľský prefix a tri caller okná. Výstupy `pass1_menu_records_more/` obsahujú 12 slotov, ASM a CSV/JSON mapy.

Z 216 B bolo 18 B relokovaných segmentov už PARTIAL. Čistý prírastok **198 B** pochádza z UNKNOWN. Aktuálne **PARTIAL 46 975 B, CLASSIFIED ONLY 9 222 B, UNKNOWN 1 098 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Predošlá mapa mala PARTIAL 46 777 B a UNKNOWN 1 296 B. Nový runtime ani replay sa nevykonal.

DOSBox-X plán: porovnať počiatočné a zmenené BYTE +5, skutočné textové pointery a sentinel prechody vo všetkých troch caller cestách. Ďalší krok: štruktúry po 21C16h a ich callbacky; nepotvrdené medzery ostávajú UNKNOWN.


## Aktualizácia 13 oblastí

Nové sémantické percento všade N/A: chýba úplný inventár kontraktov/polí/vetiev. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické čísla sú orientačné.

| Oblasť | Predošlý odhad | Nové % | Nový dôkaz | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | no new resource format evidence | formát a bounds | DS:3F64 producent |
| Dátové typy a konštanty | 95 % | N/A | 216 B UI records PARTIAL; net +198 | ostatní writeri | write xrefs |
| Tabuľky a ukazovatele | 93 % | N/A | 9 FAR fields; 3 initial sentinels | resource index | caller bounds |
| Funkcie / ASM / CFG | 90 % | N/A | three direct callers and stride-18 consumer | prirodzená dosiahnuteľnosť | UI pointer trace |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping/VGA stav | framebuffer/DAC |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | helper 04C7:1692 |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | UI text pointer and coordinate reads | renderer contract | 0D29:0096 |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | pointer restore | tabuľky po LOAD |
| Windows Win16 | 92 % | N/A | bez nového dôkazu | runtime selektory | DS callbacku |
