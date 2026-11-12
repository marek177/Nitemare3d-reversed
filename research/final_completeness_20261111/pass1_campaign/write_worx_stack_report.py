"""python write_worx_stack_report.py OUTPUTS_DIR"""
import hashlib,json,sys
from pathlib import Path
r=Path(sys.argv[1]);s=json.loads((r/'worx_private_stack_replay/summary.json').read_text());c=json.loads((r/'campaign_catalog/summary.json').read_text());a=json.loads((r/'dosbox_keyboard_stack_runtime/independent_verification.json').read_text());w=json.loads((r/'dosbox_worx_stack_window_runtime/independent_verification.json').read_text())
assert s['cases']==1152 and s['failures']==0 and c['functions']==136 and c['runtime_tests']==19 and c['data_bytes_with_local_evidence']==58018 and w['worx_stack_window_verified']
for item in s['files']+a['files']+w['files']:assert hashlib.sha256(Path(item['path']).read_bytes()).hexdigest()==item['sha256']
text=f'''# DOS2: súkromný zásobník zvukového časovača a IRQ framy

Nová dávka pridáva **dve funkcie,203B/87 inštrukcií**, **1152 riadených replay scenárov**, **30B presne typovaných dát mimo PASS320 NON-CODE** a **dva zachované DOSBox-X scenáre**. Identifikuje vlastný SS/SP zvukového segmentu15BFh a presný návratový bod nových klávesnicových interrupt framov. Starší alternatívny key IRQ však nebol zopakovaný: jeho presný interrupted PC zostáva otvorený.

Katalóg:136 funkcií,5232 inštrukcií/13047B,58018 typovaných file-backed B,989775 riadených replay prípadov a19 original-EXE runtime scenárov. Tento počet zahŕňa explicitné debugger zásahy uvedené pri jednotlivých behoch. PASS320 ostáva **57102B PARTIAL /149B CLASSIFIED ONLY /44B UNKNOWN /0B DEEP VERIFIED**. Nové dáta a kód neležia v pôvodnom57295B NON-CODE baseline.

## Ohraničené funkcie a proveniencia

|Pracovný názov|Kanonický interval|Image interval|Code B /inštrukcie|
|---|---|---|---|
|worx_private_stack_tick|15BF:40E7..4150|[19CD7,19D40)|105/42|
|worx_timer_irq_dispatch|15BF:4150..41B3|[19D40,19DA3)|98/45|

Druhý span má99B a iba98 dosiahnuteľných inštrukčných B; neimportovaný alignment byte sa nevydáva za hlboko dokázaný padding. Všetky hranice/inštrukčné bajty sa zhodujú so starým inventárom a nezávislým16-bit decode. ASM a CFG sú uložené samostatne.

Segment15BFh bol v skorších dávkach identifikovaný ako zvuková knižničná oblasť WORX. Táto dávka identifikuje konkrétny stack/timer mechanizmus a nerozširuje to na source-match presnej knižničnej verzie. Herný main scheduler sa tým neuzatvára.

Statický installer context15BF:2EE0..2F03 získava cez INT21h pôvodný vector08h, ukladá ho do CS000A/000C, potom cez AH25h/AL08h inštaluje DS:DX=CS:4150. Je to vector08h, teda klasický timer IRQ0; klávesnicový vector09h/IRQ1 je odlišný handler.

## Inicializácia vlastného SS/SP

Initializer15BF:2EBC..2ECC vypočíta `40E5h-4=40E1h`, uloží ho do CS3EE1 a vlastné CS do CS3EE3. Preto je aktívny stack top **40E1h**, nie samotná referencia40E5h. Táto4B odchýlka mení interpretáciu starších SP hodnôt.

|CS offset|Typ|Potvrdený lokálny význam|
|---|---|---|
|3EDD|WORD|uložené caller SP|
|3EDF|WORD|uložené caller SS|
|3EE1|WORD|konfigurované private SP, initializer40E1h|
|3EE3|WORD|private SS, initializerCS|
|40E5|WORD|počítadlo preskočených private callbackov v nested vetve|

Pôvodný file WORD CS3ED4 jeFFFFh; v tejto dávke sa taký sentinel nepredpokladá iba podľa názvu alebo testu. CSV initial_control_constants uchováva jeho skutočné bajty spolu s ostatnými počiatočnými hodnotami. Prevádzkovú hodnotu všetkých polí v ľubovoľnom okamihu tým nezaručujeme.

## Algoritmus private callbacku

```text
CLI
CS.savedSP = SP
CS.savedSS = SS
SP = CS.privateSP
SS = CS.privateSS
STI
save AX,BX,CX,DX,BP,DI,SI,DS,ES  # WORD registers
DS = CS
CS.countdown32 = DWORD(CS.countdown32 - CS.unit16)
if signed_HIGH_WORD(CS.countdown32) < 0:
    CS.pending_BYTE = 1
if CS.flags_BYTE & 20h:
    CALL NEAR 555Dh
if CS.flag3ED6_BYTE != 0:
    CALL NEAR 5DF2h
restore saved WORD registers
CLI
SP = CS.savedSP
SS = CS.savedSS
RET NEAR
```

Countdown je CS2C4B/2C4D, decrement WORD CS2C49 a pending BYTE CS2C53. SUB/SBB má32-bit wrap. Nezáporný výsledok pending flag **nenuluje**; podmienený zápis1 je odlišný od všeobecného priradenia BOOL.

SP sa mení pred SS v úseku s CLI. To je mechanizmus pre maskovateľné IRQ; odolnosť voči NMI, faultom alebo všetkým nested scenárom sa tým nedokazuje. Callback po návrate ponechá IF vymazané a NEAR caller sa o konečný interrupt návrat stará sám. Táto rutina ukladá16-bit WORD registre, nie PUSHAD; horné16 bity32-bit GP registrov a skutočné správanie hlbších callees musia zostať samostatnou otázkou.

## Algoritmus timer dispatchera a reentrancia

```text
CLD; CLI
if CS.flags_BYTE & 16h:
    save WORD registers
    CALL NEAR 4476h
    restore WORD registers
phase = WORD(phase + 1)  # CS2DB4
if phase >= threshold_WORD_at_CS2DB6:  # unsigned compare
    phase = 0
    PUSHF
    CALL FAR saved_vector08_at_CS000A
    IRET
depth = WORD(CS3ED4 + 1)
OUT BYTE(20h),20h  # PIC EOI in this branch
if depth != 0:
    CS40E5 = WORD(CS40E5 + 1)
else:
    CALL NEAR private_stack_tick
CS3ED4 = WORD(CS3ED4 - 1)
IRET
```

Pri počiatočnom depthFFFFh vznikne po INC nula a private callback sa vykoná. Pri ďalšom nested vstupe depth prejde0→1, callback sa preskočí a rastie counter40E5. Každá lokálna vetva potom depth zníži späť. Legacy-chain vetva má vlastný IRET a jej uložený handler je v replay IRET stub; jeho skutočná PIC obsluha sa netestuje týmto modelom.

Callees4476/555D/5DF2 sú v riadených testoch nahradené NEAR RET stubmi. Označenia mixer/music/digital v skripte sú pomocné názvy nad adresami a už známymi flagmi; plná audio sémantika týchto tiel sa tým neuzatvára.

## Presné dátové intervaly a limit kandidátskeho stack bloku

|Image interval, end exclusive|B|Nová typová evidencia|
|---|---:|---|
|[19ACD,19AD5)|8|4WORD uložené a private SS/SP|
|[19CBD,19CD1)|20|9WORD uložených registrov a1slot zdieľaný PUSH CS/POP DS a NEAR return adresou|
|[19CD5,19CD7)|2|WORD missed/skipped callback counter|

Tieto30B sú nové PARTIAL typované dáta mimo pôvodného NON-CODE baseline. Oproti tomu **[19AD5,19CD5) má512B pôvodných núl a je iba kandidátska backing oblasť**. Jej dolná kapacitná hranica nie je dokázaná samotnou medzerou a horným SP. Z512B je20B podložených priamymi stack operandmi; ďalších492B sa nepridáva do typed-data únie iba kvôli nulovej hodnote. Horné4B medzi privateSP40E1 a40E5 tiež nie sú automaticky potvrdený padding.

`data_fields.csv/json` obsahujú len tri presné intervaly30B s file-range SHA. `stack_capacity_candidate.csv` zachováva512B kandidáta ako CLASSIFIED ONLY s explicitnou neistotou. Katalóg nepreklasifikuje túto celú medzeru na DEEP VERIFIED stack.

## Riadené replay:1152 prípadov

576 samostatných callbackov = 2 relokácie ×2 caller stack segmenty ×6 DWORD counterov ×3 decrement WORD ×2 pending hodnoty ×2 flag20h stavy ×2 flag3ED6 stavy. Overujú sa counter/pending, volania, SS/SP a WORD registre, uložený caller kontext a IF=0 pri návrate. Mock callee checkpoint navyše vidí SS=CS, DS=CS, SP40CDh a IF=1. Zdieľaný WORD CS40CD po návrate obsahuje CS pri žiadnom helper volaní,4130h po prvom helperi alebo413Bh po poslednom helperi; jeho rola nie je univerzálne iba návratová adresa.

576 timer IRQ prípadov používa **pôvodný private callback**, nie jeho stub: 2 relokácie ×3 thresholdy(0/1/3) ×3 fázy(0/2/FFFF) ×2 depth(0/FFFF) ×4 flag kombinácie ×2 flag3ED6 ×2 missed count hodnoty(7/FFFF). Kontrolujú sa chain/EOI vetvy,16-bit wrap fázy/depth/missed count, countdown, obnovený interrupt frame a low16 FLAGS vrátane testovaného IF/DF. Arbitrážne nested hardware IRQ a fyzické tempo časovača v tejto matici nie sú modelované.

## Nové runtime framy: čo presne dokazujú

Prvý nový scenár nadväzuje na17. zachovaný vstupný beh, ale pridáva6B hardvérové framy pri IRQ entry a pred IRET aj128B stack kontexty. Má56 raw captures. Oba IRQ v tomto novom behu vstúpili s **SS:SP=2F95:E7B0** a frame obsahoval **returnCS:IP=1402:00C6, FLAGS7202h**. Entry/exit6B sa zhodujú presne.

Po odpočítaní load0824h je interrupted PC **0BDE:00C6**. Pôvodný ASM tam porovnáva DX s uloženou hornou WORD deadline vo foreground busy-wait helperi0BDE:00AE. Nie je to dôkaz IRQ priamo vo WORX callees. Make39h/breakB9h, game0200h, BIOS3920h a následné dequeue zostávajú overené; fonty0/1/2 sa zhodujú.

Predošlý17. beh mal pri break IRQ SS1DE3h, SP40D9h, ale hardware frame sa v ňom nezachoval. Nové meranie túto vetvu nezopakovalo. Dodatočné debugger zastavenia menia načasovanie a nemožno si domyslieť pôvodný returnPC z nového bežného stacku.

## Výslovne pozastavené WORX okno

Druhý nový scenár pridáva breakpoint **15BF:40FD**, skutočne **1DE3:40FD**, po vykonaní prepnutia SS/SP a STI, pred prvým PUSH AX. Breakpoint sa inštaluje až po wait entry; skript potom zámerne čaká vo wall-clock okne, aby bolo možné preskúmať interakciu s podporovaným AUTOTYPE. Pozastavenie nie je neprerušovaný beh ani časová parita.

Zachytený stav:

|Pole|Runtime hodnota|
|---|---|
|aktívne CS:IP|1DE3:40FD|
|aktívne SS:SP|1DE3:40E1|
|DS|2F95|
|uložené caller SS:SP zCS3EDD..3EDF|2F95:E7AA|
|private SS:SP zCS3EE1..3EE3|1DE3:40E1|

Tým je identifikovaná private stack oblasť zodpovedajúca segmentu staršieho alternatívneho SS. Starší SP40D9 leží v jej hornom používanom úseku. **Presný interrupted PC staršieho break IRQ však naďalej nie je potvrdený.** Aj v tomto riadenom okne oba nové key IRQ napokon prerušili0BDE:00C6 s bežným SS; pokus sa nevydáva za úspešné zachytenie nested key IRQ na private stacku.

Scenár má61 raw captures vrátane private control8B a512B susednej storage oblasti, desať input-stop bodov a zachovaný command transcript. Jediná dodatočná zmena debugger kontroly je zmazanie tohto code breakpointu; zostávajúcich44 BPLM breakpointov sa zachovalo. Neboli vykonané portové, RAM alebo CPU-register zápisy debuggerom.

## Rozsah uzavretia a reprodukcia

Nové dôkazy oddeľujú foreground clock-wait, hardvérový keyboard frame a knižničný timer private stack. Podporujú pôvod WORX SS oblasti; neuzatvárajú presný starší interrupted PC, celú512B kapacitu, high32-bit register kontrakt, všetky nested IRQ, fyzické audio alebo herný scheduler.

UNKNOWN44B v oboch scenároch nemalo cached-value udalosti a FAR candidate hook4B ostal na koncoch rovnaký. Čítania/same-value writes/host callback internals naďalej nie sú vylúčené, preto žiadne NON-CODE preklasifikovanie.

- `audit_replay_worx_private_stack.py IMAGE INVENTORY DECODER EMULATOR OUT`:2 ASM/CFG rozsahy, init/vector context, data intervaly a1152 prípadov.
- `runtime_watch_keyboard_stack.py DOSBOX_EXE GAME_DIR IMAGE RELOCS OUT WORK startup CD_ASSET`:56 captures a IRQ frame probe.
- `runtime_watch_worx_stack_window.py ...`:61 captures a explicitné paused private-stack okno.
- `verify_keyboard_stack_capture.py IMAGE RELOCS MAP OUT WORK`: nezávisle overuje relokácie,23 nezmenených vstupov, command whitelist, oba hardvérové framy, private kontext, BIOS queue a fonty. Starší verifier a17. runtime proof ostávajú nezmenené.
- `independent_decode_and_catalog.py` importuje iba30B priamych polí, nie512B kandidáta; centrálne byte_intervals.csv/json obsahujú nový presný partition stav.

Predchádzajúca overená GitHub snímka má17 runtime scenárov. Táto dávka zostáva lokálna, kým nie je zapísané nové potvrdenie publikácie.

## Aktualizácia 13 oblastí

TABLE_PLACEHOLDER

## Runtime testy na vykonanie

1. Zachytiť key IRQ skutočne vnorené do timer private callbacku spolu s interrupted frame; súčasné paused okno tento výsledok neposkytlo.
2. Zachytiť celý priebeh timer IRQ08 vrátane saved vector chain, PIC stavu a nestovaného depth/missed count. Odmerať väzbu na hru a audio callees4476/555D/5DF2.
3. Nájsť dôkaz dolnej hranice a potrebnej hĺbky private stacku;492B kandidáta nemožno povýšiť na typované dáta len z núl.
4. Pokračovať za083D:0054 k textu/menu a map init; aktuálne scenáre končia pri font1 ready.
5. Rozšíriť UNKNOWN44 read/write pokrytie a uzavrieť neznáme DS2356 hook callery; stabilné hodnoty pri intro nestačia.
'''
prev=(r/'KEYBOARD_IRQ_FONT1_RUNTIME_REPORT.md').read_text(encoding='utf-8');table=prev[prev.index('## Aktualizácia 13 oblastí'):prev.index('## Runtime testy na vykonanie')]
table=table.replace('font1:1145B→127 záznamov/889B bitmap; header11,11 ≠ max10,10','nových30B direct stack/control polí mimo NON-CODE;512B kandidat len CLASSIFIED').replace('header sémantika a signed-char domény','492B candidate backing bez potvrdenej kapacity')
table=table.replace('4nové funkcie388B/152inštrukcií;114IRQ starts absent v starom inventári','2nové funkcie203B/87inštrukcií;1152 stack/timer replay').replace('nestedIRQ, drain/mode producenti a Win ekvivalent','old interruptedPC, audio callees a Win ekvivalent').replace('IRQ kontext a register restore vetvy','celý timer chain a nested IRQ')
table=table.replace('IRQ make/break s odlišnými SS; foreground stack obnovený','WORX private SS/SP a timer phase/depth/EOI vetvy').replace('mode4/scheduler a pôvod alternate SS','herný scheduler, tempo a celý timer chain').replace('interrupted CS:IP a stack owner','timer08 entry/exit trace a väzba na main loop')
table=table.replace('port60 make39/breakB9; game0200; BIOS3920; prirodzený wait exit','nové frame návraty0BDE:00C6; paused WORX SS kontext').replace('DEMO poradie, nestedIRQ, flags/mode producenti','presný old alternateIRQ PC a DEMO poradie')
text=text.replace('## Aktualizácia 13 oblastí\n\nTABLE_PLACEHOLDER\n\n',table)
receipt=r/'CAMPAIGN_WORX_STACK_PUBLICATION_RECEIPT_20261112.json'
if receipt.exists():
 pub=json.loads(receipt.read_text());text=text.replace('Predchádzajúca overená GitHub snímka má17 runtime scenárov. Táto dávka zostáva lokálna, kým nie je zapísané nové potvrdenie publikácie.','Táto dávka je publikovaná a blob po blobe overená v analytickom commite '+pub['commit']+'. Strojové potvrdenie: CAMPAIGN_WORX_STACK_PUBLICATION_RECEIPT_20261112.json; metadata follow-up môže mať novší branch head.')
(r/'WORX_PRIVATE_STACK_RUNTIME_REPORT.md').write_text(text,encoding='utf-8');print(json.dumps(dict(report='WORX_PRIVATE_STACK_RUNTIME_REPORT.md',functions=136,runtime_tests=19,new_typed_data=30,replay_cases_added=1152)))
