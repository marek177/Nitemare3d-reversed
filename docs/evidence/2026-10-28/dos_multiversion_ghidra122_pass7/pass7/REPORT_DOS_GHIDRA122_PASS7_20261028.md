# Nitemare 3D DOS — Ghidra 12.2 pass 7, 2026-10-28

## Finding

Obnovený konkrétny dátový a behaviorálny model NITE3D.BSF: 54-bajtová hlavička, 52-bajtový opakovaný XOR kľúč, dispatcher režimov 0..5, loader blokov a nešpecifikované návraty režimu 0/neplatných režimov. V Ghidre sú pomenované tri rutiny na obraz a vytvorený typ hlavičky. Počty dokončených C zostávajú stock3445/3468 a explicit3460/3468; ide o sémantické spresnenie, nie ďalší nárast C úspešnosti.

Nové dôkazy: **78 úplných vykonaní dekodéra bez hookov**, **186 callbackových prípadov** (96 bez hookov,90 s riadenými závislosťami), **60 loaderových integračných prípadov** s riadeným OS/alokačným rozhraním a pôvodným dekodérom. Spolu324 vykonaní; samostatne12 checksum porovnaní pôvodných EXE/MAP súborov. Nejde o324 DOSBox behov ani o324 vykonaní celej hry.

## Evidence

| Status | Zistenie | Zdroj | Confidence |
|---|---|---|---|
| Confirmed | Režim0 načíta54 B z nite3d.bsf, dekóduje ich a kontroluje XOR pôvodných encoded bajtov==0. N3D.EXE kontroluje vždy; MAP.1 iba pri decoded flagu+3==0. | pôvodné opcode, callback traces, header_file_checksums.json | High pre tok a pripravené závislosti |
| Confirmed | Režim2 vracia DS:header+4. Režimy3/4/5 odovzdávajú loaderu presné offsety a dĺžky z hlavičky. | callback_mode_emulation.json, bsf_resources.json | High pre testované stavy |
| Confirmed | Decoder transformuje byte[i] ^= SS:key[i%52], pričom AL vracia XOR pôvodných bajtov. | decoder_emulation.json, pôvodný helper, všetky6 buildov | High |
| Confirmed | Loader píše nulový terminátor ZA blok, potom dekóduje len L bajtov a vracia uložený DX:AX buffer. Nevetví podľa krátkeho/chybového read výsledku. | loader_emulation.json a assembly | High pre wrapper pri riadených závislostiach |
| Confirmed | Režim0 a mode>5 vracajú hodnoty závislé od dvoch neinitializovaných lokálnych wordov. | callback_mode_emulation.json, rôzne seed hodnoty, assembly | High pre kontrolované stavy |
| Unknown | Úplná implementácia CRT/OS a alokátora, presné EOF krajné správanie file checksum helpera, prirodzená dosiahnuteľnosť chybných vstupov. | OS/allocator/file validator boli vo väzbových testoch nahradené | Neuzavreté |

## Runtime header structure

Pracovný názov typu N3DBsfHeader54, presne54 B, bez paddingu:

| Offset | Veľkosť | Použitie doložené kódom |
|---|---:|---|
| +0x00 | 1 | Bajt prispievajúci k encoded XOR podmienke; samostatný decoded význam sa netvrdí |
| +0x01 | 1 | Očakávaná hodnota file-checksum pre n3d.exe |
| +0x02 | 1 | Očakávaná hodnota file-checksum pre map.1 |
| +0x03 | 1 | Flag: pri nule sa vykoná MAP.1 kontrola; mode1 vracia jeho adresu iba ak je nenulový |
| +0x04 | 32 | Uložená oblasť mena; mode2 vracia jej adresu |
| +0x24 | 4 | Little-endian file offset bloku pre mode4 |
| +0x28 | 4 | Little-endian file offset bloku pre mode3 |
| +0x2C | 4 | Little-endian file offset bloku pre mode5 |
| +0x30 | 2 | Little-endian byte length pre mode4 |
| +0x32 | 2 | Little-endian byte length pre mode3 |
| +0x34 | 2 | Little-endian byte length pre mode5 |

V dodaných súboroch je oblasť mena NUL-terminated a obsahuje napr.ASP-CD, Public (software) Library, P(s)L, America Online, Author-Direct; v DOS1.2 je David P Gray a flag+3==1. Samotný mode2 žiadny NUL nepridáva ani nevynucuje. Pomenovanie flagu ako registrácia/licencia by vyžadovalo ďalší kontext; v tomto reporte sa uvádza jeho presné použitie.

