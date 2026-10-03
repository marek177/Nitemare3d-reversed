# NITE3W — next audit load spritov and animačných podkladov

**Date:** 25. september 2026.  
**Nadväzuje on:** `NITE3W_Sprites_Audit_2026-09-24`.  
**Range new vykonaného rozboru:** rekonštruovaný C++ parser `ImgArchive`, actual file I/O, predpoklady indexácie obrázkov, diagnostika prekrývania animačných range with obrazovými dátami.

## Result

Zistená and reprodukovaná was validačná medzera: `ImgArchive::load()` accepts some nonzero address references dovnútra headers or pixelov obrázka, which subsequently own `frameAtExactOffset()` nevie vyriešiť. Pripravená local correction checks all nonzero references compared with exact začiatkom rámcov zisteným thereby istým parserom.

Second reprodukovaný result: `hasSequenceDefinitions()` sa zapína only according to celkovej size file. On syntetickom file with jediným veľkým obrázkom sa therefore as animačné arrays return obyčajné image pixely. This result dokazuje nedostatočnosť size kritéria for **semantic confirmation** animation, nie chybu v originálnom hernom assete.

**Performed:** 20 syntetických testovacích cases proti neupravenému parseru also locally opravenej verzii, therefore 40 spustení skompilovaného C++ probe programu. Further 6 testov diagnostického nástroja. All očakávané results sa confirm. Kompilácia and merania C++ prebehli with AddressSanitizer and UndefinedBehaviorSanitizer, with zastavením during chybe and kontrolou diagnostického výstupu.

**Nevykonané:** spustenie original NITE3W.EXE, new analysis its instructions, meranie its fronty or comparison original framebufferu. Was not available original EXE/complete ASM export nor reálny IMG file on locally testovanie. Repo contains rekonštrukciu and previous audity. Pokus o získanie verejného Win16 shareware ZIP neposkytol locally binary data. None results tohto package therefore are not marked as new runtime evidence original.

## 1. Identita analyzovaného source code

Repository: `marek177/Nitemare3d-reversed`. Pevná referencia:

```text
9e002c10d0449885af883177d36c3037f2179e82
```

Content piatich file was load through GitHub konektor and local copy was verify výpočtom Git blob SHA-1, nielen vizuálnym compare textu.

| File | verify Git blob |
|---|---|
| `src/formats/ImgArchive.cpp` | `f9a0bfcccbf4a5450d3dc5cabc7482a376f23cdc` |
| `src/formats/ImgArchive.hpp` | `2522980cd578b292cee855dfc52db15300d73af6` |
| `src/formats/ImgSequenceLayout.hpp` | `87a8a2e56bc10e47a3f47a08cd9007951ca1d4d0` |
| `src/formats/BinaryIO.cpp` | `784ca822ee2ba4aa65a422c8144534becfebb4b0` |
| `src/formats/BinaryIO.hpp` | `08df52c70bd74fbcfcb5cb848efd4a58270e520c` |

Meraný `ImgArchive` nor `BinaryIO` are not testovacími náhradami. Malý `img_probe.cpp` only calls their verejné rozhranie and vypisuje results. Input IMG files are new synthetic data vytvorené v teste, nie vydané game data.

Exact hashe and size: `results/source_integrity.json`. Source URL and range evidence: `source_manifest.json`.

## 2. New finding L01: reference v file is not automaticky reference on image

### Check v original kópii C++ parsera

During read address parser for nonzero offset requires only:

```text
firstDataOffset <= offset < fileSize
```

Subsequently from `firstDataOffset` sekvenčne dekóduje rámce and writes their exact začiatky to `exactOffsetToFrame_`. After dokončení however neporovná address references with touto množinou.

### Reprodukcia

Synthetic rámec 2 × 2 has:

```text
začiatok rámca: 0x800
hlavička:      0x800..0x809
pixely:        0x80A..0x80D
koniec súboru: 0x80E
```

| Reference | Neupravený parser | `frameAtExactOffset` | Local correction |
|---|---|---|---|
| `0x800` | prijme | finds rámec | prijme |
| `0x801` — vnútro headers | prijme | `nullopt` | odmietne |
| `0x80A` — first pixel | prijme | `nullopt` | odmietne |
| `0x80D` — last pixel | prijme | `nullopt` | odmietne |
| `0x80E` — EOF | odmietne | nevolá sa | odmietne |

These results are not derived only read code: vykonal their skompilovaný program. Test contains also prípad with nesprávnymi odkazmi v oboch address naraz.

### Consequence for sprity

