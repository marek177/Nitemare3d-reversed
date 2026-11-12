# DOSBox-X: INT9 a pomocná vstupná inicializácia

Piaty zachovaný scenár pôvodného packed DOS2 EXE pokračuje za resource init až po **0476:015C**. Overené sú prirodzené keyboard/aux mode0 vetvy; registre, game kód ani OS odpovede sa nedosadzujú. Dávka pridáva tiež štyri krátke statické wrappery do funkčného katalógu. Pôvodné22 vstupné súbory sa po behu znovu hashovali bez zmeny.

## Pozorovaný INT9 životný cyklus

Vstup **06B0:0134**, skutočne **0ED4:0134**, má návrat0C9A:0148 a WORD mode0. Pred vstupom sú BYTE DS0B3E/0B3F rovné0/0. Pôvodný IVT9 je **F000:E987** (bajty87E900F0). Po návrate je IVT9 **0ED4:0000** (0000D40E), uložený FAR v DS3F52 je byte-exact pôvodný IVT9 a príznaky sú1/0. DS=SS2F95 v oboch bodoch.

To potvrdzuje prirodzené get-vector/save/set-vector v emulovanom DOS prostredí. Nevykonával sa zatiaľ prirodzený shutdown mode1 s obnovou vektora ani celý IRQ handler kontrakt. Staršia mode1/mode0 seeded lifecycle analýza zostáva osobitným dôkazom, nie prirodzenou close skúškou.

## Pomocný vstupný probe

Vstup **06B0:018C**, skutočne0ED4:018C, má návrat0C9A:015C a mode0. Na **06B0:01A8** sa po návrate z0831:000E pozorovalo **AX=FFFFh**; rovnaký WORD je v DS3F56 register bufferi. Po caller normalizácii sú príznaky DS0B3E/0B3F=1/1 a dostupnosť DS414C=1. Dostupnosť bola1 aj pred volaním; overená je výsledná hodnota a probe, nie prechod dostupnosti0→1.

Probe je odvodený od explicitného INT33 volania cez CRT adapter11EE:24EA. V tejto dávke sa nepreukazuje pohyb fyzickej myši, tlačidlá, chovanie neexistujúceho ovládača alebo kompletné reg-pack ABI. HodnotaFFFF sa vyhodnocuje unsigned ako >=1; nejde o signed negatívnu chybu.

## Oddelenie runtime wrapperov od hernej politiky

|Rozsah|B/inštrukcie|Kontrakt a závislosť|
|---|---:|---|
|11EE:39E2..39F4|18/10|WORD vector arg; AH35h/INT21; vráti DX:AX z ES:BX, ES ostáva API výsledok|
|11EE:39F4..3A09|21/12|WORD vector+FAR handler; uložíDS,LDS DX argument,AH25h/INT21,obnovíDS,AX0|
|0831:000E..0028|26/8|nastaví WORD DS3F56=0; ten istý near buffer dá ako in/out11EE:24EA pre interrupt33h; vráti WORD3F56|
|0831:0028..003F|23/7|rovnaká buffer príprava/interrupt33h; nemá explicitný návratový loadAX|

Všetky štyri sú straight-line FAR funkcie, bez skokovej tabuľky; hranice a každá inštrukcia sú byte-exact overené nezávislým dekóderom proti inventáru. Calleri odstraňujú argumenty. Get/set wrappery majú BP rámec a prirodzene patria vrstve DOS API v CRT segmente; presný názov/autor knižnice či kompilátora nie je týmto identifikovaný. Probe/close wrappery zdieľajú herný BSS buffer a volajú externý runtime adapter. Herná politika, kedy tieto operácie vykonať a ako normalizovať dostupnosť, je v06B0:0134/018C, ktoré boli v katalógu už skôr.

Lokálny pseudokód get/set:

```text
get_vector(v): AX=WORD(v); AH=35h; INT21; return FAR(ES:BX) as DX:AX
set_vector(v,p): save DS; AX=WORD(v); DS:DX=p; AH=25h; INT21;
                 restore DS; return AX=0
probe(): WORD[3F56]=0; int_adapter(33h, near3F56, near3F56); return WORD[3F56]
```

Vstupné AL vektor číslo je lowBYTE WORD argumentu; testovaná prirodzená hodnota je9. Efekty INT21/33 a ďalšie registre sa nevyhlasujú za uzavreté mimo pozorovaného prostredia. Predchádzajúce tvrdenie DS=ES z niektorých startup bodov nie je invariant cez get-vector alebo ďalšie API volania.

