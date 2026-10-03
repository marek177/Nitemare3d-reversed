# NITE3W — audit piatich areas

**Date:** 25. september 2026  
**Repository:** `marek177/Nitemare3d-reversed`  
**Preskúmaný snapshot:** `9d485e82a84ef1241eff7165c390c82eaff47970`  
**Range:** check available rekonštruovaných source, comparison existing RE reportov, reprodukčné test C++ modelu and parsera.

## Main result

Audit priniesol **jednu reprodukovanú error binary layout MFC modelu and jednu reprodukovanú medzeru in valid IMG**. For obe are pripravené locally patche. Moreover spresnil boundary evidence during HUD, SEQDEF, sound and bossových event.

Original Win16 EXE nor actual game data files sa v this kole nespúšťali and znova nedisassemblovali. Specifically addresses and interpretácie original below pochádzajú z citovaných project reportov. New experimenty test moderný C++ code or exact minimálny model its fields. Patche **were not zapísané on GitHub**.

| Area | Result tohto kola | What is not closed |
|---|---|---|
| MFC / runtime / memory | Reprodukcia nesúladu 40 version 38 B; local correction packingom and check offset. | Complete štart/termination, error branches and životný cyklus object v original Win16 behu. |
| HUD / UIF / menu / automapa | Prepojenie draw HP with mutáciou game state; oddelenie automapového buffera from purpose čierneho panel. | Exact UIF index, portréty, update condition and konečné draw targets. |
| IMG / SEQDEF | Parser accepts references dovnútra images; correction verifies boundary. Length flag is not valid sequence. | actual source sekvenčných records, prekrytie banky, their meaning and object links. |
| Sounds events | identify problem neovereného prevodu requirement on index archívu. | Complete matica event → call → preklad → item SND → play. |
| Level and bossovia | Distinguish premeny from smrti and shared flag from čisto text events. | Complete order animation, sound, zmien sveta, save and completion events. |

## 1. MFC, C++ runtime, initialization and memory

### Supported v existing source

Header `Win16MfcMemory.hpp` eviduje 31 runtime-class deskriptorov, four handle mapy and 20 first slotov CWnd vtable. Mapy are CWnd/HWND on `0x4250`, CDC/HDC on `0x44F2`, CGdiObject/HGDIOBJ on `0x451C` and CMenu/HMENU on `0x4548`. CDC eviduje two handle arrays. [1]

Temporary obal sa searches up to after persistent. Before likvidáciou temporary obalu sa zapožičané handle arrays vynulujú; zánik obalu therefore is not totožný with zničením systémového object. Exact Win16 životný cyklus must confirm original beh. General difference between temporary and persistent map vysvetľuje also dokumentácia MFC, but is not independent evidence specific adries this EXE. [1, 12]

| Address original according to reportu | Safe analytický name / meaning |
|---|---|
| `1:068A` | `RuntimeClass_IsKindOfLike` — prechod after predkoch |
| `1:06C0` | `RuntimeClass_CreateObject` — generická tvorba object |
| `1:0730` | `RuntimeClass_InvokeCreateCallback` |
| `1:114A` | `CWnd_DefaultConstructor` |
| `1:1AEC` | `CWnd_CreateObjectThunk` |
| `1:1666` | `CWnd_TeardownBody` |
| `1:171C` | `CWnd_DestroyWindowAndDetach` |
| `1:281E` | `CWnd_DeletingDestructor` |

These names sumarizujú already evidované meaning; is not eight novo objavených functions. Arrays CWnd `+0x16` and `+0x18` do not have be premenované on specific class or own relationship without next evidence. [1]

### New reprodukovaný problem: HandleMap16 has 40 B

Source skladá `HandleMap16` z dvoch 16-byte `MfcMap16` and troch 16-bit values. Content therefore zaberá `16 + 16 + 2 + 2 + 2 = 38` bytes. `MfcMap16` however contains `uint32_t`, so during test predvolenom ABI has zarovnanie 4. Kompilátor for end entire `HandleMap16` doplní two bytes and result is 40. Členské offset are correctly; nesprávna is overall size including final paddingu. Source pritom požaduje `static_assert(sizeof(HandleMap16) == 0x26)`. [1, 2]

