# Pass 77 — direct command-line flag effects and version map

## Finding
Confirmed in six distinct supplied DOS binaries: options b,o,p,r,s,t,x directly change parser-local/global state; their repeated use is idempotent for the observed state. Presence of `windir` causes the same two direct global writes as option t. The recovered switch maps add option q in1.1 and option a in1.7. Supplied1.8/1.9 are identical. These are parser-local effects, not complete subsystem meanings.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Flags o,p,r,s,t,x perform exact direct byte/word stores | Recovered original ASM and original execution | High |
| Confirmed | b sets a stack-local byte forwarded in final call | Original parser and low-byte call argument assertion | High |
| Confirmed | getenv name is windir; nonnull result matches t's two writes | Exact name bytes and controlled return fixtures | High |
| Confirmed | Repeating each of seven options preserves same tested final state | Single/repeated argv fixtures | High |
| Confirmed | q is default/error in1.0 and accepted from1.1; a accepted from1.7 | Raw original switch maps and pass76 dispatch evidence | High for dispatch/classification |
| Unknown | Complete semantic names of all target fields | Downstream consumers not all traced here | Raw addresses retained |

## DOS1.9 local effects
| Option | Store/effect |
|---|---|
| -b | local byte1, forwarded as low byte of final mode argument |
| -o | DS3cd0 byte=1 |
| -p | DS3cc7 byte=0 |
| -r | DS3cd6 word=1 |
| -s | DS3cc6 byte=0 |
| -t | DS3ccf byte=0; DS3cc2 word=18 |
| -x | DS3cce byte=0 |

`windir` is tested for presence, not parsed as a numeric boolean in this function. A nonnull return makes the same stores as -t before option processing. The byte/word widths matter; no adjacent byte is intentionally changed by these instructions. Per-build exact offsets are in flag_tests.json. Globals began with66h sentinels so zero/one writes remain observable rather than merely confirming already initialized values. Repeated options repeat processing; idempotent final state does not imply no repeated calls or no side effects in real callees.

## Remaining option map
The140 original table entries are listed in option_map.csv. Static recovered C/ASM classifies a as a string-conversion/config-reload path; c,d,f as numeric conversions to globals; e/l as low/high word conversion of a local pair; q as a two-value path checking both conversion counts; w as width conversion/alignment/setup. Unsupported letters map to usage/error. This pass does not execute native numeric/string conversion or prove full behavior of these paths; w was separately tested in pass75. No human-friendly subsystem name is assigned merely from a letter.

## Verification
168 cases pass: six distinct binaries × seven direct/local options × windir absent/present × one/two repetitions. The original parser executes from entry to return; every parser callee is mocked. The first helpers therefore do not reproduce configuration/startup effects. getenv return is controlled after checking exact windir string. Final watched globals and the low byte forwarded by b are compared with the static instruction model; the local pair remains1,1 in these direct-flag fixtures. Native helper implementations, OS environment, audio/XMS effects and full startup are not tested.

## Provenance
This pass uses the six successfully recovered Ghidra12.2 parser C exports and original MZ instruction evidence from pass76. No new native database mutation was necessary. The repaired project and reference evidence are preserved by the bundled pass76 dependency archive. Input hashes are in its baseline specifications; parser entries and raw option destinations are retained in the new evidence.

## Unknowns and next test
Execute remaining conversion/error-count branches and follow direct-field consumers to name effects accurately. Inspect missing argument handling and order-sensitive combinations, then native conversion routines. Full parser semantics, in-game menu limits and complete renderer parity remain open. Confidence High for direct stores, local forwarding and version switch differences; incomplete for downstream meaning and helper behavior.
