# Nitemare 3D: 12 areas — verify status and remain evidence

23. 9. 2026. verify are stored audity and binaries `N3D-UNFU(2).exe` (SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`) and `nite3w(20260921-205703).exe` (SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`). Designation DOS 2.0 and Win16 1.10 z predchádzajúcich auditov sa nesmie without separate version fingerprintu automaticky preniesť on these specifically files. This dokument nepredstiera complete reconstruction source code.

## New priame verify binary

- **DOS has also `debug.txt`.** V DOS file are two nulou terminate výskyty on physical offset `0x19D5E` and `0x19D68`; Win16 has jednu on `0x2DFDA`. Thereby sa opravuje older dojem, that diagnostic file existuje only in Win16. Itself string nedokazuje, that ho normal game creates or that existuje switch `-debug`.
- **Obe binaries contain `Invalid command line`.** DOS on `0x19FB6`, Win16 on `0x2CDB0`. Is to reason cielene process referencie on string and input parser; itself prítomnosť v binary nedokazuje game argumenty, because can ísť o knižničný runtime.
- Win16 is format NE for Windows 3.x, DOS file MZ. Audit NE fixupov for identical Win16 hash zaznamenal 446 relocation records, which sa rozbalia on 6 082 miest. Z nich is 4 904 interných odkazov and 1 178 importov. This count **is not** count all XREF: near calls nevyžadujú fixup.

## Status 12 areas

| # | Area | What is supported | What still bráni completion |
|---:|---|---|---|
| 1 | GUARD AI | 26 B record, switch `00–15`, LOS through map to 8 buniek, directional mask troch sektorov, proximity ±64 | All writery and branches state `0A–0D`, boss strategy, sluch, reprodukovateľné dynamic trasy |
| 2 | Render | Projection VEC, ownership column, spájanie to 20 B spanov, palette stmavenie | Orientačné compare during prekrytí, mask wall, finálny texel loop, DOS/Win16 image match |
| 3 | Projectiles | Eight slotov × 42 B, pool v SAVE, update, collision, animation dopadu | Nepomenované bytes embedded OBJECT, exact damage path and timing; DOS parita after raw disassembly |
| 4 | OBJECT | 350 × 28 B v SAVE, links on projectile and GUARD | Reader/writer matica each offsetu and differences according to tried |
| 5 | SEQDEF | Obe IMG banky, all 90 B fields, selector arithmetic, 10 B disk header + pixel stream, frame count, intervaly and aliasy valid v troch IMG | Exact EXE/episode/IMG pairing; runtime link selectorov on wall/object/guard, alternate/facing results, event/SFX and cross-build timing |
| 6 | Weapons | Modes 0/1/3 projectile, 2 hitscan; cooldown `[2,1,3,1]` krokov in Win16 audite | Complete vzorec damage, range/spread, ammo and class×difficulty proti všetkým target |
| 7 | Walls | ID/class map, some special branches; completion explodujúcej walls in Win16 nuluje map bytes | Complete ONE_SHOT/SPECIAL1 and DOS completion chain, dynamic test |
| 8 | USE | Väčšina kľúčov, door, warpov, remote commands | Neoznačené special handlers and combinations all map variant |
| 9 | USER.SAV | Slot `0xD6E7`; 94 B on `+0x2035` pokryté offset after offset; direct-use arrays, derived pointer and load rebase zdokumentované | Several nexrefovaných bytes and partial arrays require raw disassembly/save diff; 8 script flagov, load/rebase hrany and širšie runtime test |
| 10 | DEMO | Header 6 B, record 8 B, monotónne time arrays | Bit map input, jednotka time, assign DEMO.2/3 k map |
| 11 | Debug | `debug.txt` directly v oboch skúmaných file; Win16 logger and its flag v older audite | Cross references oboch DOS výskytov and Win16 flagu, aktivátor, distinguish from cheat menu and knižničného parsera |
| 12 | Resource | SND directory/aliasy; UIF 32 slotov; FLI 488 v header and 489 physical frame block | UIF 0–2 loader, SND payload/codec parita, exact final FLI right and IMG metadata |

Podrobný field-by-field save audit, corrected IMG layout and 1,536 selectorový valid listing are v `Nitemare3D_save_animation_closure_2026-09-23.md` and `Nitemare3D_IMG_SEQDEF_frame_inventory_2026-09-23.csv`.

## Specifically following evidence role

1. Získať **complete Ghidra/IDA exporty** oboch exactly hashovaných file (including assemblera and segment map). Doterajší ZIP with XREF contains relocation miesta and skript for export IDA, nie export itself IDA XREFov.
2. V DOS search all references on physical strings `0x19D5E`, `0x19D68`, `0x19FB6`; in Win16 on `0x2DFDA`, `0x2CDB0`, and subsequently check functions and their callerov. Nepovažovať physical offset automaticky for segment addresses.
3. For remain GUARD/OBJECT arrays and nexrefované USER.SAV bytes create raw-instruction read/write table; SEQDEF 90 B static matica and three IMG stream inventory are already closed. Dynamic confirm selector/facing/alternate result and save/load diffs.
4. During each z 12 areas spárovať same input data, tick and image/status v DOS also Windows; differences write as test cases. Percento completion up to after takejto valid.

## Opravy and neistoty older podkladov

- Older veta `guard+0x12=8` as *pain timer* is v rozpore with neskorším read `+0x12` as invalidácie directional sprite cache. Without prechodu all prístupov is correctly držať second výklad as lepšie podložený and this rozpor explicitne test.
- Designation `DAT_51A4` raz as remote-door mask, inokedy as safe/combo progres, is konflikt named; needs to vyťažiť all readerov/writerov and verify, whether is tú istú address and binary version.
- Older približné percentá are not measure. 1 358 párovaných z 1 486 functions does not mean 91,4 % semantic znalosti.

**Východiskové podklady:** `Nitemare3D_deep_unknowns_2026-09-23.md`, `Nitemare3D_projectile_pool_deep_map_2026-09-23.md`, `Nitemare3D_unknown_logic_audit_2026-09-23.md`, `Nitemare3D_DEMO_playback_analysis_2026-09-23.md`, `Nitemare3D_nite3w_xref_audit_2026-09-22.zip` and listed two binaries. Table sumarizuje previous static analysis; new directly performed binary verify is v element oddiele.