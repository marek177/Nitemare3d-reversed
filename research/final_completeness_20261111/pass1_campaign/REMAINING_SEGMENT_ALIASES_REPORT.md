# PASS1: aktuálny zvyšok a rozlíšenie segmentových aliasov

Nový scan aktuálnej mapy `3021969d4e4348715816361fa387631e7d6cfd9fc9dcc136e26073f0f9984d1b` kontroluje všetkých 35648 dodaných začiatkov inštrukcií proti skutočným bajtom a nezávislému dekóderu. Zvyšok mimo PARTIAL je **63 intervalov / 193 B**: 149 B CLASSIFIED ONLY a 44 B UNKNOWN. Z toho 140 B má nulový obsah. Nuly nie sú dôkaz paddingu. Presná CSV/JSON mapa zvyšku je `remaining_noncode_current/interval_ledger.csv/json`.

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

SHA kandidátskeho CSV: `ec3e5e14bed63176b54a3d2903ce7526263d254a50809d7bc8cbba0cfcdddbed`. Pôvodné EXE ani mapa sa nemenili. **57 102 B PARTIAL /149 B CLASSIFIED ONLY /44 B UNKNOWN /0 B DEEP VERIFIED**. Funkčný katalóg zostáva 115 rozsahov; tri uchované runtime scenáre a replay počty sa nemenia. Táto dávka je lokálna, nie nová GitHub publikácia. Nové percentá sa nevypočítavajú bez úplných menovateľov.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Úplné menovatele chýbajú, preto N/A. Iniciačný runtime nie je percento gameplay completeness.

| Oblasť | Predošlý odhad | Nové % | Aktuálny dôkaz (staršie riadky zachované) | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|skutočný BSF54 B load/decode|iné BSF/role blokov|resource sloty v runtime|
| Dátové typy a konštanty |95 %|N/A|511 runtime DWORD mimo file|149 B iba klasifikované, 44 B UNKNOWN|nepriame segmentové prístupy|
| Tabuľky a ukazovatele |93 %|N/A|12 lokálnych FAR konštrukcií 21FD:264E odlíšených od DS:264E|aliasy/dynamické indexy|watchpointy na 44 UNKNOWN B|
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

Sledovať päť súvislých UNKNOWN oblastí [1BDA2,1BDB0),[1C070,1C080),[1D0EC,1D0F0),[20B88,20B90),[2770E,27710) pri skutočnom štarte, načítaní mapy a prvom frame. Samotná nezmena dumpu nedokáže neprítomnosť dočasného zápisu ani čítania; na tento účel treba read/write stopu alebo watchpointy so zachyteným CS:IP a segmentmi. Rozlíšiť nominálny index calendar lookup od neplatných month hodnôt. Pokračovať za posledným VGA breakpointom podľa predchádzajúceho runtime reportu.
