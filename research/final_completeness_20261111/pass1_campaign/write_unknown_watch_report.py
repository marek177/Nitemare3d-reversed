# -*- coding: utf-8 -*-
"""python write_unknown_watch_report.py OUTPUTS"""
import csv,hashlib,json,sys
from pathlib import Path
r=Path(sys.argv[1]);out=r/'dosbox_unknown_watch_runtime_v3';p=json.loads((out/'independent_verification.json').read_text());s=json.loads((out/'summary.json').read_text());assert p['verified'];sha=lambda b:hashlib.sha256(b).hexdigest()
for item in p['files']:assert sha(Path(item['path']).read_bytes())==item['sha256']
old=(r/'WIN110_PALETTE_CONSUMER_REPORT.md').read_text(encoding='utf-8');table=old[old.index('## Aktualizácia 13 oblastí'):old.index('## Runtime testy na vykonanie')]
table=table.replace('|511 runtime DWORD mimo file|149 B iba klasifikované, 44 B UNKNOWN|nepriame segmentové prístupy|','|44 UNKNOWN adries sledovaných v skutočnom DOSBox behu; bez udalosti zmeny|čítanie, rovnaké zápisy a herný loop|read/write stopa za init|')
table=table.replace('|7-slot CRT rodina v8 DOS verziách; piaty slot otvorený|vypočítané aliasy/writeri DS2356|runtime hook watch|','|hook DS2356 má rovnaký relokovaný obsah v oboch endpoint dumpoch|medzistavy a nepriame čítanie|bezpečná kalibrácia nenulového watch|')
initial={int(k):v for k,v in s['initial'].items()};final={int(k):v for k,v in s['final'].items()};load=s['load_segment'];rows=[]
for a,n in [(0x1bda2,14),(0x1c070,16),(0x1d0ec,4),(0x20b88,8),(0x2770e,2)]:
 raw=bytes(initial[load*16+a+j] for j in range(n));rows.append(dict(image_start=a,image_end_exclusive=a+n,length=n,physical_start=load*16+a,initial_hex=raw.hex(),final_hex=bytes(final[load*16+a+j] for j in range(n)).hex(),value_change_events=0,status='UNKNOWN',scope='memory-change breakpoint only, CRT0018 through main017C'))
