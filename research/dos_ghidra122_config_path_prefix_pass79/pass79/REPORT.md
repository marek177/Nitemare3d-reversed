# Pass 79 — native -a prefix and configuration path construction

## Finding
Confirmed for DOS1.7 and supplied1.8/1.9: option-a scans one whitespace-delimited prefix using original%s, then reloads configuration. The original path helper concatenates prefix and filename with no separator insertion. DOS1.7 returns its local stack buffer, while supplied1.8/1.9 returns a global buffer. Exact original file-open internals and practical lifetime consequences remain unverified. Supplied1.8/1.9 are identical; two distinct binaries tested.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | -a runs native%s and reloads configuration | Original parser→CRT→config-loader→path-helper chain | High |
| Confirmed | No separator is inserted | Direct helper cases and intercepted open names | High |
| Confirmed | Empty%s input leaves existing prefix, but reload still runs | Native conversion and repeated open trace | High |
| Confirmed | 1.7 returns BP−52h after LEAVE/RETF | Original helper bytes and returned pointer | High |
| Confirmed | 1.8/1.9 returns DS3464 global buffer | Original helper bytes and returned pointer | High |
| Unknown | Native open preserves/overwrites the1.7 returned stack bytes before consuming them | Open call is boundary mock | No game-visible failure inferred |

## Behavior model
The helper copies the prefix including NUL into its result buffer, finds the end, appends the requested filename including NUL, and returns a near pointer. It does not normalize paths, insert a slash/backslash or treat whitespace specially. Therefore a direct prefix `data path/` is retained, while native-a input `a b/` stores only`a` through%s. Prefix`C:\N3D` plus config.sav becomes`C:\N3Dconfig.sav`; a trailing separator must already be in the prefix if desired.

Both versions use helper1277:0c20. DOS1.7 prefix is DS3c4c; its helper allocates82 stack bytes and returns BP−82 after releasing that frame. DOS1.8/1.9 prefix is DS3cdc and result buffer is DS3464. Same-stack direct calls reuse the same1.7 pointer; global calls likewise overwrite the same1.9 buffer. Neither pointer promises a permanent independent string copy. The returned1.7 pointer is no longer protected by the helper's live frame; whether a particular native caller overwrites it requires separate runtime evidence. Ghidra's local-pointer C model alone would not prove an observed failure.

The parser initializes configuration once before options. Every processed-a triggers another configuration load, even if%s assigns nothing. Repeated-a with foo/ then bar/ produces open names config.sav,foo/config.sav,bar/config.sav; prefixes replace each other rather than accumulating. The test uses a missing-file result, so original configuration defaults and viewport setup execute on each reload. Exact CRT file-open side effects are not modeled.

## Verification
44 cases pass:15 direct helper fixtures and7 original CLI fixtures per distinct binary. Direct fixtures combine five prefixes with three filenames, then call again to verify shared/reused storage. CLI fixtures use native%s for normal, missing-separator, whitespace, empty and repeated prefixes. Original parser, scan wrapper/core/helpers, configuration defaults, path helper and viewport/projection/clipping code execute unchanged. Only open returns missing-file, plus unrelated startup/final parser helpers are mocked. No DOS interrupts are permitted. DS=SS and DF0 are fixture preconditions; native conversion uses explicit valid CRT stack limit8000h with SPe000h.

No overly long prefix or capacity guarantee is tested. Copy loops and unbounded%s in this path do not establish safe lengths; actual valid asset paths remain to be audited. The open-name assertion observes the pointer before native open implementation runs, intentionally retaining the1.7 lifetime limit.

## Ghidra evidence and next test
Fresh Ghidra12.2 helper exports for both binaries are included along with raw helper instructions, prefix/result locations and native test traces. Recover and execute native open until its OS request to resolve the1.7 stack-buffer lifetime in the real caller. Trace all prefix-helper consumers, actual defaults and path capacity, then missing argv handling. Confidence High for tested string composition/native-a flow and storage locations, incomplete for full file/runtime behavior and overall parity.
