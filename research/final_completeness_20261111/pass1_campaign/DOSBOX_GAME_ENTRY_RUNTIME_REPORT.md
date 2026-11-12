# DOSBox-X runtime: CRT→herný main, argumenty, INT0 a defaults

**Druhá samostatná runtime session originálneho packed DOS2.0 EXE úspešne dosiahla prvý herný vstup a bod pred spracovaním argumentov.** Ide o DOSBox-X built-in DOS a debuggerom riadený originálny EXE bez náhradných herných/CRT funkcií, seeded registrov alebo zmeneného diskového EXE. Test končí v 0476:035C; menu, schedulovaný gameplay, AI, zvuk a render parity týmto nie sú overené. Stav výsledkov zostáva PARTIAL, DEEP VERIFIED0.

## Prostredie a reprodukovaná vstupná cesta

Portable Windows SDL2 DOSBox-X v2026.10.01 a originálny EXE majú rovnaké SHA ako prvá dávka DOSBOX_STARTUP_RUNTIME_REPORT.md: emulator EXE a82adcfa7af2784566cfeff74c077cefed08505396db2948b7e6aa7d4cee0832, game EXE552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301. Samostatný pracovný mount obsahuje kópie podľa inputs.csv, originály naL: zostali po teste byte-for-byte nezmenené. Config/command args sú v summary.json. Normal CPU, svga_s3, fixed20000cycles, SDL dummy a nosound nie sú dôkaz grafického alebo audio výstupu.

Nová session znovu overila celý171360 B runtime image po1670 relokáciách, pôvodný packed→CRT transfer, BSS47584 nulových B a DS=ES=SS pri11EE:00B3. Tieto zopakované kontroly sú prekrývajúcim sa pokrytím prvého testu; nie sú novým percentom byte completeness. Všetky breakpointy a dumpy majú surový transcript a hash.

## Nové runtime body a segmenty

| Bod | Skutočný CS:IP | DS / SS | ES | SP |
|---|---|---|---|---|
|pred optional init|1A12:00B3|2F95 /2F95|2F95|E82A|
|herný main pred ENTER|0C9A:0326|2F95 /2F95|07CA|E80E|
|po defaults/getenv pred argv logikou|0C9A:035C|2F95 /2F95|2F95|E800|

Load0824h dáva canonical CS0476→0C9A a DS2771→2F95. Vektorové a environment inicializácie medziB3 a main menia ES; rovnosť DS=ES=SS zB3 sa teda nesmie automaticky predpokladať pri vstupe do hry. ES=07CA pri main sa zhoduje so segmentom environment program-name pointera. Pri035C je ES už znova DS po vykonanom near getenv helperi. To je dôkaz tejto cesty, nie univerzálny callee register ABI.

## Argumenty a názov programu

CRT globals DS:213E/2140/2142 obsahujú argc1, argv E818h, envp E8BAh. Na vstupe main má stack presne FAR návrat1A12:00DF a za ním tri WORD argumenty **1,E818,E8BA**. Tým je priamo potvrdené prepojenie globálov na caller stack v pozorovanom prostredí. Pointer tabuľka argv má jeden near pointer a NULL terminátor.

argv[0] aj FAR program-name DS:2144 (07CA:008E) ukazujú na ASCII **C:\N3D20.EXE**. Celé používateľské/hostiteľské prostredie sa nevypisuje; kontroluje sa iba meraný programový názov a surové dáta zostávajú v pracovných dumpoch. Spúšťaný súbor bol len pre8.3 mount pomenovaný N3D20.EXE, obsah je pôvodný a SHA súhlasí. Špecifický názov alebo počet argumentov nie sú univerzálny výsledok pre všetky spustenia.

## Optional init a INT0

PredB3 je WORD DS:2532 nulový. Táto session teda prirodzene preskočí voliteľný NEAR callback. Úplný kontrakt nenulového callbacku tým nie je runtime uzavretý.

Pôvodný INT0 má FAR hodnotu **F000:CA60**, encoded60CA00F0. Pred herným main je uložený v DS:210A bez zmeny a tabuľka IVT0 obsahuje **1A12:00E5**, encodedE500121A. To zodpovedá skutočne vykonaným INT21/AH35 a AH25 v CRT122. IVT sa meria vnútri DOSBox emulácie; hostiteľské vektory sa nemenia. Obnovenie vektora pri prirodzenom ukončení zatiaľ nebolo testované: proces je po breakpoint capture ukončený harnessom.

## Defaults a getenv

