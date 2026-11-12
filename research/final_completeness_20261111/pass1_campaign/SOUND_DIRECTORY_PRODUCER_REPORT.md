# SND.DAT: producent 79-položkovej zvukovej tabuľky

Nový dôkaz uzatvára konkrétnu dovtedy otvorenú väzbu **producenta DS3F64** z reportov resource bufferu a zvukového dispatchera. Statická funkcia **0277:0AE0..0B40**, image **[3250,32B0)**, má **96 B /33 inštrukcií**. Desiata zachovaná session pôvodného DOS EXE dosiahla **0476:0190**, koniec úvodnej inicializácie pred FAR návratom, a zachytila celý obsah tabuľky.

## Presný presun a polia

Funkcia otvára `snd.dat` cez near filenameDS0554 s argumentom8000h. Vloží seek argumenty `(handle,C0h,0000h,0000h)`, teda DWORD offset192 a origin0. Potom žiada **474B=1DAh** do near buffera **DS3F64**. Návrat read musí byť presne1DAh, inak sa zavolá herný error wrapper. Nakoniec sa zavrie handle a obnovíSI; FAR návrat, bez vlastných argumentov.

```text
handle = open("snd.dat", 8000h)
if handle == FFFFh: error_wrapper(filename, format)
seek(handle, 192, origin0)       // return not checked here
got = read(handle, near3F64h, 474)
if got != 474: error_wrapper(filename, format)
close(handle)
```

Open test je rovnosťFFFFh, nie všeobecný signed negatívny test. Seek návrat sa v tejto funkcii nekontroluje; neúspešný seek s následným474B čítaním môže prejsť lokálnym read-count testom. Úplný error-wrapper non-return kontrakt ani tieto I/O chybové vetvy sa v novej session nevyvolávali. Funkcia lokálne neprepínaDS/ES/SS; near buffer vyžaduje správny zdedenýDS. Native close/OS registre nie sú týmto celé garantované.

**Runtime `[DS3F64,DS413E)` sa byte-exact zhoduje s pôvodným `SND.DAT[192,666)`.** Samostatný producer/consumer audit ukazuje layout79×6B:

|Offset v zázname|Šírka|Doložená rola|
|---:|---:|---|
|+0|WORD|dĺžka zvukového payloadu|
|+2|DWORD|absolútny zdrojový file offset|

Spotrebiteľ0C2B:039E počítaID*6, číta WORD na3F64 a DWORD na3F66; porovná dĺžku s15000B a používa predtým doložený file-backed buffer[1D0F0,20B88). Dispatcher03D6 najprv odmietne nulovú dĺžku. Preload wrapper0277:0B40 staticky iterujeSI0..78 (unsigned porovnanie s4Fh), čo nezávisle podporuje nominálny počet79. Nepreukazuje to rozsah ID od všetkých herných callerov ani celé telá resource/WORX routines.

## Skutočný asset a hranice

Pôvodný SND.DAT má548930B. Z79 záznamov je **7 nulových a72 nenulových**. Každý offset aj `offset+length` je v hraniciach súboru. Najväčší payload má **14306B**, takže všetkých79 metadátových dĺžok aktuálneho assetu vyhovuje buffer limitu15000B; z toho sa nevyvodzuje úplná ID alebo inoverziová bezpečnosť.

Dve dvojice ID zdieľajú presne tú istú nenulovú source oblasť: **37/38** a **41/42**. Ide o rovnaký offset a dĺžku, nie iba podobný obsah alebo odhad zvukového významu. CSV uchováva aj SHA každého payloadu. Ich kodek, vzorkovanie, prirodzené playback udalosti a fyzický význam zostávajú otvorené. Prvých192B kontajnera ani ostatné časti sa týmto auditom nevyhlasujú za dokončené.

Tabuľka v default DGROUP patrí do image-relative **[2B674,2B84E)**, BSS mimo file image končiaceho29D60h. Samostatný runtime BSS katalóg preto pridáva474B; **nepridáva žiadny bajt k historickému PASS320 ani k file-typed dátam**. Naďalej PARTIAL, nie DEEP VERIFIED.

## Prirodzený capture a UNKNOWN monitoring

`runtime_watch_sound_directory.py` používa pôvodné EXE a22 kópií assetov, archivovaný support helper a44 BPLM breakpointov od CRT0018 po main0190. V rozšírenom okne sa nezaznamenala žiadna udalosť zmeny hodnoty na44 UNKNOWN bajtoch; všetky endpoint dumpy ostali nulové. Hook4B má iba zhodné endpoint dumpy. Nejde o read ani same-value-write stopu a nevylučuje host callback medzistavy.

Nový capture poskytuje finálny474B table dump. Seek a read argumenty pochádzajú z byte-exact statického producenta; táto session nezachytáva každý file API entry ako samostatný breakpoint. Zhoda buffera so source slice je runtime potvrdenie, nie úplná časová stopa všetkých writerov. Hra ešte nevstúpila do mapovej hernej slučky. Po capture harness ukončí svojDOSBox; nejde o prirodzený exit.