## Reprodukcia a evidencia

`runtime_dosbox_startup.py DOSBOX_EXE GAME_DIR IMAGE RELOC OUT WORK input_init`, potom `verify_dosbox_startup_capture.py IMAGE RELOC OUT WORK`. Verifier kontroluje68 memory-dump príkazov, úplný runtime image po1670 relokáciách, všetky skoršie startup/init body, nové stacks/IVT/flags/probe a SHA každého dôkazu. Povolené debugger operácie sú query/code BP/RUN/dump; žiadne dosadzovanie registrov/pamäte. Raw dumpy sú vo WORK, strojové summary/transcript/registers/inputs/proof v `dosbox_input_init_runtime/`.

`audit_input_runtime_wrappers.py IMAGE INVENTORY ABS_DECODER OUT` reprodukuje štyri ASM katalógy. `write_input_init_runtime_report.py OUTPUTS WORK` pred generovaním znovu kontroluje všetky runtime proof hash položky. Harness ukončí svoj DOSBox po poslednom bode, nejde o prirodzený game exit.

Summary SHA `9ba35f37aafcbb650d89b248848cde080f7475f64b024269016e78917ba256e0`. Proof SHA `07905c5d36d2472992f1c81f73e2fe85f024760cd4140b1fc06e4b849c9f6dfb`. Packed EXE SHA `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`.

## Meranie

Prirodzené zachované scenáre4→5; ich prefixy sa prekrývajú a každý breakpoint sa nepočíta ako ďalší scenár. Katalóg118→122rozsahov, +37inštrukcií/+88B. Žiadny nový seeded replay. PASS1 bez zmeny57102PARTIAL/149CLASSIFIED ONLY/44UNKNOWN/0DEEP VERIFIED. BSS saved-vector a register buffer sa nepripočítavajú k historickým file bajtom. Dávka je lokálna, nie nová GitHub publikácia; Win16 a plná vstupná/DEMO parita zostávajú otvorené.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Úplné menovatele chýbajú, preto N/A. Iniciačný runtime nie je percento gameplay completeness.

| Oblasť | Predošlý odhad | Nové % | Aktuálny dôkaz (staršie riadky zachované) | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|skutočný BSF54 B load/decode|iné BSF/role blokov|resource sloty v runtime|
| Dátové typy a konštanty |95 %|N/A|511 runtime DWORD mimo file|149 B iba klasifikované, 44 B UNKNOWN|nepriame segmentové prístupy|
| Tabuľky a ukazovatele |93 %|N/A|14 prirodzených FAR resource pointerov,6B hlavičky0|plný resource lifetime a obsah|resource slot consumers|
| Funkcie / ASM / CFG |90 %|N/A|4 nové API/probe wrappers,88B/37inštrukcií|INT86 a ISR telá|ISR interrupt kontrakt|
| RNG |97 %|N/A|bez RNG runtime|prvý srand/rand|RNG caller trace|
| Scheduler |96 %|N/A|clock init prebehol medzi bodmi|main loop/scheduler|loop vstup|
| DEMO a vstupy |96 %|N/A|prirodzený INT9 install a aux probeFFFFh|key IRQ/DEMO poradie/close|prvý vstupný tick|
| Renderer / VGA |94 %|N/A|mask/plane store,transparentnosť a unsigned depth|skutočné VGA registre a výstup|DOSBox frame dump|
| GUARD / bossovia |93 %|N/A|bez AI runtime|map init|selector doména|
| Zbrane / projektily |92 %|N/A|bez damage runtime|effect callery|damage trace|
| Sprity / HUD / paleta |92 %|N/A|VGA init, nie vizuálna parita|paleta/sprity|resource load|
| SAVE / LOAD |92 %|N/A|BSF native file-check vrátený|SAVE/LOAD a chybové I/O|diskové scenáre|
| Windows Win16 |92 %|N/A|bez Win runtime|NE prostredie|samostatný Win16 test|

## Runtime testy na vykonanie

Pokračovať za0476:015C k RNG seed/asset inicializácii a prvému scheduler/input ticku. Samostatne zachytiť prirodzený IRQ9 handler a obnovu uloženého vektora pri mode1. Pre DEMO treba párovú input/RNG stopu, nie iba initialized flags. Pre NON-CODE44B zostáva read/write alias audit; tieto vstupné BSS polia ho nenahrádzajú.