| Kompilátor | Nezmenené declaration — measure | WITH original size assertom | Local model with `pack(push, 2)` |
|---|---:|---|---:|
| GCC / g++ | 40 B, align 4 | Očakávané failure `40 == 38` | 38 B, align 2; success |
| Clang / clang++ | 40 B, align 4 | Očakávané failure `40 == 38` | 38 B, align 2; success |

**Correction:** `mfc_layout.patch` locally obalí four binary structures to `#pragma pack(push, 2)` / `#pragma pack(pop)`. Dopĺňa check offset `0x00`, `0x10`, `0x20`, `0x22`, `0x24`. `pop` zabraňuje nechcenému ovplyvneniu next hostiteľských object. Scope pragma must začínať before define, ktorých layout upravuje. [13]

Neodstraňovať check size and nemenovať 40 B for correct historical stride. Correction modelu does not change finding o 38-byte original record. During directly read data is also still vhodnejší explicitný parser individual fields than nekontrolované pretypovanie bytes on C++ object.

**boundary test:** six kompilátorových konfigurácií minimálneho modelu, four úspešné run and two očakávané errors kompilácie. Nie complete build project, MSVC test nor run original EXE.

## 2. HUD, UIF, menu and automapa

### Important link: HUD is not only read game state

Project report umiestňuje to `3:A4CE..A502` unsigned obmedzenie HP on 100 with spätným write to `0x4C1D`. Also moderný helper `clampForHud` this status changes. Some pickupy najprv execute sum, so between operation can vzniknúť values nad 100. [3, 4]

Z toho follows riziko during optimalizácii: vynechanie celej routines during nezmenenom HUD or change its poradia can remove game vedľajší effect. **Separate draw from normalizácie state does not mean ľubovoľne move normalizáciu on other miesto cyklu.**

Čisto arithmetic example, nie runtime record original: HP 95, pickup +20, damage 10. Order pickup → clamp → damage gives 90. Order pickup → damage → clamp gives 100. Is therefore needed dohľadať and preserve original order, nie only same konečné draw functions.

### What známa address still nedokazuje

Globally source ammo `4C1F/4C20/4C44`, weapons `4C23`, inventory `4C28/4C29/4C45` and field `4BF6/4BF8` neuzatvárajú specifically UIF image, rozmery blitov, field number, boundary portrétov nor condition invalidácie. Nor známy prevod movement on map cells with mierkou 64 automaticky nedokazuje exact format coordinates HUD. [5, 6]

Automapa has v rekonštruovaných data separate 4096-byte block, stored from `USER.SAV+0xC5A3`; meaning each byte remains partial. To samo osebe nepreukazuje, that right čierny obdĺžnik HUD is target automapy. Needed is link specific draw routines on its target pixely. [5, 6]

`Menu.cpp` modeluje items and action according to active game and edície. Is not to complete reconstruction original process focusu, key, mouse, sound and prekresľovania. [7]

**Additional uzatvárateľné body:** miesto and condition calls AND4CE; čitateľ each inventory mask; input index and target obdĺžnik UIF blitu; portrétové branches; všetci write to čierneho panel. This bodom so far neprideľovať new addresses according to odhadu.

## 3. IMG / SEQDEF — image and sequences

### Existing rozpor address

Report dokumentuje read `FUN_1010_4B86` with výpočtom `8 + 90 * selector`. Low selector uses `id`, high `0x100 | id`. During interpretácii v tom istom IMG by nízke records 0–22 prekrývali image address `0x0000..0x07FF`; selector 23 starts on `0x081E`. High banka starts on `0x5A08`. [8]

This arithmetic is zrozumiteľná, but meaning prekrývajúcich sa bytes is not closed. Najvyššiu value has dohľadanie **specific file/handle, základu and pôvodu seeku** on danej branch and párovania EXE–data. Without toho is not correctly prepisovať format only therefore, that očakávame neprekrývajúce sa tables.

### New reprodukovaná medzera: offset v range does not have to be start image

`ImgArchive::load` checks, whether is nonzero reference between element dátami and koncom file. Then separate skenuje headers and creates `exactOffsetToFrame_`. Original version these two množiny already neporovná. Therefore reference on second byte headers or first pixel prejde element check, hoci `frameAtExactOffset` ho neskôr nenájde. [9]

