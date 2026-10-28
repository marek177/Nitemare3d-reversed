# Nitemare 3D Win 1.10 — Ghidra 12.2, prechod 2

## Zistenie

Najväčší zostávajúci neklasifikovaný rozsah `1018:48B7–563B` obsahuje jeden úvodný bajt a **865 po sebe idúcich 4-bajtových far pointerov** na `48B8–563B`. Každý selector word je doložený originálnym NE segmentovým relokačným reťazcom. Pointery mieria na **317 jedinečných kódových cieľov**; 94 nemalo samostatný funkčný vstup v predchádzajúcom projekte. Obnovil som všetkých 94 vstupov a tabuľku definoval ako dáta s explicitnými referenciami.

Pri 92 nových krátkych funkciách je presne doložené telo vrátane návratových registrov a stack cleanup. Pri 37 getteroch je návratová konštanta spojená s pomenovaným deskriptorom triedy. Ide prevažne o MFC framework, nie o novú hernú mechaniku.

Úplná sémantická obnova hry ani runtime parita nie sú dokončené. Tento prechod nevykonal žiadny beh hry.

## Identita a nástroj

- EXE: 230 400 B, SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`.
- Ghidra 12.2, build 20261016; Java 25.0.2; headless, uložený projekt `WIN110`.
- Adresy `1000/1008/1010/1018` zodpovedajú NE kódovým segmentom 1–4. Inicializované DS dáta sú NE segment 10, v projekte `1048`.

## Dôkazový reťazec

| Status | Tvrdenie | Primárny zdroj a miesto | Istota |
|---|---|---|---|
| Confirmed | Celá oblasť 48B8–563B pozostáva zo 865 far pointerov. | NE seg4 relokačné záznamy #1, #2, #3 (číslované od 0), rozbalené type-2 source chains; zdroje selectorov presne `48BA,48BE,…,563A`. | High |
| Confirmed | V tabuľke je 593 cieľov do NE1, 219 do NE2 a 53 do NE3. | `pass2/far_pointer_table.tsv`, `relocation_chain_sites.json`. | High |
| Confirmed | 865 načítaných pointerov v Ghidre sa zhoduje s offsetom a selectorom odvodeným z pôvodného EXE. | `N3DDefineFarTable.java`: kontroluje oba wordy pred definovaním dát; úspešný beh `pass2-verify-console.log`. | High |
| Confirmed | 94 cieľov nemalo predchádzajúci samostatný funkčný vstup; všetkých 94 bolo vytvorených. | `scripts/candidates3.txt`, `pass2-results/recovery3.tsv`. | High pre adresy, hranice zložitejších funkcií zostávajú predmetom kontroly |
| Confirmed | 92 krátkych tiel presne zodpovedá pôvodným bajtom. | `verify_leaf_bodies.py`, `pass2/leaf_byte_verification.json`; 498 B a dva selector operandy overené cez relokačné reťazce. | High pre inštrukčné správanie |
| Confirmed | `1000:0862` vracia `DS:0544`; deskriptor obsahuje far názov `1000:04FA`, text `CFile`, veľkosť objektu 8 B a predka `DS:04EE`. | Getter, načítané DS dáta a názov v kódovom segmente. | High |
| Confirmed | `1000:068A` porovnáva deskriptor a nasleduje word `descriptor+0x0C`, kým nenájde zhodu alebo nulu. | Disassembláž a C export; slot 0 objektovej virtuálnej tabuľky poskytuje prvý deskriptor. | High |
| Confirmed / Inferred | `1000:06C0` je runtime tvorba objektu podľa deskriptora. | Číta veľkosť na `+4`, alokuje cez `1008:5FE0`, cez `0730` kontroluje/volá callback na `+8/+0A`, pri zlyhaní uvoľní pamäť cez `5FD0`. Presná výnimková a ABI časť zostáva Partial. | High pre operácie, Medium pre úplný kontrakt |
| Confirmed / Inferred | `1000:092C` patrí do CFile cesty otvorenia/vytvorenia. | `0890` zapisuje vtable `1018:4934`; slot 0 → getter `0862` → deskriptor/názov CFile; slot `+18h` na `494C` → `092C`; helpery `6FB2/6FEC` nastavujú DOS AH `3C/3D`. | High pre triedu a operácie, Medium pre úplný C++ podpis |

Dve nezávislé reprezentácie pointerov sú pôvodné NE reťazce a načítaná Ghidra pamäť. Nejde o dva runtime dôkazy. Class binding navyše podopierajú zápisy virtuálnych tabuliek v konštruktorových cestách a spotrebiteľ deskriptorov `068A`.

## Overené krátke telá

| Tvar | Počet | Presne doložené správanie |
|---|---:|---|
| `MOV AX,imm; RETF n` | 59 | AX dostane konkrétny word; far návrat odstráni n bajtov argumentov. |
| `RETF n` | 16 | Žiadne telo pred far návratom; AX nie je nastavovaný touto funkciou. |
| `XOR AX,AX; RETF n` | 12 | AX = 0; neznamená automaticky konkrétny C typ alebo pomenovanú operáciu. |
| `XOR AX,AX; CWD; RETF n` | 3 | DX:AX = 0. |
| `MOV AX,imm; MOV DX,selector; RETF n` | 2 | Konkrétny DX:AX pár; selector potvrdený NE relokáciou. |

Všetkých 92 tiel je explicitne anotovaných v projekte. Samotná znalosť krátkeho tela nepotvrdzuje runtime používanie metódy. Šestnásť prázdnych funkcií nemá zaručený nulový návrat.

Zvyšné dve nové funkcie:

- `1008:2ADE`: zložitejšia cesta s virtuálnymi volaniami, stavom objektu, obdĺžnikom z `GETCLIENTRECT` a výpočtom posunu. Úplná sémantika zostáva **Unknown/Partial**.
- `1008:6EFC`: iba `MOV AX,19h; JMP 1008:3C3D`. Zdieľaná chybová cesta vedie k ukončovacím API. Presný runtime kontrakt zostáva **Partial**. Automatický C export expanduje aj následný kód a obsahuje varovania; nie je dôkazom, že tento šesťbajtový vstup vlastní celé expandované telo.

## Pomenované deskriptory

37 nových getterov bolo spojených s týmito priamymi názvami v binárke:

`CObject`, `CException`, `CMemoryException`, `CNotSupportedException`, `CArchiveException`, `CFile`, `CFileException`, `CPtrList`, `CMapWordToPtr`, `CWnd`, `CFrameWnd`, `CView`, `CControlBar`, `CStatusBar`, `CToolBar`, `CDialogBar`, `CPreviewDC`, `CDialog`, `CFileDialog`, `CPrintDialog`, `CResourceException`, `CUserException`, `CDC`, `CClientDC`, `CWindowDC`, `CPaintDC`, `CGdiObject`, `CPen`, `CBrush`, `CMenu`, `CCmdTarget`, `CDocument`, `CDocTemplate`, `CSingleDocTemplate`, `CScrollView`, `CPreviewView`, `CWinApp`.

Presné adresy názvov, veľkosti a deskriptorové wordy sú v `runtime_class_descriptors.tsv`. Deskriptorový výrez má priamo podopreté polia:

| Offset | Podopreté použitie |
|---|---|
| `+0/+2` | Far pointer na názov triedy; obsah čítaný v načítanej pamäti. |
| `+4` | Veľkosť pre alokáciu; spotrebiteľ `06C0`. |
| `+6` | Vo vybraných 37 záznamoch `FFFF`; presný všeobecný schema kontrakt tu netestovaný. |
| `+8/+0A` | Far callback tvorby/inicializácie; spotrebiteľ `0730`. |
| `+0C` | Near pointer na deskriptor predka; spotrebiteľ `068A`. |

Príklad implementačne podopretého výrezu `068A`:

```text
descriptor = object.virtual_slot_0(object)
while descriptor != 0:
    if descriptor == requested_descriptor: return 1
    descriptor = read_word(DS, descriptor + 0x0C)
