# Win110 pass86 — bounded idle message-loop execution

## Finding
Confirmed / High:3A34 resets idle count for each outer processing cycle, checks PEEKMESSAGE before calling virtual+48, and passes the previous count while incrementing its local count before the virtual call. Both a pending message and virtual return0 lead to39EE. Nonzero39EE restarts the outer cycle; zero invokes virtual+50 and returns.

## Correction to pass85
Pass85 described the increment as occurring after the virtual call. That was imprecise: instructions3A70/3A73 push the old high/low count,3A76/3A7A increment the local words, then3A80 calls the method. Its argument sequence is0,1,2..., but the caller's local count is alreadyone greater during the call. This pass records and verifies that distinction explicitly. Preserve it for stack observations/reentrancy analysis.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Reset both local count words each outer cycle |3A52–3A57 | High |
| Confirmed | PEEKMESSAGE receives six stack words0,0,0,0,app+2C,DS |3A5A–3A67 and traced arguments | High |
| Confirmed | Pending message bypasses virtual+48 |3A6C–3A6E | High |
| Confirmed | Old count passed, local increment precedes call |3A70–3A80 and callback-time local checks | High |
| Confirmed | Any nonzero virtual AX continues idle checking |3A84–3A86; stubFFFF | High |
| Confirmed |39EE nonzero resets count, zero calls+50 and returns |3A88–3A9B | High |

## Behavior model
`for(;;) { count=0; while(!peek()) { old=count; count++; if(!virtual48(app,old)) break; } if(!pump39EE(app)) { virtual50(app); return; } }`

The shown loop is reached after earlier startup checks. Test application+1E is nonzero, so7C10/POSTQUITMESSAGE are bypassed; those paths remain unexecuted. The actual queue is not consumed by the modeled peek. Full message semantics of39EE are not established in this pass.

## Verification
36 two-cycle plans pass: Cartesian product of six cycle shapes (message immediately, message after1/3 idle calls, virtual return0 after1/2/4 calls). Each checks both cycles' exact counts starting0, caller-local count at each virtual boundary, API argument words,39EE-driven reset, exit method, finalSPD006 and restoredBP/SI.

Original3A34 executes without instruction patches. Four calls are intercepted before dispatch: PEEKMESSAGE consumes12 bytes; virtual+48 consumes6;39EE and virtual+50 each consume2. Stub return values drive the bounded plans. The virtual method body3D72 is not executed in this test, nor is actual Windows queue or dispatch. Synthetic object7000/table5000:6000 supplies LES operands; callback targets themselves are not fetched because calls are intercepted. DS1048 differs from SS4000, CS2000.

Run `python3 pass86/verify_idle_loop.py` with Unicorn2.1.4. Original EXE SHA256:12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Includes preserved Ghidra12.2 native export; no fresh database update or real Win16 execution.

## Implementation-ready findings
Reset count after each successful pump cycle, peek before idle work, and preserve old-value argument with pre-call local increment. Treat nonzero idle result as continue and zero pump result as exit. Do not count queued-message cycles as idle calls.

## Unknowns and next test
Trace39EE's actual message acquisition, translation and dispatch. Initial7C10/POSTQUITMESSAGE and long-count carry/overflow remain outside these short loop plans. Confidence High for bounded loop ordering under declared call results; live Windows event timing Unknown.
