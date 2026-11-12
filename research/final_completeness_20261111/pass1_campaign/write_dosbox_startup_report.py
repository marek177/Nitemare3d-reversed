# -*- coding: utf-8 -*-
import json
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'dosbox_startup_runtime';s=json.loads((d/'summary.json').read_text());v=json.loads((d/'independent_verification.json').read_text());assert s['success'] and v['verified']
text='''# Prvý originálny DOSBox-X runtime: EXEPACK a CRT startup

**Úspešne vykonaný jeden startup test originálneho packed DOS2.0 EXE pod DOSBox-X pre Windows.** Nie je to syntetický Unicorn replay, nie sú nasadené náhradné herné/CRT funkcie a nie sú seedované registre hry. Je to debuggerom inštrumentovaný beh originálneho EXE v DOSBox-X built-in DOS, nie dôkaz reálneho historického DOS/hardvéru ani celej gameplay parity.

Vykonávanie bolo úmyselne zastavené po bode 11EE:00B3 pred voliteľným inicializátorom. Proces potom ukončil harness; návratový kód1 nie je prirodzený herný exit ani potvrdenie pádu hry. Menu, gameplay, renderer a audio testy týmto neprebehli. DEEP VERIFIED zostáva0.

## Nástroj a presné vstupy

Použitý je oficiálny [DOSBox-X v2026.10.01 portable Windows64](https://github.com/joncampbell123/dosbox-x/releases/tag/dosbox-x-v2026.10.01), SDL2 build. ZIP 44 575 207 B, SHA-256 `3c50915e63aefe35777d65ebb4391a06b4a2c2342e4c75cbee6bbda4c6916e33`, zhodný s digestom oficiálneho release assetu. EXE 25 836 544 B, SHA `a82adcfa7af2784566cfeff74c077cefed08505396db2948b7e6aa7d4cee0832`. tool_manifest.json uchováva presné URL, veľkosti a hash extrahovaných súborov. Použité sú prenosné súbory, bez systémovej inštalácie alebo driver DLL.

Game N3D-UNFU.exe 116606 B, SHA `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`, bol skopírovaný do oddeleného workspace drive_c ako N3D20.EXE (nemení sa obsah). Ďalšie herné dáta majú celý manifest inputs.csv. Pôvodné súbory na L: sa nemountujú; po teste sa znovu hashujú a zostali nezmenené. Skutočné dáta ostávajú lokálne, dumpy pôvodného image sa nepublikujú ako súčasť textových reportov.

Konfigurácia: normal CPU core, fixed20000 cycles, svga_s3, memsize16MB, SDL video/audio dummy a software renderer. Mixer nosound. Tieto nastavenia nepreukazujú obrazový alebo zvukový výstup. Hostiteľský smoke test úspešne vykonal DOS echo a exit; počíta sa osobitne, nie ako herný runtime prípad.

## Riadenie a merané body

[Oficiálny DEBUGBOX príkaz](https://github.com/joncampbell123/dosbox-x/wiki/DOSBox%E2%80%90X%E2%80%99s-Supported-Commands) zastaví program na vstupe. Externé debug control rozhranie je overené v tagovanom src/debug/debug_mcp.cpp: lokálny TCP newline protokol REQ/BEGIN/END s PING/EXEC. Server počúva iba127.0.0.1; emulátor sa k nemu pripojí. Zápisy registrov a pamäte hry sa nepoužívajú; iba breakpointy, RUN, EV a MEMDUMPBIN. Breakpoint mechanizmus je inštrumentácia, nie nepodmienečne neinštrumentovaný trace.

| Bod | CS:IP | DS / ES | SS:SP | Dôkaz |
|---|---|---|---|---|
|packed entry|2396:0010|0814 /0814|32E0:0080|MZ entry a PSP→load0824|
|po EXEPACK, CRT entry|1A12:0018|0814 /0814|3D98:0800|originálny SS/SP z unpack parametrov|
|pred optional init|1A12:00B3|2F95 /2F95|2F95:E82A|DS=ES=SS=relocated DGROUP|

Vstupný load segment je0824h, PSP0814h. Všetky hodnoty sú čítané zo skutočného emulovaného procesu, nie zadané ako očakávané vstupné registre. snapshots.json a transcript.json obsahujú surové odpovede a poradie príkazov. DOS version výsledok uložený do2122 je0005h, swapped2120 je0500h, teda pozorované správanie built-in DOS verzie5.0 v tejto konfigurácii.

## Bajtová a stavová kontrola

Pri CRT0018 bol celý runtime image 171360 B porovnaný s kanonickým rozbaleným image po aplikovaní všetkých1670 skutočných EXEPACK relokácií pri load0824h. **Nulové rozdiely**, žiadna dodatočná maska na breakpoint byte. Tým sa potvrdzuje presný pozorovaný image pri tomto transferi; nejde o sémantické overenie každého jeho bajtu alebo vykonanie všetkého kódu.

Pri00B3 má BSS [DS:2650,DS:E030) presne47 584 B a všetky bajty sú nula. Toto je rozsah za počiatočným file image, mimo historických57 295 NON-CODE bajtov. Runtime potvrdil20DC=E82Ah stack snapshot,20E2=2F95h,211E=0814h PSP a swapped verziu DOS. Celý runtime memory capture má hash uvedený nižšie a nezávislá kontrola ho znovu porovnáva byte-for-byte.

Dumpy sa čítajú po úsekoch najviac8000h B s normalizovaným segmentom. Prvý nesegmentovaný pokus sa začal odchyľovať od offset10000h kvôli16-bitovej real-mode adresácii debug dumpu; nebol započítaný ako dôkaz rozdielu EXE. Chunkovaný výsledok je presný. Prvé tri pokusy s konzolovým rozhraním skončili hostiteľským kódomC0000409; problém bol odstránený pridelením samostatnej Windows konzoly namiesto presmerovaných stdio pipes. Nie je to dôkaz chyby hry. Staré neúspešné logy sú zachované v dosbox_startup_runtime_attempt1..4 a nepočítajú sa ako úspešné runtime prípady.

## Reprodukcia a nezávislé overenie

1. acquire_dosboxx_windows.py WORKDIR METADATA_OUT stiahne alebo overí presný ZIP a extrahuje len vybrané portable súbory.
2. runtime_dosbox_startup.py DOSBOX_EXE GAME_DIR IMAGE RELOCATIONS OUT WORK vytvorí oddelený mount, hash manifest a konfiguráciu, spustí originálny EXE, nastaví breakpoints, zachytí registre a pamäť a ukončí tento vlastný proces. Všetky časy sú ohraničené, nie je potrebný ručný NEXT.
3. verify_dosbox_startup_capture.py IMAGE RELOCATIONS RUNTIME_OUT WORK nezávisle porovná skutočné dumpy,1670 relokácií, BSS, registre, manifest a surový transcript. independent_verification.json pinne hash všetkých použitých výstupov; central catalog ich pri importe znovu overí.

Pri opakovaní sa PSP/load adresa môže zmeniť; skript ju odvodzuje z DOS procesu a nepredpisuje0824h ako pevný vstup. Fixed release URL a lokálne SHA sú súčasťou provenance. [Oficiálne command-line options](https://github.com/joncampbell123/dosbox-x/wiki/DOSBox%E2%80%90X%E2%80%99s-Command%E2%80%90Line-Options) dokumentujú explicitnú konfiguráciu, časový limit a logovanie.

'''
text+=f"Runtime image SHA `{v['runtime_image_sha256']}`. BSS SHA `{s['checks']['bss_sha256']}`. Summary SHA `{v['summary_sha256']}`.\n\n"
text+='''## Meranie

PASS1 ostáva **57 102 B PARTIAL,149 B CLASSIFIED ONLY,44 B UNKNOWN,0 B DEEP VERIFIED**, spolu57 295 B. Počet originálnych runtime testov sa mení **0→1**, presne jeden debuggerom pozorovaný startup DOS2.0 pod DOSBox-X built-in DOS. Controlled Unicorn replay count sa tým nezvyšuje. Sémantické percentá a DEEP VERIFIED sa tým automaticky nemenia. Historické reporty uvádzajú runtime0 v čase svojho vzniku; aktuálny consolidated report ich nahrádza pre súčasný stav.

Publikovaná analytická snímka ba27379dd28c9a689d15233b0fd7017867f50114 túto novú lokálnu runtime dávku ešte neobsahuje. Linux ELF balík používateľa zostáva oddelený audit; jeho nevyužiteľnosť vo Windows už neblokuje tento portable Windows startup test.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Menovatele stále chýbajú, preto N/A. Presná bajtová zhoda image a jeden startup nie sú percentom dokončenia hry.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|EXEPACK runtime image presný|ostatné DOS/Win verzie|opakovať originálny loader|
| Dátové typy a konštanty |95 %|N/A|BSS nulovanie a DOS version v runtime|149 B iba klasifikované|watchpointy writerov|
| Tabuľky a ukazovatele |93 %|N/A|DS=ES=SS priB3, PSP snapshot|neskoršie zmeny|optional init a startup koniec|
| Funkcie / ASM / CFG |90 %|N/A|packed→CRT→B3 skutočná cesta|zvyšok inicializácie|post-callback body|
| RNG |97 %|N/A|bez nového RNG runtime|poradie hry|prvý srand/rand trace|
| Scheduler |96 %|N/A|bez gameplay runtime|prirodzené callery|vstup do main loop|
| DEMO a vstupy |96 %|N/A|bez input runtime|driver ABI|prirodzené demo spustenie|
| Renderer / VGA |94 %|N/A|bez grafickej parity|render a clipping|VGA mode/init trace|
| GUARD / bossovia |93 %|N/A|bez AI runtime|selector doména|map init trace|
| Zbrane / projektily |92 %|N/A|bez damage runtime|damage callery|effect trace|
| Sprity / HUD / paleta |92 %|N/A|bez nového runtime|resource identity|skutočný resource load|
| SAVE / LOAD |92 %|N/A|bez herného file I/O runtime|formát a chyby|config/save loader trace|
| Windows Win16 |92 %|N/A|bez Win runtime|NE prostredie|samostatný Win16 audit|

## Runtime testy na vykonanie

Pokračovať za00B3 cez optional callback a CRT inicializáciu, potom sledovať prvý herný entry, srand/rand a VGA setup. Odlišovať nepozmenený súbor od debugger inštrumentácie a built-in DOS od historického MS-DOS. Pre gameplay/alokátor/renderer testy treba samostatné merateľné scenáre. Vstupná 17 B nulová medzera aj ostatné NON-CODE neznáme vyžadujú vlastné writer/consumer dôkazy; startup image zhoda ich nemení na padding. PE32 sa nevytvára.
'''
(r/'DOSBOX_STARTUP_RUNTIME_REPORT.md').write_text(text,encoding='utf-8')
