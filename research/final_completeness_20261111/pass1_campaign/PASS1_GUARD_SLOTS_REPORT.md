# PASS1: nominálne GUARD pole 100 × 26 bajtov

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Pole **21FD:264E..3076**, obraz **[2461E,25046)**, má nominálne 100 slotov po 26 B, spolu 2 600 B. Celé je počiatočne nulové. Status PARTIAL; hranice sa neurčovali podľa nulového behu ani susednej tabuľky.

## Producent, limit a segment

Objektový scan na B8DB testuje bit 08h objektového poľa +5. Pri jeho nastavení B8E2 porovná signed WORD DS:6276 s 100; B8E7 pri menšej hodnote preskočí diagnostiku `MAXGUARD exceeded (%d)`. Inak volá error helper s argumentom 100. B924 vloží pôvodný count ako argument, B928 ho zvýši a B92C volá `04C7:1692`.

Konštruktor `[6302,6377)` na 6308 počíta BX = WORD SS:[BP+6] * 1Ah, na 630C pridá 264Eh a na 6310 načíta ES z DS:255E. Tento globál leží v obraze 29C6E, má počiatočnú hodnotu 21FDh a skutočnú EXEPACK relokáciu. Pri normálnom count 0..99 je presný nominálny rozsah 100*26 B. End 3076h sa zhoduje so začiatkom už analyzovaného ďalšieho poľa, ale táto zhoda nie je primárnym dôkazom.

DS:6276 je pri default DS=2771h v runtime obraze 2D986h, mimo súboru a pôvodných NON-CODE bajtov; do prírastku sa nezapočítava. Signed porovnanie ani konštruktor nezabraňujú zápornému indexu pri poškodenom stave. Error helper smeruje na CRT exit, jeho globálny non-return kontrakt ešte nie je uzavretý. Preto limit nie je dokázaná ochrana všetkých možných zápisov.

## Pozorované počiatočné zápisy

| Pole slotu | Šírka | Zápis |
|---|---:|---|
| +2 | 4 B | 0 |
| +6 | 2 B | 0 |
| +8 | 2 B | argument SS:[BP+0C] |
| +0D | 1 B | 0 |
| +10 | 1 B | FFh |
| +0E | 1 B | AL helpera 00F7:0176, iba keď AX != FFFFh |

Nasledujú volania 04C7:1660 a 083D:117A s pointermi na tento slot a pôvodný objekt. Ich kompletné účinky, všetky polia a AI stavové prechody zostávajú otvorené. Samotná alokácia záznamov neuzatvára GUARD správanie ani bossov.

```text
if object.flags & 8:
    if signed16(guard_count) >= 100: error_helper(...)
    index = guard_count
    guard_count += 1
    construct_guard(index, object_pointer, object_index, variant)

construct_guard(index, ...):
    slot = segment_global_255e : ((0x264e + index*26) & 0xffff)
    initialize_observed_fields(slot)
    call_remaining_initializers(...)
```

## Meranie a reprodukcia

`audit_pass1_guard_slots.py IMAGE PRIOR_MAP DECODER_DIR OUT` používa `relocations.csv` vedľa IMAGE. Kontroluje SHA, relokáciu, limit/count volanie, konštruktorový stride a bázu, počiatočné nuly a intervalové SHA. Produkuje 100 presných slotov, dátový rozsah, nezávislé ASM a CSV/JSON mapu v `pass1_guard_slots/`.

Nových **2 600 B PARTIAL** bolo UNKNOWN. Aktuálne **PARTIAL 45 891 B, CLASSIFIED ONLY 9 222 B, UNKNOWN 2 182 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Predošlá mapa: 43 291 / 9 222 / 4 782 / 0 B. Nové originálne runtime/replay testy: 0.

DOSBox-X plán: logovať count/index, segmentový globál a zápisy do prvého/posledného slotu, error vetvu pri 100 a životnosť po LOAD/zmene úrovne. Ďalší krok: zvyšných 2 182 UNKNOWN bajtov a podvolania konštruktora, bez odvodzovania AI parity z layoutu.


## Aktualizácia 13 oblastí

Nové sémantické percento všade N/A: chýba úplný inventár kontraktov/polí/vetiev. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické čísla sú orientačné.

| Oblasť | Predošlý odhad | Nové % | Nový dôkaz | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | no new format evidence | formát a bounds | DS:3F64 producent |
| Dátové typy a konštanty | 95 % | N/A | 2 600 B guard slots PARTIAL | ostatní writeri | write xrefs |
| Tabuľky a ukazovatele | 93 % | N/A | 100 nominal records, stride 26 | resource index | caller bounds |
| Funkcie / ASM / CFG | 90 % | N/A | producer limit and constructor layout | prirodzená dosiahnuteľnosť | runtime dĺžky |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping/VGA stav | framebuffer/DAC |
| GUARD / bossovia | 93 % | N/A | 100x26 nominal slots and initial fields | AI and lifecycle | helpers 1660/117A |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | resource binding | draw xrefs |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | pointer restore | tabuľky po LOAD |
| Windows Win16 | 92 % | N/A | bez nového dôkazu | runtime selektory | DS callbacku |
