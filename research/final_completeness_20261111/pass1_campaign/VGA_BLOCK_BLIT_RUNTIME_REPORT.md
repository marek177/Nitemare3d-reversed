# DOS2: stĺpcový VGA blitter a prirodzený CD back-buffer

Nová dávka analyzuje celý ohraničený **0156:07DE..088C**, image **[01D3E,01DEC)**: **174 B, 78 inštrukcií, 86 relatívnych CFG hrán**. Pribudlo 2880 úplných samostatných replay prípadov, 4 integrácie pôvodného PCX dekodéra s pôvodným rendererom a 6 oddelene počítaných prefixových prípadov s nulovými počítadlami. Prirodzený DOSBox-X beh potvrdil všetkých **64000 indexovaných pixelov zadnej VGA stránky** s výslovne pridaným CD assetom.

PASS320 mapa zostáva **57102 B PARTIAL /149 B CLASSIFIED ONLY /44 B UNKNOWN /0 B DEEP VERIFIED**. Nové dôkazy dopĺňajú funkčný kontrakt a runtime renderer; nepredstierajú uzavretie zostávajúcich NON-CODE bajtov.

## Vstupy, ABI a segmenty

|BP offset|Typ|Lokálne potvrdený význam|
|---|---|---|
|+06,+08|FAR pointer|offset a segment source bitmapových bajtov|
|+0A|WORD|x; unsigned x>>2 a x&3|
|+0C|WORD|y; násobí sa len AL, teda y&255|
|+0E|WORD|v tejto funkcii sa nečíta; PCX caller odovzdáva320|
|+10|WORD|vzdialenosť medzi začiatkami zdrojových stĺpcov v B|
|+12|WORD|počet stĺpcov, bez kontroly nuly|
|+14|WORD|počet riadkov v stĺpci, bez kontroly nuly|
|+16|WORD|0 vyberá WORD DS:012E; nenulové DS:012C|
|+18|signed WORD|záporné = opaque; inak sa BYTE pixel porovná s dolným BYTE key|

Nejde o obvyklý riadkový memcpy: zdroj sa číta zvisle a medzi začiatkami stĺpcov sa posúva zadaným stride. Argument +0E nie je týmto vyhlásený za nepoužitý v celom hernom API.

Rutina najprv používa pôvodné DS na výber page segmentu do ES. `LDS SI,[BP+6]` zmení DS na source segment; lokálne premenné a argumenty cez BP stále používajú SS. Na návrate obnoví pôvodné DS, BP, SI, DI a SS/SP ostávajú konzistentné; **ES zostáva zvoleným VGA segmentom**. AX/BX/CX/DX a príznaky sú pracovné. Replay zahŕňa aj DS!=SS a samostatný source segment. Kompletná proveniencia autora alebo CRT/WORX knižnice tým nie je určená.

## Presný algoritmus pre bežné DF=0

```text
ES = (page == 0) ? DS.word[012E] : DS.word[012C]
base = WORD(80 * BYTE(y) + (WORD(x) >> 2))
mask = ROL8(11h, x & 3)
OUT 3C4h, 2
OUT 3C5h, mask
source_column = source.offset
for column in WORD_loop_count(columns):
    SI = source_column
    DI = base
    for row in WORD_loop_count(rows):
        value = source[SI++]
        if signed_WORD(key) < 0 or value != BYTE(key):
            ES[DI] = value
        DI = WORD(DI + 80)
    carry = bit7(mask)
    mask = ROL8(mask, 1)
    OUT 3C5h, mask
    base = WORD(base + carry)
    source_column = WORD(source_column + stride)
```

`WORD_loop_count(0)` znamená 65536 iterácií: telo sa vykoná pred LOOP a chýba JCXZ. Šesť patologických prefixových experimentov sa zámerne zastavilo po16 zápisoch; nepočítajú sa medzi úplné replay prípady.

Maska 11h,22h,44h,88h opakuje nibble. Použité low4 bity určujú rovinu; carry pri rotácii 88h→11h posunie bajtovú adresu. Na rozdiel od iných sprite slučiek sa nová maska vypíše aj po poslednom stĺpci.

