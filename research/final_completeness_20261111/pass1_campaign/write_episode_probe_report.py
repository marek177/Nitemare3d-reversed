# -*- coding: utf-8 -*-
"""python write_episode_probe_report.py OUTPUTS"""
import json,sys
from pathlib import Path
r=Path(sys.argv[1]);s=json.loads((r/'episode_available_probe/summary.json').read_text());old=(r/'HOOK_FAMILY_CROSS_VERSION_REPORT.md').read_text(encoding='utf-8');table=old[old.index('## Aktualizácia 13 oblastí'):old.index('## Runtime testy na vykonanie')]
table=table.replace('|skutočný BSF54 B load/decode|iné BSF/role blokov|resource sloty v runtime|','|episode1..6 scan a výsledok7;256 modelovaných prípadov|skutočné access výsledky|prirodzený episode probe|')
table=table.replace('|4 nové API/probe wrappers,88B/37inštrukcií|INT86 a ISR telá|ISR interrupt kontrakt|','|nový episode probe75B/31inštrukcií|caller výsledku7 a externé telá|0476:0169/016F runtime|')
text='''# Výber prvej dostupnej epizódy pred načítaním herných dát

Nová ohraničená funkcia **0D29:2696..26E1**, image **[F926,F971)**, má **75B/31inštrukcií**. Priamy init caller je0476:0169; vrátenéAX sa na016E vloží na zásobník a odovzdá0277:0336, ktorý ho ukladá do epizódového globáluDS626A a formátuje názvy dát. Funkcia nie je RNG seed rutinou. Doteraz staticky známy reset RNG cez0FBA:01A6 sa nachádza neskôr na0D29:271C; jeho prirodzená udalosť a poradie RNG spotreby zostávajú otvorené.

## Dátové väzby a algoritmus

File reťazce **DS2000 image[29710,29715)**=`map.\\0`, **DS2005 image[29715,2971A)**=`%s%d\\0`. Formátovací caller explicitne vloží current episode, prefix,format a near cieľ lokálneho16B buffera naSS:[BP-10h], potom voláCRT11EE:278C. Výsledný názov je pri nominálnych1..6 `map.1` až `map.6`. Tieto reťazce už majú PARTIAL dôkazy v predošlom type katalógu; táto dávka ich nepromuje ani nepripočítava znovu.

```c
uint16_t first_available_episode(void) {
    uint16_t episode = 1;
    do {
        format_local_filename("%s%d", "map.", episode);
        if (access_wrapper(local_filename, 4) == 0) {
            farptr registered = bsf_dispatch(1);
            if (registered != NULL || episode == 1)
                return episode;
        }
        ++episode;
    } while ((int16_t)episode <= 6);
    return 7;
}
```

Access návrat sa testuje výlučne proti0. Názov wrappera a argument4 sú presne doložené; táto dávka nepovyšuje celý DOS/filesystem access kontrakt na overený. BSFmode1 sa volá **iba po úspešnom access**. Jeho FAR výsledok sa testuje ORDX,AX, teda NULL iba pri oboch nulových WORD. Pri registrovanej dostupnosti sa vráti prvá prístupná epizóda1..6. Pri nulovom BSF výsledku je prijateľná iba epizóda1; existujúca epizóda2..6 sa aj tak preskočí.

Ak nič nevyhovuje, výsledok je **7**, pretožeSI sa zvýši po epizóde6 a funkcia vraciaSI bez dodatočnej normalizácie. Hodnota7 nie je touto funkciou potvrdená ako platná hrateľná epizóda; ďalší caller a jeho chybové vetvy musia byť posúdené osobitne. Nezamieňať s automatickým návratom1 pri chýbajúcich dátach.

## CFG, ABI a pamäť

ENTER10h,saveSI,SI1; jedna slučka s increment a signedJLE6, vetvy access/registered/episode1, jeden spoločný FAR return. Bez jump tabuľky. Volania FARCRT formatter278C,access3990 aBSF083D:29CA. Bez vlastných vstupných argumentov, výsledokAX, SI/BP/SP obnovené. Externé volania nemajú všeobecne uzavretý AX/BX/CX/DX/ES/flags zachovávací kontrakt.

Lokálny filename je vytvorený adresouSS buffera, ale odovzdáva sa ako near pointer. **DS=SS je potrebná caller podmienka** pre tieto near knižničné operácie, nie vlastnosť samotného ENTER. Predchádzajúce skutočné init body DS=SS potvrdili len v už zachytených bodoch; samotný vstup2696 ešte nebol prirodzene zachytený. Netvrdí sa všeobecná rovnosťDS=ES.

## Reprodukcia a meranie

`audit_replay_episode_probe.py IMAGE INVENTORY ABS_DECODER ABS_EMULATOR OUT` overuje kanonickýSHA, všetkých75B/31inštrukcií, oba presné reťazce a1670 relokácií pre dva load segmenty. Originálne telo sa vykonáva; modelované sú výslovne iba3 callee: formatter,access aBSFmode1. Formatter model kontroluje všetky4 argumenty a zapisuje názov do správneho lokálneho buffera; access kontroluje argument4 aj presné názvy; BSF kontroluje mode1 a vrátiNULL/alebo nenulový FAR pointer.

**256prípadov,0odchýlok** = 2load ×64 všetkých dostupnostných masiek6epizód ×2registrované stavy. Kontroluje sa presné poradie každého callu, argumenty, výsledok aj DS/SI/BP/SP. Exhaustívnosť sa týka len tejto boolovej modelovanej domény; nejde o úplný test filesystemu, formattera alebo BSF telies. `callee_events.csv` obsahuje call stopy, `cases.csv` vstupy/výsledky aASM je v `episode_available_probe.csv`.

'''+f"SHA cases `{s['cases_sha256']}`. Katalóg122→123rozsahov,+31inštrukcií/+75B. Seeded replay+256; prirodzené DOSBox scenáre ostávajú5. PASS1 stále57102PARTIAL/149CLASSIFIED ONLY/44UNKNOWN/0DEEP VERIFIED. Táto nová lokálna dávka nie je súčasťou práve publikovaného analytického commitu2ced761cb0bf1eece24a224e92c05636058ab0ae.\n\n"+table+'''## Runtime testy na vykonanie

Pokračovať z0476:015C na0D29:2696 a prvý access call. ZachytiťDS/SS, pôvodný lokálny filename, návrataccess a BSFmode1pointer, potom návratAX a odovzdanie0277:0336. Pri dostupných pôvodnýchmap.1..3 nepredpokladať výsledok bez capture. V oddelených kópiách dát preveriť chýbajúceepizódy a caller výsledku7. RNG reset sledovať neskôr na0D29:271C; nevysvetľovať ho časovým seedom bez dôkazu.
'''
(r/'EPISODE_AVAILABLE_PROBE_REPORT.md').write_text(text,encoding='utf-8');print(json.dumps(dict(report='EPISODE_AVAILABLE_PROBE_REPORT.md',cases=s['cases'])))
