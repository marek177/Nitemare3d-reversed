# DOS 2.0 — celobrazový atlas pevných CS dátových odkazov

11. 11. 2026. Nový **CLASSIFIED ONLY** kandidátny katalóg, oddelený od sémantickej centrálnej partition. Žiadny nový DEEP VERIFIED bajt ani runtime test.

## Metóda a menovateľ

`build_dos_cs_reference_atlas.py` overuje celý171 360 B obraz a hash historického inventára, následne pre všetkých35 648 inštrukčných položiek kontroluje surové bajty, CS*16+IP mapovanie a nezávislé dekódovanie/dĺžku. Ich historická inštrukčná únia je92 972 B. Toto nepotvrdzuje globálnu dosiahnuteľnosť ani sémantickú správnosť historických funkcií.

Iced-x86 memory-access informácie oddeľujú CS operand bez base/index od vypočítaného operandového základu. Pri pevnom operande skript eviduje šírku1/2/4 B, access enum a cieľ CS*16+displacement. Kontroluje file bounds aj segmentový limit. Samotná šírka prístupu **neidentifikuje úplný dátový typ alebo objekt**; napríklad dva WORD prístupy môžu patriť jednému DWORD.

## Merateľný výsledok

| Metrika | Výsledok |
|---|---:|
| CS pamäťové operandy v inventári | 730 |
| Z nich vypočítané base/index, vylúčené z pevných cieľov | 128 |
| Pevné operandové záznamy | 602 |
| Known runtime-patched displacement, vylúčený z cieľovej mapy | 1 |
| Únia zahrnutých cieľových bajtov | 228 B |
| Z toho historicky dekódované inštrukčné bajty | 12 B |
| Referencované bajty mimo historickej inštrukčnej únie | 216 B |
| Z týchto216 B zatiaľ mimo lokálneho sémantického katalógu | 139 B |
| Intervaly úplnej referenčnej partition | 213 |

Šírky všetkých602 fixných operandov:194×1 B,387×2 B,21×4 B. Ich súčet nie je dátové pokrytie, pretože sa opakovane odkazujú na rovnaké bajty. Unikátne ciele sa počítajú po bajtoch.

## Nezamieňať počiatočný operand so živou adresou

CS load na1927F má v kanonickom obraze displacement5555h. Naivný sken ho preloží na image1B145, ktorý patrí historickému kódu. Doložený writer na1927B však tento displacement mení pred spotrebou. Skript preto používa `dos_sample_irq/operand_overlays.csv`, uchováva kanonický operandový záznam s dôvodom `runtime_patched_displacement_requires_state`, ale cieľ1B145 **nezaradí** do referenčnej mapy.

Zostávajúcich12 referencovaných historických kódových bajtov tvorí šesť už potvrdených sample IRQ operandov. Sú to overlay dáta v kóde, nie ďalších12 disjunktných DATA bajtov. Iné zatiaľ nezistené samomodifikácie nemožno globálne vylúčiť; ostatné ciele preto zostávajú podmienené historickým CS kontextom a vykonaním zdrojovej inštrukcie.

## Priorita ďalších polí

`candidate_priority.csv` obsahuje iba nové kandidátne intervaly mimo centrálnej lokálnej evidence, zoradené podľa počtu pevných referenčných operandov. Vyššia frekvencia je plánovacia pomôcka, nie vyšší stupeň pravdivosti.

Prvé ciele: image189E0..189E2 (CS:2DF0,21 odkazov),189B4..189B5 (CS:2DC4,20),1A5AA..1A5AC (CS:49BA,17),1A4CF..1A4D1 (CS:48DF,16). Význam sa má rekonštruovať z producentov, spotrebiteľov a životnosti; samotné podobné adresy nenahrádzajú kontrakt. Počet odkazov je počet operandových záznamov, nie počet nezávislých funkcií alebo runtime vykonaní.

## Výstupy a reprodukcia

```text
python build_dos_cs_reference_atlas.py IMAGE HISTORICAL_INSTRUCTIONS ABSOLUTE_DECODER_DIRECTORY CAMPAIGN_CSV OPERAND_OVERLAYS_CSV OUT_DIR
```

`dos_cs_reference_atlas/references.csv` drží presné zdrojové bajty, dekódovaný text, šírku/access a rozlíšenie zahrnutia. `byte_intervals.csv` aj `.json` tvoria úplnú partition obrazu s end-exclusive hranicami, hashom, reference IDs, historickým prekryvom a stavom centrálnej mapy. `candidate_priority.csv` tvorí pracovný rad; `summary.json` nesie hashe vstupov a súčty.

**139 B sa nepripočítalo k808 sémanticky lokálne posúdeným DATA bajtom.** Centrálna partition zostáva1 796 B kódu/808 B dát. Tento atlas je samostatná klasifikačná vrstva s obmedzenou dôkazovou silou. Pôvodné PASS320 intervaly stále chýbajú; prienik216 alebo139 B s57 295 NON-CODE sa nedá určiť a žiadne percento sa nevypočítava.

Nasledujúci konkrétny krok: uzavrieť WORD CS:2DF0 ako prvý najčastejší neposúdený cieľ, potom producer/consumer lifecycle CS:48DF/48E1. Žiadny kandidát sa nepovýši len podľa mena, konštantyFFFFh ani validného dekódovania zdroja.
