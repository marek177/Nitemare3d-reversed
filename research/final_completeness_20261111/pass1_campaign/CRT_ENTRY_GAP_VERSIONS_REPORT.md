# PASS1 / PASS5: 17-bajtová nulová medzera pred CRT vstupom

Nové krížové overenie všetkých ôsmich DOS označení (sedem jedinečných image SHA). Každé má 17 nulových bajtov bezprostredne pred rovnakou 13-bajtovou vstupnou signatúrou CRT. Pre DOS2.0 ide presne o historický NON-CODE interval **[11EE7,11EF8)**. Stav zostáva CLASSIFIED ONLY; bez dôkazu všetkých referencií a writerov sa neoznačuje za DEEP VERIFIED padding.

## Presné hranice

| DOS označenie | CS:IP vstupu podľa unpack/MZ | Image medzera [start,end) | Predchádzajúci BYTE |
|---|---|---|---|
|10|119B:0010|[119AF,119C0)|CB na 119AE|
|11|11BC:0018|[11BC7,11BD8)|CB na 11BC6|
|12|11C2:0018|[11C27,11C38)|CB na 11C26|
|15|11C7:001C|[11C7B,11C8C)|CB na 11C7A|
|17|11D1:0018|[11D17,11D28)|CB na 11D16|
|18|11EA:001C|[11EAB,11EBC)|CB na 11EAA|
|19|11EA:001C|[11EAB,11EBC)|CB na 11EAA|
|20|11EE:0018|[11EE7,11EF8)|CB na 11EE6|

Signatúra B430CD213C02730533C00650CB zodpovedá úvodu s DOS version query a vetvou pre starý DOS. Skener overuje jej jedinečnosť v každom image, presnú zhodu všetkých 17 nulových bajtov a BYTE CB tesne pred medzerou. Samotný CB sa tu nevydáva za dokázanú vykonávanú RETF inštrukciu, ak chýba vstupná CFG cesta. Zistenie podporuje hypotézu linkovacej/oddeľovacej medzery, nie univerzálny dôkaz nepoužitia.

Dôležitá korekcia hraníc: DOS2.0 segmentový základ 11EE0 nie je začiatkom 24 nulových bajtov. [11EE0,11EE7) obsahuje nenulové bajty nadväzujúce na predchádzajúci obsah; nulový interval začína až 11EE7. Vstupné IP sa medzi verziami líši, preto sa adresy nesmú odvodiť od predpokladu rovnakého IP=18h vo všetkých DOS verziách.

## Proveniencia a reprodukcia

audit_crt_entry_gap_versions.py VERSION_MANIFEST CANONICAL_IMAGE UNPACK_PROOF OUT. Pre každú verziu kontroluje SHA image voči manifestu, CS:IP v unpack.json a CS:IP MZ reconstructed.exe. Celý image za MZ headerom musí byť totožný s príslušným unpacked_image.bin. Výstup versions.csv uchováva SHA všetkých troch artifactov, presné adresy a hash medzery aj signatúry.

Pre hlavný DOS2.0 sa navyše hash skutočného N3D-UNFU.exe porovnáva s lokálnym reprodukovaným unpack dôkazom a kontroluje sa zhodný canonical image aj entry. Pre ostatné verzie ide v tejto dávke o vzájomnú kontrolu existujúcich rozbalených artifactov, nie o nové nezávislé rozbalenie pôvodných EXE. MZ reconstructed header a unpack metadata môžu mať spoločný generátor; ich zhoda preto nie je nezávislým dôkazom pôvodného loadera.

Nové controlled replay prípady0, prirodzený DOSBox-X runtime0. Toto meranie nevyhľadáva všetky CS/DS/ES/SS aliasy, dynamické skoky alebo runtime zápisy. Na potvrdenie definitívneho paddingu nestačí nulový obsah, rovnaká dĺžka medzi verziami ani podpis entry.

## Meranie

PASS1 ostáva **57 101 B PARTIAL, 150 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57 295 B. Pre presne 17 z CLASSIFIED ONLY bajtov pribudla nová cross-version evidencia hraníc, bez zmeny statusu. Posledná publikovaná GitHub snímka tieto lokálne dôkazy ešte neobsahuje.

SHA canonical source `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`; SHA image `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; SHA version manifest `e38ee99642f8b435f9398b0d9a96812668607e58d187a1c3101ff2becb8da7e9`.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, preto N/A. Počet verzií a zhoda medzery nie sú percento sémantickej úplnosti.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|entry proti unpack/MZ v 8 DOS|iné pôvodné EXE unpack|nezávislé overenie verzií|
| Dátové typy a konštanty |95 %|N/A|17 B medzera presne zhodná|padding sémantika|alias/writer dôkaz|
| Tabuľky a ukazovatele |93 %|N/A|entry hranice bez IP predpokladu|dynamické referencie|segmentové kontexty|
| Funkcie / ASM / CFG |90 %|N/A|byte signatúra CRT vstupu|predchádzajúca cesta|CFG pred entry|
| RNG |97 %|N/A|bez nového dôkazu|prirodzené poradie|DEMO trace|
| Scheduler |96 %|N/A|bez nového dôkazu|prirodzené callery|call graph|
| DEMO a vstupy |96 %|N/A|bez nového dôkazu|driver ABI|input closure|
| Renderer / VGA |94 %|N/A|bez nového dôkazu|setup|VGA init CFG|
| GUARD / bossovia |93 %|N/A|bez nového dôkazu|selector doména|descriptor flag8|
| Zbrane / projektily |92 %|N/A|bez nového dôkazu|damage callery|effect producer|
| Sprity / HUD / paleta |92 %|N/A|bez nového dôkazu|resource identity|resource parser|
| SAVE / LOAD |92 %|N/A|bez nového dôkazu|prirodzené I/O|stream trace|
| Windows Win16 |92 %|N/A|bez nového Win dôkazu|NE odlišný layout|Win entry vlastný audit|

## Runtime testy na vykonanie

V DOSBox-X zachytiť pôvodný EXEPACK transfer a prvý CS:IP pre DOS2.0; watchpoint na presných 17 B sleduje prípadné zápisy. Negatívny trace z jedného behu nepotvrdzuje úplnú absenciu použitia. Pre každú ďalšiu verziu vykonať vlastný loader trace; rovnaká signatúra nevytvára Win16 ekvivalenciu. PE32 sa nevytvára.
