# -*- coding: utf-8 -*-
"""python write_post_vga_runtime_report.py OUTPUTS CAPTURE_WORK"""
import csv,hashlib,json,struct,sys
from pathlib import Path
r,w=map(Path,sys.argv[1:]);out=r/'dosbox_post_vga_runtime';s=json.loads((out/'summary.json').read_text());proof=json.loads((out/'independent_verification.json').read_text());assert proof['post_vga_checks_passed']
sha=lambda b:hashlib.sha256(b).hexdigest()
for item in proof['files']:assert sha(Path(item['path']).read_bytes())==item['sha256']
before=(w/'slots_before_init.bin').read_bytes();after=(w/'slots_after_init.bin').read_bytes();assert not any(before)
mutations=[dict(slot=n,ds_offset=0x50f2+n*18,image_relative=0x2c802+n*18,before=before[n*18],after=after[n*18]) for n in range(100)]
ptr=(w/'resource_pointers.bin').read_bytes();pointers=[]
for n in range(14):
 off,seg=struct.unpack_from('<HH',ptr,n*4);pointers.append(dict(index=n,pointer_ds_offset=0x34cc+n*4,offset=off,segment=seg,linear=seg*16+off,header_bytes=6,header_hex=(w/('resource_header_%02d.bin'%n)).read_bytes().hex()))
for name,rs in [('slot_mutations',mutations),('resource_pointer_observations',pointers)]:
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:writer=csv.DictWriter(f,fieldnames=list(rs[0]));writer.writeheader();writer.writerows(rs)
old=(r/'SPRITE_PIXEL_REPLAY_REPORT.md').read_text(encoding='utf-8');table=old[old.index('## Aktualizácia 13 oblastí'):old.index('## Runtime testy na vykonanie')]
table=table.replace('|12 lokálnych FAR konštrukcií 21FD:264E odlíšených od DS:264E|aliasy/dynamické indexy|watchpointy na 44 UNKNOWN B|','|14 prirodzených FAR resource pointerov,6B hlavičky0|plný resource lifetime a obsah|resource slot consumers|')
table=table.replace('|celé pôvodné telo,4608 pixel scenárov|clipped draw a caller domény|kombinovaný clipping/pixel test|','|prirodzený slot init a resource mode0 návrat|clipped draw a ďalšia init cesta|pokračovať za0476:0134|')
table=table.replace('|statický post-VGA init 100 BYTE s krokom18|rola slotov, clipping, frame|spotrebitelia DS:50F2|','|prirodzený post-VGA init100 BYTE|úplný frame/slot lifecycle|prvý pending flush|')
text='''# DOSBox-X: prirodzená post-VGA slot/resource inicializácia

Nová štvrtá zachovaná session spustila pôvodný packed DOS2 EXE a pokračovala za predchádzajúci návrat z VGA. Oproti seeded testom sa tu nemenia game registre, inštrukcie ani odpovede podvolaní. Kópie22 pôvodných vstupných súborov sú v izolovanom C:; originály boli po behu znovu hashované a zostali nezmenené. Použitý DOSBox-X aj packed EXE majú rovnaké SHA ako predchádzajúce tri scenáre.

## Presné body a dôkazy

|Kanonické miesto|Pozorované miesto|Výsledok|
|---|---|---|
|0201:000A|0A25:000A|slot initializer entry; DS=SS2F95,ES=A400|
|0476:012D|0C9A:012D|návrat slot init; BX57FA|
|0768:0024|0F8C:0024|resource mode0 entry; stack návrat0C9A:0134,arg0|
|0476:0134|0C9A:0134|resource mode0 vrátený; DS=SS2F95,ES=C3FF|

Loader základ je0824h. Slot vstupný stack obsahuje návrat0C9A:012D bez vstupných argumentov. Pred ním je všetkých1800B `[DS:50F2,DS:57FA)` nulových. Po návrate sa zmenilo **presne100B,0→1**, na offsetoch50F2+18*n,n0..99. Ostatných1700B zostalo byte-exact nezmenených. Dump pred/po a `slot_mutations.csv` uchovávajú tento dôkaz. Nepreukazuje to neprítomnosť dočasných zápisov počas slučky; tie podporuje už samostatne overené statické telo.

Po návrate resource inicializácie `[DS:34CC,DS:3504)` obsahuje **14 nenulových FAR pointerov s14 rôznymi linear adresami**. Pri každom z nich bol prečítaný presný6B header; všetky sú nulové. CSV `resource_pointer_observations.csv` uvádza slot, FAR aj linear adresu a header. Toto nie je dôkaz nulovosti celého alokovaného bloku ani úplný allocation trace. Funkcia môže vykonávať ďalšie alokácie alebo I/O, ktoré tento ohraničený bod neuzatvára. ES po návrate jeC3FF, teda nemožno rozšíriť DS=ES z niektorých starších bodov na celú init cestu.

## Nezávislá kontrola a reprodukcia

`runtime_dosbox_startup.py DOSBOX_EXE GAME_DIR IMAGE RELOC OUT WORK post_vga` vytvorí novú session. `verify_dosbox_startup_capture.py IMAGE RELOC OUT WORK` nezávisle overí celých171360 runtime image bajtov po1670 relokáciách, skoršie BSS/CRT/BSF/audio/VGA body aj všetky nové dumpy/stacks/stages. Transcript má56MEMDUMPBIN príkazov; allowlist pripúšťa iba PING,register query,code breakpointy,RUN a memory dump. Nepoužíva SR/SM na dosadenie stavu. Po poslednom bode harness ukončí svoj emulátor; jeho process return1 sa nepovažuje za pád hry ani prirodzený exit.

Každý dôkazový súbor má SHA v `independent_verification.json`; vstupné originály a kópie v `inputs.csv`, príkazy v `transcript.json`, registre v `snapshots.json`. Raw memory dumpy sú v priradenom WORK adresári. Generátor tejto správy pred zápisom znovu overuje všetky proof hash položky.

'''+f"Summary SHA `{proof['summary_sha256']}`. Proof SHA `{sha((out/'independent_verification.json').read_bytes())}`. Slot pred SHA `{sha(before)}`, po SHA `{sha(after)}`.\n\n"+'''## Meranie

Prirodzené zachované DOSBox scenáre **3→4**. Scenáre majú spoločný startup prefix; nepočíta sa každý opakovaný breakpoint ako samostatný runtime test. Žiadny nový function range ani seeded replay prípad v tejto dávke. Katalóg118rozsahov a file-byte klasifikácia57102PARTIAL/149CLASSIFIED ONLY/44UNKNOWN/0DEEP VERIFIED ostávajú. Sloty aj heap sú mimo file image a PASS320 baseline. Nie je to úplná gameplay/render/audio/Win16 parita. Dávka je zatiaľ lokálna, nie nová GitHub publikácia.

'''+table+'''## Runtime testy na vykonanie

Pokračovať za0476:0134 cez ďalšie inicializátory k resource dekódovaniu a prvému prirodzenému pending flush. Zachytiť pôvodné sloty/source/depth/VGA registre a porovnať štyri VRAM roviny. Pre NON-CODE44B treba stále read/write stopu nepriamych aliasov; úspech BSS inicializátora tieto intervaly neuzatvára.
'''
(r/'DOSBOX_POST_VGA_RUNTIME_REPORT.md').write_text(text,encoding='utf-8');print(json.dumps(dict(report='DOSBOX_POST_VGA_RUNTIME_REPORT.md',slot_mutations=100,resource_pointer_headers=14)))
