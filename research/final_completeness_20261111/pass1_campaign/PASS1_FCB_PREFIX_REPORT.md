# PASS1: dva parsed FCB prefix buffery

**32 B CLASSIFIED ONLY → PARTIAL**, 10 dielčích polí v dvoch susedných 16-bajtových záznamoch. Image [29BE0,29BF0), DS:24D0 a [29BF0,29C00), DS:24E0. Počiatočné bajty sú nulové. Typ je doložený pôvodnými INT21/AX2901 volaniami a nezávislým primárnym zdrojom MS-DOS2.0, nie samotnými nulami. Žiadny DEEP VERIFIED.

## Typy a hranice

| Offset v každom zázname | Dĺžka | Lokálne doložený typ |
|---|---:|---|
|0|1|drive BYTE|
|1|8|filename BYTE[8]|
|9|3|extension BYTE[3]|
|12|2|WORD nulovaný pri parse inicializácii|
|14|2|WORD nulovaný pri parse inicializácii|

Nie je to tvrdenie o celom 37-bajtovom otvorenom FCB. Parser vytvára prefix, ktorý potrebuje EXEC parameter blok. Iné polia otvoreného FCB sa k týmto 16 B nedopĺňajú. Predchádzajúca analýza spawn parametrov už doložila FAR pointery na 24D0/24E0; táto dávka uzatvára základné prefix členenie, nie celé exec/spawn.

Primárny zdroj [Microsoft MS-DOS2.0 FCB.ASM](https://github.com/microsoft/MS-DOS/blob/main/v2.0/source/FCB.ASM) obsahuje MakeFcb: inicializácia drive, 8+3 znakových oblastí a dvoch WORD za nimi. [MISC.ASM](https://github.com/microsoft/MS-DOS/blob/main/v2.0/source/MISC.ASM) spája funkciu 29h s MakeFcb a vrátením posunutého SI. Lokálne kópie a presné SHA/pevné raw URL sú v dos_parse_reference/source_manifest.json. Pri prenose záveru na konkrétny neskorší DOS alebo DOSBox implementation zostáva verzia a správanie otvorené; úplný write-bound dôkaz všetkých parserových vetiev a KANJI konfigurácií sa tu netvrdí.

## Pôvodný caller a segmenty

11EE:34DE..34F5, image [153BE,153D5), 23 B. PUSH DS/POP ES; SI=WORD[24C4]+1; DI=24D0; AX=2901; INT21; potom znovu AX=2901 a DI=24E0; INT21. SI sa pred druhým volaním neobnovuje. Prvý AL návrat sa neporovnáva, druhé volanie prebehne aj pri AL=FFh. Druhý AL/SI zostávajú v registroch na konci testovaného prefixu. SS je v emulácii nezávislý; oba destinačné pointery majú ES=DS. Žiadne nové celé funkčné pokrytie: je to vnútorný úsek spawn rutiny.

```text
ES = DS
SI = WORD[24C4] + 1
INT21(AX=2901, DS:SI, ES:DI=24D0)
// Bez kontroly prvého AL alebo obnovenia SI
INT21(AX=2901, DS:SI_vrátené_parserom, ES:DI=24E0)
```

## Kontrolovaná emulácia a reprodukcia

72 prípadov = 2 load bázy × 3 prvé návratové statusy × 3 druhé statusy × 4 vrátené SI. Statusy 0,1,FFh, SI 0,1,300Ah,FFFFh. Vykonáva sa pôvodný caller; INT21 parser je modelovaný, zapíše rozlíšiteľné 16-bajtové vzory. Overené presné AX/DS/ES/DI/SI na oboch volaniach, výsledné registre, nezmenený SP a guard BYTE okolo 32 B. Nulové odchýlky. Tieto vzory nie sú očakávanými skutočnými FCB pre nejaké meno a emulácia neoveruje OS write bounds; prefix typ a členenie sa opierajú osobitne o primárny zdroj.

audit_replay_pass1_fcb_prefix.py IMAGE INVENTORY DECODER EMULATOR SOURCE_DIR OUT; promote_pass1_fields.py s mapou pass1_startup_segments; verify_pass1_partition.py. Skript kontroluje SHA zdrojov a charakteristické inicializačné kroky, ale sám nevykonáva MAKEFCB. Kanonický image SHA-256 e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297. Iced-x861.21.0/Unicorn2.1.4. Exporty obsahujú rozdelenie polí, ASM prefix, cases a summary. Prirodzený DOSBox-X runtime0.

## Meranie

**57 101 B PARTIAL, 150 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57 295 B. Nezávislá kontrola 887 intervalov potvrdila presné členstvo, všetky hash hodnoty a nulové diery/prekryvy. Integrita partition nie je úplná sémantika. Nové lokálne dôkazy zatiaľ nie sú v poslednej publikovanej GitHub snímke.

SHA mapy `899ba518a5b8b64b24837e4f40f14e0c918e0bbb2777d2e13ae0803bb42482ed`; SHA cases `71cba5717e3996544502ec2dc4567e7120a5a824da802252f4b3f4cf578fb8e8`; SHA source manifestu `7303ef395594ffa44db16e58a470cbec08b7622de64dd151140d03a6268ae918`.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, preto N/A; historické odhady sa nemenia podľa test count alebo mapovej integrity.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|externý DOS FCB prefix kontrakt|konkrétna DOS verzia|parser runtime trace|
| Dátové typy a konštanty |95 %|N/A|32 B / 10 polí PARTIAL|150 B iba klasifikované|zvyšné alias odkazy|
| Tabuľky a ukazovatele |93 %|N/A|dva 16 B exec prefixy|úplný EXEC ABI|parameter block trace|
| Funkcie / ASM / CFG |90 %|N/A|23 B caller prefix|celá spawn rutina|spawn CFG closure|
| RNG |97 %|N/A|bez nového dôkazu|prirodzené poradie|DEMO trace|
| Scheduler |96 %|N/A|bez nového dôkazu|prirodzené callery|call graph|
| DEMO a vstupy |96 %|N/A|bez nového dôkazu|driver ABI|input closure|
| Renderer / VGA |94 %|N/A|bez nového dôkazu|setup|VGA init CFG|
| GUARD / bossovia |93 %|N/A|bez nového dôkazu|selector doména|descriptor flag8|
| Zbrane / projektily |92 %|N/A|bez nového dôkazu|damage callery|effect producer|
| Sprity / HUD / paleta |92 %|N/A|bez nového dôkazu|resource identity|resource parser|
| SAVE / LOAD |92 %|N/A|CRT spawn dáta oddelené|herné I/O|stream trace|
| Windows Win16 |92 %|N/A|bez nového Win dôkazu|iné exec mechanizmy|Win runtime kontrakt|

## Runtime testy na vykonanie

V DOSBox-X sledovať skutočný INT21/29 parser, SI/AL a presný write rozsah do oboch prefixov; použiť mená s diskom, prázdne meno, wildcard a neplatný drive. Potom sledovať EXEC parameter blok bez automatického spúšťania hostiteľských programov. Testovať príslušný DOS variant, nie prenášať MS-DOS2 source ako univerzálny dôkaz. PE32 sa nevytvára.