## Reprodukcia a katalógy

1. `runtime_watch_sound_directory.py DOSBOX_EXE GAME_DIR IMAGE RELOCS OUT WORK` zachytí nový beh.
2. `verify_unknown_watch_capture.py IMAGE RELOCS CURRENT_MAP OUT WORK` overí image/relokácie, presnú44B množinu, breakpoint lifecycle, endpoint0190,14 raw captures, source/copy hash a SND slice.
3. `audit_sound_directory_producer.py IMAGE INVENTORY ABS_DECODER SND RUNTIME_OUT WORK OUT` nezávisle dekóduje96B producenta, kontroluje runtime proof hashe, všetkých79 offsetov/dĺžok a ohraničené consumer/preload kontexty.
4. `write_sound_directory_report.py OUTPUTS` a štandardný catalog/status rebuild aktualizujú reporty.

Výstupy: `sound_directory_init.csv`, `runtime_directory_records.csv`, `shared_payload_aliases.csv`, `consumer_contexts.csv`, `external_bss_tables.csv`, summary a runtime proof/transcript/snapshots. Raw zvukové payloady sa nekopírujú do dôkazového katalógu. Žiadny nový seeded replay ani nová prehrávacia audio skúška.

SND.DAT SHA `f3434984d315531602d32285cb8ff55990bba786f5fb37f53710e88379388614`. Runtime474B SHA `bec36bda9a47cbae4f5c256ccfee1684f67e5c7e66f288281741bd32ae7e7020`. Runtime proof SHA `e6f45cdfc56bb91e65bfc8f6f23aba6722cce98cecdbdbf0cfb547b304bae61b`.

## Meranie

DOS katalóg125→126 funkčných rozsahov,+33 inštrukcií/+96B. Runtime scenáre9→10. Samostatné runtime BSS tabuľky2044+474=2518B mimo file image; nejde o sémantické percento. Win paletový doplnok4 rozsahy/22 replay prípadov zostáva samostatný. PASS1 stále57102 B PARTIAL,149 B CLASSIFIED ONLY,44 B UNKNOWN,0 B DEEP VERIFIED. Nové percentáN/A bez plných menovateľov. Dávka je lokálna, zatiaľ nepublikovaná.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Úplné menovatele chýbajú, preto N/A. Iniciačný runtime nie je percento gameplay completeness.

| Oblasť | Predošlý odhad | Nové % | Aktuálny dôkaz (staršie riadky zachované) | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|SND.DAT[192,666) → 79 runtime záznamov; všetky payload bounds platné|audio formáty a zvyšok kontajnera|payload spotrebitelia/WORX|
| Dátové typy a konštanty |95 %|N/A|BSS DS3F64 má doloženého producenta a 79 WORD/DWORD záznamov|alias writeri a runtime ID domény|sound caller trace|
| Tabuľky a ukazovatele |93 %|N/A|hook DS2356 má rovnaký relokovaný obsah v oboch endpoint dumpoch|medzistavy a nepriame čítanie|bezpečná kalibrácia nenulového watch|
| Funkcie / ASM / CFG |90 %|N/A|sound directory init96B/33inštrukcií a main0190 endpoint|I/O chyby, seek failure a resource callee|short-read a herný vstup|
| RNG |97 %|N/A|bez RNG runtime|prvý srand/rand|RNG caller trace|
| Scheduler |96 %|N/A|clock init prebehol medzi bodmi|main loop/scheduler|loop vstup|
| DEMO a vstupy |96 %|N/A|prirodzený INT9 install a aux probeFFFFh|key IRQ/DEMO poradie/close|prvý vstupný tick|
| Renderer / VGA |94 %|N/A|768 emulovaných DAC zložiek byte-exact; bits6/maskFF|framebuffer, clipping, fyzický VGA|video roviny a prvý frame|
| GUARD / bossovia |93 %|N/A|bez AI runtime|map init|selector doména|
| Zbrane / projektily |92 %|N/A|bez damage runtime|effect callery|damage trace|
| Sprity / HUD / paleta |92 %|N/A|DOS DAC readback = runtime buffer = asset SHR2|Win OS paleta a celková obrazová parita|Win capture a paired frame|
| SAVE / LOAD |92 %|N/A|BSF native file-check vrátený|SAVE/LOAD a chybové I/O|diskové scenáre|
| Windows Win16 |92 %|N/A|Win1104funkcie/229inštrukcií,23fixupcalls,22replay|skutočnéWin16DS/API/runtime|CreatePalette/WinG trace|

## Runtime testy na vykonanie

Pokračovať zmain0190 cez prirodzenú nasledujúcu cestu do prvej mapy a scheduler/input ticku. Pri zvuku zachytiť ID, resource lookup/load, payload a WORX volania; odlíšiť BSS metadáta od skutočného playback formátu. Oddelene preveriť short-read/seek chyby a dosahovanie alias ID dvojíc. UNKNOWN44B vyžaduje stále read/write alias dôkaz, nie iba nulový počet value-change breakpointov.
