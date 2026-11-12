# -*- coding: utf-8 -*-
"""python write_palette_asset_comparison_report.py OUTPUTS"""
import json,sys
from pathlib import Path
r=Path(sys.argv[1]);s=json.loads((r/'palette_asset_comparison/summary.json').read_text());p=json.loads((r/'win_palette_pcx/summary.json').read_text());groups=json.loads((r/'palette_asset_comparison/groups.json').read_text());old=(r/'PALETTE_LOAD_AND_RUNTIME_REPORT.md').read_text(encoding='utf-8');table=old[old.index('## Aktualizácia 13 oblastí'):old.index('## Runtime testy na vykonanie')]
table=table.replace('|GAME.PAL EOF-768 a byte-exact native konverzia|prefix1156B a varianty assetu|prefix/formáty verzií|','|32asset kópií/3varianty;WindowsPCX celý ohraničený|DOSprefix1156B a bare768 pôvod|DOSprefix spotrebitelia|')
table=table.replace('|20 native replay a runtime768B palety|DAC readback a vizuálna zhoda|zachytiť DAC/screenshot|','|PCX320x200 dekódovaný;Windows/DOS255farebných záznamov rozdielnych|Winconsumer a prevod|Winpalette loader|')
table=table.replace('|DOS8štítkov/7obrazov krížovo overených; Win bez zmeny|WinNE prostredie a algoritmické mapovanie|Win hook rodina|','|12Windows asset kópií zhodných;PCXformat nie runtime|Win16decoder/API a pôvod assetu|nájsťGame.PALconsumer|')
lines=[]
for g in groups:lines.append('|%d|%d|%d|`%s`|'%(g['count'],g['bytes'],g['prefix_bytes'],g['sha256']))
text='''# GAME.PAL: tri varianty a Windows PCX obsah

Audit32 explicitne uvedených lokálnych kandidátnych súborov našiel **3 unikátne celé SHA**, aj3 unikátne prefixy a3 odlišné768B tail palety. Všetky32 súbory sa úspešne načítali. Adresárové názvy sú len lokátory; nepredstavujú overenie verzieEXE alebo pôvodu balíka. Dvanásť zhodnýchWindows súborov nie je12nezávislých verzií hry.

|Kópie|VeľkosťB|PrefixB pred768B tail|CelýSHA256|
|---:|---:|---:|---|
'''+ '\n'.join(lines)+'''

Devätnásť1924B kópií sa zhoduje s kanonickýmDOS súborom. Dvanásť5459B kópií vrátane `L:\\nite3d\\nite3\\windows\\GAME.PAL` obsahuje identickýPCX. Jedna768B kópia je v `dos/N3D-Dos/1/`; nie je totožná sDOS tailom ani jehoSHR2 výsledkom. Jej pôvod a použitie zostávajú otvorené. Rovnaký názovGAME.PAL teda neoprávňuje preniesť bajty ani prevod palety medziDOS aWin16.

## Windows variant: celý asset má reprodukovateľné hranice

Štruktúrne overenie vychádza z pôvodného [ZSoft Technical Reference Manual,revision5,Dean Ansley,mirrored](https://www.neperos.com/article/rntibjd550e697a4). Použité sú polia128B headera, počet scanline bajtov, byte RLE a0Ch marker pred256RGB trojicami. Náš dekóder porovná presné hranice s reálnym súborom; netvrdí zhodu sWin16 herným dekóderom.

|Interval,end exclusive|B|Doložený typ|
|---|---:|---|
|[0,128)|128|PCXheader:0A050108,window0,0..319,199,1plane,bytesperline320|
|[128,4690)|4562|RLE stream,2748packetov,200riadkov|
|[4690,4691)|1|marker0Ch|
|[4691,5459)|768|256 RGB BYTE trojíc|

Dekóder vytvoril presne64000indexov, bez prekročenia jedného320B riadka, bez nedočítaných packetov alebo zostávajúcich zakódovaných bajtov. Každý packet a každý riadok má samostatný záznam. Celý5459B asset je presne rozdelený bez dier a prekryvov. HeaderPaletteInfo je pozorované0, čo sa neprepisuje na štandardne popísané1/2; štrukturálny decode tento nepoužitý údaj nevyužíva. Filler sa nevydáva za všeobecne dokázané alignment bajty hry.

Všetky intervaly majú **PARTIAL hernú sémantiku**, aj keď presná štruktúrna partition aRLE decode sú reprodukované. To nepreukazuje prirodzenúWin16 spotrebu súboru, Winpalette API prevod alebo display parity.

![Rekonštruovaný PCX obsah súboru GAME.PAL; nejde o screenshot hry](win_palette_pcx/reconstructed_win_game_pal.png)

PNG je rekonštrukcia indexov pomocou pripojenejPCX palety. Vizuálne obsahuje dve série drobných oranžových motívov; ich gameplay význam sa neidentifikuje iba z obrazu. Pôvodný súbor sa nemenil.

## Presné rozdiely vo farbách

Z256 RGB trojíc je medziWindowsPCX tailom aDOS tailom **zhodná iba1**, odlišných255; po jednotlivých komponentoch sa líši **747 z768B**. Toto je porovnanie raw8bit asset hodnôt, nie prevod cezDOS6bitDAC, Windows systémovú paletu alebo screenshot. `palette_comparison.csv` uvádza každú trojicu a počet jej indexu v dekódovanomPCX. Žiadny algoritmus Win16 sa z tejto rovnosti/nerovnosti nedovodzuje.

## DOS prefix: pozorovaná pravidelnosť, stáleUNKNOWN

Prefix kanonickéhoDOS assetu `[0,1156)` začína BYTE sekvenciou3A3C001F. Zvyšok `[4,1156)` sa dá presne rozdeliť na36blokov po32B a **každý blok obsahuje jedinú opakovanú hodnotu**. Pri19zhodných kópiách je to684 identických obsahových pozorovaní, nie684nezávislých typových dôkazov. Zatiaľ nie je doložený game consumer týchto blokov; nevydávajú sa za shading tabuľku, grafiku, padding aleboPCX. DOS paletový loader ich preskakuje relatívnymseekomEOF−768.

## Reprodukcia a artefakty

`audit_palette_candidates.py PATH_LIST CANONICAL_GAME_PAL OUT` používa `palette_candidate_paths.txt`, overí hashe, rozdelí prefix/tail a vytvorí files.csv,groups.json,asset_intervals.csv/json,prefix_32byte_chunks.csv a summary. Kandidáti boli vyhľadaní cez filenameGAME.PAL podL:\\nite3d, ale explicitný32riadkový manifest sa nepovažuje za úplný obsah všetkýchZIP archívov.

`audit_win_palette_pcx.py WIN_GAME_PAL DOS_GAME_PAL OUT` kontroluje oba presnéSHA, header, per-rowRLE aEOF palette hranice; vytvorí asset_intervals.csv,scanlines.csv,rle_packets.csv,palette_comparison.csv,summary aPNG. Nevkladá third-party binárky ani nemení asset. `write_palette_asset_comparison_report.py OUTPUTS` generuje túto správu a13oblastí.

'''+f"ManifestSHA `{s['path_manifest_sha256']}`. Windowsdecoded64000B SHA `{p['decoded_sha256']}`; PNGSHA `{p['png_sha256']}`.\n\n"+'''## Meranie

Žiadna zmena125funkčných rozsahov, seeded replay počtu ani7prirodzených DOSBox scenárov. Toto je externýasset audit; PASS320 zostáva57102PARTIAL/149CLASSIFIED ONLY/44UNKNOWN/0DEEP VERIFIED. Presná file partition5459/5459B znamená integrity tohtoassetu, nie nové percento sémantickej úplnosti celejWin16 oblasti. Nové percentáN/A, pretože úplné menovatele chýbajú. Dávka je lokálna, zatiaľ nepublikovaná naGitHube.

'''+table+'''## Runtime testy na vykonanie

NájsťWin16 consumerGAME.PAL vEXE/import/CFG kontexte a overiť, či používa ibaEOF paletu alebo celýPCX obraz. Sledovaťprevod8bit RGB doWinpalette a systémové rezervované farby. PriDOS skúsiť read/watch dôkazprefix blokov a overiť pôvod samostatnej768B kópie. ScreenshotPCXrekonštrukcie nenahrádza screenshotpôvodnej hry ani zhody rendererov. PASS1 UNKNOWN44B zostáva samostatnou prioritou.
'''
(r/'PALETTE_ASSET_COMPARISON_REPORT.md').write_text(text,encoding='utf-8');print(json.dumps(dict(report='PALETTE_ASSET_COMPARISON_REPORT.md',asset_files=s['files_read'],unique_assets=s['unique_file_hashes'],status_changes=0)))