Nie je tu clipping, kontrola viewportu ani detekcia prekročenia source/destination bufferu. Počiatočné y=256 sa správa ako y=0; veľké x používa unsigned SHR a môže adresovať mimo viewportu. Ukazovatele SI/DI sú16-bitové a wrapujú. Replay pokrýva konkrétne hodnoty, nie bezpečnosť ľubovoľnej pamäte.

## Direction flag a transparentná farba

Rutina neobsahuje CLD. Pri DF=1 sa source SI znižuje. V opaque vetve je `MOVSB; ADD DI,4Fh`, preto sa DI medzi riadkami posúva o78, nie80. V transparentnej vetve je `LODSB`, prípadný samostatný store a `ADD DI,50h`, teda krokDI=80 aj pri DF=1. DF sa nemení. Tieto rozdiely sú byte-exact potvrdené v syntetickom replay; prirodzený caller s DF=1 sa nepreukázal.

KeyFFFFh a8000h vyberajú opaque vetvu. Key001Fh vynecháva31. Key0001h a0101h vynechávajú rovnaký BYTE1; vrchný BYTE pozitívneho WORD nie je súčasťou porovnania farby.

## Matica úplných replay prípadov

2880 prípadov = 2 load bázy ×6 x hodnôt ×3 y hodnoty ×2 page selektory ×5 key hodnôt ×4 source geometrie ×2 DF. x=(0,1,2,3,319,65535), y=(0,199,256). Geometrie zahŕňajú rôzne positive columns/rows, stride0, prekrytie source stĺpcov, offsetFFFEh s wrapom a rozdielne lokálne nepoužité WORD hodnoty.

Každý prípad porovnáva **všetky source byte read adresy, VGA byte write adresy/hodnoty/low4 masky a všetky OUT porty** s oddeleným modelom. Source read hook je obmedzený na source segment; netvrdí všeobecné sledovanie stack alebo všetkých čítaní funkcie. Kontrolujú sa obnovené registre a zachovaný DF.

Štyri integrácie = 2 load bázy ×2 cieľové page segmenty. Pôvodný dekodér0277:1600 vykonáva pôvodný renderer0156:07DE; modelované ostávajú iba CRT I/O a fatal handler. Každá integrácia kontroluje200 skutočných vstupov rendereru,64000 store udalostí a64400 OUT udalostí. Model rovín sa zhoduje s každým deinterleavovaným pixelom reálneho DSTOPEN.IMG.

## Prirodzený DOSBox-X beh a štyri VGA roviny

Pôvodný zabalený DOS2 EXE sa vykonal v izolovanom disku s23 vstupmi: bežných22 a explicitne pridaný `L:\nite3d\dos\n3dcd\DSTOPEN.IMG`. Táto zmes je analytický scenár, nie tvrdenie o pôvodnej distribúcii alebo CD EXE. Hashy všetkých zdrojov ostali nezmenené.

Cieľ je **0D29:07A2**, skutočne **154D:07A2**, po návrate dekodéra, pred caller cleanup/testom AL. AL=1. DS page WORD hodnoty sú012C=A000h a012E=A400h. Pri výstupe GC hlási read-map0, read-mode0, write-mode0, bitmaskFF; sequencer map-mask1; unchained M_VGA, display start0.

Prvý read-only dump cez pôvodný read-map0 z A400h presne zodpovedal rovine0. Dump A000h obsahuje nuly **iba v zachytenej rovine0**; ostatné front-page roviny tým nie sú overené.

Potom, pri zastavenom CPU, nasledovalo presne:

```text
OUTP 03CE 0004
for p = 0..3:
    OUTP 03CF p
    MEMDUMPBIN A400:00000000 00003E80 vga_plane_p.bin
OUTP 03CF 0000
OUTP 03CE 0006
```

