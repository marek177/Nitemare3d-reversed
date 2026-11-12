# Win16 1.10: skutočný spotrebiteľ GAME.PAL a dve paletové cesty

Nová dávka spája reálnyWin110EXE s predchádzajúcim externýmasset auditom. NEautodata segment je10; jediný `game.pal\0` je **segment10:0EAE**, file2CEEEh. Tri explicitnéPUSH odkazy v3:4909,491A,493E patria loaderu a jeho error argumentom. Filename zhoda sama sa nepovažuje za dostatočnú; ďalšieFAR ciele sú overené rozbalenýmiNEfixup reťazcami.

## Ohraničené funkcie

|Segment3 rozsah,end exclusive|InštrukčnéB/inštrukcie|Rola|
|---|---:|---|
|4904..4989|133/48|open/EOF−768/read768/dispatch/query/close|
|3AF4..3B15|32/12|backend dispatch podľaBYTE DS46B0|
|3ACC..3AF4|40/22|VGA uploader768 sSHR2 pri každej položke|
|31AA..335F|436/147|logická paleta aWinG/GDIAPI cesty|

Spolu **641inštrukčnýchB/229inštrukcií**,23relocation-backedFAR calls. Dva span bajty mimoentryCFG sa nepočítajú ako inštrukcie ani sa nevyhlasujú za dokázanýpadding. SamostatnýWin katalóg používaNEsegment:offset/file adresy; nikdy sa neprekladá doDOSunpacked image indexov.

## Loader: tail namiesto dekódovania PCX obrazu

Loader otvorínear filename0EAE s8000h, vykonáseek signed32−768,origin2, potom768krátread1 do **DS5B7E..5E7D**. Na rozdiel odDOS loadera **nevykonávaSHR2 pri čítaní**. Nasledujevolanie3:3AF4 s dvomaWORD argumentmi `(near5B7E, mode0)`, post-query3:2AAC(0) aclose. Readreturn sa nekontroluje; open/seek error vetvy ostávajúneuzavreté.

Táto cesta pre Windows5459B asset začína čítať naoffset4691 a **nečíta128BPCXheader aniRLE obraz**. PredchádzajúcaPCXrekonštrukcia preto nedokazuje, že tento loader vykresľuje motívy zprefixu. Ich použitie môže byť iné alebo žiadne; neprítomnosť ďalších consumerov sa netvrdí.

```text
buffer768 = read_tail768("game.pal")    // preserved8bit bytes
if BYTE[46B0] != 0:
    upload_VGA(buffer768)              // output each BYTE>>2 to3C9h
else:
    logical_palette(buffer768, mode0) // 8bit RGB entries, OS dependencies
```

Dispatchkopíruje DWORD zo stacku, ale v tomtoABI ide o **dveWORD hodnoty near pointer/mode**, nie dôkazFARpointera. PriVGA targete sa druhýWORD ignoruje. Skutočné runtime selektory ani prirodzenéDS=autodata zatiaľ nie sú zachytené.

## Windows logická paleta

Na31AA sa vytvorí stack priestor40Eh; WORD header300h a100h a256štvorbajtových položiek. Layout zodpovedá definíciám [LOGPALETTE](https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-logpalette) a [PALETTEENTRY](https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-paletteentry): dveWORD hodnoty aRGB+flags. Tieto súčasnéMicrosoft dokumenty podporujú iba názvy/layout; nenahrádzajú dôkazWin16ordinalov alebo ABI.

Mode0 získa systémovépoložky cezGDIordinal375 a nastaví ichflags0. Pri **DS46AF=0** prepíšeRGB všetkých256položiek zo source a nastavíflags1. Pri **DS46AF!=0** zachováRGB prvých10 a posledných10 systémovýchpoložiek sflags0; preindex10..245 použijesourceRGB aflags1. Presnývýpočet10/0 jeCMPBYTE,1;CMC;SBB;AND0Ah, tedaBYTE255 tiež zvolí10.

PredGDIordinal360 sa odovzdá FAR pointerSS:stack_logical_palette. NázvyAPI z doterajšiehoASM súCreatePalette360,GetSystemPaletteEntries375 aSetSystemPaletteUse373; relocácie tu nezávisle dokazujúmodule/ordinal. Po creation nasledujústatickySelectPalette/RealizePalette cesty a prevodRGBflags do **B,G,R,0** bufferuDS4D9A preWINGordinal1006. CeláAPI realizácia a výsledokscreenpalety sa touto prefixskúškou nevykonávajú.

Mode2 staticky pripravuje236položiek odindex10 a voláGDIordinal367 so start10/count236. Ostatnémodes prechádzajúsharedrelease cestou. Ani mode2 ani chybovýCreatePalette return0 nie sú zahrnuté vnovomreplay. Pôvodnérestore/cleanup telo3:2CC6 zostáva externou modelovanou závislosťou.

## Reprodukcia a dôkazový rozsah

`audit_win110_palette_consumer.py EXE ASM FIXUPS ABS_DECODER ABS_EMULATOR GAME_PAL OUT` pripínaEXE,ASM,asset aobidvefixupCSV hashe. ZrekonštruujeCFG každéhorozsahu a každáinštrukcia sa byte-exact porovná sEXE ajinventárom. Pri23FARcall overujezáznamfar_candidates ajexpanded_sites vrátanesource typu aoffsetu fixupu. PôvodnéFARselector WORD môžu obsahovať NEchain link, preto sa nesmú použiť ako runtimeadresy.