Test was execute with celým load parserom, nie with its napodobeninou. Five usage source file was verify proti Git blob SHA; manifest is part of package. Input were small synthetic files, nie upravené komerčné game data.

| Synthetic input | Nezmenený parser | Local correction |
|---|---|---|
| Valid references including aliasov on same image | Prijatý | Prijatý |
| Wall reference `frameStart+1` — dovnútra headers | Prijatý; one nerozlíšený reference | Rejected |
| Object reference `frameStart+10` — dovnútra pixel | Prijatý; one nerozlíšený reference | Rejected |
| Reference exactly on EOF | Rejected | Rejected |
| Large image from `0x800`, file long than `0xB408` | Prijatý; SEQDEF flag true | Same; meaning SEQDEF sa neopravoval |
| Small image from `0x800`, kratší file | Prijatý; SEQDEF flag false | Same |

**Correction:** `img_frame_boundary.patch` after skončení skenovania verify each nonzero reference oboch address through `exactOffsetToFrame_.contains(offset)`. Preserves duplicity/aliasy, because viac items smie odkazovať on same start image. Nezavádza neoverenú condition jedinečnosti.

### Flag dostupnosti is not semantic confirmation

`hasSequenceDefinitions_` sa sets only according to condition `bytes.size() >= 0xB408`. Synthetic large image therefore can aktivovať this flag, hoci read data sekvenčné bytes ležia v its pixeloch. To nedokazuje correct takého file for original hru; dokazuje to only slabšiu záruku current API. [9]

Safe meaning flag is „can be prečítať kandidátsky range bytes“, nie „all sequences are valid and semantic confirmed“. Distinguish available bytes, structure valid and confirm usage is proposal next úpravy; priložený patch these verejné meaning does not change.

## 4. Sounds events and enemies

Známy format SND.DAT nesmie nahradiť evidence usage sound. Older audio audit distinguishes MIDI 1–15, rezervované items 16–33 and logical SFX items 34–110. Moreover 69/70 shared same PCM block and 73/74 shared next. Same bytes therefore neznamenajú same game event. [10]

### Neoverený preklad: requirement 0x12 version item 18

Report flag states during class `0x16`, GUARD state 9 requirement sound `0x12`. During directly chápaní as index archívu is to 18, what lies v rezervovanej areas auditu SND. [10, 11]

This comparison **nepotvrdzuje error original game** nor specific prepočet. Can ísť o relatívne ID, type events, other audio helper or nepresnosť anotácie. Until sa nedohľadá call routine and its all transformácie argumentov, nevkladať for example nepreukázaný posun `+34`.

Needed record each evidence:

`class a state → address call → celý list argumentov → preklad/table → index SND → PCM offset → condition a time play`

Osobitne evidovať logical identify events, item archívu and physical PCM block. Nezlúčiť otváranie and zatváranie only therefore, that use same vzorku.

## 5. Level events, bossovia and special strings

### Dracula: premena is separate prechod

Existing AI report dokumentuje prechod OBJECT class `0x11 → 0x14`, reset GUARD HP on `0xFF`, state `0x08`, nextstate `0x02` and timer 1. States also value related with sequence/frame `0x23` and requirement events/sound `0x22`; their complete resource meaning is not closed. First phase gives score 0, finálna death premenenej phases 200; obyčajný netopier class `0x08` is other case. [14]

Z toho follows potreba preserve path „lethal hit → transformácia → next phase“, nie terminate object during element vynulovaní HP. exact transformáciu netreba znovu označovať for celkom unknown, but still needs to close entire track grafiky, sound and konečného remove.

### Hamerstein: event marker is not evidence smrti

Write `0x51AA` prichádza z handlera GUARD state 9 for class `0x16`, with requirement sound, text and prechodom state. Itself this write neoprávňuje named `BossKilled`. Safe temporary name is marker class-16/state-9 events. [11]

### Shared flags prepájajú image, doors also boj

`0x51A6` is not only „dialog sa display“. According to reportu ovplyvňuje also selection základného damage class `0x16`: 33 during episode different from 3 and zero 51AND6, otherwise 100, still before difficulty. [11]

V E1M7 (interný level index 6) TRIGGER1 sets `51A6=1` and `51AB=1`. Nonzero 51AB switches tieňovanie on 6, zeros selection farieb podlahy/stropu and zastaví normálnu branch update door. Nadväzujúca special wall class `0x08` posunie 51AND6 on 2 and zruší 51AB. [11]