Parser can úspešne vrátiť archív, whose reference on image sa neskôr nepodarí vyriešiť. According to behavior nadväzujúceho code to can viesť k odmietnutiu object, chybovému hláseniu or náhradnému zobrazeniu. **Specific pád, nesprávny sprite nor consequence in fungujúcej hre this testom preukázaný was not.**

Before kontrolou pravidiel zakrývania is therefore vhodné odlíšiť nevyriešený grafický source from correctly load, but incorrectly vykresleného spritu.

## 3. New finding L02: size file nepotvrdzuje animačné define

V C++ zdroji applies:

```text
fileSize >= 0xB408  ->  hasSequenceDefinitions_ = true
```

Then sa without sémantickej validácie kopírujú two range after 256 × 90 bytes. High bank starts on `0x5A08`, ends before `0xB408`.

### Rozlišovací synthetic input

File contains two address and jediný rámec 255 × 200, which starts on `0x800`. Its pixely are jednotne `0x29`. Celková size is 53 058 bytes, so prevyšuje prah `0xB408 = 46 088`.

**Celých 23 040 bytes high bank is v this vstupe part of pixelov.** Getter napriek tomu oznámi prítomnosť sekvenčných define and for high selector 0 returns:

```text
intervalMs         = 0x2929 = 10 537
frameCount         = 0x29   = 41
alternateTableFlag = 0x29   = 41
```

V druhej verzii file sa zmenili only pixely z `0x29` on `0x07`. Same gettery teraz return 1 799 ms, 7 rámcov and flag 7. Synthetic input pritom has naďalej jediný rámec.

### Správna interpretation

`hasSequenceDefinitions()` momentálne dokazuje dostupnosť požadovaného range bytes, nie confirmed origin and meaning these bytes. To, that entire high bank lies v pixeloch, dokazuje also nezávislá geometrická diagnostika range, nie only vypísaná value gettera.

This umelý layout **is not vyhlásený for valid original asset Nite3W**. Test therefore nedokazuje, that originál actually reads animations z pixelov or that existujúca hypotéza bankových offsetov is define nesprávna. Dokazuje, that itself size file takú hypotézu nevie validovať.

Before uzavretím originálneho loadera needs to track specific file/handle, build, selector and call function. To opravy sa therefore nemenia bankové offsety nor interpretation intervalov. Geometrické prekrývanie predpokladaných low records with address was listed already v skoršom audite; new is performed verify behavior C++ getterov on kontrolovanom protipríklade.

## 4. New verify L03: slot 1 is at the same time predpokladaný start data

Value `readU32LE(bytes,4)` is v súčasnom modeli súčasne:

- first offset use on sekvenčné parsovanie;
- second 4-byte item wall address, therefore slot 1.

Tests confirm two dôsledky:

| Syntetická situácia | Result neupraveného also opraveného parsera |
|---|---|
| Slot 1 is nula, other directory references on fyzicky prítomný rámec | odmietnutie |
| Slot 1 smeruje on second rámec, other slot on first rámec | odmietnutie skoršieho odkazu as addresses before začiatkom data |

Is to exactly určený invariant implement. Without original loadera cannot rozhodnúť, whether is to správna property all originálnych file or obmedzenie reconstruction. Automatické prehodenie on minimum nenulových offsetov by also was only nedoloženou zmenou, therefore sa neuskutočnilo.

## 5. New verify L04: nula v rozmere and nonzero rezervovaný slot

Merania confirm prijatie rámca with šírkou 0, rámca with výškou 0 and nenulovej items wall slotu 0, pokiaľ smeruje on dekódovaný rámec.

During nulovom rozmere sa sekvenčný parser nezacyklí: always postúpi minimálne o 10 bytes headers. To is kontrolovaný pozitívny result. Nezistilo sa however, what has zero rozmer mean for original kreslič: nevyvodzuje sa zákaz, sentinel nor meaning 256.

Nonzero slot 0 sa prijme napriek komentáru v `ImgArchive.hpp`, which ho denotes for rezervovaný zero pointer. Is rozpor komentára with vynucovanou podmienkou; nie o evidence chybného historického file. Nor jedna z these otázok sa v patchi potichu does not change.

## 6. Úzka local correction

File `patches/img_directory_boundary.patch` adds after sekvenčnom load rámcov 16 riadkov. verify each nonzero wall also object reference proti `exactOffsetToFrame_` and during neúspechu uvedie name address and slot.

Preserves:

- zero nepoužité references;
- zdieľanie one rámca viacerými slotmi;
- interpretáciu rozmerov, pixelov and metadát;
- predpoklad first rámca and doterajšie animačné banky.

