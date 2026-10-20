# Nitemare 3D DOS v2.0 — Renderer 1:1, originálne IMG → SHADE → U/V → VGA, v0.80

**Dátum: 20. október 2026.** **Výsledok:** prvý presný 42-pixelový originálny stenový stĺpec, autentické DOS2 dáta, natívny C++20 replay overený voči pôvodnému výstupu. **Nie je to 100 % pixel-perfect celý remake.**

## 1. Zdrojové súbory a pôvod

Použil som súkromné používateľské archívy `all-nite3d.zip` a `N3D_DOS20_RENDER_SCALED_COLUMN_20261019.zip`, nie Windows textúry.

| Súbor / zdroj | Veľkosť | SHA-256 |
|---|---:|---|
| DOS2 unpacked `nd-3-20/N3D-E-20.EXE` | 116 606 B | `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301` |
| DOS2 `nd-3-20/IMG.1` | 2 244 774 B | `faf0cec3502d8b86ebb30a432b46b467e349864987f91a1c26358a9a5ca58cb1` |
| DOS2 `nd-3-20/MAP.1` | 90 626 B | `3eddb0ad3a29e93d63fa16e9b8cfbb434d3699a84bd5372ed2d6f4a1e89c42fc` |
| Originálny DS 64 KiB (`proof/stack_segment.bin`) | 65 536 B | `1878c03fbd7f40d06dd87691e608d6143c16de0dcb347894d0e0bd6c2a49d98e` |
| Pôvodný zdrojový segment textúr | 65 536 B | `6583c247531a69ed60e98c9d5d345178c2a6574f24676a655ed7be34e35ecc9b` |

`IMG.1` DOS2 **nie je** identické s Win16 `IMG.1` (`2d955091…60311`). Pôvodnú hru som v tomto v0.80 behu **znovu nespúšťal**; ide o *offline original execution replay* z autentického skôr zachyteného runtime.

## 2. Originálna geometria a IMG cache

Z pôvodného segmentu: 592 unikátnych VEC záznamov s dĺžkou 28 B; **592/592 VEC+04 cache indexov** presne súhlasí s pořadím **33 originálnych IMG wall streamov**. Žiadne ručné preusporiadanie cache.

Pre 3D stĺpec `x=8` má pôvodný `DS:4564[x]` owner pointer `0x89B8`, index VEC 357, `wallId=16`, `renderClass=2`, orientáciu `2`, flags `7`, animation frame `0`, cache selector `18`.

Originálna IMG wall directory pre ID16 ukazuje na stream **`0x3CCFA`**, frame 128×64. V original textúrovom segmente na `DS:SI=A742` je presná 64B textúrová columna, ktorá sa v IMG ID16 nachádza **jednoznačne na fyzickom U=106**. Súhlasí úplne **64/64 byte**, bez použitia DDA a bez zmenšovania 128×64 na 64×64.

## 3. Kľúčové zistenie: stav pred vs. po 16.16 kroku

Originálna assemblerová rutina **2500/25DC** vykonáva:

```text
image 267A: MOV AX,[BX+10h]     ; HIGH word of current span accumulator
image 2680: MOV EAX,[BX+0Ah]    ; 16.16 slope
image 2684: ADD DWORD [BX+0Eh],EAX  ; increment span accumulator
image 26A6: FAR CALL CEDC       ; perspective computation consumes original AX
```

Naše originálne DS bolo zachytené už **po** vykonaní `2684`. Uložený 16.16 akumulátor v `DS:4D7C` = `0x014B800F`, krok = `−178403`. Predchádzajúci akumulátor je preto **`0x014E38F2`**. Horné slovo použité pred krokom bolo **334** (nie 331 už uložených v pamäti).

| Výpočet | Mid-render po kroku (nesprávne pre x8) | Pred vykonaním kroku (originál) |
|---|---:|---:|
| SpanY Q4 v CEDC | 331 | **334** |
| CEDC AX | 273 | **270** |
| Miestna korekcia 25DC | −292 | −292 |
| Finálne U | 109 | **106** |
| Odlišné pixely oproti originálu na x8 | **31/42** | **0/42** |

**Nejde o „texture U bias −3“.** Opätovné použitie RAM dumpu uprostred vykresľovania ako vstupného **post-span pre-draw** checkpointu je nesprávne. Riešením je explicitne obnoviť presnú časovú fázu uloženia jednej DWORD hodnoty, s SHA kontrolou originálneho EXE/snapshotu. **Vo všeobecnom C++ rendereri nesmieme pridať konštantnú korekciu U.**

## 4. Originálny shader a pixelové zápisy

Pri originálnej úrovni `WORD DS:6278 = 2` sa používa shade amount `8` z rozsahu `[0,4,8,12,16,20,30,40]`. Z pôvodnej RGB6 palety na `DS:4A64` som nezávisle prepočítal všetkých 256 nearest-color položiek DOS funkcie `16CE` (Manhattan RGB6 + first-minimum). **256/256** sa zhoduje s pôvodnou tabuľkou `DS:D20C`; SHA256 oboch je:

`915246ff64f0553bb4d4683039c4167e885348f03b3a4e3240655f22f157c913`.

