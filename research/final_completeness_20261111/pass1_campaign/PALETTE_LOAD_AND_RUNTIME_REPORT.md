# GAME.PAL: EOF relatívna paleta, konverzia a DAC

Nová statická/replay dávka uzatvára ohraničený loader **0277:02A6..0336**, image[2A16,2AA6),144B/53inštrukcií, a uploader **0156:012A..014F**, image[168A,16AF),37B/21inštrukcií. Navyše siedma prirodzená DOSBox session zachytila túto cestu s pôvodnými súbormi aEXE až po0476:017C. ÚroveňPARTIAL: chyby I/O a fyzická/kompletná VGA parita zostávajú otvorené.

## Skutočný formát použitý touto cestou

Otvorený názov je **game.pal** zDS0245. Súbor má1924B; SHA nižšie. Originálny seek stack obsahuje handle6, WORD FD00h, WORD FFFFh, origin2. Skupinu inštrukcií `PUSH DWORD0002FFFFh;PUSH FD00h` treba čítať podľa stack ABI ako **signed32 offsetFFFFFD00h=-768 a WORD origin2**, nie seek naFD00h alebo offset0002FFFFh.

Skutočný seek vrátil DX:AX=0000:0484, teda **1156=1924−768**. Následne sa768krát číta1B do postupných near adriesDS4A64..4D63 a každý BYTE sa hneď posunie logicky doprava2. Buffer je vBSS mimo originálneho file image; nepridáva sa do PASS320.

```text
handle = open("game.pal", 8000h)
if signed16(handle)<0: fatal_error(...)
position = seek(handle, -768, SEEK_END_numeric2)
if signed16(high16(position))<0: fatal_error(...)
for i=0..767:
    read(handle, near(4A64h+i), 1)
    BYTE[4A64h+i] >>= 2
upload_DAC_768(near4A64h)
query_0277_0188(0)
close(handle)
```

Read návrat sa v slučke nekontroluje. Pri chybe/EOF môže pôvodný obsah buffera zostať a aj tak sa posunúť; konkrétne chybové kontrakty sa touto dávkou netestovali. Fatal návratový/non-return kontrakt tiež nie je týmto happy-path dôkazom uzavretý.

## Presné DAC telo

Uploader nastavíDX3C8h a zapíšeAL0, potom pôvodná slučka vykoná presne768 BYTE výstupov na3C9h v poradí buffera. Šírka port operácie je8bit. Vstup je near pointer SS:[BP+6] interpretovaný cezDS; funkcia obnovíSI/BP/SP a FARreturn, ostatné pracovné registre/flags nie sú garantované. Byte hodnoty native uploader sám nemaskuje na6bit; šesťbitová doména0..63 vzniká v tejto loader ceste predchádzajúcim SHR2.

Na posledný iteration test sa pôvodneCX zníži až naFFFFh po767→0 ukončovacom teste; nie je to štandardný priamy LOOP. Zaznamenané poradie portov je1×3C8h a768×3C9h. Samotný port trace nie je DAC readback ani screenshot porovnanie.

## Reálne dáta a native replay

`audit_replay_palette_load.py IMAGE INVENTORY ABS_DECODER ABS_EMULATOR GAME_PAL OUT` nezávisle overí bajty/CFG oboch funkcií proti inventáru. Pôvodný loader aj pôvodný DAC uploader bežia bez nahradenia. Modelované sú file open/seek/read/close, fatal cieľ (nesmie byť zasiahnutý v skúšaných prípadoch) a post-upload query0277:0188. OUT sa zaznamenáva.

**20prípadov,0odchýlok**:2load ×10obsahov (skutočný tail, BYTE ramp0..255 a konštanty0,1,3,4,127,128,252,255). Kontrolujú sa názov/flags open, všetky4seek WORD argumenty, presne768read argumentov s dĺžkou1, poradiequery/close, celý converted buffer, všetkých769 port outputov a návratDS/SI/DI/BP/SP. Skutočný asset sa v modeloch nemení. Toto nie je vykonanie pôvodných DOS file API telies.

`real_asset_dac_writes.csv` obsahuje769 presných modelovaných port udalostí. `asset_intervals.csv/json` zvlášť klasifikujú **[0,1156)UNKNOWN prefix** a **[1156,1924)PARTIAL BYTE768 komponentový stream256triplets**. Nulový/nečítaný prefix sa nepovažuje za padding. Ide o externýGAME.PAL katalóg, nie zmenu mapyEXE.

## Prirodzený DOSBox dôkaz

