# Nitemare 3D evidence campaign — 2026-11-12 snapshot

The campaign is incomplete. This update extends verified commit 8052ec6328b320633babef328e4e6f3831de041a without deleting historical evidence. No original game executable, complete asset, native decoder or emulator binary is included.

Current historical PASS320 NON-CODE map: `pass1_near_heap_flags/noncode_intervals.csv` and `.json`, exactly 57,295 bytes: PARTIAL 57,102; CLASSIFIED ONLY 149; UNKNOWN 44; DEEP VERIFIED 0. SHA-256 `3021969d4e4348715816361fa387631e7d6cfd9fc9dcc136e26073f0f9984d1b`. Independent partition checks prove membership, hashes and no gaps/overlaps; they do not prove complete semantics.

Current bounded catalog: 122 functional ranges, 4,563 instructions / 11,304 code bytes, 57,988 typed data bytes across the full image. These are campaign bounds, not the complete game inventory. Controlled original-instruction replay: 971,101 cases plus separately counted direction-prefix cases. Natural original-EXE DOSBox-X scenarios: 5. Runtime scope: retained original packed DOS2 EXE scenarios under DOSBox-X built-in DOS with debugger stops: startup/B3, main/defaults35C, BSF/audio/VGA initialization and when present post-VGA slot/resource initialization; no gameplay/audio-output/rendered-frame/Win16 runtime parity; repeated prefix checks overlap. Mocked dependencies, seeded replays and matching data layouts do not prove full gameplay or Win16 behavior parity.

See CAMPAIGN_CONSOLIDATED_REPORT.md for the current thirteen-area table. Historical batch reports retain their original counts and publication notes; those notes are not current branch status. New reports cover RNG/damage, scheduler/audio/VGA, CRT/heap/startup/FCB, actual BSF assets and DOS-version comparisons. Every open issue remains explicit; no new semantic percentage is invented without a full denominator.

Reproduction requires exact user-supplied files and historical inventories pinned by path and SHA in scripts. PUBLICATION_OMITTED_GENERATED.json records hashes and sizes for bulky generated evidence. Sources in dos_parse_reference/source_manifest.json are external Microsoft MS-DOS reference snapshots, retrieved from pinned URLs and hash-checked; their implementation is not the user's running DOS. This text-only publication excludes their complete source files; retrieve them from that manifest when needed.

Runtime proofs pin local raw capture paths. Raw memory dumps and original assets are excluded; regenerate them with runtime_dosbox_startup.py and verify_dosbox_startup_capture.py using the pinned original files and DOSBox-X binary. Included .conf files record the capture settings, not portable absolute paths.

PUBLICATION_DELTA_MANIFEST.json covers this update's changed content. Previously published files are retained. No PE32 port is included.