## Dispatcher contract

| Mode | Vstupy / účinok | Výsledok | Rozsah overenia |
|---:|---|---|---|
| 0 | Načíta a dekóduje hlavičku, vstúpi do error vetiev pri open/checksum probléme, volá EXE a podmienene MAP validátor | Nešpecifikované lokálne wordy, neinterpretovať ako pointer | Celý dispatcher s riadeným fopen/fread/fclose a file validátorom; originálny decoder beží |
| 1 | Testuje flag+3 | 0 alebo DS:header+3 | Doložené72 pôvodnými vykonaniami v pass6; tu sa nepripočítavajú znova |
| 2 | Poskytne adresu storedName | DS:header+4 bez podmienky flagu |48 prípadov bez hookov |
| 3 | File offset z+0x28, length z+0x32 | Far buffer z loadera: blok nápovedy |18 kontrolovaných dispatch prípadov + pôvodný loader/dekódovanie dát osobitne |
| 4 | File offset z+0x24, length z+0x30 | Far buffer z loadera: záverečný/ďakovný informačný text |18 kontrolovaných dispatch prípadov + loader osobitne |
| 5 | File offset z+0x2C, length z+0x34 | Far buffer z loadera: koncový text |18 kontrolovaných dispatch prípadov + loader osobitne |
| >5 vrátaneFFFF | Preskočí platné vetvy | Nešpecifikované lokálne wordy |48 prípadov bez hookov |

Názvy troch textových blokov vychádzajú z dekódovaného obsahu, nie z domnelých pôvodných symbolov. Ich úplná UI prezentácia a každá herná callsite zostávajú osobitne mimo testu. V spoločnom ABI má funkcia storage DX:AX, ale režim0 a neplatné modes nemajú zmysluplnú hodnotu. Testy s rôznymi seedmi na SS:SP_entry−6 a−4 vracajú rôzne AX/DX. Nejde o požiadavku reprodukovať náhodné dáta ako významový API výsledok; caller pri takom režime musí byť posúdený osobitne.

## Actual BSF files

V týchto šiestich súboroch sa tri bloky bez medzier nadväzujú od offset54 až po EOF. Je to vlastnosť tejto vzorky, nie obmedzenie, ktoré by samotný loader vynucoval.

| DOS obraz | Súbor B | Mode3 offset/length | Mode4 offset/length | Mode5 offset/length |
|---|---:|---|---|---|
| 1.0 | 14741 | 1711 / 12058 | 54 / 1657 | 13769 / 972 |
| 1.1 | 15245 | 1711 / 12562 | 54 / 1657 | 14273 / 972 |
| 1.2 | 10250 | 528 / 9141 | 54 / 474 | 9669 / 581 |
| 1.5 | 15495 | 1711 / 12812 | 54 / 1657 | 14523 / 972 |
| 1.7 | 15513 | 1711 / 12830 | 54 / 1657 | 14541 / 972 |
| V1.9 (input1.8/1.9) | 15800 | 1711 / 13117 | 54 / 1657 | 14828 / 972 |

bsf_resources.json viaže výsledky na zdrojovú ZIP cestu a SHA256 encoded súboru aj každého encoded/decoded bloku. Každý blok začína key indexom0; index sa neprenáša z headera ani z predchádzajúceho bloku. Kľúč je52 B z pôvodného EXE, číta sa cez SS, zatiaľ čo DS v slučke môže ukazovať na buffer. Po nenulovej slučke sa DS obnoví zSS.

Mode0 header kontroluje XOR encoded54 B==0; nekontroluje XOR už decoded headera. Pre všetky6 EXE a6 MAP súbory sa uložený očakávaný checksum zhoduje s0x7b XOR všetkých bajtov súboru. Všetkých12 súborov má posledný byte0; preto tento dátový dôkaz nerozlíši jemné správanie EOF read slučky pri nenulovom poslednom bajte. Tvrdenie presného všeobecného EOF algoritmu sa týmto neuzatvára.

## Block loader and I/O edge behavior

ReadAndDecodeBsfBlock má word filenameOffset naSP_entry+4, dword fileOffset na+6 a word byteLength na+10; výsledok DX:AX. Pôvodný wrapper:

