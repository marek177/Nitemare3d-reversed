# -*- coding: utf-8 -*-
"""python write_episode_init_runtime_report.py OUTPUTS WORK INVENTORY DECODER"""
import csv,hashlib,json,sys
from pathlib import Path
r,w,inventory,dep=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
out=r/'dosbox_episode_init_runtime';s=json.loads((out/'summary.json').read_text());p=json.loads((out/'independent_verification.json').read_text());assert p['episode_checks_passed'];sha=lambda b:hashlib.sha256(b).hexdigest()
for item in p['files']:assert sha(Path(item['path']).read_bytes())==item['sha256']
b=(r/'unpack/reproduced_image.bin').read_bytes();lookup={x['image_offset']:x for x in json.loads(inventory.read_text())};fmt=Formatter(FormatterSyntax.INTEL);asm=[]
for start,end in [(0x3990,0x39af),(0x5a2,0x5aa)]:
 pos=0x11ee0+start
 for i in Decoder(16,b[pos:0x11ee0+end],ip=start):
  raw=b[pos:pos+i.len];assert not i.is_invalid and lookup[pos]['bytes']==raw.hex();asm.append(dict(cs=0x11ee,ip=i.ip,image_offset=pos,bytes=raw.hex(),instruction=fmt.format(i)));pos+=i.len
 assert pos==0x11ee0+end
