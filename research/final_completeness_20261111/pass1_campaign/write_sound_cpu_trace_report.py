# -*- coding: utf-8 -*-
"""python write_sound_cpu_trace_report.py OUTPUTS"""
import hashlib,json,sys
from pathlib import Path
r=Path(sys.argv[1]);a=json.loads((r/'sound_cpu_memory_trace/summary.json').read_text());out=r/'dosbox_sound_trace_runtime';p=json.loads((out/'independent_verification.json').read_text());assert p['cpu_trace_manifest_verified'];sha=lambda b:hashlib.sha256(b).hexdigest()
for item in p['files']:assert sha(Path(item['path']).read_bytes())==item['sha256']
old=(r/'SOUND_DIRECTORY_PRODUCER_REPORT.md').read_text(encoding='utf-8');table=old[old.index('## Aktualizácia 13 oblastí'):old.index('## Runtime testy na vykonanie')]
table=table.replace('|BSS DS3F64 má doloženého producenta a 79 WORD/DWORD záznamov|alias writeri a runtime ID domény|sound caller trace|','|122 rekonštruovaných CPU memory ranges bez zásahu UNKNOWN44B v sound init okne|host callbacky a iné časové okná|rozšírená read/write instrumentácia|')
table=table.replace('|sound directory init96B/33inštrukcií a main0190 endpoint|I/O chyby, seek failure a resource callee|short-read a herný vstup|','|4699 x86 trace záznamov,151 canonical byte matches,6 INT21 vstupov|host callback internals a celý herný tok|prvý map/scheduler trace|')
text='''# Zvuková inicializácia: skutočný CPU log a adresy pamäťových operandov

Jedenásty zachovaný DOSBox-X scenár pridáva **krátku prirodzenú CPU stopu** odmain **0476:017C** po **0476:0190**. Táto stopa dopĺňa predchádzajúce memory-change breakpointy o konkrétne x86 pamäťové operandy, ale nezahŕňa vnútorné hostiteľské prístupy DOSBox callbackov.

## Presný rozsah a vykonanie

Raw `LOGCPU.TXT` má **5084 pre-instruction záznamov /1631964B**. Začína skutočným0C9A:017C, FAR call zvukového producenta0A9B:0AE0. Posledný záznam0C9A:0190 je už endpoint code breakpoint, jeho RETF ešte nebolo vykonané. **Tento posledný záznam je z analýzy vykonaných kandidátov vynechaný.**

Zo5083 ostatných záznamov je **4699 platných x86 inštrukčných záznamov** a **384 DOSBox host callback záznamov**. Z x86 časti sa151 výskytov inštrukcií nachádza v kanonickom game image a ich logované bajty sa presne zhodujú s obrazom po reálnych1670 relokáciách. Zvyšok zahŕňa emulovaný DOS/BIOS a idle tok. Čísla sú výskyty v konkrétnej stope, nie unikátne game funkcie, code coverage percento alebo samostatné replay cases.

## Rekonštruované pamäťové prístupy

Každý x86 záznam obsahuje skutočné bytes, CS:IP, všeobecné registre a DS/ES/FS/GS/SS. Nezávislýiced-x86 dekóder overí dĺžku a InstructionInfo poskytne šírky, segment, base/index/scale/displacement a read/write rolu. Efektívne offsety rešpektujú16/32bit address-size a segment:offset výpočet v skutočnom real mode. Skript navyše explicitne doplní real-mode INT stack zápisy a vector read; nejde iba o hľadanie konštánt vASM.

V tejto stope vzniklo **122 pamäťových rozsahov**:69read,52write a1read/write. Nie sú v nej REP inštrukcie; skript priREP skončí chybou, pretože správna granularita jednotlivých iterácií sa ešte neoverila. Nepreberá sa neoverený predpoklad, že jeden logovanýREP riadok znamená celýCX počet prístupov. LEA/no-memory operácie sa nevydávajú za čítanie.

Žiadny z122 rekonštruovaných rozsahov nezasiahol44 historických UNKNOWN bajtov ani4B hookDS2356. Rovnako nebol logovaný instruction fetch z UNKNOWN množiny. **Nulový zásah platí iba pre uvedené CPU rozsahy a toto krátke okno.** Tým sa UNKNOWN nezvyšuje na padding, unused ani DEEP VERIFIED.

## Nové prirodzené DOS API vstupy

Stopa ukazuje6 vstupov INT21; všetky so skutočnými registrami:

|AX pri INT21|BX|CX|DX|DS|Pozorovaný kontext|
|---|---:|---:|---:|---:|---|
|3D00|6|8000|0554|2F95|otvorenie názvu snd.dat|
|4400|6|8000|0554|2F95|ďalšia CRT kontrola handle|
|4300|6|8000|0554|2F95|atribútová CRT kontrola názvu|
|4200|6|0000|00C0|2F95|seek s origin0 a offset192|
|3F00|6|01DA|3F64|2F95|read474B do sledovanej BSS tabuľky|
|3EDA|6|01DA|3F64|2F95|close; ALDA je zachovaný pracovný obsah, nie ďalší argument|

Predchádzajúci producer audit odvodil seek/read argumenty staticky. Táto nová stopa ich už zachytáva **pri skutočnom INT21 vstupe** a navyše ukazuje CRT kontroly4400/4300. Runtime474B dump opäť presne zodpovedáSND.DAT[192,666). Nenormalizuje sa celéAX close na3E00; významná je skutočnáAH3E vetva.

## Hranica host callbackov

DOSBox používa vlastnýFE38 callback escape; jeho záznam sa nesmie dekódovať ako bežná x86 inštrukcia.384 takých záznamov je výslovne vedených v `host_callbacks.csv`. Medzi nimi sú DOS file API aj idle služby. Ich C++ interné read/write operácie nie sú vLOGL x86 stope, preto zostávajú neuzavreté.

Významný príklad je samotný read474B: v deklarovaných registrochDS:DX/CX a vo finálnom buffere sa doloží, ale host callback zapíše dáta bez474 samostatných x86 store záznamov. **Neprítomnosť CPU store preto neznamená neprítomnosť zápisu.** Presne z tohto dôvodu nejde o úplnú všeobecnú read/write stopu systému. Asynchrónne interrupt/hardware účinky a portové zariadenia sa tiež neprezentujú ako kompletne pokryté týmto zoznamom operandov.

## Reprodukcia a overenie

1. `runtime_sound_cpu_trace.py DOSBOX_EXE GAME_DIR IMAGE RELOCS OUT WORK` najprv dosiahne017C s44 memory-change breakpointmi. Odstráni iba starý endpoint code BP, zachová44watchov a pridá0190. `LOGL 00010000` zapne bounded log s limitom65536 riadkov; cieľ sa dosiahne skôr. Log zapisuje riadky sflush, preto je zachovaný aj po ukončení emulátora harnessom.
2. `verify_unknown_watch_capture.py IMAGE RELOCS CURRENT_MAP OUT WORK` overí tri snapshoty, endpointy, breakpointy, vstupy,14 raw captures a trace manifest/SHA. Pôvodných22 súborov sa nemenilo. Session sa ukončuje harnessom, nie prirodzeným game exitom.
3. `audit_sound_cpu_memory_trace.py RUNTIME_OUT IMAGE RELOCS MAP ABS_DECODER OUT` nezávisle parsuje celý log, vylúči terminal record a host callbacks, overí actual bytes, real-mode predpoklady a vypočíta memory ranges. Všetky očakávania sú explicitné; neznáma alebo neplatná inštrukcia, nepodporovaný register, nulová operand šírka čiREP spôsobia chybu.

Výstupy: `instructions.csv`,`memory_operands.csv`,`host_callbacks.csv`,`interrupt_inputs.csv`,summary a pôvodný raw log cez `trace_manifest.json`. Zoznam memory operands je rekonštrukcia CPU semantics zo skutočných registrov, nie nezávislý hardvérový bus analyzer. Dynamické dáta nie sú pri tom vynucované cezSR/SM/FM.

'''+f"Raw trace SHA `{a['trace_sha256']}`. Runtime proof SHA `{a['runtime_proof_sha256']}`. Map SHA `{a['map_sha256']}`.\n\n"+'''## Meranie

Úspešné originálne runtime scenáre10→11. Žiadny nový funkčný rozsah ani seeded replay; DOS katalóg126 rozsahov a samostatný Win paletový doplnok4 rozsahy/22 replay prípadov ostávajú. CPU trace záznamy sa nepripočítavajú k počtu nezávisle uzavretých funkcií alebo testov. PASS1 stále57102 B PARTIAL,149 B CLASSIFIED ONLY,44 B UNKNOWN,0 B DEEP VERIFIED. Nové sémantické percentáN/A. Dávka je lokálna, zatiaľ nepublikovaná.

'''+table+'''## Runtime testy na vykonanie

Rozšíriť bounded trace do map init a prvého scheduler ticku; osobitne overiť REP/early-exit/interrupt granularitu. Na doplnenie chýbajúcej vrstvy treba instrumentovať host callback memory API alebo explicitne analyzovať každú použitú službu a jej pointery. Sledovanie celého systému nesmie nahradiť úzky122-range výsledok. UNKNOWN44B a hookDS2356 zostávajú otvorené.
'''
(r/'SOUND_CPU_MEMORY_TRACE_REPORT.md').write_text(text,encoding='utf-8');print(json.dumps(dict(report='SOUND_CPU_MEMORY_TRACE_REPORT.md',trace_records=a['trace_records'],memory_ranges=122,runtime_tests=11)))
