"""python write_main_menu_save_report.py OUTPUTS_DIR"""
import hashlib,json,sys
from pathlib import Path
r=Path(sys.argv[1]);s=json.loads((r/'menu_save_gate_replay/summary.json').read_text());m=json.loads((r/'main_menu_runtime_fields/summary.json').read_text());p=json.loads((r/'dosbox_main_menu_runtime_v2/independent_verification.json').read_text());c=json.loads((r/'campaign_catalog/summary.json').read_text())
assert s['cases']==780 and s['failures']==0 and c['functions']==138 and c['runtime_tests']==20 and c['runtime_buffer_refinement_bytes_already_in_pass1']==4014
for item in s['files']+m['files']+p['files']:assert hashlib.sha256(Path(item['path']).read_bytes()).hexdigest()==item['sha256']
text=f'''# DOS2: prirodzené hlavné menu a SAVE metadata gate

Nová dávka zachytila **hlavné menu po úvodnom kreslení** cez pôvodnú vykonateľnú cestu. Pridáva dve funkcie,439B/157 inštrukcií,780 riadených replay prípadov a20. zachovaný runtime scenár. Súčasne analyzuje49B prefix DOS2 SAVE slotu proti piatim reálnym USER.SAV súborom a odlišuje tri deklarované dĺžky záznamu.

Katalóg:138 funkcií,5389 inštrukcií/13486B,990555 replay prípadov. Unia typovaných file-backed dát zostáva58018B; nový runtime refinement414B menu tabuliek už bol PARTIAL a nepočíta sa druhýkrát. PASS320: **57102B PARTIAL /149B CLASSIFIED ONLY /44B UNKNOWN /0B DEEP VERIFIED**.

## Prirodzený vstup cez tri intro čakania

Pôvodný packed DOS2 EXE bežal s23 izolovanými súbormi vrátane výslovne pridaného CD obrázka. Pred DEBUGBOX sa použil podporovaný AUTOTYPE s troma medzerníkmi: `autotype -w 15 -p 10 space space space`. CPU registre ani RAM hry sa debuggerom neprepisovali. Šesť skutočných make/break IN60h hodnôt39/B9, tri BIOS3920h položky a ich spotrebovanie sa zachovali v26 breakpoint stavoch.

|Wait entry|Zachovaný FAR return frame|Prirodzený význam cesty|
|---|---|---|
|0D29:0424, prvýkrát|0D29:07C5|po voliteľnom CD obrázku|
|0D29:0424, druhýkrát|0D29:07E6|po informačnej obrazovke083D:0008|
|0D29:0424, tretíkrát|0D29:080D|po title resource/page flip ceste|

Prvý pokus s pace4s neuspel: tretí medzerník prišiel počas kreslenia title resource, pred tretím wait entry; vstupný drain ho spotreboval. Tento pokus má runtime_tests0 a neimportuje sa ako overený runtime. Úspešná V2 používa pace10s a dosiahla menu. Časovanie je wall-clock vstupný experiment s debugger prestávkami, nie dôkaz normálnej neprerušovanej latencie hry.

## Dva zachytené menu body a FAR kontext

1. **0D29:2787**, skutočne154D:2787: po descriptor select a query400(6), pred volaním menu1946.
2. **0D29:19E4**, skutočne154D:19E4: po prvom vykreslení položiek a hľadaní počiatočného focusu, pred ďalšou interaktívnou vetvou.

V prvom bode už nemožno vydať aktuálne AX/DX za výsledný FAR pointer: query400 medzitým tieto registre zmenil. Preto verifier kontroluje zachované **SI=0E10h a segment z caller `[BP-2]`=28DDh**. Druhý bod má pôvodný FAR argument `[BP+6,+8]`=28DD:0E10, pracovný ES=28DDh a SI=0E10h. Vybraná je teda prvá položka s id1. Foreground DS=SS=2F95h.

## Presné menu dáta v pôvodnom NON-CODE

|Kanonický interval image|B|Štruktúra|
|---|---:|---|
|[219A0,21A1E)|126|20B9:0E10,6 záznamov ×18 + sentinel slot18|
|[21A1E,21AAE)|144|20B9:0E8E,7 záznamov ×18 + sentinel slot18|
|[21AAE,21B3E)|144|20B9:0F1E,7 záznamov ×18 + sentinel slot18|

Spolu20 položiek a3 sentinel sloty,414B. Celé dve runtime kópie sa zhodujú navzájom aj s kanonickými bajtmi po správnych relokáciách FAR string segmentov. Nezmenené dáta nie sú dôkaz nepoužitia: builder a renderer cez tieto záznamy prešli; aktuálne zápisy buildera boli idempotentné voči pripraveným hodnotám.

Lokálne potvrdené polia sú id BYTE+0, počiatočný focus marker BYTE+4, štýlový BYTE+5, x/y WORD+10/+12 a FAR string+14. Význam všetkých ostatných bajtov sa touto dávkou neuzatvára. Menu1946 pri počiatočnom výbere preskakuje položky s marker+4==0 a174C používa marker pri voľbe farby. **Nie je to univerzálny enabled/disabled flag.**

V startup tabuľke sú statické labely New game, Configure game..., Load game..., Instructions, Demo a Quit; prvý marker je1. Runtime FAR pointery sú overené; texty labelov sa dekódovali z pôvodného obrazu, samostatný koncový string dump sa nezachytával. Sentinel má nulový prvý BYTE, ktorý slučka testuje; zvyšných17 nulových bajtov slotu nevydávame automaticky za semanticky uzavretý padding.

## VGA/DAC zachytenie menu

Obidve stránkyA000/A400 boli zachytené vo všetkých štyroch rovinách, spolu128000B VRAM. Programmed a real display-start sú4000h; zobrazovacou logikou je prevzatá A400h. GC má read/write mode0, read-map0, AC je enabled. Skutočných768 DAC komponentov sa presne zhoduje s runtime buffrom aj GAME.PAL tail>>2.

![Rekonštrukcia menu z runtime VGA rovín a DAC, nie host screenshot](main_menu_runtime_fields/runtime_menu_page_a400.png)

Náhľad je rekonštrukcia zachytených indexov a DAC so škálovaním6→8bit `v*255//63`, nie capture host výstupnej plochy a nie nezávislý golden renderer. Druhá stránka je uložená samostatne. Plane dáta sa čítali až po endpoint zastavení cez dočasný read-map0..3; index6/read-map0 sa obnovili a GC/SEQ/MODE/AC hlásenia pred a po sa zhodujú. Po portovej intervencii nebolo RUN. Interné VGA read latche sa neoverovali ani neobnovovali.

Runtime má118 raw captures a presný whitelist breakpointov, RUN, dotazov, dumpov a7 povolených read-map portových zápisov. Stav menu je po úvodnom kreslení; nie je to dôkaz menu navigácie, New game výberu, map init alebo gameplay. UNKNOWN44B malo nulové cached-value udalosti, candidate hook4B ostal na koncoch rovnaký; čítania/same-value writes/host callback internals nie sú vylúčené.

## Funkcie, ASM/CFG a kontrakty

|Funkcia|Kanonický interval, end exclusive|Image|Code B /inštrukcie|
|---|---|---|---|
|main_menu_descriptor_select|0D29:252E..260A|[0F7BE,0F89A)|219/86|
|save_slot_metadata_read|0277:0D3E..0E1C|[034AE,0358C)|220/71|

Spany majú220 a222B; všetky medzery nie sú automaticky padding. Všetky importované bajty/hranice sa zhodujú s hashovaným DOS2 obrazom, historickým inventárom a nezávislým decoderom. Prvý menu draw prefix1946..19E4 sa zachováva ako ASM poznámky, ale nezapočítava sa ako tretia uzavretá funkcia. Celá interaktívna1946 má stále otvorené vetvy a CFG.

## Descriptor select: presný algoritmus

```text
for table in [20B9:0E8E,20B9:0F1E]:
    for record in table until BYTE id==0, stride18:
        record.focus_BYTE = (record.id_BYTE == 8)
result = (lowBYTE(arg_flag)!=0 and WORD[DS3CD4]!=3)
         ? FAR20B9:0E8E : FAR20B9:0E10
if WORD[DS3CD4]==3 and signed_WORD(arg_slot)>=0:
    metadata = save_slot_metadata_read(slot,"user.sav",far_stack_buffer41)
    if signed_WORD(metadata)>=0
       and BYTE(metadata)==WORD[DS626C]
       and sign_extend_BYTE(metadata>>8)==WORD[DS626A]:
        result = FAR20B9:0F1E
        CALL FAR0277:1176(slot,"user.sav")
return DX:AX = result
```

Saved-slot follow-up0277:1176 je v testoch nahradený stubom a jeho úplná sémantika nie je určená. Kontext otvára súbor pre čítanie; **neoznačujeme ho za delete operáciu**. Mode3CD4 sa popisuje hodnotovým testom, nie nepodloženým názvom herného stavu. Startup runtime vrátil0E10h a nepreukazuje sám vetvu user.sav probe/follow-up.

Builder pri spracovaní druhých dvoch tabuliek prepína DS na ich segment a obnovuje ho cez PUSH SS/POP DS, nie cez uložené pôvodné DS. Replay aj foreground runtime majú DS=SS; všeobecný kontrakt DS!=SS tým nie je uzavretý. Dočasný41B buffer je na stacku. Triedenie id a focus zapisuje aj pri neskoršom výbere inej tabuľky.

## DOS2 USER.SAV prefix a výsledná metadata WORD

Reader má signed WORD slot, near filename a voliteľný FAR description pointer. Otvorí cestu po helperi0277:0C20 s8000h. Ak signed handle<=0, vrátiFFFFh bez close; handle0 sa teda tiež odmieta. Pri kladnom handle:

```text
seek(handle, signed_WORD(slot) * 54758, origin0)  # result ignored
read_near(4B, local_record_size)                 # count ignored
if far_description != NULL:
    read_far(41B, description)                  # count ignored
else:
    seek(handle,41,origin1)                     # result ignored
read_near(2B, local_episode)
read_near(2B, local_level_result)
if record_size != 54758:
    result = FFFFh
else if query083D:29CA(1) is NULL and signed_WORD(episode)>1:
    result = FFFFh
else:
    result = level_WORD | (lowBYTE(episode) << 8)
close(handle)
return AX = result
```

Query vracia hodnotu v DX:AX testovanú OR; nie je preukázaná všeobecná BOOL-return ABI. Model rozlišuje iba NULL a konkrétnu nenulovú hodnotu. Žiadny read count alebo seek result sa v tomto tele nekontroluje. Kontrola record_size nastáva až **po** opise/episode/level read, takže zamietnutý formát môže stále zmeniť výstupný description buffer.

|Slot-relative interval|B|Lokálne doložený typ|
|---|---:|---|
|[0,4)|4|DWORD record_size, požadované0000D5E6h|
|[4,45)|41|BYTE description[41], bez dopísania NUL tejto funkciou|
|[45,47)|2|WORD episode; signed porovnanie pre NULL query|
|[47,49)|2|WORD level/result, následne OR s episode BYTE<<8|
|[49,54758)|54709|payload v tejto dávke neanalyzovaný|

Nejde o univerzálny validátor SAVE: level nemá lokálnu range kontrolu, jeho highBYTE sa pred OR nemaže a záporné episode WORD prejdú signed<=1 testom. Negatívny slot sa v caller builderi filtruje, ale samotný reader vykoná signed seek; model záporného file offsetu nie je prirodzená DOS seek-failure reprodukcia. Truncated fixture používa vopred inicializované lokály a nemožno z nej vyvodiť prirodzený neinicializovaný stack obsah.

## Päť skutočných SAVE kandidátov a krížové rozdiely

|Lokálny zdroj|B súboru|Deklarovaná dĺžka|Počet konzistentných stride záznamov|DOS2 reader s pozitívnym modeled handle|
|---|---:|---:|---:|---|
|dos/nite3d-A/USER.SAV|54758|54758|1|AX0101h pre prvý header|
|dos/N3D-Dos/USER.SAV|54758|54758|1|AX0100h pre prvý header|
|dos/n3dfull/USER.SAV|273780|54756|5|FFFFh, odlišná size WORD/DWORD hodnota|
|win/n3w-5/user.sav|55015|55015|1|FFFFh, odlišná record_size|
|win/100MEDIA/n3w/user.sav|55015|55015|1|FFFFh, odlišná record_size|

Všetky súbory boli prečítané z reálnych L:\\nite3d ciest, hashované a v modeled I/O použité ako skutočné vstupné bajty. Deväť kandidátskych record intervalov sa zmestí do súborov bez zvyšku a na každom začiatku sa zhoduje DWORD s deklarovanou stride. To je **CLASSIFIED ONLY hranicová evidencia**, nie plná schéma všetkých payloadov.

Názov priečinka neurčuje verziu pôvodného EXE. Rozdiel54756/54758/55015 preto neprekladáme na neoverenú presnú DOS/Win verziu. Pre Windows kandidátov sa nedokazuje správnosť DOS2 vnútorných offsetov ani kompatibilita Win110; iba rozdiel veľkosti a výsledok konkrétneho DOS2 reader modelu.

Description obsah sa nepublikuje: katalógy uchovávajú hranice a hashy zdrojov/záznamov, nie celé SAVE súbory alebo používateľské texty.

## 780 riadených replay scenárov

600 selector prípadov = 2 relokácie ×5 flag WORD hodnôt(0,1,0100,0101,FFFF) ×3mode hodnoty(0,3,FFFF) ×4slot hodnoty(-1,0,1,32767) ×5metadata výsledkov. Dva upravované focus tables sú pred volaním seedovanéA5h, takže test nemôže prejsť iba porovnaním pôvodne idempotentných hodnôt. Kontroluje sa celých414B, návratový DX:AX, dependency call poradie a zachované registre. Metadata/follow-up sú v tomto prvom modeli stubované.

180 metadata prípadov = 2 relokácie ×15 input patterns ×2 NULL/non-NULL query stavy ×3 open returny(FFFF/0/7). Patterny zahŕňajú päť reálnych súborov, syntetické high-bit/level/episode hodnoty, nesprávnu dĺžku, NULL description, negatívny slot, truncation a explicitný model, ktorý kopíruje bajty, ale vracia0. Posledný model overuje ignorovanie read-result control flow, nie správanie skutočného zero-byte DOS read.

Native reader body zostáva pôvodný, ale filename/path, open/seek/read/close a query sú modelované. Počet/near adresy read operandov, FAR description adresa/dĺžka a jej konečný obsah sú overené. Prirodzené SAVE vytvorenie, obnovenie alebo full LOAD sa tým nedokazuje a zdrojové súbory sa nemenia.

## Artefakty a reprodukcia

- `runtime_watch_main_menu.py DOSBOX_EXE GAME_DIR IMAGE RELOCS OUT WORK startup CD_ASSET`, frozen `dosbox_watch_support_menu_v2.py`: úspešná vetva je dosbox_main_menu_runtime_v2.
- `verify_main_menu_capture.py IMAGE RELOCS MAP OUT WORK`:118 captures,26 bodov, tri wait framy, šesťIRQ scanov, BIOS dequeue,414B records, všetky fonty a obidve VGA stránky/DAC.
- `audit_main_menu_fields.py IMAGE RUNTIME WORK OUT`:20 records,20 focus fields,3 intervaly414B a rekonštrukcie stránok. Nepovyšuje už PARTIAL dáta druhýkrát.
- `audit_replay_menu_save_gate.py IMAGE INVENTORY DECODER EMULATOR OUT`:2 ASM/CFG funkcie,600+180 prípadov,49B SAVE prefix schéma s UNKNOWN payloadom a9 record kandidátov CSV/JSON.
- Centrálny katalóg obsahuje138 funkcií a runtime refinements4014B/12 intervalov, z toho3600B fontových bufferov a414B menu tabuliek. Je to evidencia nad už klasifikovanými bajtmi, nie nový semantický percentuálny denominator.

Predchádzajúca overená GitHub snímka má19 runtime scenárov. Táto dávka zostáva lokálna, kým nie je uložené nové potvrdenie publikácie.

## Aktualizácia 13 oblastí

TABLE_PLACEHOLDER

## Runtime testy na vykonanie

1. Ovládať menu cez skutočné IRQ klávesy: New game, epizóda a obtiažnosť; zachytiť map init a prvý gameplay tick.
2. Reprodukovať save metadata probe s vhodným izolovaným reálnym USER.SAV a zodpovedajúcim game mode/current epizóda-level, bez zápisu do originálov.
3. Uzavrieť follow-up0277:1176 a celé interaktívne1946 CFG, navigation, bounds a event návraty. Aktuálne menu capture končí pred jeho interaktívnou slučkou.
4. Doplniť DOS/Win EXE väzby k54756/54758/55015 a skontrolovať celý payload/round-trip SAVE LOAD. Hlavičková stride zhoda nestačí.
5. Rozšíriť UNKNOWN44 read/write dôkaz za menu, do map init a gameplay; stabilné cached-value dáta nie sú DEEP VERIFIED.
'''
prev=(r/'WORX_PRIVATE_STACK_RUNTIME_REPORT.md').read_text(encoding='utf-8');table=prev[prev.index('## Aktualizácia 13 oblastí'):prev.index('## Runtime testy na vykonanie')]
table=table.replace('CD DSTOPEN.IMG:128B header,19781B RLE,769B tail; 64000 pixelov','5reálnych SAVE súborov/9stride intervalov; DOS2 prefix49B').replace('iné PCX/IMG domény; stride/planes ignorované','celý SAVE payload a EXE väzby k variantom').replace('textové resource a menu dáta','full SAVE/LOAD schema a map init')
table=table.replace('nových30B direct stack/control polí mimo NON-CODE;512B kandidat len CLASSIFIED','20menu focus BYTE polí a49B SAVE prefix; count/seek výsledky ignorované').replace('492B candidate backing bez potvrdenej kapacity','ostatné record polia a payload54709B')
table=table.replace('nových128 font1FAR; všetky384FAR pointery skupín0/1/2 byte-exact','3runtime menu tabuľky414B, FAR28DD:0E10 a firstfocusid1').replace('pointer index0 a signed-char indexy','iné descriptor varianty a cursor domény')
table=table.replace('2nové funkcie203B/87inštrukcií;1152 stack/timer replay','2nové funkcie439B/157inštrukcií;780menu/save replay').replace('old interruptedPC, audio callees a Win ekvivalent','celá1946, follow-up1176 a Win ekvivalent').replace('celý timer chain a nested IRQ','menu CFG a SAVE follow-up')
table=table.replace('nové frame návraty0BDE:00C6; paused WORX SS kontext','3wait návraty,6make/break scanov,3BIOS dequeue; menu ready').replace('presný old alternateIRQ PC a DEMO poradie','menu navigácia, DEMO poradie a gameplay vstupy')
table=table.replace('programmed4000→real4000 v neskoršom bode;4roviny a AC overené','menu initial draw;128000B oboch stránok aDAC zachované').replace('host-surface/úplný scanout, text/menu','host-surface/scanout, nezávislý menu pixel golden')
table=table.replace('BSF native file-check vrátený','DOS2 metadata reader proti5reálnym SAVEs;54758size gate').replace('SAVE/LOAD a chybové I/O','full SAVE/LOAD, seek/read error model a rollback').replace('diskové scenáre','izolovaný metadata runtime a follow-up1176')
text=text.replace('## Aktualizácia 13 oblastí\n\nTABLE_PLACEHOLDER\n\n',table)
receipt=r/'CAMPAIGN_MAIN_MENU_PUBLICATION_RECEIPT_20261112.json'
if receipt.exists():
 pub=json.loads(receipt.read_text());text=text.replace('Predchádzajúca overená GitHub snímka má19 runtime scenárov. Táto dávka zostáva lokálna, kým nie je uložené nové potvrdenie publikácie.','Táto dávka je publikovaná a blob po blobe overená v analytickom commite '+pub['commit']+'. Strojové potvrdenie: CAMPAIGN_MAIN_MENU_PUBLICATION_RECEIPT_20261112.json. Metadata follow-up môže mať novší branch head.')
(r/'MAIN_MENU_SAVE_GATE_RUNTIME_REPORT.md').write_text(text,encoding='utf-8');print(json.dumps(dict(report='MAIN_MENU_SAVE_GATE_RUNTIME_REPORT.md',functions=138,runtime_tests=20,replay_cases_added=780)))
