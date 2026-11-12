import csv,json
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'pass1_literal_consumers';s=json.loads((d/'summary.json').read_text());p=json.loads((d/'independent_partition_check.json').read_text())
text='''# PASS1: skutoční konzumenti zostávajúcich reťazcov

85 B / 16 NUL-ukončených polí prechádza z CLASSIFIED ONLY na PARTIAL. Každý počiatočný pointer operand je overený voči kanonickému obrazu a následnému call kontextu; 247 kontextových riadkov obsahuje aj opakovania pri blízkych poliach. Žiadny bajt sa neoznačuje DEEP VERIFIED. Prirodzené DS kontexty a úplné telá CRT zostávajú otvorené.

| Image začiatok | Exkluzívny koniec | Obsah | Použitie | CS:IP odkaz |
|---|---|---|---|---|
'''
for f in csv.DictReader((d/'data_fields.csv').open(encoding='utf-8')):
    text+=f"|{int(f['start']):05X}|{int(f['end_exclusive']):05X}|`{f['text']}`|{f['type']}|{int(f['reference_cs']):04X}:{int(f['reference_ip']):04X}|\n"
text+='''
## Nové statické dôkazy

height, wall a object sú argumenty diagnostického wrappera 0FBA:000C; wall/object vyberá podmienka pred spoločným PUSH AX. Nejde o dokazovanie významu vykresľovaných objektov. Dve config.sav kópie vstupujú do lokálneho skladania cesty 0277:0C20, potom do CRT 11EE:1C72 s odlišnými flagmi. Režimy rb a uif.dat vstupujú do 11EE:06E6; wrapper staticky posunie argumenty a nulu do 06BA. Úplné fopen a I/O sa v tejto dávke nevykonávajú.

Päť trojbajtových formátov %i/%d ide do 11EE:27E4 s lokálnym výstupom a vstupným textom. Následné kontroly návratu a limitov sú zachované v consumer_contexts.csv, nejde o nové overenie celého parsera alebo jeho rozsahových chýb. Formát %d of %d ide do 278C s destináciou na stacku, %c do printf 07E0; char vstup sa rozširuje pomocou CBW. Tieto roly sú potvrdené call cestou, pôvodné CRT formátovanie sa nereplayovalo.

## Uzavretý lokálny rozsah skladania cesty

0277:0C20..0C6E, image [03390,033DE), 78 B / 39 inštrukcií. FAR vstup, near pointer argument [SS:BP+6], návrat AX=3466h. Uloží BP, DI a SI; ES nastaví na DS a tak ho ponechá. SS môže byť odlišný od DS. REPNE SCASB používa DF=0; funkcia sama CLD nevykoná. Oba zdroje aj destinácia sú v DS.

```c
// Platí pre neprekrývajúce sa NUL-ukončené vstupy a DF=0.
nearptr config_path_concat(nearptr suffix) {
    ES = DS;
    copy_including_nul(DS:3466, DS:3CDC);
    append_including_nul(DS:3466, DS:suffix);
    return 3466;
}
```

Prefix sa prekopíruje vrátane NUL pomocou MOVSW a prípadného MOVSB; druhé skenovanie hľadá koniec destinácie a NUL prepíše suffixom. Lokálna kontrola kapacity ani vkladanie oddeľovača chýba. Obe pracovné oblasti sú mimo počiatočných súborových dát (image 2AB76h a 2B3ECh), preto sa nedopĺňajú ako typované bajty pôvodného NON-CODE. Schopnosť callerov garantovať kapacitu, terminátor, neprekrývanie a DF zostáva otvorená.

28 pôvodných emulačných prípadov = 2 load bázy × 7 prefixov × 2 skutočné suffix pointery. Prefixy prázdny, cesta s oddeľovačom, text bez oddeľovača a dĺžky 31/127/255. Overený celý výsledok vrátane NUL a dvoch guard bajtov, AX, ES=DS, DS a obnovenie SP/BP/SI/DI. Bez stubov a bez OS volaní. 0 odchýlok. Nie je to dôkaz bezpečnosti ľubovoľne dlhých alebo prekrývajúcich sa vstupov.

## Reprodukcia a meranie

Spustiť audit_replay_pass1_literal_consumers.py IMAGE INVENTORY DECODER EMULATOR OUT, promote_pass1_fields.py IMAGE pass1_small_state/noncode_intervals.csv OUT/data_fields.csv OUT a verify_pass1_partition.py. Kanonický obraz má SHA-256 e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297. Skript overuje konkrétnu pointer hodnotu aj všetky použité inštrukčné bajty.

**57 015 B PARTIAL, 236 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57 295 B. Nezávislá kontrola 864 intervalov potvrdila hash hodnoty, presné členstvo a nulové diery/prekryvy. PARTIAL zahŕňa aj dva relokačné bajty bez uzavretého typu. Integrita mapy nie je dôkaz úplnej sémantiky. GitHub posledná publikovaná snímka zatiaľ túto lokálnu dávku neobsahuje.

'''
text+=f"SHA mapy `{p['map_sha256']}`; SHA cases `{s['cases_sha256']}`.\n\n"
text+='''## Aktualizácia 13 oblastí

Metodika nového percenta: dôkazmi uzavreté jednotky / úplný inventár oblasti. Úplné menovatele stále chýbajú, nové percentá N/A. Historické percentá sú orientačné. Počet reťazcov alebo úspešných prípadov sa nepoužíva ako sémantické percento.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|názov uif.dat a rb konzument|celé spracovanie dát|loader closure|
| Dátové typy a konštanty |95 %|N/A|85 B / 16 polí PARTIAL|236 B iba klasifikované|zvyšné immediate/alias odkazy|
| Tabuľky a ukazovatele |93 %|N/A|skutočné near string argumenty|runtime DS a kapacity|caller DS trace|
| Funkcie / ASM / CFG |90 %|N/A|78 B / 39 inštrukcií|okolité config funkcie|uzavrieť 0C6E caller|
| RNG |97 %|N/A|bez nového dôkazu|prirodzené poradie|DEMO trace|
| Scheduler |96 %|N/A|bez nového dôkazu|prirodzené callery|call graph|
| DEMO a vstupy |96 %|N/A|bez nového dôkazu|driver ABI|input closure|
| Renderer / VGA |94 %|N/A|diagnostické názvy odlíšené|renderer algoritmus|VGA setup|
| GUARD / bossovia |93 %|N/A|bez nového dôkazu|health/lifecycle|health updater|
| Zbrane / projektily |92 %|N/A|bez nového dôkazu|damage callery|effect producer|
| Sprity / HUD / paleta |92 %|N/A|formát %d of %d konzument|skutočné UI hodnoty|UI caller ABI|
| SAVE / LOAD |92 %|N/A|config.sav cesta a scan formáty|prirodzené I/O a parser|config read/write closure|
| Windows Win16 |92 %|N/A|bez nového Win dôkazu|parita path buildera|nájsť ekvivalent|

## Runtime testy na vykonanie

V DOSBox-X sledovať prirodzené DS:3CDC a výslednú cestu DS:3466 pred otvorením config.sav, vrátane spustenia z iného pracovného adresára. Overiť skutočný DS/DF kontext, kapacity a oba flag režimy callera. Reťazce a CRT scanner sledovať na skutočnom konfiguračnom vstupe; nezamieňať tento plán s vykonaným runtime testom. Prirodzených DOSBox-X testov stále 0; PE32 sa nevytvára.
'''
(r/'PASS1_LITERAL_CONSUMERS_REPORT.md').write_text(text,encoding='utf-8')
