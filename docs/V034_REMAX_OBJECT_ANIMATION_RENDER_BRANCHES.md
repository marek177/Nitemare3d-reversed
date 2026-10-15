# Nitemare 3D RE MAX v0.34 – animačné vetvy OBJECT v renderer-i

**15. október 2026.** Pokračovanie po v0.33.  
**Dôkaz:** priamo skontrolovaný pôvodný DOS v2.0 unpacked MZ image, SHA-256
`e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`,
171 360 bajtov po odrezaní MZ hlavičky. Adresy nižšie sú **offsety v tomto
image**, nie offsety Windows NE, pôvodného packed DOS EXE ani aktuálne fyzické
segmentové adresy počas behu.

**Nový výsledok:** tri konkrétne cesty menia bajt animačného snímku
`OBJECT+03` v rámci kreslenia SPAN alebo projekcie objektu. Nie je dokázaný
jeden univerzálny scheduler, ktorý bezpodmienečne iteruje všetky OBJECT
záznamy v jednom hernom ticku.

## 1. Pôvodné priame CALL hrany

Nasledujúce adresy sú overené z originálnych CALL inštrukcií vrátane
16-bit segment:offset normalizácie. Samotná existencia priameho volania
**nepotvrdzuje**, že sa vykoná každý tick; branch preconditions, culling a
vnorenia je potrebné overovať oddelene.

| CALL site | Priamy cieľ | Kontext |
| --- | --- | --- |
| `C1EA` | `C150` | normálny FAST, len keď je príslušný pomalý bucket due a DEMO mode=0 |
| `C22E` | `C150` | alternatívny FAST v DEMO vetve pri starom render-generation bit0=1 |
| `C239` | `BF36` | samostatná frame/render vetva outer scheduleru |
| `BF40` | `213E` | zostavenie/obnovenie viditeľných SPAN dát; počítadlo `DS:4D64` |
| `BF5A` | `2500` | prechod po SPAN záznamoch |
| `2721` | `241E` | aktualizácia frame na SPAN objekte, len pri nenulovom intervale |
| `BF5F` | `21F0` | priechod po priestorovo zoradených objektoch |
| `2225` | `B2D4` | projekcia jedného vybraného objektu zo zoradenia |
| `8307` | `B2D4` | **projektily** tiež volajú tú istú projekčnú funkciu |
| `B521` | `B22C` | normálna projekčná animácia |
| `B532` | `B17E` | smerová alternatíva pre triedy `0x2C/0x2D` |
| `C246` | `0AEA` | samostatný posun secret panelu vo frame vetve |
| `C24B` | `8230` | samostatná aktualizácia projektilového poolu vo frame vetve |

Dve korekcie starých domnienok:
- `C153` volá `C51A`, kde je samostatná inštrukcia `RETF`; **nie je to OBJECT update**.
- `C172` volá `0E50` – podľa v0.33 ide o šesťbajtový **PUSH** pool, nie všeobecný OBJECT scheduler.

## 2. Presné lokálne podmienky aktualizácie

### SPAN → `241E`

Volajúca funkcia `2500` číta SPAN pool `DS:4D64/4D6E` a cez
`OBJECT+04` vyhľadáva 8-bajtový descriptor. Na `2716` kontroluje
`word descriptor+02 != 0` pred volaním `241E`. Inými slovami:
**každý OBJECT v pamäti sa touto cestou automaticky nespracuje**.

V `241E`:
- `2427–242F`: porovnáva `OBJECT+08` (32-bit animačný deadline) s
  časom `DS:081E`; skok `JA` vynechá budúci deadline.
- `2433`: ak už termín nastal, zvýši `OBJECT+03` o 1.
- `2436–24E5`: triedovo/sekvenčne špecifické rozhodnutia (vrátane tried
  `0x07`, `0x2D`, `0x2F` a resetu frame).
- `2478`: variantná vetva volá spoločný RNG na `0FBA:01A0`, maskuje
  výsledok `& 7` a môže sa vracať do výberu variantu.
- `24E6–24F9`: zapisuje nový 32-bit deadline z aktuálneho času +
  intervalu descriptoru.

**Dôsledok pre 1:1:** pri render-coupled vetve môže vzniknúť RNG draw.
Preto nie je bezpečné modelovať RNG len ako GUARD/combat tick stream alebo
predpokladať, že počet RNG odberov je od počtu vizuálne spracovaných objektov
nezávislý. Presný draw-count v konkrétnej scene ešte treba zachytiť runtime.

### Projekcia → `B22C / B17E`

`B2D4` najprv na `B2E0` testuje `OBJECT+05 & 1` a ďalej vykonáva
projekčné a clipping kontroly (napr. `B325`, `B38E`). Pred výberom
animátora oddeľuje triedy:

- **Trieda `0x05`**: bez tohto animation callbacku.
- **Triedy `0x2C` a `0x2D`**: `B532` volá `B17E`, bez
  podmienky `descriptor+02 != 0` používanej v normálnej vetve.
- **Ostatné triedy**: `B515` vyžaduje nenulový interval a následne `B521` volá `B22C`.

