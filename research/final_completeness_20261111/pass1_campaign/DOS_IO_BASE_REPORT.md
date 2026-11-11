# DOS 2.0 — I/O báza, setter/getter a DSP detekcia

11. 11. 2026. PARTIAL, nové DEEP VERIFIED0 B, hardware/originálny runtime0. Prvý prioritný kandidát z CS atlasu má teraz konkrétny lokálny dátový kontrakt.

## Dátové polia

| Image end-exclusive | CS15BF pole | Typ a počiatočný stav |
|---|---|---|
| 189E0..189E2 | 2DF0 | WORD báza I/O portov, inicializované0 |
| 17C00..17C02 | 2010 | WORD device/mode code, inicializované0; setter zapisuje zero-extended AL |

Pole2DF0 nie je súborový handle:21 fixných referencií ho načítava do DX pre IN/OUT alebo ním konfiguruje tieto operácie. Názov konkrétneho device/mode code pri2010 zatiaľ nie je uzavretý. Rozsahy, initial bytes a SHA sú v `dos_io_base/data_intervals.csv`; referencie v `io_base_xrefs.csv`.

## Lokálne funkčné rozsahy

| Kandidát | Image end-exclusive | Inštrukcie/B | Tabuľkový AH selector |
|---|---|---:|---|
| mixer_index0c_write | 17DCC..17DDC | 8/16 | 4Bh |
| mixer_index2e_write | 17DDC..17DF8 | 14/28 | 4Ch |
| mixer_index0a_write | 17DF8..17E08 | 8/16 | 4Ah |
| bios_tick_wait | 18A31..18A46 | 15/21 | bez zhody v82 slotoch |
| io_base_setter | 1A44A..1A456 | 4/12 | 02h |
| io_base_getter | 1A456..1A45C | 3/6 | 37h |
| dsp_base_probe | 1B768..1B7BB | 30/83 | bez zhody v82 slotoch |

Setter uloží BX do bázy, vynuluje AH a uloží AX do2010. Nevaliduje port, nenulovosť ani podporovaný device code. Getter vráti AX=báza a vykoná CLC, teda jeho CF **nepotvrdzuje prítomnosť zariadenia**.

Tri indexové write rutiny pošlú index0Ch/2Eh/0Ah na base+4 a dátový BYTE na base+5. Pri0Ch/0Ah je údaj vstupBL. Pri2Eh je údaj `BL | ((BL<<4)&FFh)`; zároveň mení BH aj BL. Bez obmedzenia vstupného BL sa táto operácia nesmie zjednodušiť na čisté zdvojenie nízkeho nibble. Tieto rutiny neukladajú všetky menené registre a FLAGS, preto caller ABI ostáva samostatnou otázkou.

## DSP probe algoritmus

Rutina nastaví base=0200h. Pre kandidáta pošle1 na base+6, zavolá wait s BX=1, pošle0 na ten istý port a nastaví CX=200. Polluje base+0Eh, kým bit7 nie je1 alebo kým LOOP nevyčerpá počet. Pri pripravených dátach prečíta base+0Ah a vyžadujeAAh. Nesprávny BYTE vedie priamo k ďalšej báze, nie k obnoveniu poll počtu na tej istej adrese.

Po neúspechu zvýši pole base o10h. Pokračuje pri base<0300h. Testuje teda16 báz0200h..02F0h;0300h už netestuje. Úspech zavolá wait s BX=4 a vráti CF=0. Konečný neúspech vracia CF=1 a **v globálnom poli nechá0300h**. Nevráti ho na nulu. Skutočné poradie BIOS tickov, zariadenie a runtime caller reakcia zatiaľ nie sú overené.

Identifikácia protokolu má primárny podklad v Creative [Sound Blaster Series Hardware Programming Guide](https://www.ardent-tool.com/sound/Sound_Blaster_HW_Programming_Guide_1st.pdf), DSP I/O/reset kapitola (PDF strany24–25): reset+6, status+Eh, read+Ah a odpoveďAAh. To identifikuje zamýšľané rozhranie, nie fyzicky prítomnú kartu ani zhodu s jej minimálnym časovaním. Manuál nebol kopírovaný do výstupov.

## Wait kontrakt a otvorené okraje

Wait ukladá AX,BX,CX,DX, nastaví AX=0, zavolá INT1Ah a k vstupnému BX pripočíta získané DX. Potom opakovane volá INT1Ah, porovnáva DX s cieľovým BX a čaká cez unsigned JBE. Pri normálnom návrate obnoví uložené registre; FLAGS neobnovuje. DSP probe sa spolieha aj na obnovenie DX portu cez tento helper.

Ide o porovnanie dolného WORD, nie uzavretý32-bitový elapsed-time algoritmus. Pri obtočení cieľa môže podľa lokálnej aritmetiky skončiť skôr; cieľFFFFh nemá v16-bitovom DX väčšiu hodnotu a jeho ukončenie z tohto porovnania nevyplýva. Presný BIOS návratový kontrakt a prirodzené tick hodnoty treba overiť; zatiaľ sa z toho nerobí potvrdený runtime bug.

## Reprodukcia a pokrytie

`python audit_dos_io_base.py IMAGE ABSOLUTE_DECODER_DIRECTORY REFERENCE_ATLAS_CSV OUT_DIR` kontroluje hash obrazu, kritické strojové vzory, celé kandidátne rozsahy, RET konce,21 referencií a82-slotové väzby. Výstup má sedem inštrukčných CSV, xrefs, dáta a summary.json. CFG slučky a vetvy sú dostupné priamo v presne dekódovaných adresách; externý INT1Ah kontrakt je otvorený.

Nezávislé zlúčenie pridalo182 B kódu a4 B dát bez konfliktu. Centrálna partition:27 kandidátnych funkcií,867 inštrukcií/1 978 B,812 B dát,168 570 B aktuálne neposúdených,86 intervalov. Žiadny prírastok DEEP VERIFIED.

Kandidátny atlas bol znovu vytvorený do `dos_cs_reference_atlas_after_io/`, s hashom aktuálnej centrálnej partition. Neposúdená kandidátna únia klesla139→135 B; ide o4 B prechod CLASSIFIED ONLY→lokálny PARTIAL, nie o percento PASS320. Pôvodná snímka atlasu ostáva zachovaná. Členstvo pôvodného ledgeru UNKNOWN.

Nasledujúce testy DOSBox-X: log setterBX/AL; pri probe log16 kandidátov, IN status/read odpovede, CF a výslednú bázu; po neúspechu sledovať callerov s bázou0300h; pri wait zaznamenať vstupný tick, cieľ a wrap situácie. Žiadne porty sa pri tejto statickej dávke nevykonali na skutočnom hardvéri.
