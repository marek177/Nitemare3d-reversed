# BSF: skutočné súbory, hlavička, bloky a DOS codec

40 súborov / 21 jedinečných SHA-256 obsahov zo stromu L:\nite3d. Všetky majú 54-bajtovú kódovanú hlavičku a tri bloky s presnými hranicami. Všetkých 40 encoded header XOR je nula. Toto sú nové dôkazy zo skutočných súborov, nie zo syntetických BSF. Stav PARTIAL; nejde o uzavretie celého formátu ani Win16 runtime parity.

Súpis ciest je bsf_candidate_paths.txt, assets.csv obsahuje veľkosť a SHA celého súboru aj hlavičky, resources.csv presné intervaly a SHA encoded/decoded blokov, decoded_headers.json všetkých 54 decoded bajtov každej hlavičky. externý katalóg external_header_fields.csv odlišuje lokálne potvrdené polia od neznámych.

## Hlavička a poradie režimov

Dekóduje sa XOR so skutočným 52-bajtovým kľúčom v kanonickom DOS obraze [29755,29789), od indexu nula pre každý blok zvlášť. Hlavička nie je celý súbor. Pre každý zo 40 vstupov platí:

```text
offset[0] = 54
offset[1] = offset[0] + length[0]
offset[2] = offset[1] + length[1]
file_size = offset[2] + length[2]
```

| Decoded offset | Typ | Režim dispatchera / použitie |
|---|---|---|
|0|BYTE neuzavretého významu|nulový XOR celej encoded hlavičky neurčuje jediný checksum byte|
|1,2|BYTE|mode0 volania helpera s n3d.exe a map.1; celý význam otvorený|
|3|BYTE nonzero flag|mode1 pointer/NULL a mode0 podmienka druhej kontroly|
|4..35|32 BYTE kandidát name region|mode2 vracia pointer; obsah za NUL sa neoznačuje padding|
|36,40,44|tri DWORD little endian file offsety|slot 0→mode4, slot1→mode3, slot2→mode5|
|48,50,52|tri WORD little endian dĺžky|rovnaké poradie slotov|

Pre hlavný DOS súbor sú bloky [54,528), [528,9669), [9669,10250). Pre hlavný Windows súbor [54,149), [149,9797), [9797,10378). Platí byte-level kompatibilita rozdelenia pri použití DOS decoder kľúča na tieto vstupy; pôvodný Win16 loader nebol vykonaný. Identické cesty alebo názvy neurčujú pôvod verzie; manifest presne rozlišuje SHA.

## Pôvodný loader a calleri

Nové statické čítanie 0277:1B02 ukazuje otvorenie súboru s flagom 8000h, alokáciu length+1, seek na DWORD offset, read cez 0FBA:009E, zápis NUL za blok, close a XOR cez 0FBA:01B2. To vysvetľuje spotrebu hlavičkových polí. Táto dávka neuzatvára celé telo loadera ani I/O chyby a nepridáva ho ako novú úplne overenú funkciu. Pôvodné resource významy zostávajú otvorené; len printable obsah alebo NUL count nie je dôkaz presného textového formátu.

audit_bsf_callers.py bajtovo overil 8 priamych FAR callerov 083D:29CA v dodanom inventári, 88 kontextových riadkov. Volanie 0476:00DA posiela mode0 a pred nasledujúcim call nezistí použitie AX/DX; tým sa lokálne oslabuje hypotéza chyby z nedefinovaného návratu inicializácie. Nie je to dôkaz všetkých dynamických callerov. Mode1 používa 0277:0DED,0476:01E4,0D29:2177/264F/26C5; mode4 0D29:1634. 0D29:1467 posiela callerom dodaný WORD, jeho úplná doména je otvorená. Export callers.csv/caller_contexts.csv.

## Native controlled replay

320 prípadov = 40 súborov × (hlavička + 3 bloky) × 2 load bázy. Pôvodná DOS XOR rutina beží bez stubov s kanonickým SS key kontextom, skutočnými relokáciami a načítanými encoded dátami. Porovnáva sa celý decoded blok s nezávislým byte modelom, AL checksum, dva guard BYTE, DS a SP/BP/SI/DI. Nulové odchýlky. Pre súbory z Windows priečinkov je vykonaná DOS rutina nad ich dátami, nie Win16 kód. Žiadne pôvodné OS file I/O, celý dispatcher alebo game startup tu nebeží. Prirodzené runtime testy 0.

Reprodukcia: rg --files L:\nite3d s filtrom BSF vytvorí zoznam ciest; audit_bsf_assets_native_codec.py IMAGE PATH_LIST EMULATOR OUT. Doplnok audit_bsf_callers.py IMAGE INVENTORY DECODER OUT. Iced-x861.21.0/Unicorn2.1.4; kanonický image SHA e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297.

## Meranie

PASS1 ostáva **57 067 B PARTIAL, 184 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**. Externých 40 súborov a nový hlavičkový katalóg nemenia menovateľ 57 295 B pôvodného NON-CODE. Nových replay prípadov 320, natural runtime0. GitHub posledná publikovaná snímka tieto lokálne dôkazy zatiaľ neobsahuje.

SHA cases `407347518e0ab6101a1a5152ce6d5df407a4e93c7cd2626a7f0a4e6d17104f4b`; SHA path list `f51a042edcbbd3d2787ee99e79a0d5a09c21a3e02a5f24895ae367e0d4e1f993`.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Bez úplných menovateľov N/A. Historické odhady sa neprepočítavajú z integrity partition alebo test count.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|40 BSF presných partition|celá sémantika blokov|resource konzumenti|
| Dátové typy a konštanty |95 %|N/A|externý header katalóg|184 B iba klasifikované|zvyšné alias odkazy|
| Tabuľky a ukazovatele |93 %|N/A|3 DWORD offsety + 3 WORD dĺžky|header BYTE0..2|overovací helper 28EE|
| Funkcie / ASM / CFG |90 %|N/A|8 byte-verified callerov|dynamické mode vstupy|0D29:1448 calleri|
| RNG |97 %|N/A|bez nového dôkazu|prirodzené poradie|DEMO trace|
| Scheduler |96 %|N/A|bez nového dôkazu|prirodzené callery|call graph|
| DEMO a vstupy |96 %|N/A|bez nového dôkazu|driver ABI|input closure|
| Renderer / VGA |94 %|N/A|bez nového dôkazu|setup|VGA init CFG|
| GUARD / bossovia |93 %|N/A|bez nového dôkazu|selector doména|descriptor flag 8|
| Zbrane / projektily |92 %|N/A|bez nového dôkazu|damage callery|effect producer|
| Sprity / HUD / paleta |92 %|N/A|tri decoded resource sloty|skutočná identita|resource parser|
| SAVE / LOAD |92 %|N/A|mode0 návrat lokálne ignorovaný|prirodzené I/O|read/seek trace|
| Windows Win16 |92 %|N/A|súbory kompatibilné s DOS codec|pôvodný Win loader|Win byte/CFG match|

## Runtime testy na vykonanie

V DOSBox-X zachytiť header a tri bloky po pôvodnom read/seek/XOR, zhodu SHA s týmto manifestom a skutočné mode callery. Overiť účel BYTE1/2 v helperi 28EE a flag BYTE3. Win16 samostatne sledovať jeho vlastný loader; kompatibilita dát nenahrádza vykonanie Win kódu. PE32 sa nevytvára.