assert b[0x15876:0x1587b]==bytes.fromhex('b80043cd21')
with (out/'access_wrapper_context.csv').open('w',newline='',encoding='utf-8') as f:writer=csv.DictWriter(f,fieldnames=list(asm[0]));writer.writeheader();writer.writerows(asm)
old=(r/'EPISODE_AVAILABLE_PROBE_REPORT.md').read_text(encoding='utf-8');table=old[old.index('## Aktualizácia 13 oblastí'):old.index('## Runtime testy na vykonanie')]
table=table.replace('|episode1..6 scan a výsledok7;256 modelovaných prípadov|skutočné access výsledky|prirodzený episode probe|','|prirodzený map.1 probe a názvy map/img/demo.1|platnosť obsahu a iné scenáre|map/resource skutočné čítanie|')
table=table.replace('|nový episode probe75B/31inštrukcií|caller výsledku7 a externé telá|0476:0169/016F runtime|','|prirodzené2696→access→BSF1→0336|caller výsledku7 a ďalšia init|0476:0174 pokračovanie|')
text='''# DOSBox-X: prirodzený výber epizódy a príprava názvov dát

Šiesty zachovaný scenár pôvodného packed DOS2 EXE pokračoval po input init cez **0D29:2696** a prípravu epizódy0277:0336 až po návrat **0476:0174**. Pôvodné registre, game kód ani odpovede volaní sa nedosadzujú. Skoršie startup/BSF/VGA/input body sú znovu overené ako spoločný prefix, nie ako nové samostatné testy.

## Skutočný priebeh

|Kanonický bod|Zachytený výsledok|
|---|---|
|0D29:2696|DS=SS2F95; návrat0C9A:016E|
|0D29:26AE|pôvodný formatter vytvoril `map.1` v lokálnom16B buffere DS:E7E6|
|11EE:3990|near filenameE7E6,arg4; návrat154D:26BC|
|0D29:26BC|AX0 z pôvodného access wrappera|
|0D29:26CA|BSFmode1 vrátil FAR2F95:363B|
|0476:016E|AX1 z episode probe|
|0277:0336|návrat0C9A:0174,WORD episode1|
|0476:0174|DS626A=1; buffery627C/628C/629C obsahujúmap.1/img.1/demo.1|

Lokálny filename offset je nezávisle vypočítaný zo vstupnéhoSP−18 podľa ENTER16 a uloženiaBP; verifier ho porovnáva s reálnym stack argumentom access. Nie je odvodený len z harness summary. BSF pointer ukazuje na flag v pôvodnom decoded headeri. Tento capture potvrdzuje bežnú existujúcu epizódu1; ešte neuzatvára neúspešný scan, unregistered vetvu alebo caller výsledku7.

## Čo skutočne robí access wrapper

Nový ohraničený ASM kontext **11EE:3990..39AF** je v `access_wrapper_context.csv`, nezávisle byte-exact overený proti kanonickému obrazu a inventáru. NačítanieDXfilename nasleduje **AX4300h;INT21h**. Pri carry skočí na zdieľaný normalizátor05A2. Pri úspechu kontroluje iba bit2h druhého argumentu; ak je bit nastavený aCL atribút bit1h je nenulový, vytvoríAX0D00h,STC a znovu prejde normalizátorom. Inak ponechá úspech.

```text
query_attributes(filename) via AX4300h/INT21
if DOS carry: tail common_result
if (mode & 2) != 0 and (CL & 1) != 0:
    AX=0D00h; carry=1
tail common_result

common_result at05A2:
    if carry: branch error path05B9   // full error mapping not closed here
    AX=0; restore SP/BP; FAR return
```

Pri skutočnom argumente **4** sa bit2h netestuje ako zapnutý. Úspešný probe teda v tejto implementácii nepotvrdzuje skutočné otvorenie/čítanie mapy ani platnosť jej obsahu. Prirodzený capture overil výsledokAX0, nie každú atribútovú a chybovú vetvu wrappera. Táto krátka závislosť sa zatiaľ nepridáva ako uzavretá celá funkcia do katalógu, pretože zdieľaná error tail cesta nie je v dávke vykonaná.

## Reprodukcia

`runtime_dosbox_startup.py DOSBOX_EXE GAME_DIR IMAGE RELOC OUT WORK episode_init` a `verify_dosbox_startup_capture.py IMAGE RELOC OUT WORK`. Verifier preverí74MEMDUMPBIN príkazov,1670relokácií a celých171360B runtime obrazu, všetky skoršie registre/stacks/headers aj6 nových raw dumpov. Nové súbory sú episode_probe_stack,episode_filename,episode_access_stack,episode_prepare_stack,episode_global,episode_asset_names. Hashované sú spolu s transcript,snapshots,inputs aconfig v independent_verification.json. Raw memory je vo WORK, nie v GitHube.

`write_episode_init_runtime_report.py OUTPUTS WORK INVENTORY ABS_DECODER` znovu overí všetky capture proof hash položky a ASM závislosť. Originálne22 vstupné súbory zostali po behu nezmenené. Harness ukončí svojDOSBox po poslednom bode; nejde o prirodzený exit hry. Skutočná grafika/zvuk aWin16 zostávajú mimo tejto skúšky.

'''+f"Summary SHA `{p['summary_sha256']}`; proof SHA `{sha((out/'independent_verification.json').read_bytes())}`.\n\n"+'''## Meranie

Prirodzené zachované scenáre5→6. Žiadna nová funkcia ani seeded replay v tejto dávke; katalóg zostáva123rozsahov. PASS1 bez zmeny57102PARTIAL/149CLASSIFIED ONLY/44UNKNOWN/0DEEP VERIFIED. Nové near filename aepisode globals sú BSS/stack, nie nové file-backed promócie. Lokálna dávka zatiaľ nie je súčasťou publikovanej päť-scenárovej snímky2ced761cb0bf1eece24a224e92c05636058ab0ae. Nové percentá N/A bez úplných menovateľov.

'''+table+'''## Runtime testy na vykonanie

Pokračovať za0476:0174 do čítania palety0277:02A6 a resource/game init; zachytiť skutočné file offsety a počty, nie iba existenciu. V oddelených pracovných kópiách overiť chýbajúceepizódy, atribútové chyby a spracovanie výsledku7. RNGreset0D29:271C zostáva neskorší prirodzený bod, nie časový seed v tejto vetve. PASS1 UNKNOWN44B stále vyžaduje priamy read/write alias dôkaz.
'''
(r/'DOSBOX_EPISODE_INIT_RUNTIME_REPORT.md').write_text(text,encoding='utf-8');print(json.dumps(dict(report='DOSBOX_EPISODE_INIT_RUNTIME_REPORT.md',new_runtime_scenarios=1)))
