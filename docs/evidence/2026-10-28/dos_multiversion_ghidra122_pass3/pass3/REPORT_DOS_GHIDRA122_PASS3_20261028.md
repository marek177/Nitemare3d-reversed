# Nitemare 3D DOS — Ghidra 12.2 pass 3, 2026-10-28

## Finding

Šesť obnovených C dekompilácií CRT formátovacej rutiny; zlyhania 33 → 27, bez novej zlyhanej dekompilácie a bez pridania/odstránenia funkcií. Pre ďalších 12 zostávajúcich funkcií je dostupný normalizovaný Ghidra IR. IR sa nezapočítava ako obnovený C dekompilát.

| Obraz | Dokončené C predtým | Dokončené C teraz | Zostávajúce zlyhania |
|---|---:|---:|---:|
| 1.0 | 569/575 | 570/575 | 5 |
| 1.1 | 570/577 | 571/577 | 6 |
| 1.2 | 570/578 | 571/578 | 7 |
| 1.5 | 575/579 | 576/579 | 3 |
| 1.7 | 577/580 | 578/580 | 2 |
| V1.9 (vstupy 1.8/1.9) | 574/579 | 575/579 | 4 |

## Evidence

| Status | Zistenie | Zdroj | Confidence |
|---|---|---|---|
| Confirmed | V každom obraze je z počiatočného stavu 0 uzavretá množina stavov 0..7 formátovacieho dispatchera. | evidence/xlat_proofs.json, bajty EXE a startup DS operand | High pre statickú tabuľku |
| Confirmed | Všetkých 256 vstupných bajtov × 8 stavov × 6 obrazov dáva očakávaný stav a cieľ: 12288 prípadov. | evidence/xlat_emulation.json; scripts/verify_xlat_dispatch.py | High pre fragment so vstupným stavom a bajtom |
| Confirmed | V1.9 producent 183c:01c6 má signed 16-bit operácie, typovo závislé aritmetické posuny, horný signed clamp 255 a žiadny dolný clamp. | audit/DOS18/instructions.tsv; evidence/damage_producer_emulation.json; scripts/verify_damage_producer.py | High pre bajty a testované vstupy pri nahradenom RNG |
| Inferred | Pole record+0x18 a DS:4550 tvoria rozdiel používaný v základe poškodenia; DS:418d určuje režim a DS:417e škálovanie. | producer dataflow, caller 14c7:1304 | Medium pre herné pomenovanie |
| Unknown | Dosiahnuteľnosť záporných rozdielov/overflow zo skutočnej hry; účinky potlačeného far-call pre typ 0x15. | Celá hra a callee sa netestovali | Neuzavreté |

## XLAT behavior model

Po znížení vstupného bajtu o 0x20 sa hodnoty mimo rozsahu 0..0x58 mapujú na triedu 0; inak sa použije dolný nibble DS tabuľky. Nový stav je horný nibble table[8*class + old_state]. Počiatočný stav je 0; pevný bod pri všetkých statických triedach je presne {0,1,2,3,4,5,6,7}. Tabuľka obsahuje triedy 0..8, preto najvyšší transition index je 71, v rámci 89 dostupných bajtov. Predpokladom je pôvodný obsah tabuľky; tento pass nedokazuje absenciu ľubovoľného runtime prepisu pamäte.

| Obraz | Entry | DS | Klasifikačná tabuľka | Skok |
|---|---|---|---|---|
| 10 | 219b:1744 | 3360 | 21c4 | 219b:1796 |
| 11 | 21bc:1648 | 3395 | 22bc | 21bc:169a |
| 12 | 21c2:1648 | 339b | 22b8 | 21c2:169a |
| 15 | 21c7:164c | 374a | 228a | 21c7:169e |
| 17 | 21d1:1648 | 3754 | 228e | 21d1:169a |
| 18 | 21ea:164c | 376d | 22c8 | 21ea:169e |

Startup MOV DI,imm → MOV SS,DI a PUSH SS/POP DS poskytuje dátový segment. Presný operand je uvedený v xlat_proofs.json. Do projektov boli doplnené iba osemcílové override a opravené flow referencie. Bajty EXE sa nemenili. Testuje sa fragment dispatchera, nie výsledný text pre všetky formátovacie reťazce.

## V1.9 damage producer model

```c
// w16 means signed interpretation after truncation to 16 bits.
v = w16(w16((record.word_18 - DS4550) << 3) + signed_rng_AX % 25);
v = transform_by_type(v, record.byte_06, DS418d, DS6268);
if (DS417e == 2) v = arithmetic_shift_right(v, 1);
else if (DS417e == 0) v = w16(v + v);
if (v > 255) v = 255; // signed comparison; no lower clamp
return v;
```

Model a emulácia používajú nezáporné vložené RNG hodnoty 0,24,32767; správanie pri zápornom RNG nie je týmito testami pokryté. Funkcia vykonáva CWD/IDIV 25, teda signed delenie.

Nižšie s je DS:418d, h je DS:6268. Všetky posuny sú aritmetické a aplikujú sa na signed 16-bit v. Význam typových ID ani s/h sa tu nepremenuje na konkrétnu zbraň alebo nepriateľa bez ďalšieho dôkazu.

