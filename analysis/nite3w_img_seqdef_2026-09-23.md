# NITE3W IMG and sequence-definition loader audit — 2026-09-23

## Scope and conclusion

This pass traces the Win16 1.10 loader in the extracted executable, checks the same selector arithmetic in Win16 1.8 and DOS v2.0, and compares it with the supplied MAP/IMG exports.

The loader's directory reads, 90-byte record size, bank formulas and caller-selected bank are now confirmed. The supplied IMG file has valid wall and object image-offset directories, but its low sequence bank physically overlaps those directories for selectors 0–22. Several decoded low-bank values are implausible for a separate sequence table; some map-used wall selectors produce a zero frame count. This is a concrete unresolved data-layout/build-pairing issue. It does not prove that the original game has an animation bug.

## Confirmed executable behavior

### Image directories

Win16 1.10 `FUN_1010_4C8A` opens the episode IMG file and reads 0x400 bytes from its start into a 256-entry dword table. Wall VEC resource IDs index this table as `directory[id]`. After that read, the file pointer is at 0x400; the loader reads another 0x400 bytes sequentially into the same buffer. Object resource IDs index this second table.

The loader reuses a decoded image group when two VEC records have the same file offset. The callsites select sequence-definition banks as follows:

| Caller | Selector | Bank choice passed to reader |
|---|---|---|
| Ordinary wall VECs | VEC byte +0 | `param6=1`, selector is the byte value |
| Object VECs | object VEC byte +0 | `param6=0`, selector is `0x100 | id` |
| Special class-5 wall path | wall ID | `param6=0`, selector is `0x100 | id` |

The call setup is visible in raw Win16 segment 3: wall call near 0x4DB2 pushes 1; object and class-5 paths near 0x4F9F and 0x50B0 push 0.

### Sequence-definition and frame reads

Win16 1.10 `FUN_1010_4B86` computes a 16-bit selector, seeks to `8 + 90*selector` with origin 0, and reads exactly 90 bytes. The loader uses word +0 as the frame interval, byte +2 as frame count, and byte +3 as a nonzero test for allocating/copying the optional 90-byte selector table. The remaining bytes are preserved without assigning unsupported names.

For each counted frame, `FUN_1010_4AB0` reads a 10-byte frame header and advances by `10 + width*height` bytes to the next image. The timed wall updater `FUN_1010_65A6` uses the interval as milliseconds, updates VEC frame byte +3, wraps ordinary sequences, and uses an eight-entry selector table when the optional table pointer is present. Class-specific exceptions remain in that updater.

The address logic has independent source matches:
- Win16 1.10: `FUN_1010_4B86`, with raw selector-bank branch and 0x5A multiply.
- Win16 1.8: `FUN_1010_4AE2`, same record size and arithmetic.
- DOS v2.0: `FUN_1000_2CF4`, same low/high selector construction and seek formula.

This supports shared loader logic; it does not by itself prove matching episode assets or runtime-visible animation.

## Recovered layout

| Region | File offsets | Size | Meaning established by code |
|---|---:|---:|---|
| Wall image directory | `0x0000–0x03FF` | 256 × 4 B | wall selector → first frame offset |
| Object image directory | `0x0400–0x07FF` | 256 × 4 B | object selector → first frame offset |
| Low sequence bank | begins `0x0008` | 256 × 90 B | selector = `id` |
| High sequence bank | begins `0x5A08` | 256 × 90 B | selector = `0x100 | id` |
| High bank end | `0xB408` | — | first offset after its final record |

The low bank spans `0x0008–0x5A07`. Its records for selectors 0–22 overlap the two directory blocks; selector 11 straddles the `0x0400` boundary. Selector 23 starts at `0x081E`, after the directory region. The high bank does not overlap either directory.

This is a direct consequence of the executable's address arithmetic. Whether the shared bytes are an intentional multi-use encoding or the supplied executable and IMG came from different episode/build extractions is not yet known.

## Supplied-data check

Input: `IMG(10).1`, 2,250,921 bytes, SHA-256 `0d7b5bf9a3348be263d337201bd98e867f765b87be3f15666164c39763dc1267`. The second local IMG copy has the same hash.

Scanning 10-byte frame headers from the first image at `0xBC00` reaches EOF cleanly after 840 frames. The two 256-entry directories contain 150 nonzero wall offsets (117 unique) and 167 nonzero object offsets (92 unique); all 317 nonzero entries point exactly to a scanned frame boundary. This validates the directory boundaries and offsets for this data sample.

The low selector records read from the same bytes include:

| Low selector | Record offset | Interval | Frame count | Byte +3 |
|---:|---:|---:|---:|---:|
| 1 | `0x0062` | 4 ms | 84 | `0xDD` |
| 2 | `0x00BC` | 56,900 ms | 7 | `0x00` |
| 3 | `0x0116` | 10 ms | 42 | `0x8F` |
| 4 | `0x0170` | 41,126 ms | 14 | `0x00` |
| 5 | `0x01CA` | 2 ms | 130 | `0x4C` |
| 6 | `0x0224` | 0 | 0 | `0x00` |
| 12 | `0x0440` | 17,144 ms | 20 | `0x00` |

Selector 12's record begins inside the object image directory. In the supplied 11-map MAP, wall ID 6 occurs in map data despite its decoded record reporting no frames. These observations make the low-bank bytes unsafe to present as an independently stored, fully understood sequence table. They may still be valid inputs to the original loader if the selected asset or selector interpretation differs from this sample.

## Code change and verification

`src/formats/ImgSequenceLayout.hpp` now records the confirmed directory/bank offsets and computes selector offsets without inventing the remaining field meanings. `ImgArchive` now exposes separate 256-entry wall and object directories and preserves raw records from both sequence banks. The inspector reports the two directories independently.

The new `n3d_img_archive_layout_test` constructs a small synthetic IMG with both directories, a frame, and a record in each non-overlapping selector region. It checks the 256-entry tables, exact frame-offset lookup, and the selector formulas, including the transition where low records stop overlapping the directories. The test is scoped to parsing/layout facts; it does not attempt to validate animation output.

## Remaining proof needed

1. Verify the exact filename/episode ID chosen by the 1.10 loader against the supplied IMG export and its extraction provenance.
2. Obtain a runtime capture or memory dump for representative low selectors (especially wall IDs 1, 2 and 6); verify loaded frame counts, group indices and VEC frame indices.
3. Check whether the overlapping low-bank bytes are deliberately shared by the data packer, or whether the executable and assets are from incompatible builds.
4. Decode the eight optional selector entries only after step 2 confirms which raw records the engine consumes.
5. Match DOS VGA, Win16 WinG and the current IMG assets before claiming renderer/animation parity.
