# Viewport command-line branch — pass 28

## Finding
108 original-code tests confirm decimal width conversion, 16-bit wrapping and alignment without range checking in six distinct DOS EXEs. This closes the CLI branch left open in pass 26. Menu limits remain unresolved.

## Evidence
| Status | Claim | Source/location | Confidence |
|---|---|---|---|
| Confirmed | Width option dispatch table selects `v` in DOS 1.0/1.1/1.2/1.5 and `w` in DOS 1.7/1.8 supplied image | CS jump tables and targets recorded in cli.json; supplied 1.8/1.9 EXE identical | High, static mapping |
| Confirmed | Conversion format is `%d`; source is the next argv pointer | Original fragment and format bytes; V1.9 1476:04bc–04c9 | High |
| Confirmed | Conversion return is ignored; only low three bits of width are cleared | V1.9 1476:04ce–04da; original sscanf executions | High |
| Confirmed | Original setter runs after successful, failed and EOF conversion | 108 bounded paths, two setter dependencies observed per path | High within scope |
| Unknown | Full argument-dispatch behavior with missing arguments and menu width limits | Full dispatcher/menu not executed | Unresolved |

## Behavior model
Take next argv element, run original sscanf with `%d` into existing width, ignore return, clear low three bits of the width word, call original viewport setter. Conversion failures retain the previous word before alignment. Starting from 311, empty input returns ffff (EOF), `x` returns 0, and both leave width 304 after masking. `0x130` parses decimal zero; `0304` parses decimal 304. `  +319junk` parses 319 then aligns to 312.

| Input | Stored/aligned width |
|---|---:|
| 311 | 304 |
| 328 | 328 |
| -1 | 65528 |
| 32768 | 32768 |
| 65535 | 65528 |
| 65536 | 0 |
| 65537 | 0 |

## Verification
Run `/usr/bin/python3 scripts/verify_viewport_cli.py` with Unicorn 2.x. 18 strings × six images. Original CLI fragment, sscanf and viewport arithmetic execute; only the two downstream viewport setter calls are mocked. Stop after caller stack cleanup. Check conversion return, stored width, dependency count, unchanged DS/SP and argv-index increment. This is not a full DOSBox gameplay run or whole-game parity proof. Ghidra 12.2 preserved instruction exports supply locations; no Ghidra project database edited in this pass.

Exact per-build entries, jump-table words, EXE hashes and test results are in evidence/cli.json. Original inputs and export dependencies are included in the archive.

## Implementation-ready findings
Distinguish raw configuration loading (pass 27, no alignment) from CLI loading (this pass, alignment). Preserve decimal parsing, 16-bit overflow and failed-conversion behavior for local compatibility. A clamp would be a deliberate behavior change.

## Unknowns and next test
Menu settings-copy paths do not prove limits. Follow indirect width writes via settings pointers or the renderer's derived width, identify increment/decrement dispatch, and test both bounds. Separately run the full argv dispatcher with a missing width argument to establish its error path.

## Confidence
High for tested local conversion paths and static option mapping; no conclusion about complete menu validation or full executable coverage.
