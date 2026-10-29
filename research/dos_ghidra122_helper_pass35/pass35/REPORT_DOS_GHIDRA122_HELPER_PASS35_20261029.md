# First column projection helper — pass35

## Finding
5,184 executions verify the complete first helper previously mocked in passes33–34. It returns a signed32-bit result in DX:AX and selects four arithmetic paths by an orientation flag and kind2/3. 2,592 cases return and2,592 intentionally invalid cases raise CPU divide error. The second helper remains unresolved.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Full helper has no callee dependencies and uses signed32-bit IDIV | V1.9 1c79:0710–07e4; bodies and hashes in projection_helper.json | High |
| Confirmed | Nonzero orientation flags use coefficientB, zero uses coefficientA | Original path selection and tests flag0/1/ffff | High |
| Confirmed | kind2 and3 select alternate path | V1.9 compares071d/0722/0767/076c | High |
| Confirmed | Zero scale or zero selected coefficient raises interrupt0 | Deliberate tests, stopped before DOS handler | High locally |
| Inferred | A/B are trigonometric projection coefficients and return is projected texture position | Caller context and global reuse | Medium; producer/units not fully traced here |

## Behavior model
Analytical far-call arguments: kind16, x16, scale16, bias32 (five argument words). Let F=(orientationFlag!=0), K=(kind==2 or kind==3), useX=(F!=K), C and D be the pass29 arithmetic outputs. All division is signed with truncation toward zero; scale is zero-extended16-bit. s16/s32 explicitly wrap to their signed widths.

```
if useX:
    term = trunc(s32(s16(x-centerX) * D) / uint16(scale))
    numerator = s32(term + bias) if F else s32(bias - term)
else:
    term = trunc(C / uint16(scale))
    numerator = s32(term - bias)
result = trunc(numerator / (B if F else A))
```

V1.9 globals: orientation DS415c; A DS41b0; B DS41b2; centerX DS454e; C DS3684; D DS3688. Exact per-version addresses recorded. Multiplication uses low32 bits before subsequent sign extension/division; do not replace with an unbounded product. The returned DX:AX is observed, not a floating-point approximation.

## Verification
`/usr/bin/python3 scripts/verify_projection_helper.py` with Unicorn2.x: six images × flag0/1/ffff × kind0/2/3/4 × scale0/1/152/65535 × x0/160/319 × coefficient pairs(100,200),(-100,-200),(0,0) × bias0/1234567 =5,184. Fixed C81715200,D459074,center160. Original helper executes without mocks; independent integer formula checks outputs. Successful paths check far return, stack and DS. Fault paths check interrupt0, not DOS response. A fresh CPU instance per case prevents exception state carrying between cases.

This is helper arithmetic recovery, not complete renderer/gameplay parity. Synthetic globals do not establish that zero divisors occur in ordinary gameplay. Preserved Ghidra12.2 exports provide locations; no project database edits. Supplied1.8/1.9 are identical.

## Implementation-ready findings
Preserve signed width conversions, zero-extended scale, low32 product and signed division. Keep kind2/3 handling distinct from orientation. Name semantic units only after producer/consumer chains are resolved.

## Unknowns and next test
Recover second helper (V1.9 1201:02ba), then remove both mocks from the caller-chain test. Trace actual coefficient producers and valid scale bounds. Confirm per-x projected-height behavior and framebuffer/DAC separately.

## Confidence
High for arithmetic and exceptions over tested inputs; medium for projection/texture semantic names.
