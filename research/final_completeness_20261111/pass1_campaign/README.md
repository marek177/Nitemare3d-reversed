# Nitemare 3D evidence campaign — 2026-11-12 snapshot

The campaign is incomplete. This update extends verified commit 52924ebf849dd79d15af9d7c164b8304f50cae87 without deleting historical evidence. No original game executable, complete asset, native decoder or emulator binary is included.

Current historical PASS320 NON-CODE map: `pass1_fcb_prefix/noncode_intervals.csv` and `.json`, exactly 57,295 bytes: PARTIAL 57,101; CLASSIFIED ONLY 150; UNKNOWN 44; DEEP VERIFIED 0. SHA-256 `899ba518a5b8b64b24837e4f40f14e0c918e0bbb2777d2e13ae0803bb42482ed`. Independent partition checks prove membership, hashes and no gaps/overlaps; they do not prove complete semantics.

Current bounded catalog: 109 functional ranges, 4,068 instructions / 10,156 code bytes, 57,987 typed data bytes across the full image. These are campaign bounds, not the complete game inventory. Controlled original-instruction replay: 915,637 cases plus separately counted direction-prefix cases. Natural DOSBox-X/game runtime: zero. Mocked dependencies, seeded replays and matching data layouts do not prove full gameplay or Win16 behavior parity.

See CAMPAIGN_CONSOLIDATED_REPORT.md for the current thirteen-area table. Historical batch reports retain their original counts and publication notes; those notes are not current branch status. New reports cover RNG/damage, scheduler/audio/VGA, CRT/heap/startup/FCB, actual BSF assets and DOS-version comparisons. Every open issue remains explicit; no new semantic percentage is invented without a full denominator.

Reproduction requires exact user-supplied files and historical inventories pinned by path and SHA in scripts. PUBLICATION_OMITTED_GENERATED.json records hashes and sizes for bulky generated evidence. Sources in dos_parse_reference/source_manifest.json are external Microsoft MS-DOS reference snapshots, retrieved from pinned URLs and hash-checked; their implementation is not the user's running DOS. This text-only publication excludes their complete source files; retrieve them from that manifest when needed.

PUBLICATION_DELTA_MANIFEST.json covers this update's changed content. Previously published files are retained. No PE32 port is included.