Originálny writer `097A:0599..05D5` pri `x=8`, `y=59..100`, `CX=42` používa zdrojový 16.16 krok `0x00018F9C`. Skutočné IMG U106 + živý XLAT vytvorili **42/42 správnych indexovaných pixelov**. Originál zmenil iba týchto 42 pozícií v interleaved VRAM, a rekonštrukcia celej nasledujúcej **2 097 152 B VRAM** má **0 rozdielnych bajtov**. Je to kontrola jedného *pôvodného vykonaného writeru*, nie hotovej celohrovej scény.

## 5. Natívna aktuálna C++20 implementácia spustená

Namiesto iba statického Python modelu som získal aktuálny headless Linux C++20 `n3d_dos20_wall_replay` z úspešného GitHub Actions buildu [39487291966](https://github.com/marek177/Nitemare3d-reversed/actions/runs/39487291966), artefakt `n3d-dos20-wall-replay-ubuntu-latest` (SHA256 ZIP: `f1c8b61fc069e62e89ce7fd22031789391d158616c99a04d710ef8c0ac07b76c`). Kód a exe boli zostavené bez pôvodných komerčných dát; až tu som ich lokálne spojil s používateľovým originálnym DOS2 checkpointom a IMG.

**Natívny C++20 beh po obnovení pred-krokovej fázy:** 592 VEC, 9 spanov, 304 vykreslených stenových stĺpcov, **16 930 generovaných stenových pixelov**, nula vynútených animation-frame clampov. `candidate.u` má 304 bajtov, SHA256 `6417793492df2c4a83a7797de30092a01204c5607c75161324792e06f3293cd1`. V natívnom výstupe je v stĺpci x8 fyzické IMG U106, `y=59..100`, zhodných **42/42 indexov** s originálnym skutočným writerom.

Pri pôvodnom **neopravenom mid-render** DS generuje C++ v x8 U109 a **31/42** chybných pixelov — priamy príčinný kontrast. Ak sa do pôvodného **pred-zápisového** 64 000-bajtového indexed framebufferu vloží **iba tento jeden** korektný C++ stĺpec, výsledok má **64 000/64 000** bajtov zhodných s pôvodnou *nasledujúcou jednou originálnou writer snímkou* (SHA256 oboch `b0f5604753329d7aa58a248b90c9aee651c25733e264dc2a2213c1003145e8cf`). Tento limitovaný single-writer test sa **nesmie nazývať 100 % paritou remaku**.

**Žiadny platný porovnateľný originálny post-wall celý frame** nemáme pri tomto reálnom 304-stĺpcovom výstupe. Dvojica pôvodných VRAM dumpov je z intervalov **pred/po jednom zápise x8**, nie pred/po vykreslení všetkých 304 stĺpcov. Preto neuvádzam „16 930/16 930 matched“ ani nula full-frame rozdielov originál↔port.

## 6. Reprodukcia (všetko bez originálnych dát v distribučnom ZIP)

```bash
python3 tools/n3d_v080_authentic_img_wall_oracle.py \
  --game-zip /private/all-nite3d.zip \
  --renderer-zip /private/N3D_DOS20_RENDER_SCALED_COLUMN_20261019.zip \
  --out /tmp/v080_original_img_wall.json

python3 tools/n3d_v080_midrender_stage_normalizer.py \
  --ds /private/original_DS_65536.bin --exe /private/N3D-E-20.EXE \
  --out-ds /tmp/normalized-postspan-DS.bin \
  --out-proof /tmp/phase_alignment.json

n3d_dos20_wall_replay --ds /tmp/normalized-postspan-DS.bin \
  --img /private/IMG.1 --vec-count 592 --page 0 \
  --background-frame /private/original_pre_writer_320x200.idx \
  --output-dir /tmp/native_wall_candidate
```

V konverzačnom ZIP nájdeš zdrojové Python verifikátory, sedem selftestov a dva **odvodené** JSON výsledky. Pôvodné EXE/IMG/MAP/VRAM/DS ani binárne framebufferi nie sú v distribučnom ZIP.

**CI:** testy samotného C++ nástroja prešli na GitHub Linux aj Windows; zdrojový SHA-locked normalizátor má samostatnú asset-free GitHub Actions sadu. Lokálne testy vrátane súkromného originálneho DS/EXE/IMG/VRAM: **7/7 PASS**.

## 7. Ďalšie dôkazové povinnosti v0.81

1. Získať kontrolný bod originálneho DOS2 runtime **po dokončení celého stenového vykreslenia (`BF5F`)**, s rovnakou kamerou, RNG tickom a IMG/PAL obsahom, nielen po jednom stĺpci.
2. Na tom istom tiku spustiť C++ kandidáta, overiť 304× source IMG/frame/U/V/shade a presné tie-breaky, vytvoriť per-pixel first-divergence report.
3. Až potom zjednotiť aj sprite queue, priehľadnosť `0x1F`, HUD, background a page flip a porovnať plných **64 000 indexovaných bajtov + 768 DAC komponentov**.
4. Neprepínať `src/renderer/Raycaster.cpp`, kým máme len ohraničený writer replay namiesto scénovej a následnej regresnej parity.

**Aktuálny stav: pre jedného skutočne vykonaného originálneho stenového writeru máme prvú plne reprodukovanú DOS2 source→IMG→U/V→XLAT→VGA vetvu; celá scéna a plná hra stále otvorené.**