with (out/'unknown_interval_observations.csv').open('w',encoding='utf-8',newline='') as f:writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
text='''# PASS1: prirodzené sledovanie 44 UNKNOWN bajtov

Nová ôsma zachovaná DOSBox-X session sledovala presnú množinu **44 historických UNKNOWN bajtov**. Od rozbaleného CRT vstupu **11EE:0018** po návrat paletového loadera **0476:017C** sa nezaznamenala žiadna udalosť zmeny ich hodnoty. Toto je ohraničený negatívny runtime dôkaz, nie uzavretie dátového typu alebo dôkaz nepoužívania.

## Presná množina

|Image interval, end exclusive|B|Výsledok|
|---|---:|---|
|[1BDA2,1BDB0)|14|initial/final nula, cached-value udalostí0|
|[1C070,1C080)|16|initial/final nula, cached-value udalostí0|
|[1D0EC,1D0F0)|4|initial/final nula, cached-value udalostí0|
|[20B88,20B90)|8|initial/final nula, cached-value udalostí0|
|[2770E,27710)|2|initial/final nula, cached-value udalostí0|

Posledný súvislý2B rozsah tvorí v autoritatívnej mape dva riadky, preto ide o5 súvislých oblastí, ale6 historických intervalov. Verifier porovnáva množinu všetkých44 adries priamo s aktuálnym CSV, nie iba súčet dĺžok. Každý BYTE má vlastný BPLM breakpoint na skutočnej linear adrese `0824h*16 + image_offset`. Presné fyzické adresy a obsah sú v `unknown_interval_observations.csv`.

## Overená schopnosť debuggera a jej limity

Samostatný `probe_dosbox_debug_capabilities.py` pri zastavenom packed entry potvrdil v konkrétnej binárke podporu HELP/BPM/LOG a prijatie memory breakpointu v BPLIST. Pred a po query boli registre zhodné; probe nevykonal RUN a nepridáva sa medzi herné runtime scenáre. EXE debuggera má SHA rovnaký ako predchádzajúce session.

BPLM v tejto implementácii porovnáva uloženú BYTE hodnotu s aktuálnou pamäťou pri debug kontrolných bodoch. **Nesleduje read prístupy ani zápisy rovnakej hodnoty.** Nezachytí nevyhnutne zmenu a obnovu medzi dvoma kontrolami, napríklad vnútri hostiteľského DOS/BIOS callbacku. REP, interrupt a callback hranice sa nesmú rozšíriť na všeobecnú inštrukčnú read/write stopu. Nulový počet udalostí preto neoprávňuje označiť región ako padding, unused alebo DEEP VERIFIED.

## Problém nenulovej watch baseline

Prvý pokus zastavil verifier ešte pred monitored RUN: cache pri vytvorení breakpointov obsahovala0 aj pre nenulový hook DS2356. Druhý pokus tieto prechody identifikoval ako kalibráciu cache, nie game writes; zastavoval pri DOS/BIOS callbacke a spojenie sa potom uzavrelo. Oba neúspešné captures sú zachované v `dosbox_unknown_watch_runtime/` a `_v2/`, majú runtime_tests0 a nie sú importované ako úspešné scenáre.

Tretí pokus používa breakpointy iba na44 nulových bajtoch. Initial dump aj každý initial cached BYTE sú0, takže baseline je overene rovnaká. Hook **[29A66,29A6A)** sa iba dumpuje pred a po: oba dumpy obsahujú relokovaný **1A12:02C0**, bajtyC002121A. **Intervening hook zmeny sa tým nevylučujú.** Hook teda zostáva otvorený a jeho2 relokačné PARTIAL bajty sa typovo nepovyšujú.

## Skutočný beh a nezávislá kontrola

Po packed EXE loaderi sa zachytí CRT vstup1A12:0018. Celých171360 runtime image bajtov sa porovná s kanonickým obrazom po1670 relokáciách. Následne sa vytvorí44 BPLM a cieľový code breakpoint0C9A:017C. Medzi spustením monitorovanej cesty a finálnym breakpointom sa watchpointy nemažú. Žiadne SR/SM/FM ani dosadené game registre, súbory alebo API odpovede.

Úvodný RUN debuggera vykonáva jednu inštrukciu pred aktiváciou watch objektov; na CRT vstupe je to MOV AH,30h, bez game-memory zápisu. Aj tak sa výsledok prezentuje iba ako pozorovanie konkrétneho debuggera, nie všeobecné vylúčenie všetkých zápisov. Po dosiahnutí main017C sú DS=SS2F95. Final dumpy sú rovnaké a cached hodnoty naďalej0. Hra sa neukončuje prirodzene: harness po capture ukončí svoj emulátor.

`verify_unknown_watch_capture.py` nezávisle overuje množinu adries, počiatočnú cache, každý BPLIST výpis, presne2 RUN (packed→CRT a CRT→main017C), životnosť breakpointov, nulový event zoznam,13 raw dumpov a originálne/copied vstupy. Žiadna zmena pôvodných22 súborov. Väzba na dosiahnutý endpoint nepreberá všetky medzistavy zo starších session; je to samostatný úspešný beh.

## Reprodukcia

1. `probe_dosbox_debug_capabilities.py DOSBOX_EXE GAME_EXE OUT WORK` overí schopnosti buildu.
2. `runtime_watch_unknown.py DOSBOX_EXE GAME_DIR IMAGE RELOCS OUT WORK` spustí nový watch capture. Používa archivovaný helper `dosbox_watch_support_v1.py`; nemusí preberať budúce zmeny všeobecného harnessu.
3. `verify_unknown_watch_capture.py IMAGE RELOCS CURRENT_MAP OUT WORK` vytvorí nezávislý proof.
4. `write_unknown_watch_report.py OUTPUTS` generuje intervalový ledger a správu.

Summary, transcript, snapshots, watch_events, inputs a config sú v `dosbox_unknown_watch_runtime_v3/`; raw dumpy v `work/dosboxx_unknown_watch_runtime_v3/`. Každý dôkazový súbor je hashovaný v independent_verification.json. Neúspešné pokusy sa pri reprodukcii nesmú prepísať úspešným stavom.

'''+f"Úspešný summary SHA `{p['summary_sha256']}`. Proof SHA `{sha((out/'independent_verification.json').read_bytes())}`.\n\n"+'''## Meranie

Prirodzené úspešné scenáre7→8. Capability probe0 a dva neúspešné pokusy0 sa nepripočítavajú. DOS katalóg125 rozsahov a samostatný Win paletový doplnok4 rozsahy sa nemenia; žiadny nový seeded replay. PASS1 ostáva **57102 B PARTIAL /149 B CLASSIFIED ONLY /44 B UNKNOWN /0 B DEEP VERIFIED**. Toto meranie nezakladá nové sémantické percento. Dávka je lokálna, zatiaľ nepublikovaná.

'''+table+'''## Runtime testy na vykonanie

Rozšíriť watch okno cez resource a map init do prvého frame, pričom treba zachovať presnú baseline a odlíšiť debugger cache od pamäťových udalostí. Na uzavretie čítania a same-value writes treba skutočnú read/write inštrukčnú stopu alebo nižšiu instrumentáciu. Nenulový hook vyžaduje bezpečnú kalibráciu a overenie správania pri zastavení v host callbackoch. Nezmenené nuly stále nie sú dôkaz paddingu.
'''
(r/'UNKNOWN_BYTES_RUNTIME_WATCH_REPORT.md').write_text(text,encoding='utf-8');print(json.dumps(dict(report='UNKNOWN_BYTES_RUNTIME_WATCH_REPORT.md',watched_unknown_bytes=44,value_change_events=0,runtime_tests=8,status_changes=0)))
