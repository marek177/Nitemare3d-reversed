"""python write_xms_request_report.py OUTPUTS_DIR"""
import csv,hashlib,json,sys
from pathlib import Path
r=Path(sys.argv[1]);read=lambda p:json.loads((r/p).read_text());x=read('xms_request_replay/summary.json');e=read('episode_selector_replay/summary.json');v=read('dosbox_xms_request_runtime/independent_verification.json');c=read('campaign_catalog/summary.json');p=read('pass1_xms_move_request/independent_partition_check.json')
for item in x['files']+e['files']+v['files']:assert hashlib.sha256(Path(item['path']).read_bytes()).hexdigest()==item['sha256']
assert x['cases']==2400 and e['cases']==256 and v['verified'] and c['functions']==141 and c['runtime_tests']==21
table='''## Aktualizácia 13 oblastí

Predošlé orientačné percentá sú historické odhady, nie merané východiská. Pre každú oblasť je nová sémantická úplnosť N/A: počet uzavretých jednotiek / úplný inventár jednotiek oblasti; úplné menovatele a kritériá closure zatiaľ chýbajú. Merateľný PASS1 podiel nižšie je stav bajtovej klasifikácie, nie sémantická úplnosť. Všetky nové funkcie a dáta sú PARTIAL, DEEP VERIFIED nepribudlo. Nezmenené oblasti sú výslovne uvedené.

|Oblasť|Predošlý odhad|Nové % / metodika|Nový potvrdený výsledok|Zostávajúce neznáme|Blokujúci problém|Najbližší krok|
|---|---:|---|---|---|---|---|
|Mapy a formáty|99 %|N/A, closure/inventár|prirodzený game start epizóda1, index level0|celá map inicializácia|koncový bod map loader ešte nezachytený|pokračovať po prvom XMS prenose|
|Dátové typy a konštanty|95 %|N/A, closure/inventár|5 XMS polí /16B z UNKNOWN do PARTIAL|28 UNKNOWN B a149 CLASSIFIED ONLY B|žiadny prístup k nim v tomto scenári|sledovať zostávajúcich28B počas map init|
|Tabuľky a ukazovatele|93 %|N/A, closure/inventár|relokovaný DS:2560→1BE7:0200; FAR XMS arg|celý resource-cache lifecycle|alokácia/free a reverse direction neuzavreté|XMS handle init/free a read callery|
|Funkcie / ASM / CFG|90 %|N/A, closure/inventár|3 rozsahy /368B /152 inštrukcií;2656 replay|caller domény, diagnostika FBA:000C|externé závislosti v replay stubované|rozšíriť volací graf0768|
|RNG|97 %|N/A, closure/inventár|žiadny nový dôkaz RNG|natural srand/rand a DEMO poradie|prvý gameplay frame nezachytený|trace RNG callery po map init|
|Scheduler|96 %|N/A, closure/inventár|žiadny nový dôkaz schedulera|herná slučka a timer chain|runtime končí pred slučkou|dosiahnuť0D29:0A31|
|DEMO a vstupy|96 %|N/A, closure/inventár|3SPACE+3ENTER; voľba main1/episode15/difficulty19|iné voľby a DEMO|iba jeden prirodzený výber|ďalšie selector domény a DEMO trace|
|Renderer / VGA|94 %|N/A, closure/inventár|žiadny nový renderer parity dôkaz|scanout a full gameplay frame|žiadny nezávislý frame golden|zachytiť prvý herný frame|
|GUARD / bossovia|93 %|N/A, closure/inventár|žiadny nový AI dôkaz|bossové vetvy a actor runtime|map init nedokončený|actor entry/dispatch po map init|
|Zbrane / projektily|92 %|N/A, closure/inventár|žiadny nový damage dôkaz|kolízie a damage callery|chýba gameplay scenár|izolovaný damage trace|
|Sprity / HUD / paleta|92 %|N/A, closure/inventár|žiadny nový closure dôkaz|textové metriky a HUD frame|gameplay endpoint nezachytený|HUD draw pri prvom frame|
|SAVE / LOAD|92 %|N/A, closure/inventár|žiadny nový SAVE/LOAD dôkaz|54709B payload a rollback|metadata nie sú celý formát|follow-up0277:1176 a runtime SAVE|
|Windows Win16|92 %|N/A, closure/inventár|žiadny nový Win16 dôkaz|Win XMS ekvivalent / DS/API kontrakt|žiadny Win16 runtime|nájsť fixup-backed ekvivalent cache|

'''
text=f'''# DOS2: uzavretie UNKNOWN XMS request a prirodzený výber novej hry

Interval **[1C070,1C080)** (hex image offsety, koniec exkluzívny) je päťpolový16B XMS move descriptor. Nové dôkazy: pôvodný zapisujúci kód, relokácia segmentového aliasu, pôvodný AH=0Bh consumer,2400 kontrolovaných replay prípadov a skutočný prvý úspešný návrat XMS pri inicializácii epizódy1. Klasifikácia **UNKNOWN→PARTIAL**, nie DEEP VERIFIED.

PASS320 presne57295B: **57118 PARTIAL /149 CLASSIFIED ONLY /28 UNKNOWN /0 DEEP VERIFIED**. Mapa892 intervalov má SHA-256 `{p['map_sha256']}`. Nezávislá kontrola overila všetky892 rozsahových hashov, presné členstvo, nula dier/prekryvov; tým sa nedokazuje celá sémantika.

Podiely počítané ako status_bytes/57295: PARTIAL {57118/57295*100:.6f} %, CLASSIFIED ONLY {149/57295*100:.6f} %, UNKNOWN {28/57295*100:.6f} %, DEEP VERIFIED0 %. Predtým UNKNOWN44B; pokles16B je merateľný, nevytvára nové percento úplnosti hry.

## Päť polí a referencie

|Image interval|B|Typ a správanie|Pôvodné inštrukcie0768|
|---|---:|---|---|
|[1C070,1C074)|4|DWORD dĺžka zaokrúhlená na KiB|02E4,02E8|
|[1C074,1C076)|2|WORD source handle, nula znamená conventional memory|02ED|
|[1C076,1C07A)|4|FAR16 source pointer, offset potom segment|02F8|
|[1C07A,1C07C)|2|WORD destination XMS handle z DS:3506|0300|
|[1C07C,1C080)|4|DWORD destination offset|031E,0322|

Konštruktor načíta ES zo segmentového WORD DS:2560. Pôvodný WORD1BE7h je v MZ relokačnej tabuľke; po load0824h má hodnotu240Bh. Alias240B:0200 sa preto prekladá presne na pôvodný image1C070. Pri návrate už ES=DS=2F95, preto sa descriptor adresa nezisťuje z aktuálneho ES, ale z relokovaného WORD a zachovaného FAR argumentu na stacku.

Identifikácia zodpovedá vendor-authored [XMS3.0 specification, funkcia0Bh](https://files.mpoli.fi/unpacked/software/programm/general/gcgpe10.zip/xms30.txt): DS:SI označuje move request, nulový source handle používa conventional FAR pointer a AX oznamuje úspech. Hranice a skutočná inicializácia sú preukázané vlastnými EXE dôkazmi, nie iba podobnosťou štruktúry. Ide o iný descriptor než starší WORX CS15BF:21CC; tieto intervaly sa nezlučujú.

## Funkcie, kontrakty a rekonštruovaný algoritmus

**0768:0294–0350**,188B/73 inštrukcií, FAR caller-cleanup: source FAR argument `[BP+6]`, WORD count `[BP+0A]`, prirodzený caller má DS=SS. Výsledok DX:AX je začiatok rezervovaného priestoru alebo FFFFFFFFh pri nedostatku kapacity. Funkcia zachová BP/SI/DS; ES sa pri prijatej požiadavke zmení na callerDS cez wrapper. Padding sa v oboch presne dekódovaných rozsahoch nevyskytol.

```c
chunks = ((uint32_t)count + 1023) / 1024;
if ((uint16_t)(used_kib + chunks) > limit_kib) return 0xffffffff;
request.length = chunks * 1024;
request.source_handle = 0;
request.source_far = source;
request.destination_handle = xms_handle;
start = (uint32_t)((int32_t)(int16_t)used_kib * 1024);
request.destination_offset = start;
(ax, dx) = xms_move_wrapper(&request);
if ((int16_t)dx < 0) diagnostic_FBA_000C(format, ax, dx);
used_kib = (uint16_t)(used_kib + chunks);
return start;
```

Kapacitná ADD je16-bitová a môže wrapnúť. Pre used>=8000h je sign extension do DWORD offsetu potvrdená pôvodným CWD; neočakávané domény sa neopravujú na želané unsigned správanie. Pri count0 sa môže odoslať nulová dĺžka. Kopírovaná veľkosť je zaokrúhlená, nie pôvodný count; platnosť source allocation v každom callerovi zostáva otvorená. Pseudokód ukazuje pokračovanie za diagnostickým call, no jej návratnosť a účinky nie sú uzavreté; replay tam zastaví.

**0768:07FE–0826**,40B/21 inštrukcií: FAR request `[BP+6,+8]`, ES=callerDS, DS:SI=request, AH0Bh, FAR CALL ES:[350E]. Pri AX!=0 vracia DX0, pri AX0 nastaví DX=BL<<8; obnoví DS/SI/BP, ES ponechá callerDS. Dokumentované XMS chyby majú horný bit nastavený, čo vysvetľuje signed DX test. Syntetické BL<80h prípady ukazujú pokračovanie bez diagnostiky; nie sú potvrdené ako prirodzené chyby manažéra. Rutina je aplikačný adaptér externého XMS ABI; konkrétny autor/kompilátorový pôvod nie je dokázaný.

Reprodukcia dekódu a CFG: `xms_request_replay/xms_append_kib.csv`, `xms_move_wrapper.csv` a oba `_cfg.csv`; byte zhoda s pôvodným inventárom aj nezávislým iced-x86 dekódom.2400 prípadov:2loady ×6countov ×5used ×4limit ×5managerresults ×2sourceFAR. Externý XMS manager je stub, diagnostická vetva končí na vstupe handlera. Nula zlyhaní; nie je to2400 DOSBox behov.

## Prirodzený runtime a úplný NON-CODE endpoint

Pôvodný packed EXE bežal v DOSBox-X s23 izolovanými vstupmi vrátane explicitne pridaného CD DSTOPEN.IMG. AUTOTYPE poslal3SPACE a3ENTER. Zachované návraty main menu AX1, episode menu AX15→episode1, difficulty menu AX19→difficulty1. Game start0D29:095A mal level index0/episode1 v pôvodnom FAR call frame.

Koncový breakpoint je **0768:032F**, po prvom XMS wrapper návrate a pred caller cleanup/capacity increment. Registre AX1/DX0; descriptor raw `002000000000ca659b8d01000000000000`:8192B zo8D9B:65CA do handle1 offset0. DS:3506/3508/350A=(1,2048,0). Úspech manažéra je natívne potvrdený; cieľové XMS bajty sme nezávisle nečítali.

Šesť cached-change udalostí zasiahlo šesť adries výlučne v tomto descriptore. Event register sampling počas RUN nie je stabilný writer breakpoint: **PC udalosti sa nevydáva za presnú zapisujúcu inštrukciu**. Writer dôkaz pochádza zo statických inštrukcií a vykonania pôvodných tiel v replay. Same-value writes a reads BPLM nepozoruje.

Zachoval sa finálny snapshot **všetkých57295 NON-CODE bajtov**:17B gap a57278B tail;10321 bajtov sa líši od počiatočného relokovaného obrazu. Rozdiel endpointov neudáva počet zápisov ani sémantické closure. Zachovaný je aj57392B DGROUP; BSS sa nesčítava do file-backed PASS1. Verifier overuje zdroje/kópie, celý počiatočný relokovaný runtime image, priebeh watched cache, FAR arg, descriptor, control words, final alias a hash manifest všetkých raw captures.

Predošlý dlhý pokus `dosbox_newgame_map_runtime` zachoval178 udalostí, ale nedosiahol game-loop endpoint a má runtime_tests0. Táto dávka neprerába jeho výsledok na úspech. Nový kratší test dosiahol vlastný jasne vymedzený endpoint a zvyšuje zachované scenáre20→21; full map load ešte nie je preukázaný. Pôvodné súbory ostali hashovo nezmenené.

## Episode selector, nové hranice sémantiky

**0D29:260A–2696**,140B/58 inštrukcií. Pre map.1..3 používa access(4) a registered query; dostupnej epizóde1 alebo registrovanej dostupnej epizóde nastaví BYTE descriptor+5 na1. Nedostupnej položke pôvodný style ponechá; opakovaný call po zmene dostupnosti preto nemá automatický reset6. Táto možná stale-state doména je modelová, nie potvrdený prirodzený file-change scenár. Menu id6 vracia0, inak id−14.256 replay prípadov pokrýva2loady,8availabilitymasks,2registered values,2initialstyles a4menu results. Formatter/access/query/menu sú stubované; ľubovoľné stub id nedokazuje výber zakázanej položky v reálnom menu.

## Aktuálne pokrytie a zostávajúce intervaly

Katalóg **{c['functions']} rozsahov /{c['independent_instruction_count']} inštrukcií /{c['independent_instruction_bytes']}B kódu**,{c['data_bytes_with_local_evidence']}B unie typovaných file dát,{c['controlled_instruction_replay_cases']} riadených replay prípadov a21 original-EXE scenárov. Nové3 rozsahy majú368B a152 inštrukcií. Typované NON-CODE dáta57116B; rozdiel2B do PARTIAL je starší otvorený relocation WORD DS2358. BSS4054B a staršie runtime refinements4014B sa nemenia.

UNKNOWN zostáva [1BDA2,1BDB0)14B, [1D0EC,1D0F0)4B, [20B88,20B90)8B a [2770E,27710)2B. CLASSIFIED ONLY149B a neúplné PARTIAL domény tiež vyžadujú uzatvorenie;28 UNKNOWN nie je jediné zostávajúce analytické zadanie. Windows/DOS cross-version pre tieto tri nové funkcie zatiaľ nebol vykonaný.

'''+table+'''## Runtime testy na vykonanie

1. Odstrániť z ďalšieho watch set už typovaný16B descriptor a sledovať zvyšných28B cez dokončenie map loadera0D29:09C4 a game-loop entry0D29:0A31; descriptor zachovať len vo fixných snapshots.
2. Zachytiť XMS handle allocation/free a ďalšie transfery, source buffer capacity a opačný smer; overiť copied destination bytes cez dokumentovaný manager readback v samostatnom teste.
3. Oddelený failure scenár: nedostatok XMS, validný BL>=80h a účinok FBA:000C; nezamieňať syntetický BL<80h za prirodzený driver výsledok.
4. Iné epizódy/obtiažnosti a file availability pred opakovaným selector call; DEMO/RNG a prvý gameplay frame až po map init.
5. SAVE/LOAD payload a Win16 ekvivalent sledovať samostatne; PE32 nevykonávať.

## Reprodukcia

`audit_replay_xms_request.py IMAGE INVENTORY DECODER EMULATOR OUT` a `audit_replay_episode_selector.py` pripínajú presné vstupy SHA. `runtime_watch_xms_request.py DOSBOXX GAMEFOLDER IMAGE RELOCS OUT WORK startup CDIMAGE` vytvorí natívny záznam; `verify_xms_request_capture.py IMAGE RELOCS HISTORICAL_MAP OUT WORK` overí pôvodnú44B watch baseline. Historická mapa musí zostať nezmenená; nová28B mapa jej dôkaz neprepisuje.

`promote_pass1_fields.py IMAGE PRIOR_MAP xms_request_replay/data_fields.csv pass1_xms_move_request` a `verify_pass1_partition.py` reprodukujú presný16B presun. Potom `independent_decode_and_catalog.py ABS_DECODER OUTPUTS` a `render_campaign_status.py OUTPUTS pass1_xms_move_request XMS_REQUEST_RUNTIME_REPORT.md` aktualizujú katalóg/report. Raw runtime binárne výpisy a pôvodné assets sa nepublikujú; ich SHA a cesty sú vo verifier manifeste. Táto dávka pri vygenerovaní reportu zostáva lokálna, kým publikáciu nepotvrdí samostatná receipt.
'''
(r/'XMS_REQUEST_RUNTIME_REPORT.md').write_text(text,encoding='utf-8');print('XMS_REQUEST_RUNTIME_REPORT.md written')
