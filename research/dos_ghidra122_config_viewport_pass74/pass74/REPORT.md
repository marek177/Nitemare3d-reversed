# Pass 74 — CONFIG.SAV width ingestion and viewport setup

## Finding
Confirmed for six distinct supplied DOS binaries: the configuration loader sets defaults, accepts only a signed-positive open handle and exactly16-byte file length, copies configuration bytes without validating width, then calls the original viewport setup chain. A synthetic16-byte configuration with width0/1 reaches divide error in projection preparation. This establishes a local ingestion path, not an observed shipped-file failure. Supplied1.8/1.9 are identical.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Default width is304 (0130h) | Original initialization and pre-open memory | High |
| Confirmed | Only signed handle>0 enters length/read/close path | Open fixtures ffff,0,8000 and1 | High |
| Confirmed | File length must equal32-bit16 | Length15,17,65552 fatal;16 accepted | High |
| Confirmed | Read return value is ignored | Zero-/one-byte return fixtures and instruction flow | High |
| Confirmed | Loaded width0/1 reaches divide error after file close | Original loader→setup→projection execution | High under synthetic file boundary |
| Unknown | Invalid widths reachable from normal UI editing | Some direct addresses lack containing Ghidra functions | Input validation elsewhere remains open |

## Behavior model
Initialize a16-byte configuration block, including width304, then open CONFIG.SAV with8000h. If the signed handle is<=0, skip length/read/close and apply defaults through viewport setup. A zero handle is not closed in this path. If handle>0, require DX:AX length exactly0000:0010; otherwise call fatal. Read16 bytes directly into the configuration block; ignore return count; close; apply the resulting width to the original geometry/projection/clipping chain. There is no local width clamp, alignment operation, checksum or signature check in the observed load function.

A short read may leave a mixture of initialized defaults and copied bytes. In the zero-byte fixture the defaults remain; a one-byte fixture replacing the width low byte40h changes width304 to320 while retaining the default high byte01h. These tests mock precisely the stated bytes and return counts, not a real filesystem transfer. A fully supplied width319 or321 remains odd and is passed unchanged. Synthetic width0/1 is also passed unchanged and faults in the downstream projection division after the handle has been closed.

Some later builds call a filename helper before open; the test mocks that helper and preserves the original name. Earlier builds open the literal directly. Full path-search semantics are not recovered here. All non-file processing, including setup and its projection/clipping callees, executes unchanged.

## Verification
84 cases pass:14 per distinct binary. Three skipped-open handles; three invalid32-bit file lengths; accepted widths0,1,64,319,320,321; zero-byte and one-byte reads. Assertions cover filename/open flags, defaults, I/O order, exact read target/count, width entering setup, resulting height, fatal and CPU divide-error branches. BIOS/VGA is not involved in this local chain. Mocked boundaries: optional filename helper, CRT open/length/read/close and fatal. Original loader and viewport chain execute.

## Locations
DOS1.9 loader1277:0c6e; configuration DS4144..4153; downstream setup1277:0bc2. DOS1.0 loader1273:0bc0; block DS3f9c..3fab. All per-build entries, defaults and events are recorded in config_load_tests.json. Input hashes are retained in baseline specs bundled with the dependency archive.

## Analysis gaps
Direct xrefs miss address-taking/indirect writes. Seeds additionally identify immediate references to the configuration address. The fresh exporter records MISSING_FUNCTION rather than silently omitting addresses without containing functions; these include menu/editor code that may align or constrain width. Such code must be recovered before asserting all UI-reachable values. A numeric pointer reference alone is not evidence of a write. Full function exports and these explicit gaps are included.

## Unknowns and next test
Recover the missing configuration-editor functions, including the observed AND low-byte,f8h path, to establish legal UI size range. Trace configuration saving and raw block layout. Test real CONFIG.SAV and full startup in DOSBox-X before describing actual failures or complete parity. Confidence High for tested ingestion behavior; incomplete for normal UI reachability and real file/runtime integration.
