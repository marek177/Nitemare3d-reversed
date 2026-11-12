# -*- coding: utf-8 -*-
"""python write_dac_readback_report.py OUTPUTS WORK"""
import csv,hashlib,json,sys
from pathlib import Path
r,w=map(Path,sys.argv[1:]);out=r/'dosbox_dac_readback_runtime';p=json.loads((out/'independent_verification.json').read_text());d=json.loads((out/'dac_readback.json').read_text());assert p['dac_register_readback_verified'];sha=lambda b:hashlib.sha256(b).hexdigest()
for item in p['files']:assert sha(Path(item['path']).read_bytes())==item['sha256']
actual=bytes.fromhex(d['actual_hex']);buffer=(w/'palette_buffer_runtime.bin').read_bytes();assetrow=next(x for x in csv.DictReader((out/'inputs.csv').open()) if Path(x['source']).name.upper()=='GAME.PAL');source=Path(assetrow['source']).read_bytes()[-768:];assert actual==buffer==bytes(v>>2 for v in source)
rows=[]
for n in range(256):
 j=n*3;rows.append(dict(index=n,source_r=source[j],source_g=source[j+1],source_b=source[j+2],buffer_r=buffer[j],buffer_g=buffer[j+1],buffer_b=buffer[j+2],dac_r=actual[j],dac_g=actual[j+1],dac_b=actual[j+2],passed=True))