Všetky dumpy sú po16000 B. Po portových zásahoch už nebolo RUN. GC index a read-map sa obnovili; GC/SEQ/MODE hlásenia pred a po sa zhodujú. Čítanie VGA mohlo zmeniť interné read latche; tie sa neoverovali ani neobnovovali. Preto ide o zásah pri zbere dôkazov po dosiahnutí endpointu, nie o tvrdenie nemenného celého zariadenia.

|Rovina|B|SHA256 runtime dumpu aj očakávaných source pixelov|
|---|---:|---|
|0|16000|`1ae3515ec21257087cf8e6d1f263ba693c9817c8d8e1f502d69a12db3bbecdaf`|
|1|16000|`e7113909c76e43c730bb7dcbda294c78a38a7da54f25571de865b8f444d5d055`|
|2|16000|`8ba55119f64bf9c3df576698605832f4cc91c3b6dc42742ad5b3536934626814`|
|3|16000|`d2a2526fff93529fbcc4776f930768a0ebc34d8eaecb137ac264f65860a188c0`|

Každá rovina p sa presne zhoduje s indexovanými source pixelmi `pixels[p::4]`. Rekonštruovaných64000 indexov má SHA256 `0a0e3ad03b3ac664d2d874c26491636a4347380765a75f6ee8353f19cb0bcec1`. Runtime tak potvrdzuje obsah **zadnej stránky pred flipom**; nepotvrdzuje viditeľný frame, RGB paletu CD assetu, ďalší text, menu ani gameplay.

Capture obsahuje26 raw súborov plus transcript/registre/konfiguráciu a oba snapshoty VGA stavu. Nezávislý verifier potvrdzuje relokovaný obraz,23 súborových vstupov, presný whitelist debugger zásahov a ich poradie, nulové UNKNOWN44 cached-value udalosti, UIF/font2/SND obsah a64000 pixelov. Predošlý pokus s nesprávnym debugger príkazom GFX zlyhal a nie je započítaný. V2 mala iba pôvodnú read-map0; do centrálneho katalógu sa importuje iba úplná V3.

## Krížové DOS porovnanie

Osem labelov10,11,12,15,17,18,19,20 predstavuje7 odlišných obrazov;18 a19 sú identické. Verzie15..20 majú presne rovnakých174 B na image1D3Eh. Verzie10..12 majú interval[1D30,1DDE), líšia sa len dvoma adresami WORD v `MOV AX,[moffs16]`: DS012C/012A namiesto012E/012C. Po normalizácii výhradne týchto dvoch operandov sa zhodujú všetky bajty,78 hraníc inštrukcií a86 relatívnych CFG hrán.

Normalizácia nie je runtime dôkaz rovnakých hodnôt page globálov. Producenti starších globálov a prirodzené callery ostávajú na overenie. Win16 ekvivalent v tejto dávke nebol určený. Zdrojové EXE/ASM inventáre a všetky hashy sú v `vga_blit_versions/summary.json` a `versions.csv`.

## Nástrojová nezrovnalosť a reprodukcia

Pri tomto fixture sa Unicorn2.1.4 s globálnym MEM_READ hookom vrátil cez RETF odlišne oproti behu bez hooku; hook obmedzený na source segment sa zhodoval s neinstrumentovaným návratom. `probe_unicorn_retf_read_hook.py IMAGE EMULATOR OUT` reprodukuje všetky tri varianty na pôvodnej rutine. Je to pozorovanie nástroja, nie chyba hry. Úplná matica používa iba source-bounded hook a kontroluje návratové registre; štyri integrácie tento source read hook vôbec nepoužívajú.

- `audit_replay_vga_block_blit.py IMAGE INVENTORY DECODER EMULATOR CD_ASSET OUT`: ASM/CFG,2880 úplných prípadov,4 integrácie,6 samostatných prefixov a reprezentatívne store udalosti.
- `audit_vga_blit_versions.py IMAGE VERSION_ROOT DECODER OUT`:8 labelov,16 hashovaných obrazových/inventárnych vstupov a presná dvojoperandová normalizácia.
- `runtime_watch_intro_loaded.py DOSBOX_EXE GAME_DIR IMAGE RELOCS OUT WORK startup CD_ASSET`: pôvodný EXE, izolované kópie,26 raw captures, dočasné read-map porty.
- `verify_unknown_watch_capture.py IMAGE RELOCS MAP OUT WORK`: nezávislé overenie runtime dôkazov. Autoritatívna úspešná dávka je `dosbox_intro_loaded_runtime_v3`.

