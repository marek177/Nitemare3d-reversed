# Krížové overenie DOS a identita Win1.10

11. 11. 2026. Táto dávka overuje bajtové identity, rozbaľovanie a presne ohraničené rovnosti. **Nepotvrdzuje plnú CFG, algoritmickú ani behaviorálnu paritu verzií.** Nové DEEP VERIFIED 0 B, runtime testy 0.

## Vstupy a reprodukcia

Zdrojový archív `L:\nite3d\N3D_ALL_VERSIONS_ASM.zip` má SHA-256 `b0e8b4d81cfbce9dcab4ee432aee6320080c35f6181fec8c585d4b7970a2bdb3`. Skript `cross_version_inputs.py ASM_ZIP OLD_DOS_OUTPUTS WIN110_EXE OUT_DIR DECODER_DIR` bol vykonaný. Výstupy sú v `cross_version/`.

Verzie sú **dodané archívne labely**. Nie sú nezávisle overenými dátumami vydania. Labely1.8 a1.9 v tomto korpuse označujú identický EXE aj rozbalený obraz. Korpus má osem DOS labelov, ale sedem jedinečných binárnych identít; rovnosť dvoch labelov sa nesmie vydávať za dve nezávislé implementácie.

## Reprodukcia ôsmich DOS vstupov

Pre každý archívny EXE sa preverila MZ dĺžka, podpis EXEPACK, bounds každého príkazu, vzťah zdrojového/cieľového prefixu, presné spätné zakódovanie158 blokov, bounds a unikátnosť relokácií a koniec relokačnej tabuľky presne na EOF. Výsledok sa porovnal bajt po bajte so zachovaným rozbaleným obrazom príslušného labelu. Všetkých osem porovnaní prešlo.

| Label | Veľkosť EXE | Veľkosť obrazu | Relokácie | Image base knižnice | Layout delta |
|---|---:|---:|---:|---|---:|
| DOS1.0 | 115152 | 154448 | 1639 | 15780h | 4 |
| DOS1.1 | 115768 | 155552 | 1651 | 158D0h | 0 |
| DOS1.2 | 115856 | 155632 | 1655 | 15930h | 0 |
| DOS1.5 | 115904 | 170672 | 1655 | 15980h | 4 |
| DOS1.7 | 116068 | 170848 | 1657 | 15A20h | 0 |
| DOS1.8 | 116556 | 171296 | 1669 | 15BB0h | 4 |
| DOS1.9 | 116556 | 171296 | 1669 | 15BB0h | 4 |
| DOS2.0 | 116606 | 171360 | 1670 | 15BF0h | 0 |

Presné SHA-256 EXE aj obrazov sú v `dos_builds.csv`. Tento dôkaz je statická transformácia, nie beh originálneho unpackera. Build-specific offset relokačnej tabuľky stub+132h je explicitný predpoklad parsera a pre každý vstup sa overil jeho presný koniec a bounds; univerzálna podpora všetkých EXEPACK buildov sa netvrdí.

## Dve rozloženia WORX

Pri prvom porovnaní sa DOS2.0-relatívny odtlačok zhodoval iba v štyroch labeloch. Skontrolovanie presného operandového displacementu dispatchera ukázalo druhý layout: lookup displacement je2024h namiesto2020h. V tých istých buildoch sa posúvajú aj scratch polia, normalizátor a WAVE hlavička o4 bajty v rámci CS.

Báza sa neberie z názvu ani z jedného náhodného reťazca. Kandidát musí súčasne obsahovať jedinečný CS-indexed CALL fingerprint, marker RIFF na očakávanom layout-relatívnom mieste, marker data a začiatok normalize_ES_DI `50 52 8C C0`. Týmto bounded testom prešlo všetkých osem obrazov. Rovnaký base model zatiaľ nie je dôkazom rovnosti celej knižnice.

### Čo sa normalizovalo

