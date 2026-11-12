# PASS1: runtime typy bitmapovej skupiny 2 z UIF.DAT

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

UIF SHA `d5964c31144a67da8b2524e545488fe243f1394e5e4e231b439284c55276c45d`. Source907B SHA `2fb4fd5a75a066c862fde19ad01069b6f1199721fcb5edc59a82058dde15b647`. Runtime1200B SHA `555999152793d9837a07e208225e606af090ecf9cd02f77a354cbb0033e2abd1`. Runtime proof SHA `665010b028ec0f450181a5c9deaaf8f03c4f503aa3a4847ebfe11f43f23a36ea`.

## Meranie

DOS katalóg126→127 rozsahov, +79 inštrukcií/+226B; úspešné prirodzené scenáre11→12. Žiadny nový seeded replay. Runtime BSS tabuľky2518+512=3030B, bez pridania do file-byte mapy. PASS1 stále **57102 B PARTIAL /149 B CLASSIFIED ONLY /44 B UNKNOWN /0 B DEEP VERIFIED**. Nové sémantické percentáN/A bez úplných menovateľov. Dávka je lokálna, zatiaľ nepublikovaná.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Úplné menovatele chýbajú, preto N/A. Iniciačný runtime nie je percento gameplay completeness.

| Oblasť | Predošlý odhad | Nové % | Aktuálny dôkaz (staršie riadky zachované) | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|UIF adresár32 a resource2:907B úplne ohraničených záznamov|ostatné UIF payloady a indexy|skupiny0/1 a ďalšie resources|
| Dátové typy a konštanty |95 %|N/A|font2:127 rozmerových/bitmapových záznamov,651 bitmapovýchB|hlavička index0 a caller domény|textový renderer a hranice znakov|
| Tabuľky a ukazovatele |93 %|N/A|128 runtime FAR pointerov font2 presne zhodných s parserom|iné skupiny a signed char indexy|úplný textový caller kontrakt|
| Funkcie / ASM / CFG |90 %|N/A|font initializer226B/79inštrukcií a prirodzený UI07D9 endpoint|group bounds a error cesty|intro/frame pokračovanie|
| RNG |97 %|N/A|bez RNG runtime|prvý srand/rand|RNG caller trace|
| Scheduler |96 %|N/A|clock init prebehol medzi bodmi|main loop/scheduler|loop vstup|
| DEMO a vstupy |96 %|N/A|prirodzený INT9 install a aux probeFFFFh|key IRQ/DEMO poradie/close|prvý vstupný tick|
| Renderer / VGA |94 %|N/A|768 emulovaných DAC zložiek byte-exact; bits6/maskFF|framebuffer, clipping, fyzický VGA|video roviny a prvý frame|
| GUARD / bossovia |93 %|N/A|bez AI runtime|map init|selector doména|
| Zbrane / projektily |92 %|N/A|bez damage runtime|effect callery|damage trace|
| Sprity / HUD / paleta |92 %|N/A|DOS DAC readback = runtime buffer = asset SHR2|Win OS paleta a celková obrazová parita|Win capture a paired frame|
| SAVE / LOAD |92 %|N/A|BSF native file-check vrátený|SAVE/LOAD a chybové I/O|diskové scenáre|
| Windows Win16 |92 %|N/A|Win1104funkcie/229inštrukcií,23fixupcalls,22replay|skutočnéWin16DS/API/runtime|CreatePalette/WinG trace|

## Runtime testy na vykonanie

Pokračovať za UI07D9 cez zobrazenie prvého intro/menu frame. Zaznamenať pointery a maskované VGA zápisy textového renderera, prirodzené char hodnoty, kerning a clipping. Pre skupiny0/1 zopakovať exact source/bitreverse/pointer porovnanie; samostatne ošetriť cache hit, neplatné WORD argumenty a error cesty. UNKNOWN44B stále potrebuje širší read/write dôkaz, nie iba stabilné endpointy.
