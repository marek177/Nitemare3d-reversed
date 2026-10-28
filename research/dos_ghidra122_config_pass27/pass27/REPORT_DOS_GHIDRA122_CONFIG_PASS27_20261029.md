# DOS configuration loader — pass 27

## Finding
Confirmed: all six distinct supplied DOS images load a 16-byte settings block without validating its viewport-width word. 132 bounded original-code executions passed. Supplied 1.8/1.9 share the same executable; this is not seven independent builds.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Default width is 304; settings storage is initialized before opening the file | Per-build initializer bodies in evidence/config.json; V1.9 1277:0c6e | High |
| Confirmed | Only a signed-positive returned file handle enters the read path | V1.9 1277:0cbe–0cc0; mock handles 0,ffff,8000 | High |
| Confirmed | Reported length must equal exactly 16 as a 32-bit value | V1.9 1277:0ccb–0cd2; lengths 0,15,17,65552 reach fatal call | High |
| Confirmed | Widths 0,1,7,8,160,304,320,328,32767,32768,65535 reach original viewport setter unchanged | V1.9 read 1277:0ce5 and setter call 0cfb; 11 widths × six builds | High |
| Confirmed | Read count is ignored; a partial read leaves remaining defaults intact | V1.9 1277:0cea–0cfb; counts 0,1,2,15 | High within modeled I/O |
| Unknown | Actual DOS/CRT read failures, full menu bounds, indirect writers and complete game reachability | Not executed here | Unresolved |

## Behavior model
Initialize 16-byte defaults. Open settings. If signed handle <=0, use defaults. Otherwise query length; if not exactly 16, call fatal handler. Read 16 bytes into settings, ignore return count, close, invoke viewport setter. No alignment mask or range clamp occurs in this loader. Handle 0 is therefore skipped by the local branch; this does not prove it normally occurs in the game's environment.

A one-byte mocked read of width ffff changes default 0130 to 01ff (511); a zero-byte read retains 304. A complete read of ffff preserves 65535. The original arithmetic setter executes with two downstream graphics dependencies mocked, as in pass 26.

Version difference: DOS 1.0 opens its settings name directly; later initializers have an additional path-builder call. Exact entries, bytes, call roles and input SHA-256 are in config.json. No project database was edited; source is the preserved Ghidra 12.2 instruction export plus reconstructed EXE bytes.

## Verification
Run `/usr/bin/python3 scripts/verify_viewport_config.py` from the package root, with Unicorn 2.x installed. 22 cases per build: three rejected handles, eleven widths, four partial-read counts, four invalid lengths. Successful paths check width, two setter dependency calls, far return, stack and DS. Fatal paths stop immediately before the original fatal handler. Path/open/length/read/close/fatal dependencies are mocked; these are not full filesystem or whole-game tests.

## Implementation-ready findings
Preserve a raw 16-byte settings block and little-endian width at offset zero. A faithful local loader must retain the missing read-count/range checks; a hardened reimplementation may add validation, but that is an intentional behavior change. The default-boundary safety conclusion from pass 26 is conditional and cannot be generalized to arbitrary configuration contents.

## Unknowns and next test
Trace viewport width adjustment commands and their dispatcher, then execute decrement/increment paths at both limits. Menu references examined here copy/restore the settings block; those copies alone do not establish width limits. Follow the command-line option dispatch and actual settings path/file contents separately.

## Confidence
High for the local initializer/control flow under stated mocks; no claim of complete DOS parity or complete unknown-code coverage.
