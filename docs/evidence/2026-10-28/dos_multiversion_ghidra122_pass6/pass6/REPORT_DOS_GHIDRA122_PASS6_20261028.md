# Nitemare 3D DOS — Ghidra 12.2 pass 6, 2026-10-28

## Finding

Doložené a zapísané dva návratové ABI v každom zo šiestich obrazov: renderer AL a mode1 callback DX:AX. Spolu 12 opráv prototypov, pričom počet C úspechov zostáva nezmenený. Pre osem zostávajúcich analytických kandidátov sa vyvrátili všetky zdokumentované pôvodné near-CALL vstupy. Neodstraňovali sa labely a nevyhlasuje sa globálna runtime nedosiahnuteľnosť.

| Obraz | Štandardný model | Explicitný real-mode model | Neuzavreté kandidáty explicitného modelu |
|---|---:|---:|---:|
| 1.0 | 571/575 | 574/575 | 1 |
| 1.1 | 571/577 | 574/577 | 3 |
| 1.2 | 572/578 | 575/578 | 3 |
| 1.5 | 577/579 | 579/579 | 0 |
| 1.7 | 578/580 | 580/580 | 0 |
| V1.9 (vstupy 1.8/1.9) | 576/579 | 578/579 | 1 |

Výsledok stock3445/3468 a explicit3460/3468 je rovnaký ako v pass5. Tento pass zvyšuje presnosť storage/argumentov a dôkazový stav kandidátov; nepridáva ďalšie úspešné dekompilácie. Samostatná DOS1.8 v dodanej sade stále nie je doložená.

## Evidence

| Status | Zistenie | Zdroj | Confidence |
|---|---|---|---|
| Confirmed | 6 rendererových funkcií používa návrat AL a word argument na SP_entry+4; 6 callbackov má pre mode1 výsledok DX:AX a word mode na SP_entry+4. | evidence/DOS*/abi_fix/abi_fixes.tsv; pôvodné opcode; pass5 renderer testy; nový far_abi_emulation.json | High pre uvedené storage a režim1 |
| Confirmed | 72 pôvodných mode1 vykonaní prešlo, bez hookov/stubov; DS={0,skutočný DS,5000,ffff}, flag={0,1,255}. | scripts/verify_far_abi_crossversion.py; evidence/far_abi_emulation.json | High pre testovaný režim a pripravený rámec |
| Confirmed | 30 pôvodných CALL inštrukcií zachovalo CS, vypočítalo správny IP a uložilo správnu návratovú IP. Ich staré kandidátne ciele boli o65536 B vyššie. | evidence/candidate_seed_audit.json; scripts/verify_candidate_seeds.py | High pre tieto konkrétne inštrukcie |
| Confirmed | Žiadny z8 kandidátov nemá nájdený relocation-backed far pointer, kanonický raw segment:offset vzor ani aktuálnu incoming ref v Ghidre. | full MZ relocation scan, raw scan, candidate_incoming.tsv | High pre uvedené statické skeny |
| Unknown | Ľubovoľný nepriamo vytvorený pointer, runtime prepísanie nulovej pamäte alebo iná vstupná cesta. | Statické skeny a30 izolovaných CALL to nevylučujú | Neuzavreté |

## Verified ABI

| Obraz | Renderer: byte v AL | Callback: dword v DX:AX | Flag offset pre mode1 |
|---|---|---|---|
| 10 | 1f85:0178 | 17f5:2966 | 34df |
| 11 | 1fa7:0170 | 1817:2966 | 35d9 |
| 12 | 1fad:0170 | 1818:2958 | 35d5 |
| 15 | 1fb2:016e | 181c:299e | 35a9 |
| 17 | 1fbc:016a | 1826:299a | 35ad |
| 18 | 1fd5:016e | 183c:299e | 3639 |

Obe funkcie používajú explicitné custom storage a __cdecl16far. Každá má jeden unsigned word argument na SP_entry+4. Callback nemá hidden return pointer. Dword znamená bitové storage DX:AX; nejde o tvrdenie jednotného sémantického významu návratu všetkých režimov.

Mode1 podľa pôvodného kódu:

```c
if (DS[flagOffset] != 0) { AX = flagOffset; DX = DS; }
else { AX = 0; DX = 0; }
```

Nenulový výsledok je zabalená far adresa DS:offset, nie už vypočítaná fyzická lineárna adresa. Testy používajú aj syntetické hraničné DS hodnoty; hardvérové správanie A20 alebo prirodzená dosiahnuteľnosť týchto DS sa nevyhlasuje za overenú.

Konkrétny opravený caller v DOS1.0 (1cdc:209a): pred ABI opravou C zobrazovalo `FUN_17f5_2966()` a dvojicu podmienok s iStack_a a iVar3. Po oprave zobrazuje `FUN_17f5_2966(1)` a porovnanie jediného dword výsledku s nulou. To zodpovedá vstupnému mode1 a páru DX:AX; nevytvára nový herný behavior.

Renderer AL kontrakt vychádza z pôvodných AL návratových opcode a z8226 post-projection prípadov pass5. Týchto8226 sa tu nepočíta ako nové vykonania. V1944 z nich by booleanAX dal iný výsledok než booleanAL. V tomto passe sa opravili metadáta, aby C nepreberalo neplatné AH ako hornú polovicu booleanu. Projekcia/prologue nie sú týmito testmi runtime uzavreté.

