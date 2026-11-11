# Nitemare 3D evidence campaign snapshot

This publication extends commit a43690cac60dea52020b557c733c239504ba9bf1. The campaign is incomplete. No original game executable, asset, native decoder or emulator binary is included.

Current NON-CODE map: `pass1_episode_files/noncode_intervals.csv` and `.json`, exactly 57,295 baseline bytes: PARTIAL 54,746; CLASSIFIED ONLY 2,505; UNKNOWN 44; DEEP VERIFIED 0. See `CAMPAIGN_CONSOLIDATED_REPORT.md` for current scope and the thirteen-area report. Historical batch reports retain the state and publication notes at their original analysis time; those notes are not current branch status.

Current bounded function catalog: 48 ranges, 1,691 instructions / 4,028 code bytes; 55,592 typed data bytes across the whole image. These are campaign bounds, not an inventory of every game function. Controlled replay: 7,909 cases plus a separate 65,548-case normalization-prefix campaign. Original DOSBox-X/game runtime tests: zero. A mock, fixture, seeded replay or chunk parser never proves full gameplay parity.

New findings include the real MAP.1 count of eleven levels, conditional music-table cross-row access, signed-only upper level guard, audio selectors/loader/toggles, DOS I/O wrappers, Win110 relocation-backed trig callers and corrected angle-function boundary. Follow individual reports for limitations.

Reproduction requires the exact user-supplied game files and historical inventories pinned in the scripts. The latest map has an independent membership/hash/overlap check. Full generated case dumps can be regenerated; `PUBLICATION_OMITTED_GENERATED.json` records their local hashes and sizes. Existing remote files are retained, including older snapshots. Publication manifests cover this delta only, and do not assert semantic completeness.
