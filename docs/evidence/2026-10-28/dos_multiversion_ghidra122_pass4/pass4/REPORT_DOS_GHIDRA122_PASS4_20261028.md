# Nitemare 3D DOS — Ghidra 12.2 pass 4, 2026-10-28

## Finding

Obnovené štyri C dekompilácie po oprave šiestich dodatočných switch inštancií. Zlyhania 27 → 23, bez nového zlyhania a bez odstránenia/pridania funkcií. Pohybový handler má v hlavnom listingu obnovených 254 inštrukcií a 776 definovaných bajtov po RETF; jeho default C dekompilácia stále zlyháva.

| Obraz | C predtým | C teraz | Otvorené |
|---|---:|---:|---:|
| 1.0 | 570/575 | 571/575 | 4 |
| 1.1 | 571/577 | 571/577 | 6 |
| 1.2 | 571/578 | 572/578 | 6 |
| 1.5 | 576/579 | 577/579 | 2 |
| 1.7 | 578/580 | 578/580 | 2 |
| V1.9 (vstupy 1.8/1.9) | 575/579 | 576/579 | 3 |

## Evidence

| Status | Zistenie | Zdroj | Confidence |
|---|---|---|---|
| Confirmed | Ďalší guarded switch má MOV AX,DI pred CMP a potom ADD AX,DI, teda platné zdvojenie indexu. Šesť tabuliek, 140 položiek. | evidence/DOS*/switch_proofs.json; switch_repair/guarded_switch_edges.tsv | High pre bajty a dispatch |
| Confirmed | 158 testov tabuliek vrátane troch hodnôt mimo rozsahu na tabuľku + 8 testov štyroch podmienených skokov = 166 zhôd. | evidence/dispatch_emulation.json | High pre testované fragmenty |
| Confirmed | Hranica 0c73/0c7d je MOV [BP-18h],BX, potom MOV [BP-16h],ES, nie CALL z posledného bajtu MOV. | evidence/DOS*/repair/boundary_repair.txt; audit/DOS*/instructions.tsv | High |
| Confirmed | Druhá pohybová slučka má rovnaké bajty v šiestich odlišných obrazoch po vynulovaní MZ relocation wordov. | evidence/second_loop_identity.json | High pre presnú bajtovú identitu maskovaného rozsahu |
| Confirmed | 464 cielených prípadov na obraz, spolu 2784; spustené originálne telo handlera s prázdnou prvou skupinou, bez hookov a externých stubov. | evidence/motion_*.json; scripts/verify_motion_crossversion.py | High pre syntetické kontrolované stavy |
| Unknown | Dosiahnuteľnosť všetkých syntetických stavov zo skutočnej hry a úplná renderer parita. | Netestovalo sa celé DOS prostredie ani framebuffer | Neuzavreté |

## Movement behavior model

Druhá skupina je samostatný pool od segment:34f6; count je signed word segment:0002 a stride záznamu je 14 bajtov. Segment sa berie z pôvodných relokovaných operandov handlera. DS/SS sa berú zo startup dôkazu z pass3. Prvá 18-bajtová skupina zostáva v testoch prázdna; jej správanie sa týmito výsledkami neuzatvára.

| Offset v 14-byte zázname | Použitie |
|---|---|
| +0,+2,+4,+6 | Štyri nullable near pointery na geometriu v DS/SS |
| +8,+10 | Far pointer na dvojbajtovú prepojenú bunku |
| +12 | Word stav, pohyb sa spracuje iba pri 2 |

1. Pre stav 2 sa najprv zapíše stav 0.
2. Sloty 0 a 2 porovnajú signed wordy geometria+0x0c a +0x10; sloty 1 a 3 použijú +0x0e a +0x12.
3. Ak start < end, start sa zvýši o 2 s 16-bitovým pretečením a stav sa nastaví späť na 2.
4. Ak sa aspoň jeden pointer pohol, čistenie sa v tomto priechode nevykoná.
5. Ak žiadny nepohol, skenujú sa záznamy s rovnakým nenulovým pointerom v tom istom slote. Na zodpovedajúcom zázname sa vo všetkých nenulových geometriách vynuluje bit 0 byte +5, oba bajty prepojenej bunky sa vynulujú a stav sa nastaví na 0.
6. Spracovanie je sekvenčné; aliasy pointerov zdieľajú pamäť. Nejde o nezávislý súbežný update snapshotov.

Tento model zodpovedal stavom, geometrii aj prepojeným bunkám vo všetkých 2784 prípadoch. Matica zahŕňa stavy 0..3, všetkých 16 kombinácií prítomnosti pointerov, rovnosť a nepárny cieľ, záporné súradnice, overflow, zdieľanie záznamov a viac priechodov.

## Temporal edge cases

