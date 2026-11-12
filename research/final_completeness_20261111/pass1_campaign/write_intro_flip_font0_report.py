"""python write_intro_flip_font0_report.py OUTPUTS_DIR"""
import hashlib,json,sys
from pathlib import Path
r=Path(sys.argv[1]);s=json.loads((r/'intro_flip_font0_fields/summary.json').read_text());catalog=json.loads((r/'campaign_catalog/summary.json').read_text());source=json.loads((r/'intro_flip_font0_fields/source_manifest.json').read_text())
assert catalog['runtime_tests']==16 and catalog['functions']==130 and catalog['runtime_bss_table_bytes_outside_file']==3542 and catalog['runtime_buffer_refinement_bytes_already_in_pass1']==2400
for item in s['files']:assert hashlib.sha256(Path(item['path']).read_bytes()).hexdigest()==item['sha256']
text=f'''# DOS2: prirodzený page flip, DAC a bitmapová skupina0

Pribudli **dva prirodzené DOSBox-X scenáre**, bez nového započítania známych funkcií alebo starších replay testov. Nový runtime dokladá rozdiel medzi naprogramovaným display-start a neskôr prevzatým real-start, presný obsah štyroch rovín stránkyA400h, zhodu všetkých použitých6-bit farieb s CD assetom a načítanie skupiny0 s127 bitmapovými záznamami/128FAR ukazovateľmi.

Aktuálny katalóg:130 ohraničených DOS funkcií,4993 inštrukcií/12456B a16 zachovaných runtime scenárov. PASS320 ostáva **57102 B PARTIAL,149 B CLASSIFIED ONLY,44 B UNKNOWN,0 B DEEP VERIFIED**. Nepribudli nové sémantické percentá.

## Dva samostatné prirodzené behy

Oba používajú pôvodný zabalený DOS2 EXE, oficiálny DOSBox-X2026.10.01 a23 izolovaných vstupov: pôvodných22 plus explicitne pridaný CD `DSTOPEN.IMG`. Nie je to dôkaz pôvodnej distribučnej konfigurácie ani beh pôvodného CD EXE. Všetky zdrojové hashy ostali nezmenené. Žiadne inštrukcie hry alebo registre CPU sa neprepisovali.

|Scenár|Kanonický endpoint|Skutočný endpoint|Page WORD012C/012E|Programmed start|Real start|
|---|---|---|---|---|---|
|po okamžitom flipe|0D29:07AE|154D:07AE|A400/A000|4000h|0000h|
|po font0 pred wait0424|0D29:07C1|154D:07C1|A400/A000|4000h|4000h|

Nejde o kontinuálny scanout trace medzi týmito bodmi; sú to dve zachované prirodzené cesty so spoločným prefixom a odlišnými endpointmi. Prvý beh zachytil stav hneď po volaní0156:008E. Druhý vykonal aj0156:0254(argument2) a0D29:016A(argument0); zastavil sa pred volaním wait0424. Klávesnicový vstup sa zatiaľ neposielal.

## Flip a význam real-start

Už analyzovaná funkcia0156:008E vymení WORD DS012C/012E a zapíše CRTC register0Ch cez WORD OUT3D4h. Nový dôkaz neopakuje jej8192 starších riadených scenárov: overuje prirodzený účinok na emulované zariadenie.

Bezprostredne po návrate je **display-start=4000h, real-start=0h**. Preto nemožno tento prvý breakpoint vydávať za dokončené prevzatie novej stránky. Po prirodzenom pokračovaní a načítaní font0 už **oba údaje majú4000h**.

Oficiálny matching-release zdroj interpretuje tieto polia cez `VGA_DisplayStartLatch`, ktorý priraďuje real-start z display-start s memory maskou; drawing následne používa real-start. [Primárny zdroj DOSBox-X](https://raw.githubusercontent.com/joncampbell123/dosbox-x/dosbox-x-v2026.10.01/src/hardware/vga_draw.cpp). Lokálna reprodukovateľná referencia má SHA256 `{source['sha256']}`; fyzické1-based riadky {source['line_display_start_latch']} a{source['line_draw_address']} sú uvedené v `source_manifest.json`. Zdroj je interpretáciou matching-release polí, nie dôkazom totožnosti build procesu prenosného EXE.

Attribute controller je enabled, color-plane-enable0Fh, pel-pan0, color-select0. GC read/write mode0, read-map0; unchained M_VGA. Zápis do CRTC a prevzatie štartovej adresy sa teda v zachytených stavoch rozlišujú merateľne.

## Pixelové dáta, DAC a RGB6 parita

V oboch behoch sa všetky4×16000 B stránkyA400h presne zhodujú s pôvodnými64000 indexovanými pixelmi dekódovaného CD assetu. Hashy rovín sú totožné s predchádzajúcou back-buffer dávkou. Rozdiel je nové prirodzené programovanie display-start a následné prevzatie do real-start.

Skutočný DAC readback má768 komponentov0..63 a presne sa zhoduje s runtime paletovým buffrom aj `GAME.PAL` tail>>2. DAC má6-bit režim a pel-maskFFh. CD paleta a GAME.PAL sa v pôvodných8-bit komponentoch líšia557-krát; po SHR2 ostanú iba3 rozdielne komponenty, všetky v indexe255:

|Index|CD RGB6|GAME.PAL a runtime DAC RGB6|Počet použití v obrázku|
|---|---|---|---:|
|255|63,63,63|15,39,3|0|

Obrázok používa71 paletových indexov. Pre každý z64000 pixelov sú všetky3 kvantované komponenty zhodné: **0 rozdielov v192000 RGB6 komponentoch**. SHA256 celej RGB6 sekvencie: `{s['quantized_frame_rgb6_sha256']}`. Tvrdenie sa týka konkrétneho CD obrázka a zachytenej emulovanej palety; nie všetkých256 farieb, pôvodných8-bit hodnôt, fyzického VGA alebo host gamma.

![Rekonštrukcia runtime rovín a DAC, nie host screenshot](intro_flip_font0_fields/runtime_page_dac6_reconstruction.png)

Náhľad vznikol zo zachytených rovín a DAC;6-bit komponenty sa pre PNG škálujú celočíselne `v*255//63`. Nie je to screenshot výstupnej plochy DOSBox-X ani záznam všetkých riadkov jedného fyzického frame. Úplná host-surface/scanout parita ostáva otvorená.

## Font0: presné intervaly a formát

Zdroj je UIF.DAT index0, dĺžka900 B, file interval[192,1092). Runtime buffer je kanonicky20B9:0000, image **[20B90,21040)** s kapacitou1200 B; skutočne28DD:0000. Zhodu po natívnom bitreverse potvrdil nezávislý parser aj raw capture.

|Image interval, end exclusive|B|Lokálne potvrdená rola|
|---|---:|---|
|[20B90,20B92)|2|header06h/07h; pointer index0, plná sémantika otvorená|
|[20B92,20F14)|898|127 záznamov:254B height/width hlavičiek a644B bitmapových payloadov|
|[20F14,21040)|300|nulový zvyšok kapacity v tomto behu, nie dokázaný padding|

Každý záznam má `BYTE height; BYTE width; BYTE bitmap[height*ceil(width/8)]`. Maximálne rozmery pozorovaných127 záznamov sú6×7. Zhoda s header06h/07h je pozorovanie; význam headera pre všetkých callerov a vstupy sa tým neuzatvára. Každý payload bajt po runtime transformácii presne zodpovedá obrátenému poradiu bitov v source bajte.

Celých1200 B patrilo do predtým PARTIAL bufferu. Táto dávka pridáva presnú typovú a source väzbu, nie ďalších1200 novo pokrytých NON-CODE B. `runtime_field_intervals.csv/json` zachovávajú explicitné hranice, typy a stav PARTIAL.

Tabuľka128FAR pointerov je DS **[3690,3890)**, image **[2ADA0,2AFA0)**,512 B mimo pôvodného171360B obrazu. Index0 ukazuje na header; index1..127 na presné začiatky záznamov. Každý segment je28DDh pri load0824h. Zdrojová skupina je0, cache flag0=1, flag2=1; font2 buffer a jeho128 pointerov zostávajú zhodné s predchádzajúcou analýzou.

![Bitmapová skupina0](intro_flip_font0_fields/font0_bitmap_atlas.png)

Atlas predstavuje raw bitmapy, nie prirodzené vykreslenie textu. Znaky128..255, signed-char indexovanie, word argumenty mimo prirodzených skupín a chyby cache/I/O zostávajú otvorené. Font1 sa v tejto dávke prirodzene nenačítal.

## Metodika a obmedzenia zberu

Prvý beh má27 raw captures, druhý29. Nezávislý verifier kontroluje pôvodný packed EXE a relokovaný runtime obraz,23 vstupov, presné breakpointy, DAC transcript, source transformáciu, pointery a portový whitelist. UNKNOWN44B malo od CRT entry po endpoint nulové cached-value udalosti; candidate hook4B ostal na koncoch nezmenený. Čítania a zápisy rovnakej hodnoty tým nie sú vylúčené.

Všetky plane dumpy sa získali až pri zastavenom CPU: dočasný OUT3CE/3CF zvolil read-map0..3, potom sa obnovil read-map0 aj pôvodný index6. GC/SEQ/MODE/AC hlásenia pred a po sa zhodujú, po intervencii nebolo RUN. VGA read latche sa neoverovali ani neobnovovali. Zásah teda neovplyvnil už vykonanú cestu hry, ale nemennosť celého interného zariadenia sa netvrdí.

Centrálny katalóg má teraz3542B pomenovaných runtime BSS tabuliek mimo EXE, z toho nových512B font0 pointerov. Oddelený `runtime_buffer_refinements.csv` obsahuje6 intervalov font0/font2 s úniou2400 už klasifikovaných B. Tieto počty sa nepripočítavajú k57100 typovaným pôvodným NON-CODE B ani k57102 PARTIAL B.

## Reprodukcia a nové artefakty

- `runtime_watch_intro_flip.py DOSBOX_EXE GAME_DIR IMAGE RELOCS OUT WORK startup CD_ASSET`: endpoint07AE, prirodzený flip a DAC.
- `runtime_watch_intro_font0.py ...`: endpoint07C1, navyše font0 buffer/pointer capture.
- `verify_unknown_watch_capture.py IMAGE RELOCS MAP OUT WORK`: explicitne rozlišuje programmed/latched start a font0 branch; overí oba zachované scenáre.
- `audit_intro_flip_font0_fields.py IMAGE UIF GAMEPAL CD FLIP_OUT FLIP_WORK FONT_OUT FONT_WORK OUT`:127 záznamov,128 pointerov,256 paletových položiek, dva stage riadky, intervalová mapa, BSS katalóg a rekonštrukcie PNG. Matching-release zdrojový súbor je iba lokálna referencia; jeho URL/hash sú v manifeste.
- `independent_decode_and_catalog.py DECODER OUTPUTS` a `render_campaign_status.py OUTPUTS`: aktuálne súčty, bez zvýšenia počtu funkcií alebo replay prípadov.

Predchádzajúca overená GitHub snímka má14 runtime scenárov. Táto nová dvojica a jej typové refinements sú lokálne, kým nie je zaznamenané samostatné potvrdenie publikácie.

## Aktualizácia 13 oblastí

TABLE_PLACEHOLDER

## Runtime testy na vykonanie

1. Zachytiť celý scanout frame alebo host-surface výstup po real-start4000h; porovnať všetky výstupné riadky a presne definované RGB škálovanie.
2. Analyzovať wait0424 a podporovaný spôsob skutočného emulovaného stlačenia klávesu; zachytiť INT9 a prirodzený odchod z čakania.
3. Pokračovať cez083D:0008 a načítanie font1; zopakovať buffer/pointer/source porovnanie. Následne prvé menu a map init.
4. Uzavrieť význam index0 headerov, signed-char domény a callerov textových metrík; negarantovať bezpečnosť neplatných WORD argumentov.
5. Rozšíriť UNKNOWN44 read/write dôkazy za intro, vrátane host callback I/O; stabilné cached-value údaje nestačia na DEEP VERIFIED.
'''
prev=(r/'VGA_BLOCK_BLIT_RUNTIME_REPORT.md').read_text(encoding='utf-8');table=prev[prev.index('## Aktualizácia 13 oblastí'):prev.index('## Runtime testy na vykonanie')]
table=table.replace('ABI10WORD polí; source stride, signed key a y lowBYTE; staršie asset intervaly zachované','font0:900B source→127 záznamov/644B bitmap; nový1200B runtime layout').replace('neuzavreté caller domény a globálne invarianty','index0 header, signed-char a caller domény').replace('callery a rozsahy zdrojových dát','textové metriky a header callery')
table=table.replace('128 runtime FAR pointerov font2 presne zhodných s parserom','nových128 font0FAR pointerov;512B BSS mimo EXE; font2 zachované').replace('iné skupiny a signed char indexy','font1 a signed-char indexy').replace('úplný textový caller kontrakt','prirodzené načítanie font1')
table=table.replace('prirodzený DOSBox back-buffer64000 pixelov vo4 rovinách byte-exact','programmed4000→real4000 v neskoršom bode;4roviny a AC overené').replace('viditeľný flip, RGB paleta a text/menu','host-surface/úplný scanout, text/menu').replace('display-start po prirodzenom flipe','scanout a prirodzený vstup')
table=table.replace('nový CD back-buffer; starší DOS DAC readback zachovaný','DAC768 zložiek;71 použitých farieb,192000 RGB6 komponentov bez rozdielu').replace('CD palette vs GAME.PAL; Win OS a celý frame','nepoužitý255 sa líši; Win OS a host frame').replace('Win capture a paired frame','scanout s DAC a font1')
text=text.replace('## Aktualizácia 13 oblastí\n\nTABLE_PLACEHOLDER\n\n',table)
receipt=r/'CAMPAIGN_INTRO_FONT0_PUBLICATION_RECEIPT_20261112.json'
if receipt.exists():
 p=json.loads(receipt.read_text());text=text.replace('Predchádzajúca overená GitHub snímka má14 runtime scenárov. Táto nová dvojica a jej typové refinements sú lokálne, kým nie je zaznamenané samostatné potvrdenie publikácie.','Táto dávka je publikovaná a blob po blobe overená v analytickom commite '+p['commit']+'. Strojové potvrdenie: CAMPAIGN_INTRO_FONT0_PUBLICATION_RECEIPT_20261112.json. Metadata follow-up môže mať novší branch head.')
(r/'INTRO_FLIP_DAC_FONT0_REPORT.md').write_text(text,encoding='utf-8');print(json.dumps(dict(report='INTRO_FLIP_DAC_FONT0_REPORT.md',runtime_tests=16,functions=130,runtime_bss=3542,used_pixel_rgb6_differences=0)))