with (out/'dac_component_comparison.csv').open('w',encoding='utf-8',newline='') as f:writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
old=(r/'UNKNOWN_BYTES_RUNTIME_WATCH_REPORT.md').read_text(encoding='utf-8');table=old[old.index('## Aktualizácia 13 oblastí'):old.index('## Runtime testy na vykonanie')]
table=table.replace('|mask/plane store,transparentnosť a unsigned depth|skutočné VGA registre a výstup|DOSBox frame dump|','|768 emulovaných DAC zložiek byte-exact; bits6/maskFF|framebuffer, clipping, fyzický VGA|video roviny a prvý frame|')
table=table.replace('|Winloader bezSHR;VGA backendSHR2, GDI8bitRGB|OSpaleta aDIB render|nativeWindows capture|','|DOS DAC readback = runtime buffer = asset SHR2|Win OS paleta a celková obrazová parita|Win capture a paired frame|')
text='''# DOSBox-X: skutočný readback emulovaného VGA DAC

Deviaty zachovaný runtime scenár spustil pôvodný packed DOS2 EXE až po návrat paletového loadera **0476:017C**, skutočne **0C9A:017C** pri load0824h. V tomto bode debugger iba prečítal stav emulovaného DAC príkazmi `VGA DAC` a `VGA DACPAL`. Ani jeden z nich nevykonáva game OUT alebo dosadenie registra/pamäte.

## Výsledok

**Všetkých256 RGB položiek, teda768 komponentov, je byte-exact zhodných v troch nezávisle dostupných reprezentáciách:**

1. Posledných768B pôvodnéhoGAME.PAL, každý BYTE logicky posunutý doprava2.
2. Reálny game buffer naDS4A64..4D63 v tejto session.
3. Polia RGB emulovaného DAC z read-only debugger výpisu.

DAC hlási **bits6, pel_maskFFh**. Všetky komponenty sú0..63. Výpis ďalej obsahuje state01h,write_index00h,read_indexFFh,pel_index00h; sú to pozorované hodnoty konkrétneho bodu, nie všeobecné invarianty hry. Presné256riadkové porovnanie je `dac_component_comparison.csv`.

Tým sa posilňuje predchádzajúci modeled OUT dôkaz: teraz je potvrdený aj výsledný **stav emulovaného DAC**, nie iba plánované výstupné hodnoty alebo buffer. Nie je to fyzický VGA hardvér, meranie analógového výstupu, úplná video-plane konfigurácia, vykreslený frame alebo Win16 paletová parita.

## Čo debugger číta

Referenčný zdroj `windows_runtime_probe/debug_reference.cpp` má v príkazeDACPAL slučku nad256 `vga.dac.rgb` záznamami a vypisuje ich red/green/blue polia. PríkazDAC vypisuje bitový režim a masku/indexy. Ide o čítanie interného stavu emulátora; neprebieha cez manipuláciu portového read indexu a nemení game paletu. Zhodu zdroja konkrétneho release s binárkou podopiera už uložený tool manifest; nejde o nezávislú formálnu verifikáciu celého emulátora.

VýstupDACPAL má32riadkov po8 RGB trojiciach. Verifier kontroluje postupné indexy00,08,..F8 a presne8 hodnôt v každom riadku; nedovoľuje vynechanie alebo duplicitné indexy. Výsledných768B znovu porovná s originálnym assetom a raw buffer dumpom. `dac_readback.json` navyše musí obsahovať presne rovnaké odpovede ako pôvodnýMCP transcript.

## Súbežný UNKNOWN watch a rozsah scenára

Táto session zachovala44 BYTE memory-change breakpointov odCRT0018 po main017C. Znovu nebola pozorovaná udalosť zmeny hodnoty; všetky cached baseline sú0. Hook4B má iba endpoint dumpy. Rovnaké limity ako v predchádzajúcom UNKNOWN reporte: nie je sledované čítanie, same-value zápis ani zmena/obnova v host callbacke. Žiadna promócia UNKNOWN alebo hook typu.

Spoločný init prefix sa prekrýva so staršími session. Nadväzujúci DAC readback a reálny buffer sú nové dôkazy tejto samostatnej session; každý breakpoint alebo komponent sa nepočíta ako ďalší runtime test. Hra sa po capture zastaví ukončením vlastného emulátora harnessom, nie prirodzeným exitom.

## Reprodukcia a dôkazy

`runtime_watch_dac_readback.py DOSBOX_EXE GAME_DIR IMAGE RELOCS OUT WORK` používa archivovaný `dosbox_watch_support_v1.py`, potom read-only DAC query a768B buffer dump. Pôvodné22 vstupné súbory zostávajú nezmenené. `verify_unknown_watch_capture.py IMAGE RELOCS CURRENT_MAP OUT WORK` rozpoznáDAC capture a nezávisle overí všetky jeho hodnoty, presnú44B množinu, breakpoint lifecycle, reálne relokácie a kompletne rozbalený runtime image. Povolené sú iba query/BP/RUN/dump a dve presnéVGA query; žiadne SR/SM/FM alebo port OUT príkazy.

`write_dac_readback_report.py OUTPUTS WORK` znovu overí proof hashe a vytvorí256riadkovýCSV katalóg. Summary,transcript,snapshots,watch_events,inputs,config,dac_readback aindependent proof sú v `dosbox_dac_readback_runtime/`;14 raw captures vrátane palette bufferu sú vo WORK. Predchádzajúca syntax chyba pri príprave skriptu nespustila žiadny DOSBox proces a nie je runtime scenár.

'''+f"Runtime summary SHA `{p['summary_sha256']}`. Proof SHA `{sha((out/'independent_verification.json').read_bytes())}`. DAC/buffer/expected768B SHA `{sha(actual)}`. GAME.PAL SHA `{d['game_palette_sha256']}`.\n\n"+'''## Meranie

Úspešné runtime scenáre8→9. DOS katalóg125 rozsahov, samostatný Win paletový doplnok4 rozsahy/22 replay prípadov a ostatné replay počty zostávajú. PASS1 je stále57102 B PARTIAL,149 B CLASSIFIED ONLY,44 B UNKNOWN,0 B DEEP VERIFIED. Ide o merateľnú zhodu768/768 komponentov v tomto bode, nie nové percento úplnosti renderer oblasti. Nové sémantické percentáN/A. Dávka je lokálna, zatiaľ nepublikovaná.

'''+table+'''## Runtime testy na vykonanie

Zachytiť sequencer/graphics-controller/video roviny a prvý prirodzený frame. Paletový readback opakovať pri fade/update cestách a porovnať s pôvodnými buffermi. Win16 CreatePalette/WinG farby sú samostatná cesta. Pre UNKNOWN44B treba rozšíriť okno do resource/map init a doplniť skutočné read/write sledovanie.
'''
(r/'DAC_REGISTER_READBACK_REPORT.md').write_text(text,encoding='utf-8');print(json.dumps(dict(report='DAC_REGISTER_READBACK_REPORT.md',components_verified=768,runtime_tests=9)))
