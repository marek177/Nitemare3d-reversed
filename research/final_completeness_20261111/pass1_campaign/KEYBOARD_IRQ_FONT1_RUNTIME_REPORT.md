# DOS2: rekonštruovaný INT09h/IRQ1, prirodzený vstup a font1

Nová dávka pridáva **štyri ohraničené funkcie,388B/152 inštrukcií**, **14336 riadených replay prípadov** a **17. prirodzený DOSBox-X scenár**. Prvýkrát je v tejto kampani zachytené skutočné čítanie make/break medzerníka v pôvodnom hernom IRQ handleri, zmena herného bitu0200h, vytvorenie BIOS3920h a jeho spotrebovanie pri prirodzenom odchode z wait0424. Nasledujúci font1 sa zhoduje s reálnym UIF.DAT v celom buffri a128FAR pointeroch.

Katalóg má134 funkcií,5145 inštrukcií/12844B a988623 riadených replay prípadov. PASS320 mapa sa nemení: **57102B PARTIAL /149B CLASSIFIED ONLY /44B UNKNOWN /0B DEEP VERIFIED**. Ani chýbajúce historické instruction-start záznamy IRQ netvorili pôvodný NON-CODE baseline; nový kód nezvyšuje code-in-NONCODE počet.

## Funkčné hranice a nezávislý ASM/CFG dôkaz

|Funkcia|Kanonický segment:IP, koniec exclusive|Image interval|Vykonateľné B /inštrukcie|
|---|---|---|---|
|keyboard_irq9|06B0:0000..0134|[06B00,06C34)|301/114|
|keyboard_bios_poll|06B0:01D0..01E2|[06CD0,06CE2)|18/7|
|keyboard_bios_drain|06B0:01E2..0203|[06CE2,06D03)|33/13|
|crt_bioskey_word|11EE:39B0..39D4|[15890,158B4)|36/18|

IRQ má308B span, ale301B dosiahnuteľných CFG inštrukcií. Sedem izolovaných bajtov90h nebolo importovaných do jeho CFG; samotná hodnota90h ani medzera nedokazuje padding. Všetkých114 IRQ instruction-startov chýba v historickom35648-start inventári. Rekonštrukcia preto dekóduje priamo hashovaný pôvodný obraz a používa známy IVT entrypoint z inštalátora a prirodzené breakpointy. Ostatné tri rozsahy sú navyše byte-exact porovnané so starým inventárom. CSV obsahujú každý ASM bajt aj lokálne CFG hrany.

Register-context kontrakt IRQ je odlišný od bežného FAR volania: vstupuje cez hardvérový interrupt frame a končí16-bit IRET. Testy explicitne pripravujú tento frame, nevydávajú RETF stub za celý handler. Pracovný názov keyboard_irq9 označuje DOS interrupt vector09h, teda klávesnicovú hardvérovú linku IRQ1, nie linku IRQ9. PUSHAD uloží aj ESP slot; POPAD tento slot preskočí. Skutočný SP sa overuje oddelene po lokálnom obnovení a IRET.

## IRQ algoritmus a dátové závislosti

```text
save EAX,ECX,EDX,EBX,ESP,EBP,ESI,EDI; save DS,ES
BP = SP
reserve 2 local bytes; preserve extra DS on local stack
DS = relocated DGROUP2771h
CLD
raw = IN_BYTE(60h)
pressed = ((raw & 80h) == 0)
scan = raw & 7Fh
update mapped game bit to pressed
  except shifts2Ah/36h are ignored after previous rawE0h
previous_raw = raw
PUSHF; CALL FAR saved_ISR_at_DS3F52
if BYTE[DS3CD1] != 0: CALL keyboard_bios_drain
if WORD[DS3CD6] == 4: WORD[DS3CD4] = 0
SP = BP
restore ES,DS and saved32-bit general registers
IRET
```

Saved ISR sa volá FAR indirect cez DS3F52 a dostáva PUSHF frame vhodný pre IRET. Jeho interné BIOS telo je v riadenom replay nahradené IRET stubom; nové runtime stopy dokazujú portové a BIOS-queue účinky, ale nepridávajú samostatný breakpoint vnútri uloženého BIOS handlera. Presný compiler/library pôvod tejto hernej obsluhy nie je uzavretý.