| record.byte_06 | Transformácia pred DS417e |
|---|---|
| 0x0C, 0x1D | v >> 3 |
| 0x0D | v >> (s==1 ? 1 : 3) |
| 0x0E,0x11,0x14 | v >> (s==2 ? 1 : 3) |
| 0x0F,0x10 | v >> (s==1 ? 8 : 1) |
| 0x12,0x13 | v >> 2 |
| 0x15 | far side-effect call, potom v=0; účinok callea otvorený |
| 0x16 | h==3 ? 3 : 0 |
| 0x17 | v >> (s==1 ? 8 : 2) |
| 0x18 | v >> (s==1 ? 8 : s==2 ? 4 : 3) |
| 0x19 | 0 |
| 0x1A | s==1 ? (v>>1) : 0 |
| 0x1B,0x1C | v >> 1 |
| 0x1E | s==1 ? 0 : (v>>3) |
| 0x1F | s==1 ? 0 : (v>>2) |
| mimo 0x0C..0x1F | v |

Testovacia matica: typy {0,12..31,255}, s={0,1,2}, signed rozdiel={-4096,-1,0,1,4095,4096}, RNG={0,24,32767}, DS417e={0,1,2}, h={0,3}: **7128 zhôd**. Z nich 2778 vracia záporný signed AX v tomto umelom testovacom priestore; tento počet nevyjadruje frekvenciu v hre. RNG návrat sa vložil; far side-effect call 183c:0263 sa preskočil. Callee môže meniť stav a musí sa samostatne overiť pred tvrdením parity celého producenta.

Praktický dôsledok: vyššie presná implementácia nesmie svojvoľne pridať max(0,v), nahradiť signed posuny unsigned posunmi alebo ignorovať pretečenie. Volajúca rutina 14c7:1304 testovaná v pass2 nuluje AH a používa iba AL; pri zápornom AX tak rozhoduje jeho dolný bajt. Dosiahnuteľnosť takýchto vstupov vo hre je TBD.

## Remaining failures and IR

- 1.0: `1000:0ae0`, `17f5:05ca`, `1cdc:209a`, `1f85:0736`, `2dec:1cb0`
- 1.1: `1000:0ae0`, `1d00:207e`, `1fa7:048e`, `2e21:19d0`, `2e21:1b14`, `2e21:1b78`
- 1.2: `1000:0ae0`, `1818:05c6`, `1d00:2080`, `1fad:048e`, `2e27:19d0`, `2e27:1b14`, `2e27:1b78`
- 1.5: `1000:0aea`, `181c:05d8`, `1d05:207e`
- 1.7: `1000:0aea`, `1d0f:207a`
- V1.9: `1000:0aea`, `183c:05d8`, `1d25:20ae`, `2d0b:2e0e`

Dve rodiny na obraz (1000:0ae0/0aea a far-data rutina 1cdc:209a/1d00:207e/1d00:2080/1d05:207e/1d0f:207a/1d25:20ae) poskytujú normalizovaný IR: 402 a 108 pcode operácií na obraz. Režim normalize zámerne neposkytuje C; nevydáva sa za opravu default dekompilácie. Súbory sú evidence/DOS*/residual/*_pcode.tsv.

Osem kandidátov zostáva bez incoming reference v aktuálnom projekte: 2dec:1cb0; 2e21:19d0/1b14/1b78; 2e27:19d0/1b14/1b78; 2d0b:2e0e. Chýbajúca referencia sama osebe nedokazuje neexistenciu funkcie. Ich labely sa neodstraňovali a neznižoval sa nimi umelo počet zlyhaní.

## Next discriminating tests

1. Zistiť pôvod a rozsah record.word_18/DS4550 a typových ID pri volaní producenta, konkrétne záporné rozdiely a rozsah umožňujúci overflow.
2. Overiť RNG 1fb7:0194 vrátane návratového rozsahu a stavu; pri type 0x15 analyzovať 1d25:0754 a jeho zmeny globálov.
3. Dve far-data rodiny: z normalizovaného IR určiť konkrétny konštrukt spôsobujúci chybu C symbolizácie; porovnať s inštrukciami a runtime adresami.
4. Osem kandidátov bez refs: prehľadať raw far-pointer tabuľky a relokácie, prichádzajúce nepriamo vypočítané ciele, hranice dátových blokov.
5. Zostávajúce menu/renderer chyby: porovnať skutočný CS/IP a blokové aliasy, nepreberať chybný cieľ len podľa zobrazenej adresy.

## Reproduction

Balík obsahuje hotové pass3 projekty, exporty, dôkazy, rekonštruované EXE a baseline functions.tsv z pass2 pre validačné porovnanie. Pre vytvorenie nových pracovných kópií cez prepare_pass3.py treba predchádzajúci balík pass2 a úpravu miestnych Java/Ghidra ciest v run_pass3.py.

```bash
python3 scripts/verify_xlat_dispatch.py
python3 scripts/verify_damage_producer.py
python3 scripts/validate_pass3.py
```

Unicorn 2.1.4; ide o fragmentové testy, nie DOSBox runtime, framebuffer porovnanie ani dôkaz celej 1:1 hry.

## Confidence

High pre doložené dispatcher ciele a aritmetiku producenta v uvedenom testovanom rozsahu. Úplná sémantika, dosiahnuteľnosť edge cases a 1:1 herná parita zostávajú otvorené.
