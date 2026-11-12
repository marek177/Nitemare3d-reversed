# -*- coding: utf-8 -*-
"""python write_font2_runtime_report.py OUTPUTS"""
import hashlib,json,sys
from pathlib import Path
r=Path(sys.argv[1]);s=json.loads((r/'font2_runtime_fields/summary.json').read_text());out=r/'dosbox_font2_runtime';p=json.loads((out/'independent_verification.json').read_text());assert p['font2_runtime_verified'];sha=lambda b:hashlib.sha256(b).hexdigest()
for item in p['files']:assert sha(Path(item['path']).read_bytes())==item['sha256']
old=(r/'SOUND_CPU_MEMORY_TRACE_REPORT.md').read_text(encoding='utf-8');table=old[old.index('## Aktualizácia 13 oblastí'):old.index('## Runtime testy na vykonanie')]
table=table.replace('|SND.DAT[192,666) → 79 runtime záznamov; všetky payload bounds platné|audio formáty a zvyšok kontajnera|payload spotrebitelia/WORX|','|UIF adresár32 a resource2:907B úplne ohraničených záznamov|ostatné UIF payloady a indexy|skupiny0/1 a ďalšie resources|')
table=table.replace('|122 rekonštruovaných CPU memory ranges bez zásahu UNKNOWN44B v sound init okne|host callbacky a iné časové okná|rozšírená read/write instrumentácia|','|font2:127 rozmerových/bitmapových záznamov,651 bitmapovýchB|hlavička index0 a caller domény|textový renderer a hranice znakov|')
table=table.replace('|hook DS2356 má rovnaký relokovaný obsah v oboch endpoint dumpoch|medzistavy a nepriame čítanie|bezpečná kalibrácia nenulového watch|','|128 runtime FAR pointerov font2 presne zhodných s parserom|iné skupiny a signed char indexy|úplný textový caller kontrakt|')
table=table.replace('|4699 x86 trace záznamov,151 canonical byte matches,6 INT21 vstupov|host callback internals a celý herný tok|prvý map/scheduler trace|','|font initializer226B/79inštrukcií a prirodzený UI07D9 endpoint|group bounds a error cesty|intro/frame pokračovanie|')
text='''# PASS1: runtime typy bitmapovej skupiny 2 z UIF.DAT

Dvanásty zachovaný scenár pôvodného DOS EXE pokračoval za úvodnú inicializáciu na **0D29:07D9**, skutočne **154D:07D9**. Tento bod je bezprostredne po inicializácii grafickej skupiny 2 v úvodnej ceste. Pribudla presná väzba reálneho resource súboru na file-backed NON-CODE buffer, jeho bitovú transformáciu a runtime FAR pointer tabuľku.

## Reálne súbory a adresy

- UIF.DAT má 526520 B. Prvých 192 B tvorí 32 záznamov `WORD length; DWORD offset`; celý runtime adresár na relokovanom `1BDB:0000` sa s nimi zhoduje.
- Záznam resource indexu 2 má dĺžku **907 B**, zdrojový offset **2237** a koniec **3144**. Jeho rozsah leží celý v pôvodnom súbore.
- Cieľ je kanonicky **20B9:0960**, image **[214F0,219A0)** s kapacitou 1200 B. Skutočný segment po load0824h je **28DD**.
- Po načítaní a transformácii sa všetkých 1200 runtime bajtov zhoduje s nezávisle vypočítaným výsledkom: 907 spracovaných B a 293 nulových bajtov zvyšku kapacity.

Týchto 1200 B už bolo PARTIAL v pôvodnej mape. Nová dávka ich nepovyšuje druhýkrát; dopĺňa skutočné typy, source väzby a prirodzený obsah. Zvyšných 293 B nie je dokázaný padding, ale pozorovaný zvyšok bufferovej kapacity.

## Ohraničený initializer a presný algoritmus

**0D29:016A..024C**, image **[D3FA,D4DC)**, má **226 B /79 inštrukcií**. Každá hranica a byte sekvencia je nezávisle overená proti obrazu aj inventáru.

```text
g = lowBYTE(argument)
selected_group = g
if initialized[g] != 0: return
initialized[g] = 1
read_resource(full_WORD_argument, far20B9:(1200*g))
pointer[g][0] = block_start
position = 2
for id = 1..127:
    pointer[g][id] = block_start + position
    height = BYTE[position]
    width  = BYTE[position+1]
    bytes  = height * ceil(width/8)
    for i = 0..bytes-1:
        reverse_bits_in_place(BYTE[position+2+i])
    position += 2 + bytes
```

Rozdiel vstupných šírok je dôležitý: výber skupiny a cache flag používajú dolný BYTE, ale resource reader dostane celý pôvodný WORD argument. Neexistuje lokálna kontrola skupiny alebo kapacity cieľa. Prirodzená hodnota je 2; iné WORD hodnoty s rovnakým dolným BYTE nie sú týmto bezpečnostne uzavreté. Cache flag sa nastavuje pred I/O, takže chybová vetva a opakovaný pokus si vyžadujú samostatnú analýzu.

## Presný vnútorný formát 907 B

|Rozsah obrazu, end exclusive|B|Dôkazmi podložená rola|
|---|---:|---|
|[214F0,214F2)|2|úvodná dvojica 09h/08h, pointer index0; úplná rola stále PARTIAL|
|[214F2,2187B)|905|127 variabilných bitmapových záznamov|
|[2187B,219A0)|293|nulový runtime zvyšok kapacity, nie dokázaný padding|

Každý záznam 1..127 má **BYTE height, BYTE width**, potom `height * ((width+7)/8)` bitmapových bajtov. Spolu ide o 256 metadátových B vrátane úvodnej dvojice a **651 bitmapových B**. Parser končí presne na907, bez neinterpretovaného zvyšku načítaného payloadu.

Poradie osí nie je odvodené iba zo vzoru. Spotrebiteľ **0156:09C4** načíta prvý WORD, používa BL ako počet riadkov, BH upraví na `(width+7)>>3` a po riadku zvyšuje video offset o80. Textový caller **0D29:00FC..0105** navyše zvyšuje X o `BYTE[record+1]+1`, čo potvrdzuje rolu druhého bajtu ako šírky. Presné ASM kontexty sú uložené; celý textový renderer sa týmto nevyhlasuje za dokončený.

Transformátor **0FBA:00D2** bol už nezávisle analyzovaný ako obrátenie poradia ôsmich bitov. Teraz sa jeho použitie prirodzene potvrdzuje porovnaním všetkých 651 payload bajtov. Dvojbajtové hlavičky sa nemenia.

![Rekonštrukcia bitmapových záznamov skupiny2, nie screenshot hry](font2_runtime_fields/font2_bitmap_atlas.png)

Atlas vznikol z reálneho runtime buffera, riadkovo a s nízkym bitom vľavo po transformácii. Záznamy sú uložené v poradí indexov; ide o rekonštrukciu dát, nie dôkaz celej VGA textovej kresliacej cesty, kerningu alebo clippingu.

## FAR pointery a otvorené indexy

Všetkých **128 FAR pointerov** na DS3A90..3C8F presne zodpovedá parseru. Index0 je 28DD:0960; index1 je28DD:0962 a ďalšie smerujú na vypočítané začiatky záznamov. Samostatný BSS rozsah **[2B1A0,2B3A0)** má512B, mimo file image aj PASS320 baseline.

Character caller používa pri BYTE znaku **CBW**, teda signed8 rozšírenie. Bajty128..255 môžu smerovať na položky pred nominálnym začiatkom skupiny. Táto dávka preto neprezentuje tabuľku ako bezpečne indexovanú pre všetkých256 znakov. Úplné domény textových vstupov, ostatné skupiny0/1 a rola index0 zostávajú otvorené.

## Runtime a nezávislá reprodukcia

`runtime_watch_font2.py DOSBOX_EXE GAME_DIR IMAGE RELOCS OUT WORK` používa pôvodné EXE a22 nezmenených source súborov. Zachytí UIF192B adresár,1200B block,512B pointer table, cache flagy a selected_group2. Presná44B UNKNOWN množina je naďalej sledovaná cez memory-change breakpointy od CRT0018 až po UI07D9; bez udalosti zmeny hodnoty. Limity read/same-value/host callback sledovania zostávajú.

`verify_unknown_watch_capture.py IMAGE RELOCS CURRENT_MAP OUT WORK` nezávisle preverí19 raw captures, oba endpointy, reálny image/relokácie, source/copy SHA a všetkých127 záznamov/128 pointerov. Ani registre, game dáta, API odpovede alebo source EXE sa nevynucujú patchovaním. Harness po capture ukončí svoj emulátor; nejde o prirodzený game exit.

`audit_font2_runtime_fields.py IMAGE INVENTORY ABS_DECODER UIF RUNTIME_OUT WORK OUT` pridáva CFG initializeru, granularitu dát a dimension consumer kontexty. Výstupy sú `font_group_init.csv`, `glyph_records.csv`, `runtime_pointer_slots.csv`, `runtime_field_intervals.csv`, `runtime_uif_directory.csv`, `external_bss_tables.csv`, summary a atlas. Všetky actual glyph payloady majú source aj runtime SHA. Súborový adresár má tiež32 bounds kontrol; sémantika ostatných payloadov sa netvrdí.

'''+f"UIF SHA `{s['uif_sha256']}`. Source907B SHA `{s['source_block_sha256']}`. Runtime1200B SHA `{s['runtime_block_sha256']}`. Runtime proof SHA `{s['runtime_proof_sha256']}`.\n\n"+'''## Meranie

DOS katalóg126→127 rozsahov, +79 inštrukcií/+226B; úspešné prirodzené scenáre11→12. Žiadny nový seeded replay. Runtime BSS tabuľky2518+512=3030B, bez pridania do file-byte mapy. PASS1 stále **57102 B PARTIAL /149 B CLASSIFIED ONLY /44 B UNKNOWN /0 B DEEP VERIFIED**. Nové sémantické percentáN/A bez úplných menovateľov. Dávka je lokálna, zatiaľ nepublikovaná.

'''+table+'''## Runtime testy na vykonanie

Pokračovať za UI07D9 cez zobrazenie prvého intro/menu frame. Zaznamenať pointery a maskované VGA zápisy textového renderera, prirodzené char hodnoty, kerning a clipping. Pre skupiny0/1 zopakovať exact source/bitreverse/pointer porovnanie; samostatne ošetriť cache hit, neplatné WORD argumenty a error cesty. UNKNOWN44B stále potrebuje širší read/write dôkaz, nie iba stabilné endpointy.
'''
(r/'FONT2_RUNTIME_FIELDS_REPORT.md').write_text(text,encoding='utf-8');print(json.dumps(dict(report='FONT2_RUNTIME_FIELDS_REPORT.md',glyphs=127,pointers=128,runtime_tests=12)))
