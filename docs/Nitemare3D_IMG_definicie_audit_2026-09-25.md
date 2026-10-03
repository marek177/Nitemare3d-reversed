# Nitemare3D — IMG, define and verify dátových odkazov

**Date:** 25. 9. 2026
**Repository:** `marek177/Nitemare3d-reversed`
**Pinned base:** `9d485e82a84ef1241eff7165c390c82eaff47970`

## Result and range

V read `DefinitionTable` were reproduced and locally corrected three príčiny tichej zámeny ID: accepted neúplného numeric write, narrowing values mimo 16-bit range and accepted negative write as neznamienkového numbers. Five named regression group on original code failure. Corrected code passed all 23 group v šiestich configuration dvoch compiler.

During IMG pribudla **diagnostic, nie new claim o complete resolved format**. Distinguishes reference to file from start frames, common image offset, presence raw sequential bytes from their meaning and possible prekrytie these bytes with image prúdom. Exist `ImgArchive.cpp` sa does not change. Unclear lower banka sa nepresúva, nedopĺňajú sa vymyslené values and count frames sa automatic neopravuje.

Base was load through connect GitHub. Seven usage original source file was locally verify according to Git blob SHA-1; exact values and SHA-256 are v `source_manifest.json`. Original NITE3W.EXE, IMG, WALLS and OBJECTS were not v this kroku locally load nor run. Evidence o original hre citované below are previous audity, nie new independent disassembly.

**75–80 % remains only last common working odhadom dátových format.** Count successful check sa neprevádza on percent reverznej analysis.

## 1. define: three príčiny tichej zámeny identify

Original code:

```cpp
rec.id = static_cast<std::uint16_t>(std::stoul(idHex, nullptr, 16));
```

This combination nezisťuje, whether sa spotreboval entire token, and before narrowing result on `uint16_t` nekontroluje its range. `stoul` moreover uses konverziu, which accepts znamienko. To is behavior libraries; missing check ID belongs to reconstruct parsera.

| Input token | Original locally reproduction result | Result fix |
|---|---:|---|
| `0001junk` | ID 1 | Odmietnutie entire tokenu |
| `10000` v hexadecimal sústave | ID 0 namiesto values 65 536 | Reject values mimo range |
| `-1` | ID 65 535 | Reject negative write |
| `0x` without number | ID 0 | Reject neúplného write |
| `0001`, zero byte, `junk` v jednom tokene | ID 1 | Reject neúplne spotrebovaného tokenu |

Last two cases patria to rodiny neúplnej konverzie, therefore **five failure group does not denote for five independent príčin**. Protokol `logs/baseline_gcc_debug.txt` capture specifically accepted results. Same failure were reproduced also Clangom.

### Correction

read reject introductory mínus. During konverzii track count process character and before pretypovaním verify `value <= 65535`. Error contains original designation row and path file.

Preserved are valid 16-bit ID, small and large hexadecimal number, initial nuly, prefixy `0x` and `0X`, original support introductory plus, CRLF, opis with medzerami and exist compare name class. Test load all **65 536 valid 16-bit ID** and compare each value.

Intentionally sa nevkladá limit 255 to generic `DefinitionTable`: its exist interface uses 16-bit ID. During directly prepojení with dvojbajtovou MAP whole is however themselves ID walls or object osembitové. New diagnostic values nad 255 označí as unused **as priame byte ID whole**, nie as automatic invalidation define for each usage.

### Duplicate ID and episodes

`find(id)` v original code returns first identical record. Two lines with same ID and difference class therefore can lead k tomu, that neskoršia modification classes does not have during search effect. This behavior sa does not change without evidence, that has be other. `inspectDefinitionIds()` ho sprístupňuje: uvedie ID, index first record and index neskoršieho occurrence.

Each load file has own priestor ID. Same value v define different episode sa nesmie automatic message as duplicate jednej tables. This separate is test. Names class v text define sa thereby nestávajú confirm internal type original EXE.

## 2. IMG: valid range is not to isté as start frames

