# Nitemare 3D — renderer v0.72: prvá rozdielna fáza a fail-closed pixelová akceptácia

**20. 10. 2026. Stav: vytvorený nový testovací a diagnostický nástroj; nie je to 100 % pixel-perfect renderer.**

## Čo je nové

Archívny Pass 45 už obsahoval analyzátor VEC → owner → spany → textúry → frame. Jeho pôvodná kontrola synchronizácie bola iba cez episode/level/player/angle/viewport. Nový `tools/n3d_v072_stage_frame_gate.py` tieto princípy prepája s prísnejšími povinnými údajmi z v0.71 a ďalšími kontrolami integrity vstupných súborov. V0.72 **nie je náhradou Pass 45**: neanalyzuje jednotlivé texelové kroky U/V; identifikuje prvú nesúhlasnú hrubú fázu pred spustením detailného Pass 45 diagnózy.

**Rovnako podstatné:** VEC, owner ani span sa neporovnávajú cez náhodne neinicializované bajty. Pôvodný DOS má 28-bajtové VEC, 16-bit owner pointery a **18-bajtové**, nie Win16 20-bajtové spany.

## Vstupné súbory: na oboch stranách rovnaká štruktúra

```text
<original-dir alebo candidate-dir>/
  manifest.json
  stages/35_span_build_end/
    vec.bin          28000 B = 1000 * 28
    owner.bin          642 B = count(2) + 320 * owner(2)
    spans.bin          910 B = 10B prefix + 50 * 18B
  frame.idx          64000 B = 320 * 200
  dac.bin              768 B = 256 * RGB6
```

Porovnáva sa **len prvých `vec_count` VEC** (v predchádzajúcom checkpointe 592), aktívnych **304 ownerov** plus zostávajúci počet, a **len použité spany** spolu s count. Nulový diff v nepoužitých slotoch sa nevyžaduje. Všetky celé zdrojové súbory však musia prejsť deklarovanou SHA-256 kontrolou.

`owner.bin` má prefix `DS:4562` a potom DS:4564+2*x. `spans.bin` má počet pri DS:4D64, 10-bajtový prefix/gap a následne aktívne záznamy. Originálny `BF45` je stav po span builderi. Originálny `C26F` je post-present; nesmú sa zamieňať ako ten istý bod vykonania.

## Povinný manifest

Príklad pre **syntetický** checkpoint:

```json
{
  "format": "n3d-dos20-stage-frame-v072",
  "role": "original-dos2",
  "reference_exe_sha256": "552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301",
  "data_manifest_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "episode": 1, "level": 1, "game_tick": 42,
  "player_x": 1440, "player_y": 3620, "angle_units": 80,
  "world_state_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "render_checkpoint": "post-present",
  "palette_phase": "gameplay",
  "stage_checkpoint": "post_span",
  "frame_checkpoint": "post_present",
  "vec_count": 592,
  "capture_sha256": {
    "vec.bin": "<SHA-256 skutocneho suboru>",
    "owner.bin": "<SHA-256 skutocneho suboru>",
    "spans.bin": "<SHA-256 skutocneho suboru>",
    "frame.idx": "<SHA-256 skutocneho suboru>",
    "dac.bin": "<SHA-256 skutocneho suboru>"
  }
}
```

Kandidát musí mať rovnaké hodnoty spoločného herného stavu a `role: candidate`, ale **svoje vlastné SHA-256 súborov**. Obsah SHA v príklade je ilustračný, nie autentický. Hash svetového stavu musí byť odvodený rovnakou kanonickou serializáciou na oboch stranách; iba ručné vypísanie zhodných hashov nepreukazuje synchronizáciu.

## Prvá odlišná fáza / návratové kódy

| Výsledok | Význam |
|---|---|
| `INCOMPARABLE` (exit 2) | Chýbajúci/mismatched manifest, súbor, dĺžka, SHA-256, VEC count, owner pointer, span pointer, owner count alebo iný herný stav. **Žiadne pixelové hodnotenie.** |
| `VEC_MISMATCH` (exit 1) | Rozdiel už v aktívnych world/projected VEC záznamoch. |
| `OWNER_MISMATCH` (exit 1) | VEC sedia, odlišný per-column owner alebo unowned count. |
| `SPAN_MISMATCH` (exit 1) | VEC/owner sú zhodné, odlišný span count / 16.16 medzivýsledok. |
| `FRAME_MISMATCH` (exit 1) | VEC/owner/spans sedia, no rozdiel v 320×200 indexed frame; prvé `(x,y)` a či patrí do 3D viewportu. |
| `DAC_MISMATCH` (exit 1) | Indexované pixely sedia, ale 768 komponentov RGB6 nie; prvý paletový index/kanál. |
| `PASS` (exit 0) | Presná bajtová zhoda **iba** pre dodané kontrolné body, nie pre celú hru. |

