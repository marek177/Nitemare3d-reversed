# Win110 pass75 — application-title selection and allocation failure

## Finding
Confirmed / High: the application-title suffix of5E94 preserves an existing+22 pointer. Otherwise it loadsE000, duplicates the loaded buffer on nonzero return or the+26 fallback on zero, then publishes the duplicate result through both+22 and0822 without checking for allocation failure.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | E000 embeds Nitemare-3D for Windows | RT_STRING block8E01,file35180; text35181 | High |
| Confirmed | Existing+22 bypasses load and duplicate calls |5F46–5F4A→5F70 | High |
| Confirmed | LoadE000 uses original3282 |5F4C–5F54 | High |
| Confirmed | Nonzero load selects BP-100; zero selects application+26 |5F59–5F64 | High |
| Confirmed | Duplicate result stored at+22, then copied to0822 including zero |5F67–5F73 | High |

## Behavior model
`if(app.title == 0) { n=load(E000,buffer); app.title=duplicate(n ? buffer : app.fallback26); } global0822=app.title;`

The title role is supported by embedded text and filename/title preparation earlier in5E94. This pass does not demonstrate that0822 is used as the caption of every dialog. The fallback+26 originates from earlier filename/title processing, which is not executed here. A preexisting pointerFFFF is preserved by this code; this synthetic word is never dereferenced in the bypass test and is not evidence of a valid runtime string.

## Verification
36 original-code cases pass: existing pointers0,7300,FFFF × fallback words0,7200,FFFF × loader returns0,21 × duplicate results0,7400. The nonzero21 loader return is a synthetic truthy fixture, not a claim about the actual embedded title length. Tests check chosen duplicate argument, call bypass/order, both resulting title words, final SPD008 and restored BP/SI/DI.

Execution starts at5F46 with an explicitly constructed5E94 frame and ends at its original far return. The original3282 wrapper runs; its LOADSTRING call is intercepted and validated, and699C duplication is intercepted before CALLF. The duplication stub leaves its cdecl argument on the stack for original POP BX at5F6C. No allocation, string copying, filename handling, or Windows API executes. Null fallback is passed to the duplication stub without dereferencing; actual699C behavior for null remains Unknown.

DS=SS1048, CS2000, application7000. Internal call selector5F57 normalizes to2000. Resource module5555 is synthetic. The test independently checks raw embedded title bytes; its initially incorrect fixed slice length was corrected to the exact string length before the successful run. Original EXE SHA256:12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Uses preserved Ghidra12.2 export and raw EXE, with no fresh database update.

Run `python3 pass75/verify_title_policy.py` with Unicorn2.1.4.

## Implementation-ready findings
Preserve existing title ownership rather than unconditionally replacing the pointer. Distinguish missing resource fallback from duplicate allocation failure. Publish the actual duplicate return, including0. Additional error recovery is not present in this suffix and must not be invented as original behavior.

## Unknowns and next test
Execute699C→609E/5AB0/606C to resolve null source, allocation size and copy contract. Trace reads of0822 to determine actual caption use. Confidence High for isolated title selection/publication; real allocator and rendered caption remain Unknown.