Takúto event therefore cannot zrekonštruovať as obyčajný listing text. Must be zachovaný input to mode, its trvanie and output z mode; correction jednej parts without others can nechať doors zastavené or damage v inom mode.

Flags `51A9` and `51AA`, for which report did not find priamych game čitateľov, neoznačovať automaticky for nepoužité. Can be part of save compatibility or indirect ciest. V E2M10 distinguish 20 call count from 20 milisekúnd — report nepotvrdzuje time ekvivalenciu. [11]

## 6. Status percent after this kole

Intervaly **45–65 %, 60–80 %, 65–80 %, 65–80 % and 65–85 %** are v zadaní older working odhady. This audit their nenahrádza novým measure celej areas.

Predovšetkým first interval nepoužívať as current evidence, that MFC is najslabšia area: deskriptory, map, parts vtable and rules obalov are already podstatne specific. Naopak one úspešný layout test nor 31 records neuzatvárajú all branches CRT, initialization and deštrukcie.

For budúci prepočet viesť osobitne: identify functions, complete analysis vetiev, semantic data, reconstruction code and comparison with original behom. Menovateľ must be vopred define list same role; nie count tabuliek or test, which sa interim changes.

## 7. Completion test and remain verify

Completion: 6 konfigurácií MFC modelu (2 očakávané kompilátorové reject, 4 úspešné run); 12 behových cases IMG (6 nezmenený parser + 6 local correction); verify piatich Git blob hashov; check aplikovateľnosti IMG patchu on entire usage file and MFC patchu on load original prefix.

Nevykonané: complete build project, test MSVC, debugger trace original Win16 programu, real game IMG/SND/MAP regresie, pixel and audio comparison. Two opravy riešia exactly listed problem, nie complete piatich subsystémov.

Najvyššia next priorita v original RE: evidence actual input SEQDEF read; complete preklad audio requirement; order HUD normalizácie; entire prechod 51AND6/51AB including save and restore. For moderný source have bezprostrednú value priložené small patche and regresné test.

## Zdroje

Project references are pripnuté on analyzovaný snapshot; names reportov with dátumom are not tvrdením, that is new experiment execute v this kole.

1. [Win16MfcMemory.hpp](https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/src/re/Win16MfcMemory.hpp), blob `7da9b2ffe125b8c663a4e607d0eccfc734594168`.
2. [CMakeLists.txt](https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/CMakeLists.txt) and [Win16_mfc_memory_test.cpp](https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/tests/win16_mfc_memory_test.cpp).
3. [PLAYER_HEALTH_RE.md](https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/docs/PLAYER_HEALTH_RE.md).
4. [PlayerHealthRuntime.hpp](https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/src/game/PlayerHealthRuntime.hpp).
5. [HUD_UI_RE.md](https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/docs/HUD_UI_RE.md).
6. [RecoveredRuntime.hpp](https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/src/game/RecoveredRuntime.hpp).
7. [MenuModel.cpp](https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/src/ui/MenuModel.cpp).
8. [nite3w_img_seqdef_2026-09-23.md](https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/analysis/nite3w_img_seqdef_2026-09-23.md).
9. [ImgArchive.cpp](https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/src/formats/ImgArchive.cpp), blob `f9a0bfcccbf4a5450d3dc5cabc7482a376f23cdc`.
10. [RE_AUDIT_CHEATS_AUDIO.md](https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/docs/RE_AUDIT_CHEATS_AUDIO.md).
11. [nite3w_user_sav_story_flags_2026-09-23.md](https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/analysis/nite3w_user_sav_story_flags_2026-09-23.md).
12. [Microsoft: TN003 — Mapping of Windows Handles to Objects](https://learn.microsoft.com/en-us/cpp/mfc/tn003-mapping-of-windows-handles-to-objects?view=msvc-170).
13. [Microsoft: pack pragma](https://learn.microsoft.com/en-us/cpp/preprocessor/pack?view=msvc-170).
14. [nite3w_ai_state_machine.md](https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/analysis/nite3w_ai_state_machine.md).

Locally experimentálne evidence: `mfc_layout_results.json`, `img_valid_results.json`, reprodukčné source and `verified_source_manifest.json` v this package.