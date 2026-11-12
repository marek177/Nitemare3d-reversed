# DOS2: voliteľný CD obrázok a dekodér úvodnej obrazovky

Nová dávka pridáva **dve ohraničené funkcie, 400 vykonateľných bajtov a 135 inštrukcií**, **26 riadených replay scenárov** a **jeden prirodzený DOSBox-X scenár**. Klasifikácia PASS320 sa nemení: PARTIAL 57102 B, CLASSIFIED ONLY 149 B, UNKNOWN 44 B, DEEP VERIFIED 0 B.

## Reálne zdroje a rozsah tvrdení

- DOS2 rozbalený obraz SHA256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; hranice inštrukcií sú nezávisle dekódované a porovnané so starším inventárom.
- CD súbor `L:\nite3d\dos\n3dcd\DSTOPEN.IMG`, 20678 B, SHA256 `af574568089f1998ca50ceeba310ff068c728279ff470cd39f47a8919228b95a`. V hlavnom zdrojovom adresári `L:\nite3d\nite3\dos` chýba. Prítomnosť v CD priečinku sama neurčuje verziu pôvodného CD EXE.
- Prirodzený runtime používa pôvodný zabalený DOS2 EXE a izolovanú kópiu 22 zdrojových súborov; CD obrázok sa do tejto kópie nepridával. Hashy zdrojov zostali nezmenené.
- Replay vykonáva pôvodné x86 inštrukcie dekodéra, ale modeluje CRT otvorenie/čítanie/zatvorenie, fatálnu chybu a celý vykresľovač riadka. Nie je to beh pôvodného CRT ani dôkaz VGA výstupu.

## Funkcie, ASM a CFG

|Funkcia|Segment:IP, koniec exclusive|Image interval|Kód / inštrukcie|
|---|---|---|---|
|intro_pcx_stream_load|0277:1600..1765|[03D70,03ED5)|356 B /119|
|intro_optional_image|0D29:079A..07C6|[0DA2A,0DA56)|44 B /16|

Prvý interval má rozsah 357 B, ale iba 356 B dosiahnuteľného kódu. Medzeru 1 B týmto nekvalifikujeme ako padding. CSV obsahujú každú inštrukciu aj CFG hrany. FAR volania používajú relokované segmenty; CRT a renderer sú v replay nahradené návratovými stubmi, vnútorné podmienené vetvy zostávajú pôvodné.

Dekodér vytvára 458 B stack frame (`ENTER 01CAh`), zachováva BP/SI/DI, používa DS na near adresy aj lokálny buffer. Replay explicitne nastavuje DS=SS; jeho použitie s odlišnými DS/SS nie je uzavreté. ES nemá replayovaný lokálny význam, pretože renderer a CRT sú modelované. Vstup je near filename argument `[BP+6]`; AL=0 pri neúspešnom otvorení, AL=1 po dokončení 200 riadkov. Ostatné výstupné registre nie sú všeobecným API kontraktom.

## Presná kontrola hlavičky

Po `fopen(filename,"rb")` sa žiada 128 B. Návratová hodnota čítania sa netestuje. Kontroluje sa len manufacturer BYTE 0Ah a nasledovná podmienka:

```text
dy = WORD(header+10) - WORD(header+6)  # 16-bit arithmetic
dx = WORD(header+8)  - WORD(header+4)
if dy != 199 and dx != 319:
    fatal(message_at_DS_0663)
```

Teda **stačí správny jeden rozmer**. Pri height=200 sa šírka netestuje. Replay potvrdil prijatie 17×200 aj 320×17 a odmietnutie 17×17. Bez ohľadu na tieto hodnoty funkcia dekóduje 200 riadkov po 320 B. Encoding, bits-per-pixel, počet planes a bytes-per-line táto rutina nekontroluje; jeden modelovaný prípad ich zmenil a stále vznikol rovnaký výstup. Úplný všeobecný PCX parser to nie je.

## RLE a riadkový buffer

