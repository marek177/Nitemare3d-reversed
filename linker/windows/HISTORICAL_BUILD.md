# Nitemare 3D — Win16 historický kompilátor/linker

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

## B. Windows 3.1 / 16-bit: NITE3W.EXE

### B1. Porovnané fázy Microsoft Visual C++ 1.5 generácie

| Súbor | Stupeň | Úloha |
|---|---|---|
| `CL.EXE` | T | Ovládač kompilácie |
| `C13216.EXE` | T | C compiler pass |
| `C1XX3216.EXE` | T | C++ compiler front-end |
| `C23216.EXE` | T | Compiler pass |
| `C33216.EXE` | T | Compiler pass |
| `LINK.EXE` | B/T | Microsoft Segmented Executable Linker; NE verzia **5.60** priamo v pôvodnom EXE |

V porovnávaných ISO Visual C++ 1.50, 1.52c a doplnkovom `MSVC15` na disku Visual C++ 2.0 bolo **všetkých päť compiler súborov bajtovo identických**. Nemožno preto presne určiť patch level samotného prekladača podľa vygenerovaného strojového kódu. V 1.52c je `LINK.EXE` identifikovaný ako 5.60.339, avšak pôvodná NE hlavička zachováva len `5.60`.

### B2. Skutočne rozpoznaný statický kód knižníc

| Súbor/modul | Stupeň | Funkcia / detail |
|---|---|---|
| `MAFXCW.LIB` | B/L | Statická knižnica **MFC 2.5**. Najsilnejšie zhodné úseky zo skúmaných vydaní pochádzajú z Visual C++ 1.50. |
| `MLIBCAW.LIB` | B/L | Microsoft 16-bit Windows C runtime; viacero dlhých zhodných úsekov v segmente 2 pôvodného EXE. |
| `DCPREV.CPP` | L | Názov pôvodného Microsoft MFC modulu v OMF archíve `MAFXCW.LIB`; verziovo diskriminujúce 112- a 66-bajtové bloky. **Nie je to pôvodný zdroj hry.** |
| `WINFRM.CPP` | L | Názov Microsoft MFC modulu v OMF archíve; verziovo diskriminujúca 68-bajtová zhoda. **Nie je to pôvodný zdroj hry.** |
| MFC triedy `CObject`, `CCmdTarget`, `CFont`, `CScrollView` | B | Triedy / symboly v pôvodnom Windows EXE; nejde o názvy vstupných súborov. |

MFC je **staticky linkované**: `NITE3W.EXE` nemá externý import `MFC250.DLL`. Práve `MAFXCW.LIB` (Visual C++ 1.50) má oproti skúmaným variantom 1.52c / MSVC15 na disku VC2 viac diskriminujúcich zhodných úsekov. Toto nie je dôkaz, že každý pôvodný compiler/linker súbor pochádzal presne z 1.50.

### B3. Originálne Win16 runtime importy (nie mená pôvodných `.LIB`)

| Import v NE | Bežné zodpovedajúce súbory pri behu | Stupeň |
|---|---|---|
| `KERNEL` | `KERNEL.EXE` / Win16 systémový modul | R |
| `GDI` | `GDI.EXE` | R |
| `USER` | `USER.EXE` | R |
| `KEYBOARD` | driver/systémový modul klávesnice | R |
| `COMMDLG` | `COMMDLG.DLL` | R |
| `MMSYSTEM` | `MMSYSTEM.DLL` | R |
| `SHELL` | `SHELL.DLL` | R |
| `WING` | `WING.DLL` | R |
| `DISPDIB` | `DISPDIB.DLL` | R |
| `joystick.drv` | dynamicky používaný driver | dynamická referencia, nie priamy NE import |

Toto je **úplný zoznam 9 priamych importovaných NE modulov** pre kontrolované pôvodné Windows V1.8/V1.10 súbory. Osobitný `.LIB` použitý pri ich linkovaní (napr. typové import knižnice SDK) nebol priamo identifikovaný. `WINGDE.DLL`, `TOOLHELP.DLL` a niektoré ďalšie závislosti sa môžu vyskytovať v samotnom WinG, no nepatria medzi deväť priamych importov NITE3W.

### B4. Pravdepodobné, ale neobnovené projektové vstupy

| Typ / možný názov | Stupeň | Čo naozaj vieme |
|---|---|---|
| Pôvodné `.CPP`, `.C`, `.H` súbory Nitemare 3D | H | Existovali vstupné zdrojové moduly, ich presné mená však pôvodný EXE nedokladá. |
| `NITE3W.CPP`, `NITE3W.H` | H | **Len možná** MFC projektová konvencia podľa mena aplikácie; nie potvrdené názvy. |
| `NITE3W.RC`, `RESOURCE.H`, `.RES` | H | Typický resource build pre Win16 MFC aplikáciu; pôvodné konkrétne názvy neoverené. |
| `WINDOWS.H`, `AFXWIN.H`, prípadne `WING.H` | H | Typické Windows SDK / MFC / WinG hlavičky; nevieme, ktoré a pod akými cestami autor skutočne inkludoval. |
| `NITE3W.DEF`, `NITE3W.MAK`, `.OBJ`, `.MAP` | H | Možné link/project medzisúbory; presné názvy a existencia nepreukázané. |
| `RC.EXE`, `NMAKE.EXE` | H | Typické nástroje dobového resource/build workflow, nie overený autorov pôvodný príkaz. |
| `LIBW.LIB` | H | Známa spoločná Windows SDK 3.1 importná knižnica (dobový Microsoft KB článok Q68081); **u Nitemare 3D jej použitie priamo nedoložené**. |
| Win16 Windows SDK / WinG import `.LIB` | H | Importy DLL v NE sú potvrdené, ale **ďalšie konkrétne názvy importných `.LIB` použitých pri linkovaní nie**. |

### B5. Porovnané a odmietnuté verzie nástrojov

- **Visual C++ 1.50 / 1.52c:** zodpovedajúce 16-bit compiler family; MFC fingerprint favorizuje 1.50.
- **Visual C++ 2.0:** hlavný toolset je Win32, ale inštalačné médium má tiež starší **`MSVC15/`** 16-bit toolset.
- **Visual C++ 4.0:** hlavný compiler je Win32, avšak doplnkový disk obsahoval `MSVC152c.iso` so starým 16-bit toolsetom.
- **Visual C++ 4.1 / 4.2 / 5.0:** skúmané hlavné toolsety sú Win32; bez samostatných starých 16-bit nástrojov nie sú pôvodnými priamymi producentmi Win16 NE hry.


## Limity a nasledujúci dôkaz

EXE hlavička 5.60 neurčuje presný LINK.EXE patch. Compiler štádiá vo VC++ 1.50
a 1.52c sú bajtovo zhodné; MFC fingerprint zvýhodňuje knižnicu 1.50,
nie jednoznačnú verziu celého IDE. Nezamieňajte runtime import s import .LIB.