Nový argumentový katalóg je `vga_column_block_blit/argument_fields.csv`. Neprekresľuje file-backed NON-CODE partition. Nová dávka je lokálna; GitHub potvrdenie staršej snímky ju automaticky nezahŕňa.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Úplné menovatele chýbajú, preto N/A. Iniciačný runtime nie je percento gameplay completeness.

| Oblasť | Predošlý odhad | Nové % | Aktuálny dôkaz (staršie riadky zachované) | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|CD DSTOPEN.IMG:128B header,19781B RLE,769B tail; 64000 pixelov|iné PCX/IMG domény; stride/planes ignorované|prirodzená paleta a page flip|
| Dátové typy a konštanty |95 %|N/A|ABI10WORD polí; source stride, signed key a y lowBYTE; staršie asset intervaly zachované|neuzavreté caller domény a globálne invarianty|callery a rozsahy zdrojových dát|
| Tabuľky a ukazovatele |93 %|N/A|128 runtime FAR pointerov font2 presne zhodných s parserom|iné skupiny a signed char indexy|úplný textový caller kontrakt|
| Funkcie / ASM / CFG |90 %|N/A|blitter174B/78 inštrukcií;2884 úplných replay;6 prefixov;8DOS CFG zhôd|callery07DE, nulové domény a Win ekvivalent|caller a page producer audit|
| RNG |97 %|N/A|bez RNG runtime|prvý srand/rand|RNG caller trace|
| Scheduler |96 %|N/A|clock init prebehol medzi bodmi|main loop/scheduler|loop vstup|
| DEMO a vstupy |96 %|N/A|prirodzený INT9 install a aux probeFFFFh|key IRQ/DEMO poradie/close|prvý vstupný tick|
| Renderer / VGA |94 %|N/A|prirodzený DOSBox back-buffer64000 pixelov vo4 rovinách byte-exact|viditeľný flip, RGB paleta a text/menu|display-start po prirodzenom flipe|
| GUARD / bossovia |93 %|N/A|bez AI runtime|map init|selector doména|
| Zbrane / projektily |92 %|N/A|bez damage runtime|effect callery|damage trace|
| Sprity / HUD / paleta |92 %|N/A|nový CD back-buffer; starší DOS DAC readback zachovaný|CD palette vs GAME.PAL; Win OS a celý frame|Win capture a paired frame|
| SAVE / LOAD |92 %|N/A|BSF native file-check vrátený|SAVE/LOAD a chybové I/O|diskové scenáre|
| Windows Win16 |92 %|N/A|Win1104funkcie/229inštrukcií,23fixupcalls,22replay|skutočnéWin16DS/API/runtime|CreatePalette/WinG trace|

## Runtime testy na vykonanie

1. Pokračovať prirodzene cez page flip0156:008E a zaznamenať display-start/viditeľné indexy a DAC. Oddeliť asset paletu od aktuálnej GAME.PAL.
2. Uzavrieť wait0424 a autentický klávesnicový IRQ vstup; následne font0/1 a prvý menu frame.
3. Preveriť všetkých callerov07DE: zdrojové stride/rows, nulové hodnoty, DF invariant a source/destination rozsahy.
4. Overiť page producentov v DOS10..12 a nájsť Win16 algoritmický ekvivalent; rovnaký kód bez runtime väzby nestačí na paritu.
5. Rozšíriť UNKNOWN44 read/write sledovanie za init/intro. Stabilné cached-value breakpointy zostávajú PARTIAL negatívnym dôkazom, nie dôkazom nepoužitia.