`ImgArchive::load()` checks, whether nonempty reference lies between assume start data and koncom file. Simultaneous skenuje image prúd and eviduje exact start frames. These two check however original load nespája: reference can ležať inside frames and read ho also tak accept.

Synthetic frame starts on `0xBC00`, has rozmery 2 × 3 and its pixely start on `0xBC0A`. Oba following references read accept:

| Reference | Umiestnenie according to skenovaného prúdu | New diagnostic |
|---|---|---|
| `0xBC01` | Second byte headers frames | `nonBoundarySlots` |
| `0xBC0A` | First pixel frames, nie its header | `nonBoundarySlots` |

`inspectImageReferences()` prejde wall also object directory and rozdelí items on zero, references on exact start and other nonzero references. None data neupravuje. For each upozornený slot preserves druh address, number slotu and original offset.

V audite original vzorky z 23. 9. was recorded, that all 317 nonzero address items directional exactly on start frames. This original vzorku sme tu neotvárali. New diagnostic allow takú property znovu measure on specific provided file, but neustanovuje without next evidence universal right reject all others variant.

### Shared offset is not automaticky same animation

Viac slotov can shared image offset. Diagnostic their preserves and creates group odkazov, namiesto označenia for error or automatic link sequential data. Previous audit opisuje repeated usage image group; specifically condition original shared sa tu nanovo nedokazujú.

Test contains wall also object slot direction on same image and verifies, that sa nestratí informácia o their different address. Separate test uses same image slot with rôznymi explicit selected sequential bankami and dostane difference count frames. Is to test API and synthetic model, nie finding takých values v original IMG.

## 3. IMG: `hasSequenceDefinitions()` does not mean confirmed animations

Original read sets flag, when size file reach end upper banky `0xB408`. Subsequently retain all 512 raw 90-byte records. Unverified however, whether some z these bytes at the same time patria to already skenovaného image prúdu.

On reprodukciu was create file with image address size `0x800` and jedinou frame 255 × 255:

```text
2 048 bajtov adresárov + 10 bajtov hlavičky + 65 025 pixelov = 67 083 bajtov
```

File is dostatočne long for exist check `hasSequenceDefinitions()`. Diagnostic tool on it nameral:

```text
frames=1 first_data_offset=2048
raw_sequence_records=512 overlaps_directories=23 overlaps_scanned_images=490
```

Therefore raw records are physical readable, but **490 z nich zasahuje to skenovaného image**. Lower record 22 zasahuje simultaneous to address also to image prúdu; category prekrytia sa therefore do not have add as disjunktné set.

Is not evidence, that takýto file is original or that original game has error. Is to counterexample k claim, that available length file automatic confirms meaning raw records as animation.

`inspectSequenceRange()` therefore separate returns offset, presence raw record, prekrytie image address and prekrytie skenovaných image. Specific interpretation intervalov, počtov and switch nevyhlasuje for correct.

## 4. Selection image and selection sequential banky

Previous audit states these choice sequential banky: normal walls use lower banku, objects upper and separate path walls classes 5 also upper. V this kroku sa original instructions nenanovo verify. Especially specific source image address in exception path tu is not new confirmed result.

New diagnostic function has therefore **explicit, separate parametre** for image directory, image slot, sequential banku and sequential selektor. Neodvodzuje banku from slovného označenia „wall“ and do not confuse number image for internal class object.

`inspectFrameRun()` distinguishes missing image slot, not found start frames, missing raw sequential data, zero raw count, count presahujúci remain naskenované frames and count, which sa to nich zmestí. Also result `FitsScannedFrames` is only check range related count frames. **Is not evidence correct konca animations, its načasovania, call directional tables nor matches with EXE.**

### Preserved open predpoklady IMG

`firstDataOffset` sa still reads z offset 4, therefore from wall slotu 1. read still reject zero slot 1 or other nonzero address reference before its value. Test these exist limit reproduction and documentation, nepredstierajú their resolved. Change on minimum all offset by was new strategy parsovania, which this audit without next original vzoriek nezavádza.

Reason prekrytia lower sequential records 0–22 with address, correctly pair build NITE3W/IMG, call directional table and all meaning metadata remain open.

## 5. Performed tests

