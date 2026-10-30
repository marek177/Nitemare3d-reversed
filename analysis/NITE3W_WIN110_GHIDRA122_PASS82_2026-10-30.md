# Win110 pass82 — integrated allocator/reserve retry

## Finding
Confirmed / High under declared API model: original5AB0 calls original12D2 and its real wrappers5B94/5BA8/5B0C. Failed modeled resize leaves the reserve available for repeated handler invocations. Once free path clears the reserve, a later allocation failure reaches12D2's exception-call boundary.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Allocation failure invokes handler12D2 through094A far pointer |5AF6 and integrated traces | High |
| Confirmed | Handler returns1 after failed resize, allowing another allocation attempt |1329→5AFD–5AFF | High |
| Confirmed | Repeated failed resize can target the same reserve | Repeated5B94/5BA8 traces with modeled unchanged capacity | High within model |
| Confirmed | Reserve free clears+7A; next failed allocation reaches132E | Integrated free/depletion cases | High |

## Behavior model
Allocation failure→handler→query reserve size→resize or free→return1→retry allocation. If the reserve was freed and retry fails, the next handler sees reserve0 and reachesCALL4564. If resize failed and the API model leaves capacity unchanged, subsequent failures can repeat the same resize attempt. There is no original retry bound in this captured cycle; infinite real Windows execution is neither run nor claimed.

## Verification
36 scenarios pass: six requests1,507,508,512,FFFC,FFFF × two resize models(success/failure) × one/two/three initial allocation failures followed by modeled success7600. Some cases stop before the scheduled success because reserve depletion reaches the exception boundary. Checks include completed successful-returnAX/SP/BP, exact reserve clearing or retention, and repeated resize counts for unchanged-capacity failed-resize cases.

Original5AB0,12D2,5B94,5BA8 and5B0C execute. API boundaries are intercepted: lock/unlock, LOCALALLOC, LOCALSIZE, LOCALREALLOC and LOCALFREE. Initial synthetic reserve7400/capacity512. Successful resize returns7400 and updates modeled capacity to requested size; failed resize returns0 and leaves capacity unchanged. Free returns0, with original12D2 clearing the reserve. These are explicit API assumptions, not observed Windows heap effects.

DS1048, SS4000, CS3000; internal selectors12F3/1308/1324 normalize to3000. Stored test handler is3000:12D2. Missing-reserve cases stop at132E beforeCALL4564; exception transfer is not simulated. All import stubs consume only API argument words and preserve other registers exceptAX. No full game, Windows heap, exception propagation or parity measurement occurs.

Run `python3 pass82/verify_integrated_retry.py` with Unicorn2.1.4. Original executable SHA256:12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Uses original EXE and previously preserved Ghidra12.2 evidence; no fresh database update.

## Implementation-ready findings
Represent allocator retry and reserve state as one linked control flow. Do not treat handlerAX1 as proof of released memory. Reserve0 changes the next failed attempt into the exception path. Do not replace original repeated failed-resize behavior with an invented fixed retry count when reproducing this code.

## Unknowns and next test
Actual LOCALREALLOC failure state, live heap capacity and reachable request ranges require Win16 execution. Trace reserve initialization and desired-size changes at application+78 to determine normal capacity policy. Confidence High for original control flow under explicit modeled API results; actual runtime heap behavior remains Unknown.