|Scan code po maskovaní7Fh|Cieľový game bit|Lokálne pravidlo|
|---|---|---|
|01|DS3F50 bit0|nastaviť podľa make/break|
|1D|DS3F50 bit7|zachovať ostatné lowBYTE bity|
|2A|DS3F50 bit6|ignorovať po rawE0h|
|36|DS3F50 bit5|ignorovať po rawE0h|
|38|DS3F51 bit0|nastaviť podľa make/break|
|39|DS3F51 bit1, teda WORD bit0200h|nastaviť podľa make/break|
|48|DS3F50 bit1|nastaviť podľa make/break|
|4B|DS3F50 bit3|nastaviť podľa make/break|
|4D|DS3F50 bit4|nastaviť podľa make/break|
|50|DS3F50 bit2|nastaviť podľa make/break|

Ostatné scany nemenia tieto game bity; raw byte sa stále uloží do DS34BA a uložený ISR sa volá. E1h sa tu nespracúva ako plná viacbajtová sekvencia. Flag3CD1 a mode3CD6 sa popisujú presným účinkom, nie nepreukázaným názvom DEMO režimu. Ich producenti a význam3CD4 zostávajú otvorené.

Všetkých šesť pomenovaných consumer polí je v runtime BSS mimo pôvodného EXE; `irq_consumer_fields.csv` nepredstiera nové file-backed dáta ani nové NON-CODE bajty.

## BIOS wrapper, poll a drain

CRT-segment wrapper11EE:39B0 načíta AH z dolného BYTE WORD argumentu, drží AH&0Fh v DL a vykoná INT16h. Presná post-normalizácia:

```text
if ZF_after_INT16 and (command & 0Fh)==1: AX=0
else if (command & 0Fh)==2: AX remains as returned
else if AX==0: AX=FFFFh
```

Je to rozpoznaný lokálny BIOS-key wrapper podľa kódu/ABI; presná verzia zdrojovej CRT knižnice nebola source-match overená. Názov `crt_bioskey_word` je pracovný funkčný názov.

Poll06B0:01D0 volá wrapper s argumentom11h a vracia **AL=0/1** podľa AX==0 aleboAX>=1. AH môže ostať zo vstupnej BIOS hodnoty; celého AX nemožno všeobecne nazvať BOOL WORD. Drain01E2 opakovane polluje a pri dostupnosti volá wrapper s10h, potom vynuluje WORD DS3F50. Poll/drain sú v tejto dávke kompletne byte/CFG dekódované, nie samostatne modelovo replayované; prirodzený wait path a queue záznamy poskytujú nový runtime dôkaz konkrétnej vstupnej cesty.

## Riadené replay testy a ich limity

12288 celých IRQ prípadov = 2 relokácie ×256 raw scan bajtov ×3 predchádzajúce raw hodnoty(00/E0/E1) ×2 komplementárne game WORD vzory(A55A/5AA5) ×2 flush flagy ×2 mode hodnoty(0/4). Starý BIOS ISR, IN60 input a conditional drain helper sú modelované. Pred stubovaným BIOS IRET sa overuje správny game WORD, uložený raw a vymazaný DF. Po návrate sa kontroluje všetkých sedem uložených32-bit GP registrov, DS/ES, SS/SP, CS/IP a low16 FLAGS pre dve pripravené IF/DF kombinácie. Nie je to dôkaz všetkých možných high EFLAGS stavov.

Pri load0 je SS=DGROUP, pri load1000h je SS posunuté o400h; handler sa testuje aj s DS!=SS. Osobitných2048 prípadov wrappera pokrýva 2 relokácie ×256 command BYTE hodnôt ×2 INT AX hodnoty(0/3920h) ×2 ZF. INT16 zariadenie je modelované; nepodporované AH hodnoty v tejto syntetickej doméne nedokazujú schopnosti skutočného BIOS.

Všetky14336 prípady prešli. Nezahŕňajú arbitrážne BIOS side effects, nestované IRQ, celé DEMO alebo gameplay. Žiadne percento sémantického uzavretia sa z počtu testov neodvodzuje.

## Prirodzený DOSBox-X vstup

