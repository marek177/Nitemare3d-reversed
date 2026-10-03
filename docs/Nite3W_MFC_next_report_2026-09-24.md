# Nite3W — next audit MFC/memory väzieb

**Date:** 24. 9. 2026.  
**Predmet tohto kroku:** correct auditného tool, which interpretuje NE segment and relocations.  
**Is not predmetom confirm:** new beh NITE3W, new read original EXE nor uzavretie all MFC string.

## Result

V source `tools/ne_render_audit.py` som reprodukoval four skupiny problem, which can decrease spoľahlivosť automatických memory assign. Create som local opravu, patch and 26 synthetic regresných check. Original version splnila 8 check; corrected version 26. Is cielenú sadu for these cases, nie o measure overall kvality programu nor percento poznania MFC.

Source was prevzatý z `marek177/Nitemare3d-reversed`, commit `9e002c10d0449885af883177d36c3037f2179e82`. Local copy has exactly 9 049 bytes; compute Git blob SHA-1 `560fa7dc8414341fefa6c40ca585ee27123fcef0` sa match with data konektora. To verifies identitu test **skriptu**, nie identitu EXE.

Repository nor original EXE som nemenil. Correction is priložená as files on locally usage or neskoršiu check integráciu.

## 1. Segment relocation sa menila on nepodložený complete pointer

### Finding v source

Original method `_expand_relocation_chains()` during `source_type == 2` and internom cieli without next evidence reads word on `source_offset - 2` and uses ho as target offset. Komentár predpokladá, that is segment field far addresses.

To is correctly only v specific already confirm layout. Separate selector can be also operandom instructions or poľom structures. Relocation record type SELECTOR itself nepotvrdzuje meaning predchádzajúcich dvoch bytes. Reference loader Wine distinguishes write itself selectora and write entire far pointer [WITH2].

### Reprodukcia — explicitly synthetic data

On start test segment are bytes `90 B8 FF FF`. Segment relocation on offset 2 cieli on logical segment 2. Previous word is `B890`, but test mu nepriraďuje meaning offset pointer.

| Version skriptu | Pozorovaný output |
|---|---|
| Original | `internal 2:B890` |
| Corrected | `internal 2:<selector-only>` |

**Consequence:** nepodložený complete target already nevznikne. On assign offset sa requires separate analysis instructions or dátovej structures. Therefore can corrected command `xrefs` nájsť menej zásahov during search exact addresses; nejde samo osebe o regresiu count evidence, but o remove automatického odhadu.

Nevieme so far vyčísliť, koľkých specific miest original NITE3W sa this situácia týka. Finding neanuluje tie older targets, which were independent confirmed instruction.

## 2. `0xFF` v internom cieli is not automaticky segment 255

Original `_read_relocations()` format all interné targets as `word1 & 0xFF : word2`. Nerozlišuje case, when `0xFF` references on ordinal v entry table. Wine for this case explicitly search input according to ordinálu [WITH2, WITH3].

Synthetic entry table map ordinal 1 on `1:0020`:

| Version skriptu | Pozorovaný output |
|---|---|
| Original | `internal 255:0001` |
| Corrected | `internal 1:0020 [entry ordinal 1]` |

Correction dopĺňa read fixed and movement input, zachovávanie poradových čísel through nepoužité skupiny, distinguish absolútnej items `0xFE` and explicit designation missing ordinálu as nevyriešeného. Logical target sa nevydáva for runtime selector nor automaticky for name MFC functions.

**Prínos for MFC:** correctly named konštruktorov, tabuliek and indirect targets must stáť on correct interpretácii these relocation. V this kroku however were not provided original records these specific MFC items, therefore their neoznačujem for novo closed.

## 3. read segmentu without file data return header EXE

`file_offset()` already v original skripte correctly reject segment without store data. `bytes_at()` however this check nemal and použil zero file základňu.

During `bytes_at(2, 0, 2)` for synthetic segment 2 without file obrazu:

- original method return `4D 5A`, therefore `MZ` z headers file;
- corrected method return error `segment 2 has no file-backed bytes`.

Is to directly reprodukovaná error methods `bytes_at()`. Is not to evidence, that entire original command `disasm` úspešne vypísal header as code: neskoršie call `file_offset()` by mohlo operation zastaviť. Difference is important for exact vyhodnotenie závažnosti.

Added are also check physical range segment v file. Synthetic shortened data sa must not ticho return as neúplný, but data valid block.

## 4. Source width relocations and aditívny offset `0xFFFF`

Original prechod checks for each source two bytes and slučku nezačne during `source_offset == 0xFFFF`.

To prehliada difference between width result write and width odkazu on next článok string. Distinguish BYTE, SELECTOR, POINTER32, OFFSET16 and others type is visible also v reference loaderi [WITH2].

Reproduced cases:

| Case | Original skript | Correction |
|---|---|---|
| Far pointer 4 B on offsete 62 v 64-bajtovom segmente | Prijme, hoci presahuje end | Odmietne |
| Aditívny BYTE on poslednom byte 64-byte segment | Reject, because chce 2 B | Prijme 1 B |
| Aditívny BYTE on offset `0xFFFF` plného 64-KiB segment | Potichu creates 0 source miest | Preserves jedno miesto |
| String relocation with dvoma miestami | Preserves obe | Preserves obe |
| Cyklický string | Reject | Reject |