Na hernom vstupe DS:082A=1. Po natívnom defaults kóde je082A=0, WORD DS:3CC2=25 a BYTE DS:3CCF=1. Native getenv na kľúčwindir sa na tejto ceste vrátil sAX=0 a alternatívna vetva nastavujúca rate18/flag0 sa nevykonala. Neznamená to univerzálnu absenciu windir vo všetkých DOS prostrediach ani uzavretie všetkých config read vetiev. Priama file-I/O trace nebola v tejto dávke samostatne overená, preto z týchto stavových hodnôt nevzniká tvrdenie o konkrétnom diskovom config.sav obsahu.

## Nezávislé overenie a reprodukcia

runtime_dosbox_startup.py DOSBOX_EXE GAME_DIR IMAGE RELOCATIONS OUT WORK **game_entry**. Režimstartup stále zastaví poB3. Potom verify_dosbox_startup_capture.py IMAGE RELOCATIONS OUT WORK. Nový verifier porovná21 raw MEMDUMPBIN výstupov/úsekov, celý image/BSS, stack argumenty, argv/progname, IVT pred/po/saved, optional pointer, default flag a rate. Povolené debug príkazy sú len PING,EV,BP,BPDEL,RUN a MEMDUMPBIN; žiadne SR/SM na seedovanie registrov alebo pamäte hry.

independent_verification.json pinne hash capture súborov; central catalog ich pri importe znovu hash-checkuje. Surové game binary dumpy sú iba v samostatnom work adresári, nie sú súčasťou textovej publikácie. Spustenie je časovo ohraničené a ukončuje len vlastný emulátor. Návratový kód1 po terminácii nie je prirodzený game exit ani potvrdenie game crashu.

SHA summary `f55c296a6d54968ceea8feaed994e1d31b84eb394a77eee61eab6f099e890e27`; harness SHA `1facf9273ecd7091bf5959180cff57672c62a9d869b0fd76e484374a5cc5a6cd`; runtime image SHA `6ff79b07a98de8873f60bf2da6d93f55bbc0d3320a1d8adbd90e02e7fde569b6`.

## Meranie

PASS1 sa nemení: **57 102 B PARTIAL,149 B CLASSIFIED ONLY,44 B UNKNOWN,0 B DEEP VERIFIED**. Originálne DOSBox-X sessions **1→2**: prvástartup→B3, druhástartup→main→035C. Jednotkou je samostatná overená session, nie každý breakpoint alebo znovu porovnaný bajt. Nové controlled Unicorn replay prípady0. Sémantické percentá sa nevymýšľajú z počtu sessions.

Nová lokálna runtime dávka nie je súčasťou poslednej publikovanej analytickej snímky ba27379dd28c9a689d15233b0fd7017867f50114. Staršie poznámky runtime0/1 zostávajú historické. PE32 sa nevytvára.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, preto N/A. Startup/main trace nepreukazuje gameplay completeness.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|opakovane presný loader image|iné verzie|original loader porovnanie|
| Dátové typy a konštanty |95 %|N/A|argc/argv/envp/default flags runtime|149 B iba klasifikované|writer watchpointy|
| Tabuľky a ukazovatele |93 %|N/A|INT0 saved/replaced a progname FAR|obnovenie pri exite|prirodzený exit trace|
| Funkcie / ASM / CFG |90 %|N/A|CRT→main→035C skutočná cesta|zvyšok main/init|ďalšie init body|
| RNG |97 %|N/A|bez RNG runtime|prirodzené srand/rand|prvý RNG caller|
| Scheduler |96 %|N/A|bez gameplay runtime|main loop|scheduler vstup|
| DEMO a vstupy |96 %|N/A|argc1 prirodzená cesta|driver a demo|demo spustenie|
| Renderer / VGA |94 %|N/A|bez render parity|VGA init|mode setup trace|
| GUARD / bossovia |93 %|N/A|bez AI runtime|map init|selector doména|
| Zbrane / projektily |92 %|N/A|bez damage runtime|effect callery|damage trace|
| Sprity / HUD / paleta |92 %|N/A|bez resource runtime|load identity|resource loader|
| SAVE / LOAD |92 %|N/A|defaults rate25/flag1 runtime|diskové config/I/O|file trace|
| Windows Win16 |92 %|N/A|bez Win runtime|NE prostredie|samostatný Win16 test|

## Runtime testy na vykonanie

Pokračovať za035C po prvé herné init/resource body a prvý srand/rand; pri každom bode zaznamenať skutočné segmenty. Osobitne otestovať argv vetvy, nenulovéwindir, prirodzený exit a obnovenieINT0. Pripraviť samostatné gameplay/renderer/AI scenáre; počet2 sessions nie je záruka ich parity.
