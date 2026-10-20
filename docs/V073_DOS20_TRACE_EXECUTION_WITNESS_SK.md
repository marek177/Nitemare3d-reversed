# Nitemare 3D — Renderer 1:1 research pass v0.73 (2026-10-20)

**Status:** `TRACE_WITNESS_TOOL_VALIDATED_SYNTHETIC`; **original DOS2 execution not rerun in this pass**; `PIXEL_PERFECT_ORIGINAL_VS_PORT = OPEN`.

## Nová forenzná hranica dôkazu

Predchádzajúci v0.70 register uvádzal **324/324 FEFA**, **1009/1060 CAB8** a **656/672 1021E** „opcode coverage“ z archívnych `N3DTRC01` CPU pre-state záznamov. Každý CPU záznam však obsahuje **až 16 bajtov lookahead**, nielen práve vykonanú inštrukciu. Ak bolo niekoľko bajtov iba v pre-state okne, nesmieme ich automaticky počítať ako vykonané.

Nový [v0.73 trace witness](../tools/n3d_v073_dos2_gap_trace_witness.py) preto rozlišuje:

1. **`lookahead_matching_gap_bytes`** — staticky zhodné bajty viditeľné v 16-B CPU trace oknách; nemusia byť vykonané;
2. **`executed_decoded_gap_bytes`** — bajty skutočnej (Capstone dekódovanej) inštrukcie, ktorej **prvá pozícia** bola zachytená ako aktuálne `CS:IP`, prefix sa zhoduje s presnou originálnou EXE a `code_valid >= instruction length`;
3. **`observed_branch_targets_from_CBF2`** — páry nasledujúcich CPU stavov po overenej skokovej inštrukcii na `CBF2`, osobitne early-return `CED6` a pokračovanie `CBF6`;
4. **`semantic_equivalence_proven = false`** — ani úplné vykonanie inštrukčných bajtov samo nepreukazuje správnosť nášho C++ algoritmu pre všetky možné stavy.

## Originálne binárky a vstupné podmienky

- Presný rozbalený DOS2 `N3D-E-20.EXE`: SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`, 116 606 bajtov. Neznáme alebo iné vydanie sa odmietne.
- `N3D_DOS20_RENDER_RUNTIME_20261019.zip` obsahuje staršie autentické `N3DTRC01` záznamy. Tieto vstupy sú v súkromnom používateľskom archíve a nie na GitHube.
- Volajúci musí explicitne dodať správny DOS real-mode **load segment** (`--load-segment`). Historicky bol pre niektoré DOS2 relácie `0x0824`, no nemá sa prenášať na iné relácie bez overenia.
- Sledované rozsahy load-image: `CAB8..CEDB` (1060 B), `FEFA..1003D` (324 B) a `1021E..104BD` (672 B). MZ file offset = load-image offset + `0x200`.
- Bez aspoň **32** zhodných vykonaných CPU inštrukcií v sledovaných rutinách je ZIP odmietnutý ako nedostatočný na forenzné hodnotenie. Táto hranica bráni náhodnému úspechu pri zlom load segmente; nie je to dôkaz autenticity pôvodu.

### Reprodukcia na súkromnom pracovnom počítači

```bash
python3 -m pip install capstone==5.0.3
python3 tools/n3d_v073_dos2_gap_trace_witness.py \
  --exe /private/N3D-E-20.EXE \
  --trace-zip /private/N3D_DOS20_RENDER_RUNTIME_20261019.zip \
  --load-segment 0x0824 \
  --out /tmp/dos2_v073_gap_witness.json
```

Ak konkrétna relácia používa inú load základňu, hodnotu zmeňte. Nástroj nikde nepublikuje strojový kód hry — produkuje iba offsety, počty, SHA-256 a flagy neistoty. Analytický výsledok nezvyšuje pixelové percentá bez samostatného framebuffer dôkazu.

## Validácia CI (syntetické dáta, bez hry)

[GitHub Actions — Linux a Windows](https://github.com/marek177/Nitemare3d-reversed/actions/runs/39444761761) skončilo **PASS**: 15/15 syntetických Python testov na každom OS. Konkrétne rozlišujú lookahead a vykonané bajty, zachytia krátke alebo poškodené CPU okno, odmietnu nesprávny relocovaný segment a testujú obidve vetvy po `CBF2`. Zahŕňajú aj falošný preskok z inštrukcie, ktorá nie je skokom. V tomto CI **nebol spustený originálny EXE ani runtime replay 14 miliónov udalostí**.

## Otvorené projekčné vetvy

| Rutinová oblasť | V0.70 trace-window coverage | Čo musí potvrdiť v0.73 original-input beh |
|---|---|---|
| `FEFA` | 324/324 B | Počet skutočne dekódovaných a vykonaných bajtov vrátane 0→2 orientačnej vetvy |
| `CAB8` | 1009/1060 B | Či `CD9D..CDCF` je vôbec vykonané, za akých uhlov, presná 16-bit clippingová aritmetika |
| `1021E` | 656/672 B | Vykonanie štyroch 4-B pokračovacích úsekov `10408`, `1043D`, `10472`, `104A6` a prípadné nepriamo dosiahnuteľné vetvy |

**Aktuálne platí:** 51+16 B je medzera **v predchádzajúcom trace lookahead pokrytí**, nie dôkaz neexistujúceho kódu ani potvrdenej mŕtvej vetvy. Samotné čísla z v0.70 **nesmú byť automaticky prezentované ako úplné vykonanie**.

## Čo najbližšie posunie 1:1

1. Získať pri rovnakom gameplay ticku originál i kandidátne `VEC/owner/spans/frame.idx/dac.bin/manifest.json` a prehnať ich cez [v0.72 Stage Frame Gate](../tools/n3d_v072_stage_frame_gate.py).
2. Ak VEC/owner/spany sedia a frame je rozdielny, využiť historický Pass 45 per-column trace na opravu konkrétneho `wall-U/V`, IMG textúry a shade LUT — bez ručných per-pixel patchov.
3. Doplniť DOS2 špecifické cardinal/near-plane a remaining FEFA runtime vetvy s novým skutočným originálnym trace.
4. Až po **0/64000 rozdielnych indexed pixelov a 0/768 DAC komponentov** vo viacerých scénach prepnúť živý VEC renderer namiesto diagnostického `Raycaster.cpp`.

**Stav GitHub main:** tento pass pridáva iba izolovaný forenzný Python nástroj, jeho testy, CI a dokumentáciu. **Produkčný DDA, `src/main.cpp` a `src/renderer/Raycaster.cpp` sa nemenia.**