During neaditívnej relocation potrebuje read článku string at least 2 B. During aditívnej relocation sa this string nečíta. Value `0xFFFF` as valid source offset jednobajtovej aditívnej relocations sa nesmie zameniť for terminate článok.

Output aditívnej relocations sa denotes as **basic target, nie result address**. Tool nesimuluje entire loader.

## Added schopnosti and boundary opravy

Import according to name teraz loads also meno z imported-name table; test uses `KERNEL / GlobalAlloc`. This is doplnenie schopnosti, nie evidence objavenia specific calls GlobalAlloc v NITE3W.

Commands `xrefs` and `json` already nevyžadujú Capstone. Ten sa importuje only for `disasm`. iterate segment are explicitne reject, because tool pracuje with priamym prevodom on file bytes and is not complete NE loaderom. OS fixupy remain marked as nepriehľadné records without predstierania vyriešeného target.

Tool still nedodáva complete graf read/write, indirect calls, own object nor MFC lifetime. Memory ownership sa cannot odvodiť only z toho, that note target relocations. Všeobecná dokumentácia MFC moreover different temporary obaly from lifetime systémových handle [WITH4]; its dnešné layout cannot without evidence preniesť to historical Win16 EXE.

## Actually performed tests

| Meranie | Result |
|---|---:|
| Count synthetic check | 26 |
| Original version: úspešné | 8 |
| Original version: nesplnené očakávania | 17 |
| Original version: neočakávaná výnimka | 1 |
| Corrected version: úspešné | 26 |
| Corrected version: neúspešné | 0 |
| Synthetic CLI export JSON | Úspešný; content skontrolovaný |
| CLI without Capstone during požadovanom disasm | Očakávaná error, exit 2 |
| Running disassembler Capstone | Nie |
| Beh original game | Nie |

Original source has import Capstone already during load modulu. Test adaptér preň uses stub **only on povolenie importu**. Its constructor disassemblera vyvolá error, keby sa použil. None disassemblácia sa thereby nenapodobňovala nor neoznačuje for test.

18 neúspešných check does not mean 18 independent missing. Sada zahŕňa viaceré variant tých istých problem also new schopnosti opravy. Nor 26/26 does not mean complete pokrytie NE format.

## exact percento MFC/memory

**Overall percento still does not have supported complete menovateľ.** Count splnených check tool sa nesmie pripočítať ku score poznania MFC.

| Pointer | Status after this kroku |
|---|---|
| Vybraná synthetic sada test opravovaného tool | 26/26 = 100 % this sady |
| Complete implement NE parsera | Nevyčíslená; is not complete loader |
| Novo closed original MFC strings z bytes EXE | 0 |
| New runtime records game | 0 |
| Overall MFC/memory semantic pokrytie | Undetermined; values 98,xxx % unconfirmed |

Skoršie addresses `1000:338C`, `1008:003A`, `1008:0266`, `1000:05E8` remain without new byte verify v this kroku. Skorší rozpor code version name classes during `1008:003A` thereby is not vyriešený.

Finding errors neoprávňujú automaticky mark skorší count 6 082 relocation miest or 4 904 interných fixupov for nesprávny. Needs to spárovať exact binary, version tool and oba output; output targets and count source miest are different veličiny.

## Usage package

Needed is Python 3.10 or novší. Parser and export JSON do not have externé knižničné depend. After rozbalení possible on Windows pretiahnuť original `NITE3W.EXE` on `run_ne_audit.cmd`. Creates sa `ne_audit_output.json`; original EXE sa only reads.

Alternatíva z command row:

```text
py -3 patched\ne_renderer_audit.py "C:\NITEMARE\NITE3W.EXE" json > ne_audit_output.json
py -3 -m unittest discover -s tests -v
```

This usage on original NITE3W v this kroku performed nebolo. Package contains original source, corrected source, unified diff, test, protokoly and výrazne marked synthetic `.ne` vzorky. Neobsahuje original game EXE.

## Zdroje

- **WITH1 — check source tool:** https://github.com/marek177/Nitemare3d-reversed/blob/9e002c10d0449885af883177d36c3037f2179e82/tools/ne_render_audit.py
- **WITH2 — Wine, primary source NE segment loadera:** https://raw.githubusercontent.com/wine-mirror/wine/master/dlls/krnl386.exe16/ne_segment.c — read 24. 9. 2026; `apply_relocations`, especially distinguish interného ordinálu, source type and aditívnych/neaditívnych ciest. Is to reference implement Wine, nie evidence exact behavior original Windows 3.11.
- **WITH3 — Wine, entry table and ordinal lookup:** https://raw.githubusercontent.com/wine-mirror/wine/master/dlls/krnl386.exe16/ne_module.c — read 24. 9. 2026; `build_bundle_data`, `NE_GetEntryPointEx`.
- **WITH4 — Microsoft, TN003:** https://learn.microsoft.com/en-us/cpp/mfc/tn003-map-of-windows-handles-to-objects?view=msvc-170 — všeobecné odlíšenie handle map and lifetime.
- **Locally evidence:** `evidence/baseline_tests.txt`, `evidence/patched_tests.txt`, `evidence/metrics.json`, `evidence/cli_smoke_log.txt`.