```text
row = 0
p = stack_buffer_320
while row < 200:
    read_1_byte(token)  # result ignored
    if (token & 0xC0) == 0xC0:
        read_1_byte(value)  # also when count == 0
        count = token & 63
    else:
        value = token
        count = 1
    repeat count times:
        *p++ = value
        if p == buffer_end:
            draw_row(buffer, row++, fixed_arguments)
            p = buffer_start
close(stream)
return AL=1
```

Nulový run spotrebuje token aj value bez zápisu. Run môže prekročiť hranicu riadka; podmienka `row<200` sa testuje až po dokončení runu. Pri riadenom poslednom rune 63 B, keď ostáva 1 pixel, sa odovzdá len posledný 320 B riadok a ďalších 62 B skončí v znovu otvorenom stack buffri; nie sú kreslené. Tým sa nedokazuje fyzický VGA výstup ani bezpečnosť následného spracovania.

Každý z 200 row callbackov mal presné WORD argumenty: `buffer_offset, DS, 0, row, 320, 1, 320, 1, 0, FFFFh`. Úplný význam posledných hodnôt a renderer 0156:07DE zostávajú otvorené.

Pri modeli čítania, ktorý zapisuje bajty, ale vracia 0, dekodér dokončí obraz bez chyby. Samostatný skrátený stream s platnou hlavičkou narazil na 21 EOF čítaní bez kontroly; experiment bol vtedy zastavený. Používal vopred nulovaný syntetický stack. Nejde o dôkaz nekonečnej slučky alebo prirodzeného obsahu neinicializovaného stacku.

## Reálny CD súbor

|Interval súboru, end exclusive|B|Dôkaz|
|---|---:|---|
|[0,128)|128|hlavička; manufacturer0A, súradnice 0,0..319,199|
|[128,19909)|19781|13408 RLE tokenov, presne 64000 výstupných B|
|[19909,19910)|1|marker0C za dekódovanými pixelmi|
|[19910,20678)|768|RGB paleta použitá iba na rekonštruovaný náhľad|

Reálny stream nemá token prekračujúci hranicu riadka. Všetkých 200 modelovaných row callbackov sa zhodovalo s nezávislým parserom. SHA256 64000 indexovaných pixelov: `0a0e3ad03b3ac664d2d874c26491636a4347380765a75f6ee8353f19cb0bcec1`. Dekodér 0277:1600 sa po 200 riadkoch zatvorí bez načítania markeru alebo palety; odkiaľ prirodzená CD cesta berie správnu paletu, zostáva otvorené.

![Rekonštrukcia CD assetu, nie runtime screenshot](intro_pcx_replay/reconstructed_cd_intro.png)

## Prirodzený runtime: chýbajúci súbor

Dosiahnutý bod je **0D29:07DD**, po návrate z 079A; skutočne **154D:07DD** pri load0824h. AL=0, DS=SS=2F95h. Samostatný verifier overil runtime obraz po 1670 relokáciách, 19 capture súborov, 22 nezmenených vstupov, neprítomnosť DSTOPEN.IMG v izolovanom disku a presnú cieľovú adresu breakpointu.

079A odovzdá DS:1C87 (`dstopen.img`) loaderu. Ak AL=0, vráti sa bez lokálnych následných volaní. Ak AL!=0, volá 0156:008E, 0156:0254 s argumentom2, initializer font skupiny0 a wait0424. Úspešná vetva je zatiaľ statická; nový DOSBox beh ju nevykonal.

Všetkých 44 UNKNOWN bajtov malo od CRT entry po UI07DD nulové cached-value udalosti; candidate hook4B bol na koncoch nezmenený. BPLM nesleduje čítania, zápisy rovnakej hodnoty ani všetky interné zmeny host callbackov. Žiadny z týchto bajtov sa nepreklasifikoval.

## Reprodukcia a artefakty

`audit_replay_intro_pcx.py IMAGE INVENTORY DECODER EMULATOR ASSET OUT` vytvára ASM CSV, CFG CSV, 26 prípadov, 13408 tokenov a 200 hashov riadkov. Dve relokačné bázy sú 0000h a1000h; prípady sú 13 odlišných vstupných kontraktov ×2. FATÁLNE vetvy sa zastavia pri modelovanom volaní handlera, jeho návrat sa nepredpokladá.

