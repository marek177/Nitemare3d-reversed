# Nitemare 3D gameplay cross-build static parity gate

This gate uses normalized function matching as a regression signal. It does not replace raw disassembly or original-runtime tests.

## WIN

| Target | Ref build | Ref function | Match | Similarity |
|---|---|---|---|---:|
| `FUN_1010_71dc` | `NITE3W16.EXE.c` | `FUN_1010_7138` | fuzzy-normalized | 98.25% |
| `FUN_1010_76fc` | `NITE3W13.EXE.c` | `FUN_1010_74e4` | exact-normalized | 100.00% |
| `FUN_1010_7920` | `NITE3W13.EXE.c` | `FUN_1010_7708` | exact-normalized | 100.00% |
| `FUN_1010_7b56` | `NITE3W13.EXE.c` | `FUN_1010_793e` | exact-normalized | 100.00% |
| `FUN_1010_8b06` | `NITE3W18.EXE.c` | `FUN_1010_8a62` | fuzzy-normalized | 93.59% |
| `FUN_1010_9d30` | `NITE3W16.EXE.c` | `FUN_1010_9c82` | fuzzy-normalized | 96.72% |
| `FUN_1010_9e20` | `NITE3W13.EXE.c` | `FUN_1010_9bfe` | fuzzy-normalized | 97.38% |
| `FUN_1010_a0ee` | `NITE3W13.EXE.c` | `FUN_1010_9ecc` | exact-normalized | 100.00% |
| `FUN_1010_a1ea` | `NITE3W13.EXE.c` | `FUN_1010_9fc8` | exact-normalized | 100.00% |
| `FUN_1010_a2ce` | `NITE3W13.EXE.c` | `FUN_1010_a0ac` | exact-normalized | 100.00% |
| `FUN_1010_a3b6` | `NITE3W18.EXE.c` | `FUN_1010_a308` | fuzzy-normalized | 98.12% |
| `FUN_1010_a97c` | `NITE3W13.EXE.c` | `FUN_1010_a75a` | exact-normalized | 100.00% |
| `FUN_1010_a9e0` | `NITE3W13.EXE.c` | `FUN_1010_a7be` | exact-normalized | 100.00% |
| `FUN_1010_aa90` | `NITE3W13.EXE.c` | `FUN_1010_a86e` | exact-normalized | 100.00% |
| `FUN_1010_abfc` | `NITE3W13.EXE.c` | `FUN_1010_a9da` | exact-normalized | 100.00% |
| `FUN_1010_b02c` | `NITE3W13.EXE.c` | `FUN_1010_ae0a` | exact-normalized | 100.00% |
| `FUN_1010_b128` | `NITE3W13.EXE.c` | `FUN_1010_af06` | exact-normalized | 100.00% |
| `FUN_1010_b5e4` | `NITE3W13.EXE.c` | `FUN_1010_b3c2` | exact-normalized | 100.00% |
| `FUN_1010_b6a0` | `NITE3W13.EXE.c` | `FUN_1010_b47e` | exact-normalized | 100.00% |
| `FUN_1010_b762` | `NITE3W13.EXE.c` | `FUN_1010_b540` | exact-normalized | 100.00% |
| `FUN_1010_b862` | `NITE3W13.EXE.c` | `FUN_1010_b640` | exact-normalized | 100.00% |
| `FUN_1010_cf60` | `NITE3W13.EXE.c` | `FUN_1010_cd3e` | exact-normalized | 100.00% |

Selected: **22**, scored: **22**, exact: **17**, fuzzy: **5**, weak: **0**.
Mean normalized similarity (excluding manual-review functions): **99.28%**.

## DOS

| Target | Ref build | Ref function | Match | Similarity |
|---|---|---|---|---:|
| `FUN_1000_5092` | `N3D-E-10.EXE.c` | `FUN_1000_4da2` | fuzzy-normalized | 96.83% |
| `FUN_1000_5342` | `N3D-E-17.EXE.c` | `FUN_1000_51de` | exact-normalized | 100.00% |
| `FUN_1000_59f0` | `N3D-E-18.EXE.c` | `FUN_1000_59f0` | weak/unresolved ⚠ manual raw review | 43.09% |
| `FUN_1000_5f26` | `N3D-E-17.EXE.c` | `FUN_1000_5dc2` | exact-normalized | 100.00% |
| `FUN_1000_6378` | `N3D-E-10.EXE.c` | `FUN_1000_609a` | fuzzy-normalized | 92.47% |
| `FUN_1000_6488` | `N3D-E-18.EXE.c` | `FUN_1000_6488` | exact-normalized | 100.00% |
| `FUN_1000_6636` | `N3D-E-18.EXE.c` | `FUN_1000_6636` | exact-normalized | 100.00% |
| `FUN_1000_676e` | `N3D-E-10.EXE.c` | `FUN_1000_6490` | fuzzy-normalized | 91.07% |
| `FUN_1000_6824` | `N3D-E-18.EXE.c` | `FUN_1000_6824` | exact-normalized | 100.00% |
| `FUN_1000_688c` | `N3D-E-18.EXE.c` | `FUN_1000_688c` | fuzzy-normalized | 81.25% |
| `FUN_1000_6914` | `N3D-E-10.EXE.c` | `FUN_1000_6636` | exact-normalized | 100.00% |
| `FUN_1000_7f96` | `N3D-E-18.EXE.c` | `FUN_1000_7f8c` | fuzzy-normalized | 96.73% |
| `FUN_1000_8142` | `N3D-E-10.EXE.c` | `FUN_1000_7cbe` | exact-normalized | 100.00% |
| `FUN_1000_8230` | `N3D-E-18.EXE.c` | `FUN_1000_8226` | fuzzy-normalized | 97.32% |
| `FUN_1000_8f12` | `N3D-E-17.EXE.c` | `FUN_1000_8da4` | exact-normalized | 100.00% |
| `FUN_1000_8f76` | `N3D-E-17.EXE.c` | `FUN_1000_8e08` | exact-normalized | 100.00% |

Selected: **16**, scored: **15**, exact: **9**, fuzzy: **6**, weak: **0**.
Mean normalized similarity (excluding manual-review functions): **97.04%**.
Below threshold: `FUN_1000_688c`.
Manual/raw override required: `FUN_1000_59f0`.