`B22C` má kontrolu deadline na `B235` a inkrement frame na
`B242`. `B17E` kontroluje deadline na `B1AE` a príslušný
inkrement na `B1B9`. Obe funkcie prijímajú referenciu na OBJECT a
pracujú so známym časovým základom `DS:081E`.

**Dôležitá výhrada:** B2D4 má viacero callerov vrátane projektilov
(`8307`). Je preto nepresné bez ďalšieho dôkazu tvrdiť, že celá jej
animačná logika je vyvolaná výhradne hlavným render loopom.

## 3. DEMO FAST používa starý render-generation counter

Pôvodný vonkajší scheduler kontroluje DEMO mode na `C21A`, potom
testuje **predchádzajúci** `DS:4540 & 1` na `C221`. Ak je bit
nastavený, `C22E` volá FAST. Až následné `C239 → BF36`
inkrementuje render-generation na `BF36`.

Preto sa DEMO odd-gate **nemôže** vyhodnocovať podľa hodnoty zvýšenej
až vo vnútri `BF36`. Toto je staticky uzavreté poradie týchto
inštrukcií, nie úplný model FAST/MAIN/DEMO catch-up alebo vnoreného RNG.

## 4. Čo je a nie je uzavreté

| Tvrdenie | Dôkaz / stav |
| --- | --- |
| CALL reťazec render pass → SPAN animator `241E` | **VERIFIED ORIGINAL STATIC** |
| Projekcia `B2D4` → animácia `B22C/B17E` | **VERIFIED ORIGINAL STATIC** |
| Deadline `OBJECT+08` a zmena frame `+03` | **VERIFIED ORIGINAL STATIC** pre uvedené tri vetvy |
| Variantný RNG z render-coupled `241E` | **VERIFIED ORIGINAL STATIC**, skutočný draw-count otvorený |
| DEMO odd render bit test pred `BF36` inkrementom | **VERIFIED ORIGINAL STATIC** |
| Automatické animovanie každého OBJECT na každom ticku | **NEDOKÁZANÉ**, nesmie sa tvrdiť |
| Úplný writer XREF census, všetky nepriame callsites a callbacks | **OPEN** |
| Viditeľnosť/occlusion a frame výsledok v DOSBox-X | **OPEN** |
| Presná jednotka času, nested FAST/MAIN a celé RNG seed=1 | **OPEN** |
| Pixel-perfect renderer a Win16 identické animácie | **OPEN** |

Tieto zistenia korigujú výskum tým, že **rozdávajú animáciu do konkrétnych
volajúcich funkcií**; samostatný monolitický OBJECT scheduler pre všetky
triedy sa nepovyšuje na CONFIRMED.

## 5. Reprodukcia (originály zostávajú súkromné)

Overenie SHA-256 aj originálnych 16 priamych CALL hrán a 18 krátkych opcode
witnessov:

```sh
python tools/n3d_v034_animation_probe.py \
    /path/to/N3D_DOS_v2.0_IDA.EXE

python -m unittest discover -s tests \
    -p "test_n3d_v034_animation_probe.py" -v
cmake -S . -B build -DN3D_ENABLE_SDL3=OFF
cmake --build build --target n3d_v034_object_animation_evidence_test
ctest --test-dir build -R n3d_v034_object_animation_evidence_test --output-on-failure
```

`n3d_v034_animation_probe.py` má **striktný hash gate** – alternatívny build
nesmie dostať tieto inštrukčné offsety. Jeho výstup explicitne obsahuje
`original_game_executed=false`,
`runtime_animation_order_verified=false` a
`complete_object_scheduler_identified=false`.
Syntetické testy verifikujú verifier, nie priebeh skutočnej hry.

**Ďalší dôkaz s najvyššou hodnotou:** DOSBox-X log od momentu vstupu do
frame branch, cez `BF36 → 2500 → 241E → RNG`, až po
`21F0 → B2D4 → B22C/B17E`, s identitou OBJECT,
hodnotou frame/deadline pred/po, počtom RNG odberov a dôvodom cullingu.
Druhá kontrolovaná scéna musí ponechať objekt mimo projekcie. Až potom
možno bezpečne povedať, či sa animácia mimo obrazu zastaví, dobieha alebo
je aktualizovaná iným callbackom.

## v0.37 refinement — DEMO FAST argument, not just frame parity

The `C221` odd-generation gate identified here is paired with a **second independent modulo-8 gate**: at `C228` the outer scheduler pushes `DS:3672` (slowCounter from `BEB4`), rather than the frame count, before calling `C150`. Inside `C150:C198` the conditional second `89A2` dispatch tests the supplied argument `&7`. Hence DEMO frame generation decides whether to call FAST, but slowCounter decides whether that FAST makes its gated second action pass. The quantizers also increment only once per changed quantized time sample; the outer scheduler has no local multi-tick replay loop. Detailed original code and regression tests: [v0.37](V037_REMAX_SCHEDULER_CATCHUP_STATIC_CLOSURE.md). Global nested callbacks and exact simulated speed are still OPEN.
