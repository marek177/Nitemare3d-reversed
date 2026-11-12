# -*- coding: utf-8 -*-
"""python write_input_init_runtime_report.py OUTPUTS WORK"""
import hashlib,json,sys
from pathlib import Path
r,w=map(Path,sys.argv[1:]);out=r/'dosbox_input_init_runtime';s=json.loads((out/'summary.json').read_text());p=json.loads((out/'independent_verification.json').read_text());assert p['input_initialization_checks_passed'];sha=lambda b:hashlib.sha256(b).hexdigest()
for item in p['files']:assert sha(Path(item['path']).read_bytes())==item['sha256']
old=(r/'DOSBOX_POST_VGA_RUNTIME_REPORT.md').read_text(encoding='utf-8');table=old[old.index('## Aktualizácia 13 oblastí'):old.index('## Runtime testy na vykonanie')]
table=table.replace('|prirodzený slot init a resource mode0 návrat|clipped draw a ďalšia init cesta|pokračovať za0476:0134|','|4 nové API/probe wrappers,88B/37inštrukcií|INT86 a ISR telá|ISR interrupt kontrakt|')
table=table.replace('|bez input/demo runtime|driver a demo|prirodzené demo|','|prirodzený INT9 install a aux probeFFFFh|key IRQ/DEMO poradie/close|prvý vstupný tick|')
text='''# DOSBox-X: INT9 a pomocná vstupná inicializácia

Piaty zachovaný scenár pôvodného packed DOS2 EXE pokračuje za resource init až po **0476:015C**. Overené sú prirodzené keyboard/aux mode0 vetvy; registre, game kód ani OS odpovede sa nedosadzujú. Dávka pridáva tiež štyri krátke statické wrappery do funkčného katalógu. Pôvodné22 vstupné súbory sa po behu znovu hashovali bez zmeny.

## Pozorovaný INT9 životný cyklus

Vstup **06B0:0134**, skutočne **0ED4:0134**, má návrat0C9A:0148 a WORD mode0. Pred vstupom sú BYTE DS0B3E/0B3F rovné0/0. Pôvodný IVT9 je **F000:E987** (bajty87E900F0). Po návrate je IVT9 **0ED4:0000** (0000D40E), uložený FAR v DS3F52 je byte-exact pôvodný IVT9 a príznaky sú1/0. DS=SS2F95 v oboch bodoch.

To potvrdzuje prirodzené get-vector/save/set-vector v emulovanom DOS prostredí. Nevykonával sa zatiaľ prirodzený shutdown mode1 s obnovou vektora ani celý IRQ handler kontrakt. Staršia mode1/mode0 seeded lifecycle analýza zostáva osobitným dôkazom, nie prirodzenou close skúškou.

## Pomocný vstupný probe

Vstup **06B0:018C**, skutočne0ED4:018C, má návrat0C9A:015C a mode0. Na **06B0:01A8** sa po návrate z0831:000E pozorovalo **AX=FFFFh**; rovnaký WORD je v DS3F56 register bufferi. Po caller normalizácii sú príznaky DS0B3E/0B3F=1/1 a dostupnosť DS414C=1. Dostupnosť bola1 aj pred volaním; overená je výsledná hodnota a probe, nie prechod dostupnosti0→1.

Probe je odvodený od explicitného INT33 volania cez CRT adapter11EE:24EA. V tejto dávke sa nepreukazuje pohyb fyzickej myši, tlačidlá, chovanie neexistujúceho ovládača alebo kompletné reg-pack ABI. HodnotaFFFF sa vyhodnocuje unsigned ako >=1; nejde o signed negatívnu chybu.

## Oddelenie runtime wrapperov od hernej politiky

|Rozsah|B/inštrukcie|Kontrakt a závislosť|
|---|---:|---|
|11EE:39E2..39F4|18/10|WORD vector arg; AH35h/INT21; vráti DX:AX z ES:BX, ES ostáva API výsledok|
|11EE:39F4..3A09|21/12|WORD vector+FAR handler; uložíDS,LDS DX argument,AH25h/INT21,obnovíDS,AX0|
|0831:000E..0028|26/8|nastaví WORD DS3F56=0; ten istý near buffer dá ako in/out11EE:24EA pre interrupt33h; vráti WORD3F56|
|0831:0028..003F|23/7|rovnaká buffer príprava/interrupt33h; nemá explicitný návratový loadAX|

Všetky štyri sú straight-line FAR funkcie, bez skokovej tabuľky; hranice a každá inštrukcia sú byte-exact overené nezávislým dekóderom proti inventáru. Calleri odstraňujú argumenty. Get/set wrappery majú BP rámec a prirodzene patria vrstve DOS API v CRT segmente; presný názov/autor knižnice či kompilátora nie je týmto identifikovaný. Probe/close wrappery zdieľajú herný BSS buffer a volajú externý runtime adapter. Herná politika, kedy tieto operácie vykonať a ako normalizovať dostupnosť, je v06B0:0134/018C, ktoré boli v katalógu už skôr.

Lokálny pseudokód get/set:

```text
get_vector(v): AX=WORD(v); AH=35h; INT21; return FAR(ES:BX) as DX:AX
set_vector(v,p): save DS; AX=WORD(v); DS:DX=p; AH=25h; INT21;
                 restore DS; return AX=0
probe(): WORD[3F56]=0; int_adapter(33h, near3F56, near3F56); return WORD[3F56]
```

Vstupné AL vektor číslo je lowBYTE WORD argumentu; testovaná prirodzená hodnota je9. Efekty INT21/33 a ďalšie registre sa nevyhlasujú za uzavreté mimo pozorovaného prostredia. Predchádzajúce tvrdenie DS=ES z niektorých startup bodov nie je invariant cez get-vector alebo ďalšie API volania.

## Reprodukcia a evidencia

`runtime_dosbox_startup.py DOSBOX_EXE GAME_DIR IMAGE RELOC OUT WORK input_init`, potom `verify_dosbox_startup_capture.py IMAGE RELOC OUT WORK`. Verifier kontroluje68 memory-dump príkazov, úplný runtime image po1670 relokáciách, všetky skoršie startup/init body, nové stacks/IVT/flags/probe a SHA každého dôkazu. Povolené debugger operácie sú query/code BP/RUN/dump; žiadne dosadzovanie registrov/pamäte. Raw dumpy sú vo WORK, strojové summary/transcript/registers/inputs/proof v `dosbox_input_init_runtime/`.

`audit_input_runtime_wrappers.py IMAGE INVENTORY ABS_DECODER OUT` reprodukuje štyri ASM katalógy. `write_input_init_runtime_report.py OUTPUTS WORK` pred generovaním znovu kontroluje všetky runtime proof hash položky. Harness ukončí svoj DOSBox po poslednom bode, nejde o prirodzený game exit.

'''+f"Summary SHA `{p['summary_sha256']}`. Proof SHA `{sha((out/'independent_verification.json').read_bytes())}`. Packed EXE SHA `{s['game_source_sha256']}`.\n\n"+'''## Meranie

Prirodzené zachované scenáre4→5; ich prefixy sa prekrývajú a každý breakpoint sa nepočíta ako ďalší scenár. Katalóg118→122rozsahov, +37inštrukcií/+88B. Žiadny nový seeded replay. PASS1 bez zmeny57102PARTIAL/149CLASSIFIED ONLY/44UNKNOWN/0DEEP VERIFIED. BSS saved-vector a register buffer sa nepripočítavajú k historickým file bajtom. Dávka je lokálna, nie nová GitHub publikácia; Win16 a plná vstupná/DEMO parita zostávajú otvorené.

'''+table+'''## Runtime testy na vykonanie

Pokračovať za0476:015C k RNG seed/asset inicializácii a prvému scheduler/input ticku. Samostatne zachytiť prirodzený IRQ9 handler a obnovu uloženého vektora pri mode1. Pre DEMO treba párovú input/RNG stopu, nie iba initialized flags. Pre NON-CODE44B zostáva read/write alias audit; tieto vstupné BSS polia ho nenahrádzajú.
'''
(r/'DOSBOX_INPUT_INIT_RUNTIME_REPORT.md').write_text(text,encoding='utf-8');print(json.dumps(dict(report='DOSBOX_INPUT_INIT_RUNTIME_REPORT.md',new_runtime_scenarios=1,new_functions=4)))
