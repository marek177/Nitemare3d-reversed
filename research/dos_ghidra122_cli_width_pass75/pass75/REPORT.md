# Pass 75 — command-line viewport-width option

## Finding
Confirmed across all six distinct supplied DOS binaries: `-w` dispatches to numeric width ingestion, aligns the stored word down to a multiple of8, then immediately invokes viewport setup. This path has no local width-range check. Synthetic conversion results0..7 become0 and fault downstream. Supplied1.8/1.9 are identical. This branch is a command-line parser, correcting the earlier tentative menu/editor description.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Width option is `-w` in every supplied distinct DOS EXE | Original switch tables and full-parser execution | High |
| Confirmed | Width branch passes `%d` and width destination to numeric conversion | Original call arguments | High |
| Confirmed | Width becomes width_word AND fff8h | AND byte-low,f8h, runtime result | High |
| Confirmed | Setup is called immediately after alignment | Original parser dispatch→setup chain | High |
| Confirmed | Values0,1,7 become0 and divide-error downstream | Original setup/projection code executes | High under injected conversion result |
| Unknown | Exact native sscanf conversion behavior for malformed/overflowing strings | Numeric conversion call mocked | Not claimed |
| Unknown | Normal menu size limits | This is CLI code, not menu validation | Separate audit remains |

## Behavior model
The parser processes near argv pointers, checks the leading hyphen, uses the next character in a computed switch, and the width branch increments the argument index before calling numeric conversion. After that call it clears low3 bits of the stored width regardless of conversion return count. Thus failure with an unchanged default304 retains304; result15 becomes8;319 becomes312;321 becomes320;ffffh becomesfff8h. No local upper clamp at320 is applied.

Immediately after alignment, original viewport setup, projection preparation and clip-table rebuild execute. A zero result reaches CPU divide error before the parser's normal tail. The tests inject conversion result0/1/7 and reproduce that path. This proves behavior of these converted values through CLI dispatch, not all native text-to-integer corner cases. Other parser callees, including configuration initialization and final setup helpers, are mocked and cannot establish complete command-line startup behavior.

## Locations
| DOS | Parser entry | Width branch | Alignment |
|---|---|---|---|
|1.0|144e:0320|144e:0458|144e:046d|
|1.1|1452:0334|1452:04a8|1452:04bd|
|1.2|1453:0330|1453:04a4|1453:04b9|
|1.5|1458:0328|1458:049c|1458:04b1|
|1.7|145f:0332|145f:04c8|145f:04dd|
|1.8/1.9|1476:0326|1476:04bc|1476:04d1|

The switch table must be interpreted with each build's preceding subtraction, rather than assuming a common first letter. All corrected option labels were then verified by executing actual `-w` argv dispatch.

## Ghidra recovery status
The parser entry functions already exist, but their defined bodies did not contain the width branch queried in pass74. This pass expands their body ranges temporarily in a read-only Ghidra12.2 run. All changes are discarded; the native baseline project is not updated. Only DOS1.1 decompiled successfully. Five attempts failed with p-code constructor/address errors; the diagnostics are preserved. No claim of six successful complete C recoveries is made. Fresh exports contain only instructions known to the current listing; parser_instructions.json supplies the full selected instruction listings from the baseline audit. Original MZ execution independently validates the selected width path.

## Verification
72 cases pass: six binaries × injected values0,1,7,8,15,64,319,320,321,32767,ffffh and conversion-failure/no-write. Tests enter the original parser with argc3 and actual near argv strings `n3d`, `-w`, value. Original dispatch, index increment, alignment and viewport/projection/clipping chain execute. Assertions cover conversion format/destination, width entering setup, final width and divide-error/normal-return state. Every other parser call site is mocked; no OS, native sscanf or real CLI startup is tested.

## Unknowns and next test
Repair parser disassembly/decompiler address issues and persist a reviewed native project update. Follow actual conversion routine and remaining parser helpers. Recover separate in-game menu/editor size limits. Complete input parsing, renderer reachability and framebuffer/DAC parity remain open. Confidence High for local width-option behavior, incomplete for full parser recovery and game integration.
