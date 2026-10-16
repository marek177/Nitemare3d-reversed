# Nitemare 3D — DOS historický kompilátor/linker

**Stav poznania: 15. 10. 2026**  
**Účel:** Archívna príloha k rekonštrukcii Nitemare 3D pre Windows 11. Nenariaďuje používať pôvodné nástroje pri modernej implementácii.

> **Rozsah a hranica dôkazov:** Nezachoval sa overený pôvodný `.MAK`/linker command line, kompletné `.OBJ` ani zdrojový strom autora. Nemožno preto poctivo vytvoriť *úplný a presný zoznam všetkých* pôvodných vstupov linkera a kompilátora. Nižšie je inventár všetkého, čo bolo možné identifikovať v dostupných starších analýzach, s výslovným odlíšením potvrdeného kódu, nájdených súborov historických nástrojov, bežných predpokladov a runtime závislostí.

## Legenda dôkazov

- **B — binárny dôkaz:** pôvodný herný EXE obsahuje identifikačný údaj alebo zhodné inštrukcie.
- **L — library fingerprint:** modul sa zhoduje s obsahom historického `.LIB`; pôvodný názov súboru pri autorovom linkovaní nie je tým automaticky potvrdený.
- **T — toolset porovnaný:** názov súboru je doložený v skúmanej distribúcii kompilátora, nie v pôvodnom build logu hry.
- **R — runtime import:** pôvodný Windows EXE má import daného modulu; jeho zodpovedajúci `.LIB` pri linkovaní sa nedá pomenovať s istotou.
- **H — hypotéza/typický build:** historicky bežná položka, presné použitie v Nitemare 3D nepreukázané.
- **X — výstup/dátový súbor:** nie pôvodný vstup kompilátora.

## A. DOS: N3D.EXE (1994–1995)

### A1. Potvrdená alebo binárne priraditeľná časť Microsoft DOS runtime

| Súbor/názov | Rodina | Stupeň | Prečo ho evidujeme |
|---|---|---|---|
| `MLIBCR.LIB` | Microsoft C/C++ 7.0, DOS Medium CRT | L | Historická knižnica obsahuje viacero strojovo zhodných modulov; porovnaný aj Microsoft C 6.00ax variant. Nemáme pôvodný linker príkaz. |
| `DOS\CRT0.ASM` | Microsoft CRT startup | B/L | Startup DOS verzie zodpovedá generácii Microsoft C/C++ 7.0; kontrola DOS verzie, volanie `main`, inicializácia CRT. |
| `GROWSEG.ASM` | CRT pomocný modul | L | Pri porovnaní s C7 dosiahnutá zhoda 138 bajtov. |
| `SEARCHSG.ASM` | CRT pomocný modul | L | Pri porovnaní s C7 dosiahnutá zhoda 124 bajtov. |
| `SCANSEG.ASM` | CRT pomocný modul | L | Pri porovnaní s C7 dosiahnutá zhoda 66 bajtov. |
| `DOS\NMSGHDR.ASM` | CRT diagnostika | L | Pri porovnaní s C7 dosiahnutá zhoda 63 bajtov. |
| `DOS\STDARGV.ASM` | CRT argumenty | L | Zhoda 153 bajtov s variantmi C6 aj C7; nerozlišuje konkrétnu verziu. |
| `MS Run-Time Library - Copyright (c) 1992, Microsoft Corp` | identifikačný reťazec v DOS EXE | B | Priamy atribučný reťazec; nejde o samostatný súbor. |

**DOS startup:** `N3D-UNFU` má C startup na file offsete `0x120F8`, sekvenciu rozlišujúcu runtime generácie na `0x121ED` a `main` na `0x4C86`. Pred `main` sa odovzdávajú tri 16-bitové argumentové slová, čo silno podporuje **Medium memory model (far code / near data)**. Tieto dôkazy nevylučujú upravený či novší patch Microsoft runtime.

### A2. WORX Toolkit 2.1

| Položka | Stupeň | Stav |
|---|---|---|
| `WORX TOOLKIT VERSION 2.1 COPYRIGHT 1993 BY MYSTIC SOFTWARE` | B | Reťazec priamo v rozbalenom DOS obraze; kód toolkit-u je integrovaný v EXE. |
| WORX audio + device subsystem | B | Statická analýza nášho archívu mapuje aplikačné wrappery `0x10BFC..0x11EE6`, prenos `INT 63h` a implementáciu toolkit-u `0x15BF7..0x1BDA1` (adresy z konkrétneho rekonštruovaného DOS obrazu). |
| **Názov pôvodného WORX `.LIB`, `.OBJ` a `.H`** | **neznámy** | Pôvodná distribúcia SDK ani úplný linker záznam neboli v dostupnom archíve overené. Nie je oprávnené tvrdiť, že sa konkrétne volali `WORX.LIB` alebo `WORX.H`. |

WORX je knižnica zvuku a hardvérového ovládania, **nie samostatný C/C++ kompilátor**. Dokumentácia komunity uvádza použiteľnosť s Microsoft C/C++, Borland C/C++, Turbo Pascal aj assemblerom; samotná prítomnosť WORX teda neurčuje výrobcu kompilátora.

### A3. Historické nástroje DOS buildu

| Súbor/položka | Stupeň | Komentár |
|---|---|---|
| `CL.EXE` | H | Typický ovládač Microsoft C/C++ kompilácie; presný súbor, verzia a spúšťací príkaz autora nie sú doložené. |
| `LINK.EXE` | H | Microsoft linker je logická rekonštrukcia build procesu; originálna DOS linker hlavička/version string neboli identifikované. |
| `.C`, `.H`, prípadne `.ASM`, `.OBJ`, `.LIB` herných modulov | H | Formáty historického build procesu; **názvy pôvodných herných zdrojových súborov neboli obnovené**. |
| `.MAK`, `.BAT`, `.MAP`, `.LST` | H | Možné projektové/pomocné súbory; nepreukázané ako konkrétne historické súbory autora. |
| `DIET` (DOS EXE packer) | B/H | Analyzovaný DOS EXE je komprimovaný typom DIET; kompresia je post-link krok. Presný názov a verzia pôvodného spustiteľného packera neboli overené. |

**Nie je potvrdené:** Borland C++ alebo Watcom ako tvorca pôvodnej DOS verzie; pozor na automatický prenos poznatkov o iných dobových hrách.


## Limity a nasledujúci dôkaz

Pôvodné .MAK/.OBJ a presný DOS linker command line nie sú známe. `MLIBCR.LIB`
znamená fingerprint rodiny DOS Medium C runtime, nie doklad originálneho
plného link input názvu. Žiadne binárky kompilátora sa nedistribuujú.
