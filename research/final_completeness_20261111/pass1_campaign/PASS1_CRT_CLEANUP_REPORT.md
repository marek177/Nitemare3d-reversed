# PASS1: počiatočné CRT cleanup ukazovatele

## Dôkaz a hranice

Rozbalený obraz má SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Nasledujúce adresy používajú default DS=2771h; konce intervalov sú exkluzívne.

| DS offset / obraz | Typ | Počiatočná hodnota | Spotrebiteľ |
|---|---|---|---|
| 2534 / 29C44..29C46 | WORD magic guard | 0 | 12107 porovná s D6D6h |
| 253A / 29C4A..29C4C | NEAR callback offset v CRT CS | 00E4h | 1210F `CALL WORD PTR [253A]`, iba po magic guard |
| 2542 / 29C52..29C56 | FAR callback, segment zároveň guard | 0000:0000 | 12152 číta segment 2544; pri nenulovom 1215B FAR CALL |
| 254E / 29C5E..29C62 | FAR cleanup záznam | 11EE:081E | 120FE..12104 nastaví rozsah [254E,2552) |

Segmentový WORD na obraze 29C60 je skutočná EXEPACK relokácia, takže po načítaní je cieľ `(load+11EE):081E`. Nulový FAR callback nie je volaný počiatočnou bežnou vetvou a počiatočný NEAR callback je vypnutý guardom. To nedokazuje ich runtime nemennosť. Magic guard môže byť tiež debugger/runtime hook; konkrétnu knižničnú identitu bez ďalšieho dôkazu nepriraďujem.

Iterátor `11EE:028B` (1216B..1217E) spracúva [SI,DI) odzadu po 4 B, preskočí iba dvojicu offset=0 aj segment=0, inak vykoná `LCALL [DI]`. Rozsah [254E,2552) má presne jeden záznam. Rozsahy [254E,254E) a [2552,2552) v susedných volaniach sú prázdne; samotná hodnota na DS:2552 sa tým neklasifikuje ako ďalší cleanup záznam.

Počiatočný cieľ `11EE:081E` (126FE..12714) volá `11EE:0CC4`, následne podľa BYTE DS:2151 môže volať `11EE:256A`, a má RETF. CRT exit nastavuje DS:2151 z CH, pre vstup 01EB je CH=0. Ak predchádzajúce helpery guard nemenia, druhé volanie sa preskočí. Vstup 0CC4 vloží argument 1 a volá NEAR 0CCC; tam sa začína iterácia nad 8-bajtovými záznamami od DS:217A. Kontrakt tejto iterácie a jej podvolaní zatiaľ nie je uzavretý, preto ani ukončenie celého error helpera neoznačujem DEEP VERIFIED.

```text
iterate_far_reverse(begin, end):
    while begin < end:             # unsigned offset comparison
        end -= 4
        if WORD[end] | WORD[end+2]:
            far_call(DS:end)

exit_cleanup_initial_state:
    iterate_far_reverse(0x254e, 0x2552)  # initial target 11EE:081E
    if WORD[0x2534] == 0xd6d6: near_call(WORD[0x253a])
    ...
    if WORD[0x2544] != 0: far_call(DWORD[0x2542])
```

## Meranie a reprodukcia

12 B má konkrétny dátový typ a spotrebiteľa; 2 B relokovaného segmentu už boli PARTIAL. Čistý prírastok PARTIAL je **10 B** z CLASSIFIED ONLY. Aktuálna PASS1 mapa: **11 841 B PARTIAL, 9 592 B CLASSIFIED ONLY, 35 862 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57 295 B. Žiadne nové sémantické percento sa neodvodzuje z počtu ukazovateľov.

Skript `audit_pass1_crt_cleanup.py IMAGE RELOCS PRIOR_MAP DECODER_DIR OUT` kontroluje SHA, relokáciu, pôvodné intervalové SHA a rozhodujúce inštrukčné bajty. Nezávisle dekóduje ohraničené okná a vytvára CSV/JSON v `pass1_crt_cleanup/`. Vstupná mapa je `pass1_error_path/noncode_intervals.csv`. Počet originálnych runtime testov tejto dávky je 0.

Ďalší krok: dokončiť iterátor 0CCC a identifikovať 8-bajtové CRT stream záznamy DS:217A a koniec DS:22BA. V DOSBox-X sledovať zápisy do štyroch uvedených polí, DS:2151, prirodzený DS a každý nepriamy cieľ počas error exit. Samotné vyhľadanie literálov v starom inštrukčnom inventári sa nepovažuje za dôkaz absencie aliasovaných writerov.

## Aktualizácia 13 oblastí

Pri všetkých oblastiach je nové sémantické percento N/A: chýba úplný inventár príslušných kontraktov/polí/vetiev. Metodika je počet uzavretých jednotiek delený úplným inventárom danej oblasti; runtime parity sa meria osobitne. Historické odhady zostávajú iba orientačné. Nové bajtové súčty vyššie majú presný menovateľ 57 295 B a nepredstavujú percento dokončenia projektu.

| Oblasť | Predošlý odhad | Nové % | Nové zistenie | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | tvorba objektov | mapový scan |
| Dátové typy a konštanty | 95 % | N/A | 12 B CRT polí PARTIAL | runtime DS a writeri | watchpoint slotov |
| Tabuľky a ukazovatele | 93 % | N/A | jeden počiatočný FAR cleanup záznam | úplné callback kontrakty | stream cleanup 0CCC |
| Funkcie / ASM / CFG | 90 % | N/A | reverse FAR iterátor, cieľ 081E | podvolania a ABI | uzavrieť cleanup iteráciu |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping/stav VGA | framebuffer/DAC |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | helper 04C7:1692 |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie/sloty | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | resource binding | draw xrefs |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | pointer restore | tabuľky po LOAD |
| Windows Win16 | 92 % | N/A | bez nového dôkazu | runtime selektory | DS callbacku |
