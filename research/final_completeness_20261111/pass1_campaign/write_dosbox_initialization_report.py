# -*- coding: utf-8 -*-
import json
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'dosbox_initialization_runtime';s=json.loads((d/'summary.json').read_text());v=json.loads((d/'independent_verification.json').read_text());t=json.loads((r/'runtime_reciprocal_init/summary.json').read_text());assert s['success'] and v['initialization_checks_passed']
text='''# DOSBox-X runtime: BSF, audio, VGA a recipročná tabuľka

**Tretí zachovaný overený scenár originálneho packed DOS2.0 EXE úspešne prešiel BSF, audio a VGA inicializáciou až po caller0476:011B.** Žiadna herná/CRT funkcia nebola nahradená, diskový EXE ani registre hry neboli patchované/seedované. Je to debuggerom inštrumentovaný beh DOSBox-X built-in DOS, nie reálny historický DOS/hardvér ani gameplay parity dôkaz. Obrazové porovnanie a zvuková waveform skúška neprebehli, DEEP VERIFIED zostáva0.

## Prostredie a auditovateľná cesta

DOSBox-X official portable Windows SDL2 v2026.10.01, EXE SHA a82adcfa7af2784566cfeff74c077cefed08505396db2948b7e6aa7d4cee0832. Pôvodný N3D-UNFU.exe SHA552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301 sa spúšťa ako byte-identická kópia N3D20.EXE v samostatnom workspace mount. Všetky22 pôvodné zdrojové súbory z inputs.csv zostali nezmenené. Normal core, fixed20000cycles, svga_s3, SDL dummy a nosound. Presné príkazy/konfigurácia sú v summary.json a runtime.conf.

Skoršie startup kontroly sa opakujú: PSP0814h/load0824h, presných171360 B image po1670 relokáciách, BSS47584 nula a main/argumenty/INT0 podľa predchádzajúcich reportov. Sú to prekrývajúce sa prefixové kontroly, nie ďalšie percento coverage. Nový scenár má samostatný transcript, capture hash a nezávislý verifier.

| Meraný bod (canonical CS:IP) | Runtime CS:IP | Nový dôkaz |
|---|---|---|
|BSF083D:29CA|1061:29CA|mode0, FAR návrat0C9A:00DF|
|XOR0FBA:01B2|17DE:01B2|DS:3638 FAR buffer, count54|
|po XOR083D:2A3D|1061:2A3D|AL=0,54 decoded bytes zhodné|
|file check083D:28EE|1061:28EE|n3d.exe, countDWORD0, expectedEC|
|caller poBSF0476:00DF|0C9A:00DF|pôvodná kontrola sa vrátila|
|audio0C2B:00DC / caller00F3|144F:00DC /0C9A:00F3|mode0 a prechod active flags|
|VGA0156:00D8 / caller011B|097A:00D8 /0C9A:011B|mode0, BDA13h, hotová recipročná tabuľka|

Na poslednom bode je DS=SS=2F95h, ale ES=A400h. Pred VGA vstupom je ES=F000h po medziľahlej časovačovej inicializácii. Žiadny invariant DS=ES zo skorého CRT sa nemá prenášať na tieto body. Surové registre sú v snapshots.json.

## BSF a file checksum

Vstupný stack pri BSF obsahuje mode0. Stack pri pôvodnom XOR presne deklaruje offset3638h, segment2F95h a count54. Encoded runtime hlavička je byte-for-byte rovnaká ako prvých54 B skutočného NITE3D.BSF. Celý decoded runtime výsledok sa zhoduje s nezávislým XOR modelom a predtým auditovaným52 B kľúčom; pôvodný AL checksum je0.

Následná file-check rutina dostane near filename1663h, obsah n3d.exe, countDWORD0 a dolný BYTE expectedECh. Pôvodné open/fread/close a DOS file I/O sa vykonajú bez stubov. Caller00DF je dosiahnutý a finálna hlavička ostáva totožná. BYTE+3 je1; podľa statickej vetvy je dodatočná map.1 kontrola pri tejto hodnote preskočená. Nie je to samostatná úplná trace všetkých možných file-check volaní alebo všetkých BSF variantov.

Pozorovaný n3d.exe končí nulou. Úspešná kontrola tohto súboru preto sama nerozlíši predtým nájdené opätovné XORovanie posledného lokálneho BYTE poEOF pri nenulovom poslednom BYTE. Hraničná fread/EOF hypotéza pre iné dáta nie je týmto normálnym behom uzavretá.

## Audio inicializácia

Pri mode0 sú active BYTE17CD/17CE/17CF pred volaním0,0,0 a po návrate1,1,1. Konfiguračné bytes414A..4151 sú3C46010101000000. Hudba/SFX požiadavky sú nenulové, tretí desired flag414F je0, aj keď backend active17CF po mode0 je1; to zodpovedá rozdielu medzi desired a initialized state z predchádzajúceho statického/replay auditu. Nie je dôvod tieto polia zlúčiť do jedného booleanu.

Vykonali sa pôvodné WORX a herné volania, nie RETF modely. Výsledok dokazuje iba túto inicializačnú stavovú cestu v emulovanom zariadení. Nosound/SDL dummy nepreukazuje počuteľný výsledok, vzorkovanie, hudobný timing ani správnosť prehrávania každého efektu.

## VGA a511 recipročných DWORD

Pôvodný mode0 VGA wrapper vstupuje s argumentom0. BIOS Data Area mode BYTE0040:0049 je pred ním03h a po ňom13h. Runtime page WORD v DS:012C/012E súA000h/A400h. Samotné BDA označenie13h ani segmentové hodnoty nepreukazujú každý neskorší VGA register, clipping alebo obrazovú parity; driver môže BIOS režim následne upravovať.

Nadväzujúci fixed initializer0156:0000..002F, image[01560,0158F), má15 inštrukcií /47 B. Nezávislý disassembly a statický loop dokazujú tento algoritmus:

```c
for (uint32_t n=1, off=0x2656; off<0x2E52; ++n, off+=4)
    DS.u32[off] = 0x400000 / n;
```

Použije lokálny DWORD counter v SS, CDQ/IDIV s kladnými deliteľmi a priame DWORD zápisy cez DS. Zachová SI/BP; EAX/EDX a flags sú pracovné. FAR návrat zodpovedá PUSH CS/NEAR CALL0 v mode0 wrapperi. Všetkých511 skutočných runtime DWORD bolo byte-for-byte porovnaných s matematickým vzorcom floor(400000h/n), n1..511, bez odchýlky. Posledný quotient2010h a zvyšok10h zodpovedajú aj AX/DX na poslednom caller breakpoint bode.

Tabuľka zaberá DS:[2656,2E52),2044 B, image-relative[29D66,2A562). Je **mimo pôvodného file image** a mimo57 295 NON-CODE baseline. Katalóg runtime_bss_tables.csv ju vedie osobitne: nezvyšuje typed file bytes ani PASS1 coverage. Dôkaz presného obsahu tejto pevnej tabuľky nie je sémantická verifikácia celého rendereru alebo všetkých konzumentov. Lokálny stav zostáva PARTIAL, žiadne percento sa z511 hodnôt neodvodzuje.

## Reprodukcia, chyby harnessu a nezávislé overenie

runtime_dosbox_startup.py DOSBOX_EXE GAME_DIR IMAGE RELOCATIONS OUT WORK **initialization**, potom verify_dosbox_startup_capture.py IMAGE RELOCATIONS OUT WORK. Ďalej audit_runtime_reciprocal_init.py IMAGE INVENTORY DECODER RUNTIME_OUT WORK OUT vytvorí nezávislé ASM, runtime_values.csv pre každé n a externý BSS katalóg. Iced-x861.21.0, originálny DOSBox-X runtime; Unicorn sa v tomto scenári nevykonáva.

Verifier kontroluje37 raw MEMDUMPBIN úsekov, všetky predchádzajúce body aj BSF/header/call stack, audio stavy, video BDA/pages a celú2044 B tabuľku. Hashy každého capture sú v independent_verification.json a central catalog ich pri importe znovu prepočíta. Binárne pamäťové dumpy ostávajú lokálne vo work adresári; textové metadáta ich identifikujú.

Prvý pokus tejto dávky nebol započítaný: textový debugger tokenDF interpretoval ako Direction Flag namiesto adresyDFh, a nastavil breakpoint na0000h. Transcript ukazuje presnú chybu, nejde o game fail. Aktuálny skript používa segmenty a offsety s vedúcimi nulami, napr.0C9A:000000DF, a nový overený pokus dosiahol správny caller. Proces sa na konci úmyselne ukončuje harnessom; exit1 nie je prirodzený herný návrat.

'''
text+=f"SHA summary `{v['summary_sha256']}`. Harness SHA `{s['harness_sha256']}`. BSF decoded SHA `{s['checks']['bsf_decoded_header_sha256']}`. Reciprocal SHA `{s['checks']['vga_reciprocal_sha256']}`.\n\n"
text+='''## Meranie

PASS1 ostáva **57 102 B PARTIAL,149 B CLASSIFIED ONLY,44 B UNKNOWN,0 B DEEP VERIFIED**. Zachované originálne runtime scenáre **2→3**: startup/B3, main/defaults a tento BSF/audio/VGA init. Jednotkou je overená session/scenár, nie počet breakpointov alebo znovu načítaných bajtov. Pribúda jeden static bounded funkčný rozsah15inštrukcií/47B a samostatný2044 B runtime BSS katalóg, bez novej file-byte promócie. Controlled Unicorn count sa nemení.

Táto nová lokálna dávka nie je súčasťou publikovanej analytickej snímky ba27379dd28c9a689d15233b0fd7017867f50114. PE32 sa nevytvára.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Úplné menovatele chýbajú, preto N/A. Iniciačný runtime nie je percento gameplay completeness.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|skutočný BSF54 B load/decode|iné BSF/role blokov|resource sloty v runtime|
| Dátové typy a konštanty |95 %|N/A|511 runtime DWORD mimo file|149 B iba klasifikované|writer watchpointy|
| Tabuľky a ukazovatele |93 %|N/A|FAR XOR buffer/pages runtime|všetci konzumenti|reciprocal calleri|
| Funkcie / ASM / CFG |90 %|N/A|15inštrukcií fixed init a init cesta|zvyšok main|post-VGA init|
| RNG |97 %|N/A|bez RNG runtime|prvý srand/rand|RNG caller trace|
| Scheduler |96 %|N/A|clock init prebehol medzi bodmi|main loop/scheduler|loop vstup|
| DEMO a vstupy |96 %|N/A|bez input/demo runtime|driver a demo|prirodzené demo|
| Renderer / VGA |94 %|N/A|mode03→13 a reciprocal511 zhoda|render/frame/clipping|prvý frame a renderer call|
| GUARD / bossovia |93 %|N/A|bez AI runtime|map init|selector doména|
| Zbrane / projektily |92 %|N/A|bez damage runtime|effect callery|damage trace|
| Sprity / HUD / paleta |92 %|N/A|VGA init, nie vizuálna parita|paleta/sprity|resource load|
| SAVE / LOAD |92 %|N/A|BSF native file-check vrátený|SAVE/LOAD a chybové I/O|diskové scenáre|
| Windows Win16 |92 %|N/A|bez Win runtime|NE prostredie|samostatný Win16 test|

## Runtime testy na vykonanie

Pokračovať za0476:011B cez resource/input inicializáciu k prvému scheduler/frame/RNG bodu. Samostatne merať paletu a video registre; headless BDA13h nie je obrazové porovnanie. Pre audio treba vlastnú capture/sample/timing skúšku. BSF alternatívne flagy a EOF s nenulovým posledným BYTE vyžadujú oddelené scenáre. Všetky nové zistenia odlišovať od pôvodnej dosiaľ neuzavretej Win16 a gameplay parity.
'''
(r/'DOSBOX_INITIALIZATION_RUNTIME_REPORT.md').write_text(text,encoding='utf-8')