```text
open(filename, 0x8000)
if handle == -1: call error dependency
buffer = allocation_callee((L + 1) modulo 65536)
if buffer == 0: call error dependency
seek(handle, fileOffset, origin=0)
read(handle, buffer, L)       // wrapper neoveruje návrat
buffer[L] = 0
close(handle)
XorDecodeAndFoldOriginalBytes(bufferOffset, bufferSegment, L)
return saved buffer DX:AX
```

60 integračných prípadov zahŕňa18 skutočných BSF blokov, zero length,52-byte hranicu kľúča, short read0/53 zo54 B, read error, open error a allocation error v každom obraze. Pri chybných open/alloc sa test zastavuje pred error callee; jeho skutočné ukončenie procesu tu nebeží. Pri short/error read sa wrapper aj tak dostane cez dekódovanie k vráteniu bufferu. Nečítané bajty zostali pripravené0xA5 a pôvodný decoder ich zmenil podľa kľúča. To dokladá chýbajúcu kontrolu wrappera, nie výsledok skutočného DOS drivera alebo pamäťového alokátora. L=FFFF a malloc overflow nie sú emuláciou pokryté.

## Ghidra changes and limits

V každom obraze sú tri analytické mená: BsfDispatchMode, ReadAndDecodeBsfBlock, XorDecodeAndFoldOriginalBytes. Sú to pracovné mená podľa dôkazov, nie obnovené zdrojové symboly. Loader a decoder dostali presné stack parametre a storage návratov. Header dostal typ54 B v runtime dátovej oblasti po kontrole, že rozsah neobsahuje definované inštrukcie. Spolu18 pomenovaných/anotovaných rutín a6 hlavičkových typových umiestnení.

Niektoré CRT/OS callees stále nemajú správne prototypy; napr.alokačný callee môže v C výstupe naďalej vytvárať in_DX. Tento report opiera kontrakty o assembly, pripravené stack argumenty a vykonané inštrukcie, nie iba o zdanlivo dokončené C. Všetky entrypointy, completed/C_available výsledky stock aj explicit modelu a celý definovaný inštrukčný listing pred/po sú zhodné. Žiadne EXE ani inštrukčné bajty sa nemenili.

## Implementation-ready findings

- BSF header layout, výber offsetov/dĺžok podľa režimu, XOR transformácia aj byte return fold pôvodných bajtov sú doložené.
- Decoder nepridáva NUL; NUL za decoded blok vkladá loader mimo rozsahu L ešte pred dekódovaním.
- Pri mode0 a invalid mode nepoužívať odhadnutý pointerový návrat; platná sémantika je vedľajší účinok alebo žiadna platná vetva.
- Short-read/error kontrola wrappera chýba; presná prirodzená dosiahnuteľnosť a správanie OS/allocácie zostávajú ďalším dôkazovým krokom.

## Unknowns and next test

1. Presné ABI a implementácia CRT open/read/seek/close/fmalloc/fread callees, vrátane short-read a posledného nenulového bajtu pri EOF v checksum helperi.
2. Calleri všetkých BSF režimov a vlastníctvo/free vrátených bufferov; netvrdiť univerzálne pointerové pravidlo iba zo storage.
3. UI formátovacie sekvencie dekódovaných textov, renderovanie, scheduler a framebuffer/DAC parita.
4. Osem pôvodných kandidátov z pass6 zostáva bez globálneho runtime dôkazu nedosiahnuteľnosti.

## Reproduction

Hotové pass7 projekty, C výstupy, BSF dáta a decoded bloky, rekonštruované EXE a dôkazy sú v archíve. Testy78/186/60 používajú priložené malé dáta a Unicorn2.1.4. Pre prepare_pass7.py a12 checksum porovnaní je potrebný pôvodný inputs/all-nite3d.zip; veľký262MB zdrojový archív sa neduplikuje v balíku. Baseline pass6 výsledky/inštrukcie sú priložené pre validáciu. Runtime Ghidra12.2 a JDK25 sa obnovili z pôvodných archívov; run_pass7.py používa lokálne runtime cesty, prípadne ich upraviť.

```bash
python3 scripts/verify_bsf_decoder.py
python3 scripts/verify_callback_modes.py
python3 scripts/verify_bsf_loader.py
python3 scripts/validate_pass7.py
```

## Confidence

High pre uvedené dáta, stack/storage a kontrolovaný tok originálnych rutín. Beh celej DOS hry, filesystemu, alokátora a1:1 renderovacia parita týmto uzavreté nie sú.