Replay používa dvasyntetickéCS/DSlayouty. Iba relocation-backedcallsites sa pripoja kpríslušnémunatívnemutelu alebo explicitnému stubu; reálneWin16loading sa tým nesimuluje celé. **16loader scenárov**=2layout×4bufferpattern(skutočnýWindows tail,ramp,FF,00)×2backend. FileAPI,query,fatal cieľ amode0GDItelo súmodelované; loader,dispatch aVGA uploader súpôvodné. Kontroluje sa768read adries,neposunutýbuffer, exact769OUT priVGA a8bitbufferargument priGDI. Zdrojovéfilebytes sa nemenia.

Ďalších **6GDIprefix scenárov**=2layout×3reserveBYTE(0,1,255). Pôvodný31AA prefix skladáLOGPALETTE; modelGetSystemEntries dodádeterministické256RGBflags acreationstub overí všetkých1028B pred zastavením. ModelovanéGetDC,SetSystemPaletteUse,GetSystemPaletteEntries ahelper2CC6;stop pred executionGDI360. Pascalcleanup importov aCcaller stack sa modelujú oddelene. DS=SS je explicitnýseedovanýpredpoklad pre near stackbuffer, **nie prirodzene potvrdenáWin16invarianta**.

**22scenárov,0odchýlok**. `instructions.csv`,`functions.csv`,`call_edges.csv`,`cases.csv`,`logical_palette_prefix.csv`,`summary.json` sú reprodukovateľné. Nie sú to skutočnéWin16runtime testy ani úplná behaviorálna paritaDOS/Win. ŽiadnyPE32port.

EXESHA `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`. AssetSHA `b6b71824a73a74c79e0f3ae12c9a423f2ae500ca956fe156f1f0d4d2307d24fc`. CasesSHA `4fb3c6d01a05e0bcc7d99be2b32fd394d52e5237926189087a59129712aff67e`.

## Meranie

DOSkatalóg ostáva125funkčnýchrozsahov; samostatnýWin110paletovýdoplnok má4rozsahy,229inštrukcií/641B a22replayprípadov. Nie je to úplnýWin16functioninventory a tieto adresy sa nesčítavajú doDOSbytepartition. PrirodzenéDOSBoxscenáreostávajú7,Win16runtime0. PASS1nezmenené57102PARTIAL/149CLASSIFIED ONLY/44UNKNOWN/0DEEP VERIFIED. Dávka je lokálna,zatiaľnepublikovaná. NovépercentáN/A bezplnýchmenovateľov.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Úplné menovatele chýbajú, preto N/A. Iniciačný runtime nie je percento gameplay completeness.

| Oblasť | Predošlý odhad | Nové % | Aktuálny dôkaz (staršie riadky zachované) | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|32asset kópií/3varianty;WindowsPCX celý ohraničený|DOSprefix1156B a bare768 pôvod|DOSprefix spotrebitelia|
| Dátové typy a konštanty |95 %|N/A|511 runtime DWORD mimo file|149 B iba klasifikované, 44 B UNKNOWN|nepriame segmentové prístupy|
| Tabuľky a ukazovatele |93 %|N/A|7-slot CRT rodina v8 DOS verziách; piaty slot otvorený|vypočítané aliasy/writeri DS2356|runtime hook watch|
| Funkcie / ASM / CFG |90 %|N/A|loader144B/53inštrukcií a DAC37B/21|I/O chybové vetvy|read failure scenáre|
| RNG |97 %|N/A|bez RNG runtime|prvý srand/rand|RNG caller trace|
| Scheduler |96 %|N/A|clock init prebehol medzi bodmi|main loop/scheduler|loop vstup|
| DEMO a vstupy |96 %|N/A|prirodzený INT9 install a aux probeFFFFh|key IRQ/DEMO poradie/close|prvý vstupný tick|
| Renderer / VGA |94 %|N/A|mask/plane store,transparentnosť a unsigned depth|skutočné VGA registre a výstup|DOSBox frame dump|
| GUARD / bossovia |93 %|N/A|bez AI runtime|map init|selector doména|
| Zbrane / projektily |92 %|N/A|bez damage runtime|effect callery|damage trace|
| Sprity / HUD / paleta |92 %|N/A|Winloader bezSHR;VGA backendSHR2, GDI8bitRGB|OSpaleta aDIB render|nativeWindows capture|
| SAVE / LOAD |92 %|N/A|BSF native file-check vrátený|SAVE/LOAD a chybové I/O|diskové scenáre|
| Windows Win16 |92 %|N/A|Win1104funkcie/229inštrukcií,23fixupcalls,22replay|skutočnéWin16DS/API/runtime|CreatePalette/WinG trace|

## Runtime testy na vykonanie

ZachytiťWin16loaderselection,prirodzenýDS/SS a46B0/46AF predpaletou; porovnaťCreatePalette vstup,APIreturny aWinGcolor table. Samostatnepreveriťreservedfarby,mode2AnimatePalette,errorreturn0,readfail acreatorcleanup. Ažpotomporovnávaťobrazovévýsledky sDOSDAC. PASS1UNKNOWN44B aCRTslot2356zostávajú samostatnouprioritou.
