# DOS v2.0 renderer v0.69 — forward visibility replay (2026-10-20)

**Evidence: ORIGINAL_RUNTIME_BOUNDED**, one archived original DOS2 E1M1 snapshot, not a new emulator execution and NOT original-vs-port pixel parity.

## Result

The standalone Python and C++20 forward models use the original 592 world VECs, list counts, view camera, octant flags and list cursors. The original saved projected coordinates, owner words and span bytes are checked only as **reference output**, never fed to the forward stages.

| Stage | Captured DOS2 result |
|---|---:|
| Initial orientation cursors | 127 / 137 / 70 / 52 |
| Octant enable flags | 0 / 1 / 1 / 1 |
| Candidate VECs visited | 72 |
| Projected VECs exact from world data | 70 / 72 |
| Unresolved offscreen projection records | 2 |
| Owner buffer in viewport (x=8..311) | **304 / 304 WORDs** |
| DOS 18-byte wall span table | **162 / 162 bytes** (9 spans) |
| Original vs remake complete framebuffer + DAC | **NOT VERIFIED** |

The four edge columns from v0.68 (x=18,40,175,269) now match the original without per-column exceptions. Processing candidates in naive orientation-list order disagrees in five columns. The replay uses orientation-aware owner conflict precedence and the original player-relative interleaving. It does **not** establish opcode-level equivalence of DOS2 0x1021E and 0xFEFA to the Win16 conflict matrix.

Two projections are still not equivalent although both lie outside this viewport: VEC pointer 0x8A28 original (-908,5514,-374,6267), model (-954,6267,-791,5514); 0x9A90 original (0,6267,0,6267), model returns both behind near plane. Their behavior in other views is OPEN.

## Evidence hashes

- Original runtime archive SHA256: 512521df5ddcafd623c65fe38b1e099bbe7e2d22f0dca7dabaf16e0272aa3e3b.
- Original 65536 B stack/global segment SHA256: 1878c03fbd7f40d06dd87691e608d6143c16de0dcb347894d0e0bd6c2a49d98e.
- Both original/recomputed 304 owner words SHA256: 55941a3a1e9e8a2a34db9a0827dae41e7efdbdfd628c7b30c063e7a24179f0cb.
- Both original/recomputed 9x18 B span records SHA256: cbf157a07ce343dc9da1fa501fdac40e8338d6d9bd3d65d786e60c4c8edb88cd.
- Separate v0.69 source/test ZIP SHA256: 2195695b6b50d5b74ab80fc695a3216fc0349380748df83afa2ce3b34df3b28c.

## Verification and limits

Standalone Python with the user-provided original archive: **16/16 tests PASS**; no original supplied: 9 pure synthetic tests PASS and original-data suite skipped. C++20 replay PASS with UBSan and strict compilation flags. Full local stage-enabled CMake/CTest: **81/81 PASS**. These are not 81 pixel-perfect game frames.

The C++ header, Python oracle, independent test suites, proof JSON, regression logs and conflict-refusing installer are in the external v0.69 research ZIP. The ZIP contains no game EXE/MAP/IMG, screenshots or 64 KiB original memory dump. Experimental components are **not wired to live rendering**.

Current src/renderer/Raycaster.cpp remains diagnostic DDA; src/main.cpp remains unmodified. The 1:1 goal still requires verified DOS opcode semantics, MAP-to-VEC reproduction, complete wall U/V/shade/sprites/HUD and synchronized original-vs-remake 64,000 indexed pixel + 768 DAC component zero-diff.