Izolovaný disk má23 zdrojových súborov vrátane explicitne pridaného CD obrázka. Pred `DEBUGBOX N3D20.EXE` sa vykonal podporovaný príkaz `autotype -w 15 -p 1 space`. [Oficiálny popis AUTOTYPE](https://github.com/joncampbell123/dosbox-x/wiki/DOSBox%E2%80%90X%E2%80%99s-Supported-Commands). Matching-release zdrojové referencie a ich hashy sú v `keyboard_runtime_control/source_manifest.json`.

AUTOTYPE používa mapper a vo vybranej implementácii čaká v samostatnom vlákne15 wall-clock sekúnd; press/release má50ms medzeru. Nie je to zápis do BIOS queue alebo hernej pamäte. Debugger breakpointy zastavujú CPU, zatiaľ čo toto vlákno môže napredovať, preto sa nevyvodzuje bežná neprerušovaná latencia vstupu. Zaznamenaný funkčný priebeh je napriek tomu skutočný: pôvodná hra číta skutočný emulovaný port a vytvára/spotrebuje BIOS položku.

|Bod|Pozorovaný raw port byte|Game WORD3F50|BIOS head/tail|Prvý BIOS WORD|
|---|---|---|---|---|
|wait0424 entry|ešte nečítaný|0000|001E/001E|0000|
|IRQ make po IN60|39h v AL|0000 pred spracovaním|001E/001E|0000|
|IRQ make pred IRET|previous raw39h|0200|001E/0020|3920|
|IRQ break po IN60|B9h v AL|0200 pred spracovaním|001E/0020|3920|
|IRQ break pred IRET|previous rawB9h|0000|001E/0020|3920|
|po prirodzenom wait návrate|previous rawB9h|0000|0020/0020|3920 v už spotrebovanom slote|
|font1 ready083D:0054|previous rawB9h|0000|0020/0020|3920|

Make IRQ vstúpilo so SS=2F95h, SP=E7B0h; break IRQ so **SS=1DE3h, SP=40D9h**, pričom DS ostával2F95h. Pri breakpointoch po IN bol SP vždy o40 nižší. Pred IRET boli zachytené AX/BX/CX/DX/DS/ES/SS/SP identické s hodnotami pri príslušnom IRQ entry. Pôvod odlišného break stacku nie je bez call-site/interrupt trace uzavretý; neoznačujeme ho automaticky za DOS, BIOS alebo herný stack.

Kanonický handler je06B0:0000, **skutočne0ED4:0000** pri load0824h. Tieto adresné priestory sa nesmú zameniť. Konečný endpoint je kanonicky083D:0054, skutočne1061:0054. Capture obsahuje50 raw súborov,9 input stopov, launch argumenty, konfiguráciu a kompletný debugger transcript. Whitelist nepovoľuje SM/SR alebo I/O portové zásahy; iba breakpointy, RUN, dotazy a pamäťové dumpy.

UNKNOWN44B malo od CRT entry po endpoint nulové cached-value udalosti a candidate hook4B sa na koncoch nezmenil. BPLM nezachytáva čítania, zápisy rovnakej hodnoty alebo všetky interné host callback zmeny; preto sa klasifikácia nemení.

## Font1 a nová nezrovnalosť headerov

UIF index1 má1145B zo source intervalu[1092,2237). Cieľ je20B9:04B0, image **[21040,214F0)**, kapacita1200B. Parser a capture sa zhodujú na všetkých zdrojových bajtoch po bitreverse a55B nulového runtime zvyšku.

|Image interval, end exclusive|B|Dátová rola|
|---|---:|---|
|[21040,21042)|2|header0B/0B, index0; úplný význam otvorený|
|[21042,214B9)|1143|127 výškových/šírkových záznamov,254B headerov +889B bitmap|
|[214B9,214F0)|55|nulový zvyšok kapacity, nie dokázaný padding|

**Header0B/0B nie je presným maximom zaznamenaných rozmerov: font1 má maximum10×10, nie11×11.** Predošlá zhoda headerov s maximami vo font0/font2 preto neoprávňuje univerzálnu interpretáciu header=max-glyph-size. Význam metrics index0 sa musí doložiť callerom alebo runtime textovou cestou.

128FAR pointerov je DS[3890,3A90), image **[2AFA0,2B1A0)**,512B BSS mimo súboru. Všetky majú správny runtime segment28DDh a offset04B0h+record_position. Flagy skupín0/1/2 sú1 a selected_group=1. V tomto jednom endpoint capture sú nezávisle overené aj nezmenené skupiny0 a2: spolu381 variabilných záznamov a384FAR ukazovateľov.

![Rekonštrukcia font1 bitmapových bajtov, nie runtime text screenshot](font1_keyboard_fields/font1_bitmap_atlas.png)

Refinement všetkých troch bufferov má3600 už PARTIAL file-backed B; nejde o3600 nových typovaných bajtov. Celkový pomenovaný runtime BSS table súčet je4054B a zahŕňa nových512B font1 pointerov. Source/field/pointer CSV a JSON mapy zachovávajú presné hranice; metriky, signed-char indexy128..255 a error/cache domény zostávajú PARTIAL.

## Reprodukcia

- `audit_replay_keyboard_irq.py IMAGE INVENTORY DECODER EMULATOR OUT`:4 ASM/CFG CSV,12288 IRQ a2048 wrapper prípadov. IRQ nikdy nepreberá chýbajúce hranice zo starého inventára.
- `runtime_watch_keyboard_font1.py DOSBOX_EXE GAME_DIR IMAGE RELOCS OUT WORK startup CD_ASSET`: pôvodný EXE, podporovaný AUTOTYPE,9 zachytených bodov; frozen helper `dosbox_watch_support_autotype_v1.py`.
- `verify_keyboard_font1_capture.py IMAGE RELOCS MAP OUT WORK`: zdrojové SHA, relokovaný obraz,50 captures, command whitelist, oba IRQ scany, register/stack konzistencia, BIOS queue a všetky tri fonty.
- `audit_font1_keyboard_fields.py IMAGE UIF RUNTIME WORK OUT`:127 záznamov/128 pointerov, dátové intervaly, consumer BSS polia,9 keyboard-stage riadkov a atlas.
- Centrálny katalóg importuje4 nové rozsahy,14336 úspešných testov a1 unikátny runtime proof. Nepridáva staršie prípady opakovane.

Najnovšia publikovaná analytická snímka pred touto dávkou má16 runtime scenárov. Táto nová dávka zostáva lokálna, kým nebude zaznamenané nové potvrdenie GitHub publikácie.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Úplné menovatele chýbajú, preto N/A. Iniciačný runtime nie je percento gameplay completeness.

| Oblasť | Predošlý odhad | Nové % | Aktuálny dôkaz (staršie riadky zachované) | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|CD DSTOPEN.IMG:128B header,19781B RLE,769B tail; 64000 pixelov|iné PCX/IMG domény; stride/planes ignorované|textové resource a menu dáta|
| Dátové typy a konštanty |95 %|N/A|font1:1145B→127 záznamov/889B bitmap; header11,11 ≠ max10,10|header sémantika a signed-char domény|textové metriky a header callery|
| Tabuľky a ukazovatele |93 %|N/A|nových128 font1FAR; všetky384FAR pointery skupín0/1/2 byte-exact|pointer index0 a signed-char indexy|textové caller domény|
| Funkcie / ASM / CFG |90 %|N/A|4nové funkcie388B/152inštrukcií;114IRQ starts absent v starom inventári|nestedIRQ, drain/mode producenti a Win ekvivalent|IRQ kontext a register restore vetvy|
| RNG |97 %|N/A|bez RNG runtime|prvý srand/rand|RNG caller trace|
| Scheduler |96 %|N/A|IRQ make/break s odlišnými SS; foreground stack obnovený|mode4/scheduler a pôvod alternate SS|interrupted CS:IP a stack owner|
| DEMO a vstupy |96 %|N/A|port60 make39/breakB9; game0200; BIOS3920; prirodzený wait exit|DEMO poradie, nestedIRQ, flags/mode producenti|menu a širšie vstupné domény|
| Renderer / VGA |94 %|N/A|programmed4000→real4000 v neskoršom bode;4roviny a AC overené|host-surface/úplný scanout, text/menu|scanout a prirodzený vstup|
| GUARD / bossovia |93 %|N/A|bez AI runtime|map init|selector doména|
| Zbrane / projektily |92 %|N/A|bez damage runtime|effect callery|damage trace|
| Sprity / HUD / paleta |92 %|N/A|DAC768 zložiek;71 použitých farieb,192000 RGB6 komponentov bez rozdielu|nepoužitý255 sa líši; Win OS a host frame|prirodzený text/font metrics a scanout|
| SAVE / LOAD |92 %|N/A|BSF native file-check vrátený|SAVE/LOAD a chybové I/O|diskové scenáre|
| Windows Win16 |92 %|N/A|Win1104funkcie/229inštrukcií,23fixupcalls,22replay|skutočnéWin16DS/API/runtime|CreatePalette/WinG trace|

## Runtime testy na vykonanie

1. Pokračovať z083D:0054 cez textové vykreslenie a ďalšie wait/menu body s presne riadenou sekvenciou klávesov. Zachytiť prirodzené menu a map init.
2. Určiť pôvod SS1DE3 pri break IRQ cez prerušený CS:IP/stack frame a call trace; nepreberať stack invariant DS=SS z foregroundu do IRQ.
3. Uzavrieť producentov3CD1,3CD4,3CD6, presné mode4 účinky, extendedE0/E1 vstupy a väzbu na DEMO/scheduler.
4. Doložiť header0B/0B consumerom a preveriť signed-char domény textových metrík. Font1 vyvracia hypotézu univerzálneho presného max rozmeru.
5. Porovnať IRQ a BIOS wrapper s inými DOS/Win16 verziami, zachytiť error/restore lifecycle a širšie UNKNOWN44 read/write dôkazy.