- 164 B servisných položiek: od každého **nenulového** WORD cieľa sa odčíta explicitná layout delta0/4 modulo65536; nulové slová zostávajú0. Nulové NEAR ciele teda nepreukazujú zhodnú sémantiku mimo normalizovaného regiónu.
- 67 B dispatcher: iced-x86 nezávisle identifikuje CS memory operandy. Od ich 16-bitových displacementov sa odčíta delta; iné bajty sa nemenia. Porovnáva sa výsledný celý67 B prúd, nie iba počet inštrukcií.
- 44 B WAVE blok: žiadna obsahová normalizácia, iba nájdenie správneho layout-relatívneho miesta.

| Porovnanie | Počet zhodných párov z28 |
|---|---:|
| Celý pôvodný EXE | 1 |
| Celý rozbalený obraz | 1 |
| Servisná tabuľka164 B, raw | 12 |
| Servisná tabuľka164 B, normalizované nenulové ciele | 28 |
| Dispatcher67 B, raw | 12 |
| Dispatcher67 B, normalizované CS displacementy | 28 |
| Hlavička44 B, raw | 28 |

To potvrdzuje lokálnu štruktúrnu a bajtovú zhodu týchto regiónov pod uvedenou normalizáciou. Neuzatvára všetky servisné ciele, rozdiely segmentových kontextov, neskoršie zápisy ani správanie hry. Žiadna DOS adresa sa automaticky neprenáša do Win16.

## Win1.10: EXE a NE segmenty

Lokálny `L:\nite3d\nite3\windows\nite3w - 110.exe` je bajtovo zhodný s `WIN_1.10/original.exe` v archíve. Má230400 B a SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`.

NE hlavička je na file offset80h, vstup je **segment index2:3718h**, nie DOS selector2. Segmentová tabuľka má10 položiek a alignment shift4. Šesť segmentov má diskové dáta a každý je bajtovo zhodný s príslušným exportom SEGxx.bin.

| NE index | File offset | File data B | Typ podľa flagu | Raw fixup records |
|---:|---|---:|---|---:|
| 1 | 04C0h | 56546 | CODE | 220 |
| 2 | E8A0h | 29694 | CODE | 95 |
| 3 | 15FC0h | 61372 | CODE | 90 |
| 4 | 25260h | 22076 | CODE | 31 |
| 7 | 2A9C0h | 5702 | DATA | 2 |
| 10 | 2C040h | 36526 | DATA | 8 |

NE indexy5,6,8,9 majú sector field0, teda v tomto parseri nemajú priradený diskový payload. CSV uchováva pôvodné length/minimum allocation slová oddelene; nulové length pole sa pri takom segmente nesmie vydávať za65536 bajtov prečítaných zo súboru. Skutočné runtime alokácie a inicializácia sa zatiaľ nesledovali.

CODE flag nie je dôkaz, že každý bajt segmentu je inštrukcia. DATA flag neurčuje automaticky sémantické typy polí.

## 446 surových fixup záznamov

`win110_raw_fixups.csv` obsahuje presných446 osembajtových záznamov vrátane surového hex, source type, target flags, source offset a target words. Bounds záznamov boli overené voči EXE. **Nie je to počet všetkých relokačných miest alebo FAR volaní.** Source chains, additive/non-additive význam, moduly, importy a efektívne runtime selektory ešte nie sú expandované ani priradené ku CFG.

## Stav požiadaviek a ďalší krok

Aktualizovaná tabuľka13 oblastí je v `CAMPAIGN_CATALOG_REPORT.md`. V tejto dávke sa doplnili tabuľky/ukazovatele a Win16 identita; ostatné oblasti nemajú nové behaviorálne tvrdenia. Nové percentá zostávajú N/A, metodika vyžaduje uzavretý menovateľ sémantických jednotiek. Toto nie je zvýšenie DEEP VERIFIED.

Ďalšie konkrétne kroky: expandovať NE source chains so segmentovými bounds, vyriešiť internal/imported ciele, porovnať konkrétne DOS servisné funkcie pri layout0/4 a overiť ich globálny kontext. PASS320 ledger stále chýba, takže prienik nových dátových regiónov s57 295 NON-CODE bajtmi nemožno vyčísliť. Runtime testy pre prirodzenú DOS/Win zhodu sa v tejto dávke nevykonali. PE32 port sa nevykonáva.