`runtime_dosbox_startup.py DOSBOX_EXE GAME_DIR IMAGE RELOC OUT WORK palette_init` pokračoval z predošlej epizódovej init cesty na loader entry, natívny CRTseek entry/return, DAC entry a návratmain0476:017C. Na DACentry je stack návrat0A9B:031D a near argument4A64; dump768B sa **byte-exact zhoduje so skutočným tailBYTE>>2**. DAC telo sa prirodzene vrátilo. Tento scenár nezaznamenáva celý port trace a nečíta hardvérovéDAC registre späť; tieto limity sa nepreberajú z modeled replay.

`verify_dosbox_startup_capture.py IMAGE RELOC OUT WORK` nezávisle overuje78MEMDUMPBIN príkazov, celý runtime obraz a relokácie, staršie prefix body aj nové4raw captures palette_loader_stack,palette_seek_stack,palette_dac_stack,palette_converted_runtime. Overuje originálnyGAME.PALhash, seek1156, reg/stack adresy a obsah. Originálne22 vstupné súbory zostali nezmenené. Harness po capture ukončí svojDOSBox; nejde o prirodzený gameexit.

GAME.PAL SHA `efd52442cbee3327d8cec045b31559049e8767b298c25674a557eb6e096a759f`. Tail SHA `c367a55c9ea7ebc397806c2befd983214d10acfae34ab9829287b92953a4c6d6`. Converted/runtime768B SHA `52768cc8fc70a3242e82214ed3dbf7136fe146670ad773916ab03132ee2fd1ce`. Replay cases SHA `a31db1fae64fe48c4df0f4d9edd73ed6e3d7b954a92d5639dc7acfdec7a619f7`. Runtime proof SHA `7893e5d95af4e656d5522ce5286a02e2237b1dd3438c2ef3c8bb310245038a45`.

## Meranie

Katalóg123→125funkčných rozsahov,+74inštrukcií/+181B; replay+20; prirodzené zachované DOSBox scenáre6→7. Prefixy scenárov sa prekrývajú. PASS1 nezmenené57102PARTIAL/149CLASSIFIED ONLY/44UNKNOWN/0DEEP VERIFIED, typovanéfile dáta57988B. Externý asset aBSS sa nepripočítavajú k57295B. Dávka je zatiaľ lokálna, publikovaný analytický commit2ced761cb0bf1eece24a224e92c05636058ab0ae má starší stav5scenárov/122rozsahov. Nové percentáN/A bez úplných menovateľov.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Úplné menovatele chýbajú, preto N/A. Iniciačný runtime nie je percento gameplay completeness.

| Oblasť | Predošlý odhad | Nové % | Aktuálny dôkaz (staršie riadky zachované) | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|GAME.PAL EOF-768 a byte-exact native konverzia|prefix1156B a varianty assetu|prefix/formáty verzií|
| Dátové typy a konštanty |95 %|N/A|511 runtime DWORD mimo file|149 B iba klasifikované, 44 B UNKNOWN|nepriame segmentové prístupy|
| Tabuľky a ukazovatele |93 %|N/A|7-slot CRT rodina v8 DOS verziách; piaty slot otvorený|vypočítané aliasy/writeri DS2356|runtime hook watch|
| Funkcie / ASM / CFG |90 %|N/A|loader144B/53inštrukcií a DAC37B/21|I/O chybové vetvy|read failure scenáre|
| RNG |97 %|N/A|bez RNG runtime|prvý srand/rand|RNG caller trace|
| Scheduler |96 %|N/A|clock init prebehol medzi bodmi|main loop/scheduler|loop vstup|
| DEMO a vstupy |96 %|N/A|prirodzený INT9 install a aux probeFFFFh|key IRQ/DEMO poradie/close|prvý vstupný tick|
| Renderer / VGA |94 %|N/A|mask/plane store,transparentnosť a unsigned depth|skutočné VGA registre a výstup|DOSBox frame dump|
| GUARD / bossovia |93 %|N/A|bez AI runtime|map init|selector doména|
| Zbrane / projektily |92 %|N/A|bez damage runtime|effect callery|damage trace|
| Sprity / HUD / paleta |92 %|N/A|20 native replay a runtime768B palety|DAC readback a vizuálna zhoda|zachytiť DAC/screenshot|
| SAVE / LOAD |92 %|N/A|BSF native file-check vrátený|SAVE/LOAD a chybové I/O|diskové scenáre|
| Windows Win16 |92 %|N/A|DOS8štítkov/7obrazov krížovo overených; Win bez zmeny|WinNE prostredie a algoritmické mapovanie|Win hook rodina|

## Runtime testy na vykonanie

Zachytiť skutočnýDAC register readback/video memory a screenshot pri tom istom paletovom buffere. Oddelene preveriťI/O chyby a skrátený/odlišnýGAME.PAL v kópiách dát. Analyzovať neprečítaných1156B asset prefixu a variantyDOS/Win. Pokračovať z0476:017C na resource init0277:0AE0 a prvýframe. Neuzatvárať z palety celý renderer, clipping aleboNON-CODE UNKNOWN44B.