Pri štarte 100 a štyroch prítomných geometriách:

| Cieľ | Stav po priechodoch | Dôsledok |
|---:|---|---|
| 100 | 0,0 | Čistenie môže nastať hneď |
| 101 | 2,0 | Preskočenie cieľa krokom +2; čistenie až v ďalšom priechode |
| 102 | 2,0 | Aj pri presnom dosiahnutí cieľa sa prvý priechod zachová stav 2 |
| 103 | 2,2,0 | Dva pohyby, potom čistenie |
| 32767, štart 32766 | 2,2,2 | 32766+2 pretečie na -32768; ďalšie signed porovnanie pokračuje |

Toto je count-exact správanie volaní handlera. Neurčuje čas medzi volaniami ani tick-exact scheduler celej hry.

## Ghidra repair and verification

Hlavný listing bol pri hranici druhej slučky poškodený; pre 1.5 a V1.9 mal v databáze aj celý handler iba jednobajtové telo. Validator to zachytil. Finálny follow-up znovu disassembloval celý doložený rozsah od entry po RETF a aktualizoval vlastníctvo. Všetkých šesť výsledných tiel má 254 inštrukcií/776 definovaných bajtov; medzery zarovnávacích NOP sa nepočítajú ako inštrukcie.

DOS10 mal neúplne dopísaný priebežný functions.tsv, hoci jednotlivé C súbory existovali. Konečný export preto vytvoril N3DFunctionExport cez StringBuilder + Files.writeString a marker FUNCTION_EXPORT_COMPLETE 575. Funkcie sa nevyraďovali; validator porovnáva presnú množinu entrypointov. Spúšťač run_pass4.py už používa tento exportér.

Štyri podmienené rendererové referencie boli opravené podľa zachovania CS/IP a otestované pri oboch hodnotách ZF. Samotná oprava referenčného grafu zatiaľ neodstránila zlyhania ich C dekompilácie. Bootstrap/data alias E9 kandidáti sa neopravovali len na základe zobrazenej adresy: skutočný CS musí byť dokázaný osobitne.

## Remaining failures

- 1.0: `1000:0ae0`, `1cdc:209a`, `1f85:0736`, `2dec:1cb0`
- 1.1: `1000:0ae0`, `1d00:207e`, `1fa7:048e`, `2e21:19d0`, `2e21:1b14`, `2e21:1b78`
- 1.2: `1000:0ae0`, `1d00:2080`, `1fad:048e`, `2e27:19d0`, `2e27:1b14`, `2e27:1b78`
- 1.5: `1000:0aea`, `1d05:207e`
- 1.7: `1000:0aea`, `1d0f:207a`
- V1.9: `1000:0aea`, `1d25:20ae`, `2d0b:2e0e`

## Implementation-ready findings

- Druhá pohybová slučka: 14-bajtová štruktúra, stav 2, signed porovnanie pred krokom, presne +2 s 16-bitovým pretečením, odložené čistenie a zdieľanie pointerov sú doložené bajtmi a kontrolovanou emuláciou.
- Nevkladať clamp na cieľ a nevykonávať čistenie v tom istom priechode, ktorý práve dosiahol/preskočil cieľ.
- Časovanie scheduleru, mapové spúšťanie a fyzické pomenovanie jednotlivých typov záznamov zostávajú TBD.

## Next discriminating tests

1. Renderer: samostatné segmentové pohľady so zachovaným správnym CS a dátovým DS; porovnať každý dekódovaný bajt a flow so zdrojovým EXE.
2. Dve far-data rodiny: opraviť C symbolizáciu z už získaného IR, nepozmeňovať herné bajty kvôli dekompilátoru.
3. Kandidáti bez incoming refs: preveriť raw callback tabuľky a relokácie pred prípadným vyradením labelov.
4. Pohyb: pozorovať skutočných callerov, počet volaní na tick a dosiahnuteľné pooly; až potom rozšíriť dôkaz na herný scheduler.

## Reproduction

Hotové projekty pass4 a úplné exporty sú v balíku; baseline functions.tsv z pass3 slúžia validátoru. Čerstvá príprava cez prepare_pass4.py vyžaduje predchádzajúci pass3 balík a lokálne upravené Java/Ghidra cesty. Test pohybu používa startup DS dôkazy z pass3, ktoré sú tiež priložené.

```bash
python3 scripts/verify_pass4_dispatch.py
python3 scripts/verify_motion_crossversion.py
python3 scripts/validate_pass4.py
```

Unicorn 2.1.4. Zastavenie je pred RETF; nejde o celú hru, DOSBox runtime ani pixel-perfect render test. EXE bajty sa nemenili.

## Confidence

High pre presný tok tabuliek a druhú slučku v uvedenom kontrolovanom rozsahu. Celková 1:1 parita zostáva otvorená.
