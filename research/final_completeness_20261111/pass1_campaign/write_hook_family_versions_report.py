# -*- coding: utf-8 -*-
"""python write_hook_family_versions_report.py OUTPUTS"""
import csv,json,sys
from pathlib import Path
r=Path(sys.argv[1]);out=r/'hook_family_versions';s=json.loads((out/'summary.json').read_text());vs=list(csv.DictReader((out/'versions.csv').open()));slotrows=list(csv.DictReader((out/'slots.csv').open()));old=(r/'DOSBOX_INPUT_INIT_RUNTIME_REPORT.md').read_text(encoding='utf-8');table=old[old.index('## Aktualizácia 13 oblastí'):old.index('## Runtime testy na vykonanie')]
table=table.replace('|14 prirodzených FAR resource pointerov,6B hlavičky0|plný resource lifetime a obsah|resource slot consumers|','|7-slot CRT rodina v8 DOS verziách; piaty slot otvorený|vypočítané aliasy/writeri DS2356|runtime hook watch|')
table=table.replace('|bez Win runtime|NE prostredie|samostatný Win16 test|','|DOS8štítkov/7obrazov krížovo overených; Win bez zmeny|WinNE prostredie a algoritmické mapovanie|Win hook rodina|')
lines=[]
for v in vs:
 slot=next(x for x in slotrows if x['version']==v['version'] and x['slot_index']=='4')
 lines.append('|%s|%04X:%04X|%04Xh|%04Xh|%s|%s|'%(v['version'],int(v['ds_segment']),int(v['hook_run_ds']),int(slot['ds_offset']),int(v['target_ip']),v['direct_DS_refs'],slot['raw_WORD_hits_whole_image']))
text='''# PASS1: neuzavretý CRT hook naprieč DOS verziami

Nová dávka rozširuje ohraničený negatívny dôkaz pre slot **DOS20 DS2356**, image `[29A66,29A6A)`. Predošlý audit overoval priame memory displacements iba v DOS20 inventári. Teraz sa hook rodina identifikuje nezávisle v každom z8 DOS štítkov (7 unikátnych obrazov) podľa7 rovnakých FAR inicializérov smerujúcich do vlastného CRT segmentu a cieľového stubu MOVAX2/JMP.

## Výsledok porovnania

|DOS|DS:začiatok rodiny|Piaty slot DS offset|Stub IP v CRT|Priame DS referencie rodiny|Raw WORD výskyty offsetu piateho slotu|
|---|---|---:|---:|---:|---:|
'''+ '\n'.join(lines)+'''

V každej verzii má rodina6 explicitných neindexovaných DS referencií, po jednej na sloty0,1,2,3,5,6. **Slot index4 (piaty) nemá žiadnu**. V rozsahu displacementov rodiny sa nenašli ďalšie indexované alebo inosegmentové kandidáty v dodaných inventároch. Toto nevylučuje register pointer odvodený inde, implicitný prístup, prepísaný pointer alebo kód mimo inventára.

V DOS20 je pri úplnom raw prehľadaní celého171360B obrazu počet dvojice bajtov **56 23 nulový**. Tento silnejší, od inštrukčných hraníc nezávislý výsledok vylučuje iba explicitne zakódovanú WORD hodnotu2356h v tomto obraze, nie vypočítanú adresu/alias. Rovnako sa v historickej code doméne nenachádza dvojica58 23 pre segmentový WORD2358h; tento doplnkový prieskum nie je základom promócie.

Dve raw zhody v iných verziách sa rozlíšili cez presné hranice inštrukcií. DOS11 offset2348h vzniká na image2409h cez `48` (DECAX) + `23` (začiatok ANDAX,DX), teda naprieč dvoma inštrukciami. DOS17 offset231Ah sa vyskytuje na image85F5h v `26 C6 44 1A 23`, t. j. spojením displacement1Ah a immediate23h pri BYTE store ES:[SI+1A]. Nejde o WORD address operand231Ah. Výstup `slot4_raw_hit_context.csv` uchováva obidva prípady a ich pôvodné instruction bytes.

## Čo zostáva neuzavreté

Sedem slotov má vždy spoločný cieľ MOVAX2 a tail JMP do CRT error cesty. Počiatočný vzhľad a stabilita nepodporujú automatické typové povýšenie siedmeho slotu podľa susednosti. DOS20 segmentový WORD `[29A68,29A6A)` preto zostáva2PARTIAL bajtmi bez uzavretej typovej roly; ďalšie2B offset WORD stále nie sú týmto auditom typovo uzavreté. Dosiahnuteľnosť a runtime modifikácie slotu sa nevylúčili. Neoznačuje sa ako unused, dead, padding ani DEEP VERIFIED.

Presné autorstvo runtime knižnice/kompilátora sa týmto neidentifikuje. Cross-version rodina je štrukturálny a byte dôkaz, nie úplná CFG/behavior parita DOS ani Win16. Metadata DS/CRT a už rozbalené obrazy sú hashované; pôvodný unpack sa v tejto dávke neopakoval pre všetky verzie.

## Reprodukcia a artefakty

`audit_hook_family_versions.py VERSION_CSV ABS_DECODER OUT` používa manifest `crt_entry_gap_versions/versions.csv`, kontroluje image SHA a metadata, hľadá jedinú7-slot rodinu so správnym target stubom, nezávisle overí všetky inštrukčné bajty a dekódovanie inventárov. Potom enumeruje explicitné memory operand kandidáty aj všetky raw WORD zhody pre každý slot. Výstupy `versions.csv`, `slots.csv`(56riadkov), `reference_candidates.csv`, `slot4_raw_hit_context.csv` a summary pripínajú dôkazy. `write_hook_family_versions_report.py OUTPUTS` generuje správu a aktualizáciu13oblastí.

'''+f"Overených inštrukčných začiatkov naprieč8 štítkami: **{s['verified_instruction_starts']}**; duplicitné18/19 nie sú dva nezávislé obrazy. Manifest SHA `{s['manifest_sha256']}`.\n\n"+'''## Meranie

Žiadne nové promócie, funkčné rozsahy, replay ani runtime session. Aktuálne57102PARTIAL/149CLASSIFIED ONLY/44UNKNOWN/0DEEP VERIFIED,122funkčných rozsahov a5prirodzených DOSBox scenárov zostávajú. Nové sémantické percentá N/A bez úplných menovateľov. Dávka je lokálna, nie nová GitHub publikácia.

'''+table+'''## Runtime testy na vykonanie

Zachytiť všetkých7 relokovaných slotov pred/po floating-support inicializácii a sledovať prípadné writeri alebo vykonanie spoločného02C0 cieľa. Použiť memory-change breakpointy len po overení ich dostupnosti v konkrétnom heavy-debug builde; neprítomnosť zmeny nie je dôkaz neprítomnosti čítania. Hľadať register-derived prístupy aj mimo pôvodného inventára, samostatne mapovať ekvivalentWin16. Pokračovať paralelne v prirodzenej inicializačnej ceste za0476:015C.
'''
(r/'HOOK_FAMILY_CROSS_VERSION_REPORT.md').write_text(text,encoding='utf-8');print(json.dumps(dict(report='HOOK_FAMILY_CROSS_VERSION_REPORT.md',versions=len(vs),status_changes=0)))