| Zostava | Skupiny | Failure | Performed check condition |
|---|---:|---:|---:|
| Original read, GCC 14.2 Debug | 23 | 5 | 66 120 |
| Original read, Clang 17 Debug | 23 | 5 | 66 120 |
| Corrected version, GCC Debug | 23 | 0 | 66 160 |
| Corrected version, GCC Release, `NDEBUG` | 23 | 0 | 66 160 |
| Corrected version, GCC UBSan | 23 | 0 | 66 160 |
| Corrected version, Clang Debug | 23 | 0 | 66 160 |
| Corrected version, Clang Release, `NDEBUG` | 23 | 0 | 66 160 |
| Corrected version, Clang UBSan | 23 | 0 | 66 160 |

During original version failure group končia during element nesplnenom expected, therefore have lower count execute condition. Successful condition are not independent game test and repeated on compiler does not increase percent poznania.

Provided prešlo eight check separate compile and poradia headers, separate CMake Release build, two CTest test and nine check command tool. Tool was verify on synthetic file, on incorrect argumentoch and on invalidation ID. Test nepoužívajú vypínateľné `assert`, so check remain active during `NDEBUG`.

Base all test is small podmnožina read and new diagnostic. **Entire repository, SDL integration, MSVC, Windows x86/x64 nor original game were not this test covered.** Detailed logy are v package; result check consist with precede MAP/DAT patchom is v `patch_valid.json`.

## 6. Files, tool and aplikovanie

Patch changes only `src/formats/DefinitionTable.cpp` and adds:

- `src/formats/DataReferenceAudit.hpp` — diagnostiku without write to data;
- `test/data_reference_audit_test.cpp` — 23 group check;
- `tools/data_reference_inspect.cpp` — separate command tool;
- `docs/DATA_REFERENCE_AUDIT_2026-09-25.md` — this audit.

Does not change `ImgArchive.cpp`, its public interface, MAP/DAT fix, render nor main CMake file. Copies unchanged depend are v package for separate build, nie as prepisujúce change v patchi.

Zostavenie separate package:

```sh
cmake -S standalone -B build/local -DCMAKE_BUILD_TYPE=Release
cmake --build build/local --config Release
ctest --test-dir build/local -C Release --output-on-failure
```

Usage tool on own data:

```sh
build/local/n3d_data_reference_inspect --img /cesta/IMG.1 --definitions /cesta/WALLS.1 --definitions /cesta/OBJECTS.1
```

In viac-configuration Windows build by executable file ležal type v `build\local\Release\n3d_data_reference_inspect.exe`; taká build sa tu nevykonala. Tool has only read mode. Return code 0 mean completion inšpekciu, nie bezchybnú animation; upozornenia can be presence. Error argumentu or load returns 1.

Before applying on newer repository needs to use `git apply --check`, nie files prepísať naslepo. **On GitHub sa v this kroku nothing nezapisovalo.**

## Source and boundary claim

Source references are pinned ku check commitu:

- [DefinitionTable.cpp](https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/src/formats/DefinitionTable.cpp)
- [DefinitionTable.hpp](https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/src/formats/DefinitionTable.hpp)
- [ImgArchive.cpp](https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/src/formats/ImgArchive.cpp)
- [ImgArchive.hpp](https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/src/formats/ImgArchive.hpp)
- [ImgSequenceLayout.hpp](https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/src/formats/ImgSequenceLayout.hpp)
- [Previous audit IMG and sequence, 23. 9. 2026](https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/analysis/nite3w_img_seqdef_2026-09-23.md)
- [C++ draft — string conversions](https://eel.is/c++draft/string.conversions): `stoul` and index first nespracovaného znaku.
- [Microsoft Learn — strtoul](https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/strtoul-strtoul-l-wcstoul-wcstoul-l?view=msvc-170): termination during nečíselnom znaku and support znamienka.

New locally evidence are synthetic input, test source and protokoly v package. During next rozbore original game is still najhodnotnejšie obtain match dvojicu EXE/IMG and track, which actual selektory, counts frames and bytes call tables sa during load use. This step nepriraďuje next original function names without disassembly evidence.