## Eight candidate entry seeds

Pôvodné near_specs.json sú obnovené z GitHub commitu930608400c83e1d507aad440200db4ca1008e224, cesta docs/evidence/2026-10-28/dos_multiversion_ghidra122_pass2/pass2/evidence/DOSxx/near_specs.json. Každá uvedená source inštrukcia sa znova porovnala s rekonštruovaným EXE a vykonala v Unicorn iba jeden krok. Overil sa CS, cieľové IP, SP−2 a uložená návratová IP. Toto nie je vykonanie celého callea.

| Obraz | Kandidát | Vyvrátené známe CALL vstupy | Počiatočný nulový beh v load image | Relokované far pointery na kandidáta |
|---|---|---:|---:|---:|
| 10 | 2dec:1cb0 | 1 | 15000 B | 0 |
| 11 | 2e21:19d0 | 5 | 15736 B | 0 |
| 11 | 2e21:1b14 | 2 | 15412 B | 0 |
| 11 | 2e21:1b78 | 2 | 15312 B | 0 |
| 12 | 2e27:19d0 | 8 | 15736 B | 0 |
| 12 | 2e27:1b14 | 2 | 15412 B | 0 |
| 12 | 2e27:1b78 | 2 | 15312 B | 0 |
| 18 | 2d0b:2e0e | 8 | 6818 B | 0 |

Nulový beh sa vzťahuje na rekonštruovaný load image pred runtime inicializáciou. Nulové bajty samy osebe nie sú dôkazom nedosiahnuteľnosti. Relokačný sken porovnáva fyzické ciele wordu pred každým relokovaným segmentovým wordom, teda nezávisí iba od jednej kanonickej segmentovej reprezentácie. Samostatný raw sken hľadá presnú kanonickú nerelokovanú dvojicu offset/segment. Dynamicky skladané pointery alebo všetky možné nekanonické nerelokované dvojice týmto nie sú vyčerpané.

Kandidáti zostávajú v projekte s komentárom o vyvrátenom zdokumentovanom seede. Žiadne funkcie ani bajty sa neodstránili. Nie je korektné prezentovať tento audit ako runtime dôkaz, že hra nikdy nemôže vykonať dané adresy.

## Verification

Celá množina entrypointov a completed/C_available výsledkov oboch modelov pred/po ABI je zhodná. Celý definovaný inštrukčný listing má rovnaké adresy a bajty. Uloženie všetkých6 projektov je v pass6/DOS*.log. Všetky kandidátne incoming-ref exporty sú prázdne. Stock a explicitný model sa naďalej uvádzajú oddelene; custom p-code callback je rovnaký úzko ohraničený analytický pohľad ako pass5.

## Implementation-ready findings

- Renderer: čítať návrat zAL, neposudzovať boolean podľa AX.
- Callback mode1: word mode argument naSP_entry+4, výsledok cezDX:AX; pred interpretáciou ako lineárnej adresy osobitne rozbaliť segment a offset.
- Pri analýze near CALL nesmie cieľ prejsť do iného CS len kvôli obtečeniu fyzickej 64KiB banky v analytickom modeli.
- Osem kandidátov nemožno používať ako potvrdené herné funkcie iba na základe odmietnutých pôvodných xrefs. Ich labely sú ponechané ako otvorené analytické položky.

## Next discriminating tests

1. Dáta verzus kód: sledovať runtime zápisy do týchto oblastí a nepriamo skladané ciele; až potom prípadne uzavrieť kandidatúru adries.
2. Doplniť presný return kontrakt callback režimov0,2..5, najmä režimov bez definovanej hodnoty.
3. Prepojiť renderer s pôvodnou projekciou a rasterizáciou; vykonať framebuffer/DAC oracle.
4. Pokračovať sémantickým registrom funkcií, schedulerom, SAVE/LOAD a DEMO; completed počet nie je percento parity.

## Reproduction

Hotové pass6 projekty, obidva modelové exporty a rekonštruované EXE sú priložené. Baseline pass5 explicit_model_results.tsv/instructions.tsv a startup DS dôkazy pass3 sú priložené pre validátor a ABI testy. Čerstvá príprava projektov cez prepare_pass6.py vyžaduje predchádzajúci pass5 balík a upravené lokálne cesty k Java/Ghidre. run_pass6.py opraví ABI a komentáre, potom exportuje všetky funkcie v oboch modeloch a konečný flow listing.

```bash
python3 scripts/verify_far_abi_crossversion.py
python3 scripts/verify_candidate_seeds.py
python3 scripts/validate_pass6.py
```

Unicorn2.1.4. Nové vykonania:72 pôvodných mode1 callbackov a30 jednotlivých pôvodných CALL. Nejde o DOSBox beh celej hry ani o pixel-perfect parity test.

## Confidence

High pre overené ABI a vyvrátenie konkrétnych30 vstupných CALL referencií. Úplná runtime dosiahnuteľnosť ôsmich adries a1:1 herná/renderovacia parita zostávajú otvorené.