Correction zabezpečuje konzistenciu with **vlastným sekvenčným rámcovým modelom reconstruction**. Is not to new implement originálnej politiky during damage file. Before integráciou remains regression test with reálnymi use IMG file; v this relácii were not available. `git apply --check` compared with lokálnej verify kópii uspel. GitHub was not zmenený.

## 7. Exact range testov

| Skupina | Count | Purpose |
|---|---:|---|
| Jednoduchý rámec, aliasy, two rámce, nulová nepoužitá item | 4 | zachovanie základných podporovaných cases |
| References to headers/pixelov, also v oboch address | 4 | reprodukcia medzery and verify opravy |
| Reference on EOF, before data, orezaná header/payload | 4 | zachovanie existujúcich odmietnutí |
| Slot 1 zero or nie najnižší | 2 | exact zdokumentovanie predpokladu |
| Nulová width/výška, nonzero slot 0 | 3 | behavior on okrajoch without hádania originálnych pravidiel |
| Two veľké pixelové vstupy and separate priestor banky | 3 | odlíšenie fyzickej dostupnosti from sémantického confirm |
| **Synthetic C++ cases total** | **20** | **each running before opravou also after nej** |
| Python diagnostika | **6** | match with C++, prekrytie range, error vstupy |

From 20 cases neupravený parser prijal 14 and corrected 10. Zmenilo sa prijatie only four intentionally chybných scenarios with odkazmi mimo začiatkov rámcov. During all others prípadoch zostalo behavior according to kontrolovaných kritérií preserved; výpisy all vstupov prijatých oboma verziami were identické.

Tvrdenie „20/20 testov prešlo“ mean, that **merania zodpovedali explicitným očakávaniam testu** — including očakávaného chybného prijatia v starej verzii. Does not mean, that stará version was bezchybná or that 20 functions original is uzavretých. Python test with viacerými vnorenými kontrolami sa ráta only raz.

Results: `results/loader_tests.json`, `results/loader_tests.txt`, `results/diagnostic_tests.txt`, `results/large_image_diagnostic.json`. Identita each syntetického vstupu is v JSON result.

## 8. Diagnostický tool usage without kompilácie

```text
python tools/inspect_img_layout.py IMG.1 --output img_layout.json
```

Requires Python 3.10 or novší, uses only štandardnú knižnicu, input does not change. Vypíše SHA-256, rámce, nevyriešené address items and prekrývanie predpokladaných animačných range with address, hlavičkami and pixelmi.

Diagnostika uses explicitly listed predpoklady reconstruction. During nedokončenom skene neoznačuje nevyriešené references as define errors formátu. Designation `semantically_validated: false` remains also during fyzicky oddelenej banke, because separate priestor is not evidence správneho animačného meaning.

## 9. What to uzatvára and what nie

**Reconstruction:** uzatvorená reprodukcia validačnej medzery and testovaná local correction; exactly určené behavior next troch okrajových skupín. Rozšírené verify zdrojov spritov before their vykreslením.

**Original NITE3W:** nevydáva sa new percento poznania. Exact sorter/fronta, tie rules, oklúzia, maskované walls, order `0x29` and remapu, tvorba `DS:8094` and pixelová match are not this behom closed. K U02 and U17 pribudli merania reconstruction, nie new inštrukčné evidence original EXE. Exact zmena evidencie is v `status_delta.json`.

## Primárne projektové zdroje

Following references identify read code and skorší audit; new results are supported lokálnymi testami above.

- https://github.com/marek177/Nitemare3d-reversed/blob/9e002c10d0449885af883177d36c3037f2179e82/src/formats/ImgArchive.cpp
- https://github.com/marek177/Nitemare3d-reversed/blob/9e002c10d0449885af883177d36c3037f2179e82/src/formats/ImgArchive.hpp
- https://github.com/marek177/Nitemare3d-reversed/blob/9e002c10d0449885af883177d36c3037f2179e82/src/formats/ImgSequenceLayout.hpp
- https://github.com/marek177/Nitemare3d-reversed/blob/9e002c10d0449885af883177d36c3037f2179e82/src/formats/BinaryIO.cpp
- https://github.com/marek177/Nitemare3d-reversed/blob/9e002c10d0449885af883177d36c3037f2179e82/analysis/nite3w_renderer.md
- https://github.com/marek177/Nitemare3d-reversed/blob/9e002c10d0449885af883177d36c3037f2179e82/analysis/nite3w_img_seqdef_2026-09-23.md