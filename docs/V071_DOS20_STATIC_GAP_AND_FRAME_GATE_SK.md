# Nitemare 3D DOS v2.0 — v0.71: opcode-gap a prísna pixelová akceptácia

**Dátum:** 20. 10. 2026. **Stav:** statický proof tooling a syntetická automatická validácia. **Nie je to hotový renderer 1:1.**

## 1. Prečo je 67 bajtov dôležitých

V0.70 pôvodný CPU trace pokrýval FEFA 324/324 B, CAB8 1009/1060 B a 1021E 656/672 B. Pri CAB8 ide o obraz `CD9D..CDCF` (51 B); pri 1021E o štyri 4-bajtové oblasti `10408..1040B`, `1043D..10440`, `10472..10475`, `104A6..104A9` (16 B).

Nejde o 67 stratených strojových bajtov. Rozbalený originálny DOS2 `N3D-E-20.EXE` je dostupný v používateľskom archíve, má 116606 B a známy SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`.

Nový [statický opcode audit](../tools/n3d_v071_dos20_opcode_gap_audit.py) presne mapuje hranice z **load-image offsetov** do MZ file offsetov (+512), vyžaduje zhodný SHA-256 celého EXE, kontroluje známu FEFA fingerprint z original trace a vytvára JSON s SHA a nulovosťou každého nepozorovaného úseku. **Nevypisuje/distribuuje komerčné strojové bajty.**

**Dodatočné statické upozornenie:** v archivovanom Ghidra exporte `N3D-E-20.EXE(5).c` má funkcia `FUN_1000_fefa` upozornenia na prekryté inštrukcie pri `0x10026/0x10028` a na nesprávne inštrukčné dáta. Preto sa pri riešení okrajových vetiev nesmie zameniť dekompilovaný C za pôvodné opcode bajty. Tento export nedokazuje, že originál skutočne vykonáva neplatný kód.

**Dôkazová hranica:** pri tomto passe nebola možná lokálna binárna exekúcia/verifikácia na originálnom EXE. Preto 67 bajtov ostáva otvorených na sémantické čítanie a runtime reachability; syntetické úspešné testy nie sú originálny runtime dôkaz.

## 2. Presná akceptačná brána originál ↔ remake

[Frame gate](../tools/n3d_v071_frame_parity_gate.py) berie už normalizované 320×200 indexed8 obrazy a 768B 6-bit DAC z **obidvoch** behov. Uplatňuje prísne porovnanie manifestov: `reference_exe_sha256`, `data_manifest_sha256`, `episode`, `level`, `game_tick`, `player_x`, `player_y`, `angle_units`, `world_state_sha256`, `render_checkpoint`, `palette_phase`. Role musia byť `original-dos2` a `candidate`.

Pri nesúhlasnom stave odmieta vydať pixelové hodnotenie; pri porovnateľnom stave vypíše počty rozdielov, prvý rozdielny index `(x,y)`, bounding box a prvý chybný DAC komponent. Syntetický beh môže byť PASS, ale označenie `SUPPLIED_PAIR_BYTE_COMPARISON_ONLY` **nepreukazuje autentickosť zdrojových súborov ani paritu iných scenárov**.

CLI:

```sh
python3 tools/n3d_v071_dos20_opcode_gap_audit.py --exe /private/N3D-E-20.EXE --out /tmp/gaps.json

python3 tools/n3d_v071_frame_parity_gate.py \
  --original-frame orig.idx --candidate-frame port.idx \
  --original-dac orig.dac --candidate-dac port.dac \
  --original-state orig.json --candidate-state port.json \
  --out /tmp/frame_diff.json
```

## 3. GitHub CI a rozsah

Reprodukčná sada sa spúšťa v [GitHub Actions workflow](../.github/workflows/renderer-v071-static-gap.yml) na Linuxe aj Windows, s Python 3.12, bez originálneho EXE a bez používateľových gameplay dát. Sú zahrnuté syntetické testy byte coverage, SHA guardu a odmietania rozdielnych herných tickov/pixelov.

**NEOVERENÉ:** samotných 51 + 16 bajtov v konkrétnom EXE cez tento nástroj, presné DOS2 kardinal clipping vetvy, zhodné MAP→592 VEC pre viac máp, originálna IMG/shading/sprite/HUD kompozícia, akákoľvek synchronizovaná originál↔remake frame dvojica.

## 4. Priorita v0.72

Staticky prečítať originálne `0xCD9D..0xCDCF` a štyri sloty `1021E` do instruction/CFG reportu, korelovať ich so skutočne vykonanými skokmi, potom v rovnakom gameplay checkpointe zachytiť originál `frame.idx + dac + state.json` a rovnaké dáta z kandidátneho VEC renderera. Neprepínať produkčný `Raycaster.cpp` bez opakovateľného 0/64000 indexed a 0/768 DAC porovnania.
