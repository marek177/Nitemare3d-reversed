# Win110 pass76 — original near string duplication

## Finding
Confirmed / High:699C obtains the length through609E, requests length+1 bytes through5AB0, and copies through606C only if allocation returns nonzero. The copied data includes its NUL terminator. Source zero is not guarded before dereference.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed |609E scans DS string using ES=DS, REPNE SCASB,CX=FFFF |609E–60B8 | High |
| Confirmed |699C increments returned length before allocator call |69AB–69B2 | High |
| Confirmed |Allocation result0 bypasses606C and returns0 |69B7–69BD | High |
| Confirmed |606C scans source including NUL then copies to destination with alignment handling |606C–609D | High |
| Confirmed |Caller retains source argument; RETF has no immediate cleanup |69C8–69D1 | High |

## Behavior model
`n = near_strlen(source); result = allocate(word(n+1)); if(result != 0) near_strcpy(result,source); return result;`

This expression summarizes the bounded terminated inputs tested here. Length arithmetic is16-bit; unbounded/nonterminated scans, wraparound and segment-limit behavior are not covered. The routines have no CLD in the captured body; tests explicitly set DF=0. Do not extend the result to DF=1.

The old699C decompiler prints a void return, but native AX propagation and repeatable return checks establish a returned near pointer in this path.606C returns the destination in AX, and699C leaves that value through its epilogue. On allocation failure AX remains0. Near zero source does not mean empty by definition: the original scan reads bytes beginning at DS:0000. Synthetic tests with differing mapped bytes at DS:0000 demonstrate that behavior, without asserting that a real null pointer is valid.

## Verification
6,159 original-code cases passed.6,150 cases cover lengths0..1024 inclusive, two source alignments5000/5001, and three allocator results0/7000/7001. Nonzero payload bytes include high-bit values from deterministic seed76. Nine additional source0 cases supply empty, ASCII ABC, and FF8001 payloads under all three allocation outcomes.

Checks: requested size equals payload length+1, exact destination bytes include NUL, immediately following canary remainsA5, allocation failure never enters copy and preserves the entire destination fixture; AX/SP/BP/DS/SI/DI match expected return behavior. EntrySPD000 returnsD004 with source argument still present. SS4000 differs from DS1048. Initial BPBEEE tests the Win16 tagged-frame prologue/epilogue.

Only the5AB0 allocation call is intercepted, returning a synthetic pointer and leaving its cdecl argument for original POP BX. Original699C,609E,606C all execute. Internal far-call selectors at69AE and69C3 are normalized to test CS3000; no helper implementation is replaced. Non-CALLF native bytes of all three functions are checked against raw EXE. Actual heap allocation and Windows imports do not execute.

Reproduce `python3 pass76/verify_strdup.py` with Unicorn2.1.4. Original executable SHA256:12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Evidence uses preserved Ghidra12.2 export and raw executable; no fresh database mutation occurred.

## Implementation-ready findings
Allocate space for terminator, return destination pointer, skip copying on allocation failure, preserve the caller-cleaned argument ABI. Combine this with pass75: a zero allocation result reaches application+22/0822 unchanged. Null fallback is unsafe to interpret as an empty string without knowing DS:0000 contents and execution mode.

## Unknowns and next test
Trace5AB0 to the actual allocator and its size/failure policy. Test real Win16 title construction only after heap/API setup is available. Overlapping source/destination, nontermination, very long strings and DF=1 remain unverified. Confidence High for the bounded original-code behavior under the declared allocation model.
