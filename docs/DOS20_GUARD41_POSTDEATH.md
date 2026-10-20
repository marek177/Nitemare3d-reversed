# DOS2 GUARD41 post-death evidence integration

Source: **README_SK(20261020-191624).md**, 2026-10-20, Library ID `libfile_f375e30a0bc88191b2488d9a957ac362`, from `N3D_GUARD41_POSTDEATH_DOS20_RUNTIME_V066_20261020.zip`. The report was read for this change. Raw N3DTRC01 traces and its verifier were not materialized or rerun here. The following are attributed reported original-runtime observations, not new captures made by this integration.

| Reported observation | Exact scope |
|---|---|
| GUARD41 +0B 00→09 | DOS2 0CEB:0E03, IMG:5A73, CPU #1 / W #5; ES:SI 2A21:2A78, linear state byte 2CC93 |
| Same writer's negative control | Same actor and CS:IP, but AL=05 and state 00→05 before death |
| GUARD41 +0B 09→0A | DOS2 1061:0322, CPU #17 / W #80 in both state9 runs |
| WORLD +05 0B→0B | CPU #15, linked WORLD 2A21:1C5A |
| RNG #19 | AEA69ED3→12DBCE4A, AX=4827; low/high writes CPU #81/#82 |
| WALL branch | ID BB, property 00, bit08 clear; 0CEB:1045→104A skips to 12B0 |
| DOS2 common epilogue | Entered at CPU #4237 / #4240 in independent runs A/B |
| DOS1.2 comparison | Same listed state/flag/RNG results and write ordinals; reference ends at 0CC6:104C before the epilogue executes |

The historical v058 header records what was known at v058, including its then-false DOS2 observation flag. It remains a historical snapshot. Current bounded status is in `N3DDos20Guard41PostDeath.hpp`; v069's earlier checkpoint evidence is superseded only for the observations above.

The new gate requires writer CS:IP, actor ES:SI, AL, old/new state and target linear byte to agree. Tests reject the actual reported pre-death 00→05 control and each of eight altered identity fields. This checks a semantic capture-selection contract; it does not authenticate arbitrary caller-supplied values, parse trace bytes, verify CPU/W correlation or replace the source archive's independent verifier.

The header preserves separate trace SHA-256 identifiers and boundaries. DOS2 phase 00→09 has 15000 I / 42387 R / 3318 W. State9 A has 12000 I / 39615 R / 14453 W; B has 4600 I / 18692 R / 12771 W. DOS1.2 reference has 4235 I / 17665 R / 12675 W. All DOS2 captures end by instruction budget. An epilogue flag here means entry was reported within that capture, not that the trace stopped there.

These are independent natural DEMO runs. They do not prove a continuous fatal-HP-to-state0A tick interval or IRQ ordering. The property-zero branch skips one conditional map action, not all item drops in the game. Cleanup elsewhere, special classes, full DOS/Win16 parity and original-versus-port frame/DAC equality remain open.

Reported input provenance: packed DOS2 EXE `a3fa02335e1d8bc531918f3bfaa66217aef65c81e562a2fdf1c749be652ca485`; unpacked `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`; DEMO.1 `25ae7e97f61d19bc3fa61d630ec13b9614a4f3193da84f7c1a3c3d519f795840`. No commercial input or private trace is distributed with this change.

Confidence: medium for this report-to-code transfer. The report describes bounded original captures and a mutation-tested verifier, but direct raw-trace reproduction remains a separate requirement.
