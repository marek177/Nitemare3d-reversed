# -*- coding: utf-8 -*-
"""python write_remaining_segment_report.py OUTPUTS"""
import json,sys
from pathlib import Path
r=Path(sys.argv[1]);s=json.loads((r/'remaining_noncode_current/summary.json').read_text());a=json.loads((r/'remaining_segment_aliases/summary.json').read_text())
previous=(r/'DOSBOX_INITIALIZATION_RUNTIME_REPORT.md').read_text(encoding='utf-8');table=previous[previous.index('## Aktualizácia 13 oblastí'):previous.index('## Runtime testy na vykonanie')]
table=table.replace('Nové potvrdenie','Aktuálny dôkaz (staršie riadky zachované)')
table=table.replace('|149 B iba klasifikované|writer watchpointy|','|149 B iba klasifikované, 44 B UNKNOWN|nepriame segmentové prístupy|')
table=table.replace('|FAR XOR buffer/pages runtime|všetci konzumenti|reciprocal calleri|','|12 lokálnych FAR konštrukcií 21FD:264E odlíšených od DS:264E|aliasy/dynamické indexy|watchpointy na 44 UNKNOWN B|')
text=f'''# PASS1: aktuálny zvyšok a rozlíšenie segmentových aliasov

Nový scan aktuálnej mapy `{s['map_sha256']}` kontroluje všetkých {s['verified_inventory_starts']} dodaných začiatkov inštrukcií proti skutočným bajtom a nezávislému dekóderu. Zvyšok mimo PARTIAL je **63 intervalov / 193 B**: 149 B CLASSIFIED ONLY a 44 B UNKNOWN. Z toho 140 B má nulový obsah. Nuly nie sú dôkaz paddingu. Presná CSV/JSON mapa zvyšku je `remaining_noncode_current/interval_ledger.csv/json`.

Toto nahrádza aktuálne použitie starého inventára `remaining_noncode/`, ktorý skúmal skoršiu mapu s 2309 B. Staré výsledky zostávajú historickým dôkazom. Zníženie zvyšku vzniklo predchádzajúcimi dávkami; táto dávka nepromuje žiadny bajt.

## Výsledok kandidátskych referencií

Scan našiel 13 vzťahov: 12 WORD immediate hodnôt 264Eh a jeden indexovaný operand `[BX+2486h]`. Priame DS operandy a priame control targety do aktuálneho zvyšku nenašiel. To neuzatvára dynamické pointery, implicitné/REP operandy, ES/SS aliasy, chýbajúci kód ani prirodzenú dosiahnuteľnosť.

Všetkých 12 immediate kandidátov má byte-exact lokálny dôkaz konštrukcie adresy **21FD:264E**, obraz **2461Eh**, namiesto naivne predpokladanej **2771:264E**, obraz **29D5Eh**. Na 374Dh/3A45h ide o stack FAR argumenty write/read wrapperov s dĺžkou A28h (2600 B). Ďalšie miesta 554Fh,5F2Ch,618Bh,61DEh,6263h,69A7h,93B8h,94C3h,999Ah,A9DCh explicitne vytvárajú segment a offset v registroch/lokáloch. Sú to image adresy inštrukcií, nie IP. Dôkazy aj dekódované witness rozsahy sú v `remaining_segment_aliases/resolved_candidates.csv` a `witness_instructions.csv`.

Rozlíšenie sa vzťahuje na uvedené lokálne sekvencie. Nepotvrdzuje všetky vstupné CFG cesty alebo indexové hranice. Posledné dva FF bajty `[29D5E,29D60)` preto zostávajú CLASSIFIED ONLY. Starší runtime-message lookup pri dosadenom dopyte FFFFh stále môže vrátiť ich adresu; táto nezávislá hraničná cesta sa tým neruší.

Jediný indexovaný kandidát je 11EE:2DD0, image14CB0h, `MOV DI,[BX+2486h]`. Predchádza mu zdvojenie WORD month argumentu v BX. Pri nominálnom month1..12 načíta nasledujúcu common-year tabuľku; samotný base displacement zasahujúci koniec leap-year vzoru nedokazuje použitie všetkých 26 B `[29B7E,29B98)`. Dôkaz prirodzených month domén zostáva otvorený; žiadna nová promócia.

## Metodika a reprodukcia

1. `audit_remaining_noncode.py IMAGE CURRENT_MAP INVENTORY ABS_DECODER_DIR OUT_REMAINING` overí obraz, všetky intervalové SHA, inštrukčné bajty a kandidátske operandy.
2. `audit_remaining_segment_aliases.py IMAGE INVENTORY OUT_REMAINING/reference_candidates.csv ABS_DECODER_DIR OUT_ALIASES` kontroluje presnú množinu 12 kandidátov, explicitné byte witnesses, hranice v inventári a nezávislé dekódovanie.
3. `write_remaining_segment_report.py OUTPUTS`, potom `render_campaign_status.py OUTPUTS` aktualizujú správu a tabuľku 13 oblastí.

SHA kandidátskeho CSV: `{a['candidate_csv_sha256']}`. Pôvodné EXE ani mapa sa nemenili. **57 102 B PARTIAL /149 B CLASSIFIED ONLY /44 B UNKNOWN /0 B DEEP VERIFIED**. Funkčný katalóg zostáva 115 rozsahov; tri uchované runtime scenáre a replay počty sa nemenia. Táto dávka je lokálna, nie nová GitHub publikácia. Nové percentá sa nevypočítavajú bez úplných menovateľov.

'''+table+'''## Runtime testy na vykonanie

Sledovať päť súvislých UNKNOWN oblastí [1BDA2,1BDB0),[1C070,1C080),[1D0EC,1D0F0),[20B88,20B90),[2770E,27710) pri skutočnom štarte, načítaní mapy a prvom frame. Samotná nezmena dumpu nedokáže neprítomnosť dočasného zápisu ani čítania; na tento účel treba read/write stopu alebo watchpointy so zachyteným CS:IP a segmentmi. Rozlíšiť nominálny index calendar lookup od neplatných month hodnôt. Pokračovať za posledným VGA breakpointom podľa predchádzajúceho runtime reportu.
'''
(r/'REMAINING_SEGMENT_ALIASES_REPORT.md').write_text(text,encoding='utf-8')
print(json.dumps(dict(report='REMAINING_SEGMENT_ALIASES_REPORT.md',status_changes=0,resolved_local_candidates=12)))
