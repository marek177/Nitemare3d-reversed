# Nitemare 3D Win 1.10 — Ghidra 12.2, prechod 7

## Zistenie a rozsah

Obnovil som posledný uložený projekt a EXE po údržbe pracovného priestoru. V Ghidre 12.2 som doplnil sedem registrovaných callback vstupov a sedem ďalších kandidátov, overil 32-slotový callback register a dva jeho odlišné návratové kontrakty, štyri ukončovacie režimy a presnú aritmetiku chunk limitera.

Projekt obsahuje **1 549 interných funkčných vstupov**. Všetky dokončili natívnu dekompiláciu pri záverečnom exporte. Neklasifikovaných zostáva **1 459 B**, z ktorých je 681 B iba **Inferred alignment**, stále ponechaných ako nedefinované bajty. Úplná sémantika všetkých funkcií ani runtime parita nie sú dokončené.

Vstup: 230 400 B, SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`. Ghidra 12.2 build 20261016, JDK 25.0.2, headless projekt `WIN110`. NE code1–4 sú adresované `1000/1008/1010/1018`, inicializovaný DS segment 10 je `1048`. DOS a Win16 1.8 nie sú týmto dôkazom posudzované.

## 1. Callback register: kapacita a dve vstupné API

**Confirmed:** word `DS:0A96` začína na `4608h`. Rozsah `DS:4608–4687` je 128 B inicializovaných nulami, teda 32 far pointerov. Spoločný kód na `1008:73D9–73FD` kontroluje pointer proti `4688h`. Pri rovnosti už nepridáva položku. Inak zvýši pointer o 4 a uloží callback selector/offset do pôvodného slotu.

| Vstup | Nastavenie pred spoločným telom | Plná tabuľka | Úspešná registrácia |
|---|---|---|---|
| `1008:73CC` | AX=FFFFh, CX=FFFFh, CWD → DX=FFFFh | AX=FFFFh | AX=0; DX ostáva selector callbacku |
| `1008:73D4` | AX=0, CX=0, CWD → DX=0 | DX:AX=0 | DX:AX = dodaný far pointer |

Ide o **atexit-style/onexit-style** kontrakty; presné pôvodné symbolické názvy sú Inferred. Automatický C návrat typu undefined4 pri prvom vstupe sa nesmie považovať za potvrdený API návrat: pri 73CC je zmysluplný AX výsledok odlišný od zvyškového DX.

Binárka nemá v tejto ceste kontrolu NULL callbacku. Nulový pointer sa zaregistruje, posunie ukazovateľ a spotrebuje slot; pri variante 73D4 potom vráti nulu aj pri úspešnom uložení. Neskorší walker nulový slot preskočí. Model pokrýva normálny inicializovaný ukazovateľ a jeho 32 platných pozícií; poškodené pointery nie sú uzavretým kontraktom. V kóde je kontrola rovnosti s koncom, nie všeobecná kontrola hraníc.

### Sedem doložených registračných call sites

Každá položka má primárny dôkaz: PUSH selector, PUSH offset, CALL `1008:73CC`. Selector immediate je navyše overený voči NE relokácii.

| Registračné volanie | Callback |
|---|---|
| `1000:110A` | `1000:10FA` |
| `1000:27FE` | `1000:27C6` |
| `1000:345A` | `1000:3442` |
| `1000:45C4` | `1000:45A4` |
| `1000:5AF6` | `1000:5AE6` |
| `1008:0F3A` | `1008:0EFA` |
| `1010:044E` | `1010:043E` |

Tieto ciele neboli priamymi CALL cieľmi, preto ich predchádzajúca obnova priamych callee nezachytila. Obnovený vstup a jeho registračná väzba sú Confirmed; presná životnosť a trieda každého uvoľňovaného objektu zostáva Partial. Samotná statická registrácia nepreukazuje vykonanie pri každom hernom behu.

## 2. Opačné poradie a štyri ukončovacie cesty

Na `1008:3913/3916` sa nastaví SI=4608h, DI=4688h a zavolá sa near helper `3994`. Ten znižuje DI vždy o 4, preskočí nulový far pointer a inak vykoná `CALL FAR [DI]`. Poradie je teda opačné k poradiu ukladania platných slotov. Walker sám sloty nenuluje ani neposúva globálny registračný pointer.

| Vstup | CX flag | Žiada prechod registrovaných callbackov | Žiada DOS AH=4Ch |
|---|---:|---|---|
| `1008:38CD` | `0000` | áno | áno |
| `1008:38DB` | `0001` | nie | áno |
| `1008:38EA` | `0100` | áno | nie |
| `1008:38FB` | `0101` | nie | nie |

CL rozhoduje o callback range; CH neskôr o požiadavke na ukončenie. Pred tým zostávajú ďalšie cleanup cesty vrátane `396B` a voliteľného dynamického callbacku `DS:20D0`. Ich úplné externé účinky sa týmto neuzatvárajú.

`win110_exit_registry_model.py` overuje všetky prefixy obsadenosti 0–32 pre oba registračné vstupy (66 prípadov), zlyhanie po zaplnení, nulový callback a opakované prečítanie nezmenených slotov. Poradie modelu predpokladá, že vykonávané callbacky počas prechodu nemenia pole ani nenarušia callee-preserved SI/DI. **Nejde o runtime test ukončenia hry.**

## 3. Chunk limiter `1000:4A7E`

Raw 47-bajtové telo na `4A7E–4AAC` prijíma DWORD na `[BP+6]/[BP+8]` a WORD na `[BP+0A]`. Vypočíta 32-bitovo `10000h - offset`, unsigned porovná s požiadavkou a výsledok oreže na `4000h`.

```text
AX = min(request_u32, 65536 - offset_u16, 16384)
```

| Vstupný príklad | AX výsledok |
|---|---:|
| request=0, offset ľubovoľný | 0 |
| request=FFFFFFFFh, offset=0 | 16384 |
| request=FFFFFFFFh, offset=FFFFh | 1 |
| request=1, offset=FFFFh | 1 |

**Confirmed, High:** aritmetika, argumentové wordy a návrat cez AX/RETF bez odstránenia argumentov. **Inferred:** pravdepodobná úloha limitera prenosu/I/O kvôli 64 KiB hranici a 16 KiB capu. Konkrétny caller nebol doložený. Funkcia sa nesmie automaticky priradiť k save/load alebo loaderu len podľa tejto užitočnej interpretácie.

Doslovný model 16-bitových SUB/SBB/porovnaní sa zhoduje s nezávislým min vzorcom pre všetkých 65 536 offsetov a deväť hraničných DWORD požiadaviek, spolu 589 824 porovnaní. Toto je overenie aritmetického výrezu, nie CPU alebo herný runtime test.

## 4. Ďalšie kódové kandidáty a triedy

Okrem chunk limitera boli manuálne otvorené `1000:569A`, near stack-probe kandidát `1008:39D2` a štyri šesťbajtové gettery. Stack helper má neštandardnú register/return-address manipuláciu a jeho automatický C export obsahuje varovanie; presný ABI sa neuzatvára.

| Getter | Deskriptor DS | Priamy názov | Veľkosť objektu | Base descriptor |
|---|---|---|---:|---|
| `1008:0E6C` | `0706` | CFont | 6 B | `06D6` CGdiObject |
| `1008:0E7E` | `0716` | CBitmap | 6 B | `06D6` |
| `1008:0E90` | `0726` | CPalette | 6 B | `06D6` |
| `1008:0EA2` | `0736` | CRgn | 6 B | `06D6` |

Názvy, hodnoty getterov a descriptor string pointers sú Confirmed z EXE/načítanej pamäte. Neznamenajú, že boli tieto konkrétne metódy za behu zavolané.

## 5. Oblasť metadát `1000:05EE–0659`

Najväčší zostávajúci rozsah bol dátový. Má dva doložené headery po dvoch far pointeroch:

- `05EE`: NULL a `1000:05F6`.
- `0636`: NULL a `1000:063E`.
- `063E`: pointer na `1000:064A` a word `0010h`, za ním NULL/FFFFh záznam.
- `064A`: 16-bajtový GUID **`00020400-0000-0000-C000-000000000046`**.

Identita GUID je **IID_IDispatch**, potvrdená aj primárnou Microsoft špecifikáciou: https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-oaut/58504586-e4af-44a3-be04-f1dc281b7429 . Samotné bajty a tri segmentové relocácie sú overené lokálnym skriptom.

Interpretácia ako frameworkové Automation/interface-map metadata je **Inferred**. Prítomnosť IDispatch GUID **nepreukazuje aktívne alebo externe dostupné scripting/Automation rozhranie hry**. Vstupný 64-bajtový región `05F6–0635` je uložený ako opaque metadata; jeho presná schéma zostáva **Unknown**, hoci už nejde o nedefinované bajty v projekte. Rozlíšenie medzi klasifikáciou dát a pochopením ich významu je podstatné.

Typované boli aj štyri priamo referencované ASCII reťazce (AfxWnd, commdlg_LBSelChangedNotify, File%d a fragment open) a názov CRgn, spolu 54 B vrátane terminátorov.

## 6. Pokrytie a zostávajúce medzery

| Metrika | Pred prechodom 7 | Po prechode 7 |
|---|---:|---:|
| Interné funkčné vstupy | 1 535 | 1 549 |
| Dokončené interné dekompilácie | 1 535 | 1 549 |
| EXTERNAL položky | 310 | 310 |
| Inštrukčné bajty | 159 674 | 159 998 |
| Definované dáta v code segmentoch | 8 069 | 8 231 |
| Neklasifikované bajty | 1 945 | 1 459 |

Pribudlo 324 B inštrukcií a 162 B dát. Funkčné vstupy pribudli v dvoch skupinách 7+7. Časť novo definovaných dát má stále neznámu schému a nové vstupy stále vyžadujú sémantické overovanie.

Read-only audit označil **681 jedno-bajtových medzier** ako **INFERRED_ALIGNMENT, Medium**: len 00/90, bez explicitného alebo zachyteného relokačného cieľa, po terminujúcej inštrukcii a pred známym funkčným vstupom. **Tieto bajty neboli v Ghidre pretypované** a stále sú súčasťou počtu 1 459. Pri zvyšných 778 B tento úzky vzor neplatí. Ani jedna množina nie je automaticky totožná s chýbajúcou hernou logikou.

## Reprodukcia, validácia a ďalší dôkaz

Obnovenie natívnych nástrojov vyžadovalo opätovné nastavenie executable práv. Prvé neúspešné dekompilačné pokusy nie sú započítané ako výsledok. Finálny native probe aj celý export úspešne skončili. Exportér je teraz chránený: pri neúspešnom `openProgram` zastaví prácu s chybou, namiesto zápisu inventára plného neúspešných riadkov.

Zachované sú modely `win110_exit_registry_model.py`, `win110_chunk_limit_model.py`, metadata verifier, read-only gap audit, source call/registration TSV, anotácie, projekt a finálny listing/C/reference export.

Ďalší test: kontrolovaný Win16 shutdown s breakpointmi 73CC/73D4/3994, záznam reálne zaregistrovaných callbackov a ich vplyvu na pamäť; caller recovery chunk limitera; overenie prípadného COM QueryInterface použitia; sémantický join funkčných kandidátov s kanonickým katalógom. Runtime scheduler, save/load prvý frame, DEMO a pixel/DAC parita zostávajú samostatne otvorené.

**Istota:** High pre lokálne operácie, registrové návraty, GUID a aritmetiku; Medium pre runtime/library roly a alignment; Unknown pre opaque schému, runtime dosiahnuteľnosť, úplné správanie a 1:1 paritu.