```bash
python3 tools/n3d_v072_stage_frame_gate.py \
  --original /secure/original-e1m1-checkpoint \
  --candidate /secure/port-e1m1-checkpoint \
  --out /tmp/n3d-stage-diff.json

python3 -m unittest discover -s tests -p test_n3d_v072_stage_frame_gate.py -v
```

Testy sú syntetické, bez pôvodných komerčných súborov. GitHub Actions spúšťa testy na Linuxe aj Windows. Aplikácia nemusí mať zatiaľ automatický export všetkých piatich súborov; **v0.72 nie je dôkaz, že už existuje synchronizovaná originál-kandidát dvojica**.

## Statický CFG probe pre 67 bajtov mimo pôvodných runtime trace

`tools/n3d_v072_dos2_gap_cfg_probe.py` dopĺňa v0.71 audit kontrolovanej originálnej DOS2 EXE. Pri **SHA-256 presne zhodnom** `N3D-E-20.EXE` používa Capstone v 16-bitovom režime a hľadá priamo dosiahnuteľné inštrukcie v oblastiach `CAB8` a `1021E` vrátane 51B a 16B medzier. Dáva offsety a mnemoniky; neexportuje celé strojové bajty pôvodnej hry.

```bash
python3 -m pip install capstone==5.0.3
python3 tools/n3d_v072_dos2_gap_cfg_probe.py \
  --exe /private/N3D-E-20.EXE \
  --out /tmp/n3d_v072_dos2_cfg.json
python3 -m unittest discover -s tests -p test_n3d_v072_dos2_gap_cfg_probe.py -v
```

**Vysoká opatrnosť:** statický 16-bitový direct-CFG disassembler nie je ekvivalent pôvodnej inštrukčne presnej analýzy. Nepriamy skok, FAR segmentový transfer, aliasovaný kód, data overlay a sémantika relatívneho IP môžu uniknúť; každý taký prípad sa uvádza ako neistota. Ani inštrukcia dekódovaná z EXE nie je automaticky runtime dosiahnuteľná. Označenie `not_reached_by_direct_cfg` nikdy neznamená preukázaný mŕtvy kód.

Na GitHub CI sa testuje len na vytvorených 8086 syntetických úryvkoch (podmienené/nepodmienené skoky, nepriamy skok, hranice funkcie, normalizácia nad 64 KiB). V tomto passe sa **nepublikuje ani nespúšťa komerčný originálny EXE v GitHub Actions**. Ak miestne vykonávanie originálneho EXE nie je dostupné, sémantická runtime uzávierka 51+16 B zostáva otvorená.

---

## Čo nie je uzavreté

1. Originálny DOS v2.0 `CAB8` zostáva na **1009/1060 runtime** opcode bajtoch; nevykonaná oblasť `CD9D..CDCF` má 51 bajtov. `1021E`: **656/672**, štyri 4B sloty. Statické čítanie ich obsahu a všetky vetvy ešte nie sú inštrukčne preukázané v tomto passe.
2. Regenerovať všetkých 592 VEC z identického MAP/EXE variantu. Správna pôvodná kamera a DEMO RNG sú nutnou, nie postačujúcou podmienkou.
3. Pripraviť automatický capture `manifest.json`, indexov, DAC aj stage medzivýsledkov v origináli a vo VEC kandidátovi pri zhodnom ticku.
4. Presné DOS U/V, texel/shade mapovanie, dynamické steny a sprity. Pri zhode spanov použite historický **Pass 45 per-column trace** pre prvý rozdielný texel.
5. Produkčný `src/renderer/Raycaster.cpp` naďalej renderuje iba **diagnostický DDA preview**. Nezapínať VEC pod označením 1:1, kým nebude skutočné original-vs-port frame+DAC zero-diff a následná širšia regresná sada.

**Proveniencia:** SHA-256 v manifestoch preukazujú integritu voči deklarovanému manifestu, **nie autentickosť pôvodu**. Aktuálny nástroj nepristupuje k DOSBox-X ani nepotvrdzuje, kto dáta zachytil.
