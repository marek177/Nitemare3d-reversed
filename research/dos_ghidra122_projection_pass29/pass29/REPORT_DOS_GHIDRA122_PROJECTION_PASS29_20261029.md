# Viewport arithmetic dependency — pass 29

## Finding
The formerly mocked first viewport-setter dependency is now executed in full. 408 tests across six distinct supplied DOS EXEs confirm four signed arithmetic outputs and 18 divide-error exceptions. Menu adjustment limits remain unknown; this pass resolves downstream arithmetic instead.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | First dependency performs signed width multiplication/division then height scaling | V1.9 1c79:0008–006b; complete bodies and hashes in projection.json | High |
| Confirmed | Width 0,1,ffff produces zero divisor in final division | V1.9 1c79:0062, original code and interrupt 0 hooks; three cases in each image | High |
| Confirmed | Width 304 produces 178,5107200,81715200,459074 | Four original dword writes at DS:367c,3680,3684,3688 | High |
| Inferred | Values are renderer projection/scaling parameters | Viewport setter call and arithmetic dependencies | Medium; consumers not fully traced here |
| Unknown | DOS exception handler result and complete game response | Execution stopped at exception hook | Unresolved |

## Behavior model
Let W=signed16(width), H=W arithmetic-shift-right 1. All divisions truncate toward zero.

```
A = trunc((12000 * W) / 20480)
B = signed32(H * 33600)
C = signed32(B << 4)
D = trunc(C / A)  // CPU divide error when A == 0
```

The routine writes A, B, C before attempting D. Widths -1,0,1 give A=0. Previous D remains unwritten on those fault paths; the test's observed initial D is not a defined routine output. 32-bit wrap at C is material: W=32767 produces C=217566208 and D=11332; W=-32768 produces C=-218103808 and D=11359.

At default W304: H152, A178, B5107200, C81715200, D459074. No clamp is performed in this routine.

## Verification
`/usr/bin/python3 scripts/verify_viewport_projection.py` with Unicorn 2.x: 68 widths × six images, including 0..17, aligned widths through 328 and signed extremes. Original viewport setter and entire first dependency execute. Only second dependency is mocked. Successful paths check four dwords, one remaining dependency call, DS, SP and far return. Fault paths check interrupt 0 and absence of the second call. Tests do not execute DOS exception handlers or full rendering. Ghidra 12.2 preserved exports provide exact instruction locations; no project database edited.

## Implementation-ready findings
Use signed 16-bit interpretation for W/H, explicit signed 32-bit wrap for C and truncating signed division. Do not substitute floating point rounding or assume that pass 26's setter arithmetic proves the complete setter returns for all inputs. Its dependency mocks hid these divide errors. Configuration width zero (pass 27) and CLI conversion to zero (pass 28) can feed this local divide-error path; complete startup behavior remains unverified.

## Unknowns and next test
Trace the four parameter consumers before assigning final semantic field names. Analyze second setter dependency (V1.9 1156:0030), still mocked, for additional conditions. Follow menu's indirect width updates independently; settings-copy references alone establish no limits.

## Confidence
High for local arithmetic, writes and CPU divide errors. Medium for projection interpretation; no whole-game parity claim.