return 0
```

Presné far/near prototypy a register/stack ABI sa nesmú prebrať z automatického C exportu bez kontroly. Údaje iných getterov vracajúcich konštantu neboli automaticky vyhlásené za class deskriptory; niektoré ukazujú na iné metadata.

## Nové pokrytie

| Metrika | Pred prechodom 2 | Po prechode 2 |
|---|---:|---:|
| Interné funkčné vstupy | 1 252 | 1 346 |
| Interné dokončené dekompilácie | 1 252 | 1 346 |
| EXTERNAL položky, osobitne | 310 | 310 |
| Inštrukčné bajty | 156 385 | 156 889 |
| Definované dáta v kódových segmentoch | 1 681 | 5 141 |
| Neklasifikované bajty | 11 622 | 7 658 |

Pokles neklasifikovaných bajtov je 3 964 B: **3 460 B dát + 504 B inštrukcií**. Nie je to 3 964 B novo vysvetlenej hernej logiky.

| Segment | Inštrukcie B | Dáta B | Neklasifikované B |
|---|---:|---:|---:|
| `1000` | 52 305 | 571 | 3 670 |
| `1008` | 28 220 | 264 | 1 210 |
| `1010` | 58 060 | 712 | 2 600 |
| `1018` | 18 304 | 3 594 | 178 |

## Reprodukcia

1. `python3 scripts/verify_far_table.py` rozbalí všetkých 6 082 relokačných sites zo vstupného EXE, overí súvislú pointerovú tabuľku a zapíše adresy 94 nových cieľov voči predchádzajúcemu `final-results/functions.tsv`.
2. V Ghidre spusti `N3DRecoverCandidates.java` s `candidates3.txt`; pôvodný generický skript navyše kontroluje štyri už existujúce adresy a zapisuje ich ako `already_owned`.
3. `N3DDefineFarTable.java` overí načítané wordy proti odvodeným cieľom, definuje 865 záznamov `NE_FARPTR16_PROVEN` a doplní dátové referencie.
4. `N3DInspectClassMetadata.java` s `pass2/metadata_offsets.txt` exportuje načítané wordy a názvy.
5. `python3 scripts/verify_leaf_bodies.py` overí 92 vybraných tiel proti pôvodným bajtom vrátane dvoch segmentových relokácií.
6. `N3DApplyEvidenceAnnotations.java` aplikuje explicitnú tabuľku `verified_annotations.tsv`; 92 krátkych tiel a tri ďalšie preskúmané výrezy. Typy a prototypy nemení.
7. `N3DDeepExport.java` exportuje všetky funkcie; `N3DCoverage.java` poskytuje bajtové merania.

## Čo zostáva otvorené

- 7 658 neklasifikovaných bajtov treba ďalej rozdeliť na code/data/padding. Nevykonávať plošnú disassembláž len kvôli zvýšeniu čísel.
- Názvy tried neposkytujú automaticky názvy všetkých ich virtuálnych metód; hranice a vlastníctvo jednotlivých tabuliek treba overovať cez konštruktory a call sites.
- Zostávajúce kandidátske funkcie z prvého prechodu potrebujú úplnú kontrolu tiel, ABI a join s existujúcimi kanonickými identitami.
- Pri `2ADE` treba zachytiť konkrétny objekt a cieľové virtuálne metódy. Pri `6EFC` treba overiť noreturn kontrakt zdieľanej chybovej cesty a zastaviť nesprávne rozširovanie C exportu.
- CFile I/O treba neskôr spojiť s konkrétnymi game asset/save/demo callermi. Identita frameworkovej metódy sama nepotvrdzuje poradie herného save/load ani DEMO správanie.

**Istota:** High pre pointerovú tabuľku, 92 krátkych tiel, priame názvy tried a konkrétne vyššie uvedené čítania/zápisy; Medium pre úplnú frameworkovú sémantiku zložitejších funkcií; Unknown pre úplné behaviorálne pokrytie a paritu.
