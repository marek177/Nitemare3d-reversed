import json
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'pass1_backslash_strings';s=json.loads((d/'summary.json').read_text());p=json.loads((d/'independent_partition_check.json').read_text())
text='''# PASS1: CRT backslash konštanty a near string rutiny

Štyri nové bajty PARTIAL: image [29884,29886), DS:2174 a [29886,29888), DS:2176. Obe polia obsahujú 5C 00, teda samostatný NUL-ukončený reťazec so spätným lomítkom. Nie sú to konce riadkov. Rozdielne pointer hodnoty sa zachovávajú ako dve polia, aj keď sú bajtovo rovnaké.

## Konzument a otvorený kontext

11EE:0658 načíta 2174h a odovzdá ho ako zdroj do FAR 2366 spolu s lokálnou destináciou BP-0Ch. Nasleduje test prvého BYTE destinácie proti 5Ch; pri nerovnosti ďalšia vetva 0674 odovzdáva 2176h ako zdroj do FAR 2326. Po tom nasleduje volanie 246E s radixom 10 a lokálnym pointerom a následný 3D0A. Tieto pozorovania podporujú skladanie pomocného názvu; kompletná identita, účel a životnosť názvu v tejto dávke nie sú uzavreté. Caller používa near adresy stack lokálov, preto pre prirodzenú správnosť treba doložiť vzťah SS=DS; samostatné helper testy to nedokazujú. Celý caller nebol emulovaný.

## Funkcie a ABI

| Rutina | CS:IP | Image interval, koniec exkluzívny | Inštrukcie / bajty |
|---|---|---|---:|
|near strcat|11EE:2326|[14206,14245)|30 / 63|
|near strcpy|11EE:2366|[14246,14278)|26 / 50|

Obe majú FAR vstup a RETF, near offset destinácie v [SS:BP+6], zdroja v +8. AX vracia pôvodný offset destinácie. SI/DI sa ukladajú do BX/DX a obnovia, BP sa obnoví zo stacku. ES nastavujú na DS a ponechajú ho tak, DS nemenia; BX/CX/DX/flags nie sú zachované. SS môže byť odlišný od DS, ale argumenty ukazujú do DS. CLD chýba: testovaný kontrakt je DF=0.

```c
nearptr strcpy_near(nearptr dst, nearptr src) {
    ES = DS;
    n = nul_scan(src) + 1;
    copy_bytes_with_word_fast_path(dst, src, n);
    return dst;
}
nearptr strcat_near(nearptr dst, nearptr src) {
    ES = DS;
    end = dst + nul_scan(dst);
    n = nul_scan(src) + 1;
    copy_bytes_with_word_fast_path(end, src, n);
    return dst;
}
```

SCASB začína s CX=FFFFh. Strcpy pred WORD cestou testuje paritu destinácie, strcat paritu zdroja. Pri nepárnej parite skopíruje úvodný BYTE a zníži počet; po REP MOVSW použije ADC CX,CX a prípadný MOVSB pre zvyšok. Toto nie sú bounded string rutiny. Správanie pri chýbajúcom terminátore, segmentovom wrape, prekrývaní a DF=1 zostáva mimo testovaného kontraktu. Jeden bajt medzi funkciami sa automaticky neklasifikuje ako padding.

## Reprodukcia a výsledky

2 400 prípadov = 2 load bázy × 2 funkcie × 2 source parity × 2 destination parity × 10 dĺžok zdroja × 5 pôvodných dĺžok destinácie × 3 nenulové byte vzory. Dĺžky zdroja 0,1,2,3,7,8,15,16,31,64; destinácia 0,1,2,15,31. Vzory ASCII, FF a meniace sa hodnoty 1..255. Overuje sa celý 256 B cieľ vrátane pôvodného chvosta a guard pred destináciou, AX, ES/DS a obnovenie SP/BP/SI/DI. Bez modelovaných callee a bez OS. Nulové odchýlky.

Reprodukcia: audit_replay_pass1_backslash_strings.py IMAGE INVENTORY DECODER EMULATOR OUT; promote_pass1_fields.py s predchádzajúcou mapou pass1_stream_cache; verify_pass1_partition.py. Kanonický image SHA-256 e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297. Exporty obsahujú polia, caller kontext, nezávislé ASM a cases.csv. Iced-x86 1.21.0 / Unicorn 2.1.4.

## Meranie

**57 041 B PARTIAL, 210 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57 295 B. Nezávislá kontrola 869 intervalov overila hash hodnoty, presné členstvo a nulové diery/prekryvy. Integrita nie je dôkaz úplnej sémantiky. Prirodzené DOSBox-X testy zostávajú 0. Nové lokálne dôkazy zatiaľ nie sú v poslednej publikovanej GitHub snímke.

'''
text+=f"SHA mapy `{p['map_sha256']}`; SHA cases `{s['cases_sha256']}`.\n\n"
text+='''## Aktualizácia 13 oblastí

Metodika nového %: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, preto N/A. Historické orientačné percentá sa nemenia z test count ani byte integrity.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|bez nového dôkazu|loader hranice|map closure|
| Dátové typy a konštanty |95 %|N/A|4 B / 2 backslash stringy|210 B iba klasifikované|zvyšné nepriame odkazy|
| Tabuľky a ukazovatele |93 %|N/A|near source pointer použitie|SS/DS kontext callera|startup segment invariant|
| Funkcie / ASM / CFG |90 %|N/A|2 funkcie, 113 B / 56 inštrukcií|celý caller|0658 kontext closure|
| RNG |97 %|N/A|bez nového dôkazu|prirodzené poradie|DEMO trace|
| Scheduler |96 %|N/A|bez nového dôkazu|prirodzené callery|call graph|
| DEMO a vstupy |96 %|N/A|bez nového dôkazu|driver ABI|input closure|
| Renderer / VGA |94 %|N/A|bez nového dôkazu|setup|VGA init CFG|
| GUARD / bossovia |93 %|N/A|bez nového dôkazu|selector doména|descriptor flag 8|
| Zbrane / projektily |92 %|N/A|bez nového dôkazu|damage callery|effect producer|
| Sprity / HUD / paleta |92 %|N/A|bez nového dôkazu|identity|descriptor producer|
| SAVE / LOAD |92 %|N/A|CRT string závislosti oddelené|prirodzené I/O|stream caller trace|
| Windows Win16 |92 %|N/A|bez nového Win dôkazu|CRT parita|nájsť ekvivalent|

## Runtime testy na vykonanie

V DOSBox-X zachytiť prirodzené near pointery a SS/DS/DF pri callerovi 0658, potom názov po 2366/2326/246E a jeho spotrebovanie pri 3D0A. Tým odlíšiť skutočne dosiahnuté vetvy od statického CFG. Win16 porovnať zachovanie segmentov a string ABI. PE32 portovanie sa nevykonáva.
'''
(r/'PASS1_BACKSLASH_STRINGS_REPORT.md').write_text(text,encoding='utf-8')