`runtime_watch_optional_intro.py DOSBOX_EXE GAME_DIR IMAGE RELOCS OUT WORK` reprodukuje prirodzenú chýbajúcu vetvu. `verify_unknown_watch_capture.py IMAGE RELOCS MAP OUT WORK` overuje zachované vstupy, transcript, registre a raw captures. Runtime proof je v `dosbox_optional_intro_runtime/independent_verification.json`.

Metodika pokrytia: počet funkcií sa počíta z jedinečných ohraničených CSV; bajty z nezávisle dekódovaných inštrukcií. Počet replay scenárov je počet úspešných riadkov cases.csv, nie percento hernej sémantiky. Prirodzený runtime je samostatný scenár, nie opakovanie syntetických testov. Úplné menovatele 13 oblastí stále chýbajú, preto nové sémantické percentá zostávajú N/A.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Úplné menovatele chýbajú, preto N/A. Iniciačný runtime nie je percento gameplay completeness.

| Oblasť | Predošlý odhad | Nové % | Aktuálny dôkaz (staršie riadky zachované) | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|CD DSTOPEN.IMG:128B header,19781B RLE,769B tail; 64000 pixelov|iné PCX/IMG domény; stride/planes ignorované|prirodzený CD asset decode|
| Dátové typy a konštanty |95 %|N/A|nové asset intervaly CSV/JSON s hashmi; fixný320B row buffer|úplná PCX hlavička a chyby čítania|CRT fread a renderer kontrakty|
| Tabuľky a ukazovatele |93 %|N/A|128 runtime FAR pointerov font2 presne zhodných s parserom|iné skupiny a signed char indexy|úplný textový caller kontrakt|
| Funkcie / ASM / CFG |90 %|N/A|PCX loader+optional wrapper:400B/135 inštrukcií;26 replay;UI07DD AL0|úspešná wrapper vetva a renderer07DE|prirodzená úspešná CD vetva|
| RNG |97 %|N/A|bez RNG runtime|prvý srand/rand|RNG caller trace|
| Scheduler |96 %|N/A|clock init prebehol medzi bodmi|main loop/scheduler|loop vstup|
| DEMO a vstupy |96 %|N/A|prirodzený INT9 install a aux probeFFFFh|key IRQ/DEMO poradie/close|prvý vstupný tick|
| Renderer / VGA |94 %|N/A|200 row callbackov byte-exact v modelovanom replay CD assetu|07DE body a planes; nový prirodzený frame chýba|07DE ASM/CFG a row capture|
| GUARD / bossovia |93 %|N/A|bez AI runtime|map init|selector doména|
| Zbrane / projektily |92 %|N/A|bez damage runtime|effect callery|damage trace|
| Sprity / HUD / paleta |92 %|N/A|DOS DAC readback = runtime buffer = asset SHR2|Win OS paleta a celková obrazová parita|Win capture a paired frame|
| SAVE / LOAD |92 %|N/A|BSF native file-check vrátený|SAVE/LOAD a chybové I/O|diskové scenáre|
| Windows Win16 |92 %|N/A|Win1104funkcie/229inštrukcií,23fixupcalls,22replay|skutočnéWin16DS/API/runtime|CreatePalette/WinG trace|

## Runtime testy na vykonanie

1. Osobitný izolovaný DOS2 disk s explicitne pridaným CD assetom; porovnať všetkých 200 prirodzených vstupných riadkov renderera. Nesmie sa zameniť s pôvodnou distribučnou konfiguráciou.
2. Uzavrieť 0156:07DE: FAR vstupný buffer, clipping, VGA planes, masky a parametre. Následne porovnať framebuffer s indexovanými pixelmi a skutočnou paletou.
3. Zachytiť prirodzený wait0424, klávesnicový vstup a následné font skupiny0/1; pokračovať k prvému menu frame.
4. Krížovo porovnať túto voliteľnú vetvu s CD EXE a Win16; doterajší DOS2 replay nič o ich ABI alebo správaní nedokazuje.

Nová dávka zostáva lokálna, kým nebude samostatne overená nová GitHub publikácia.
