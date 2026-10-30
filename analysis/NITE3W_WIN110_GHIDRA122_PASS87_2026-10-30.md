# Win110 pass87 — message pump dispatch policy

## Finding
Confirmed / High:39EE returns0 only when GETMESSAGE returnsAX0. Any nonzero WORD result invokes application virtual slot+44. Its nonzero result suppresses translation/dispatch; zero executes TRANSLATEMESSAGE then DISPATCHMESSAGE. Both nonzero-GetMessage paths returnAX1.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed |GETMESSAGE receives stack words0,0,0,app+2C,DS |39F5–3A00 | High |
| Confirmed |Zero branches straight to epilogue, preservingAX0 |3A05–3A07→3A2E | High |
| Confirmed |Virtual+44 receives application and near message pointer |3A09–3A10 | High |
| Confirmed |Nonzero virtual result bypasses translation/dispatch |3A14–3A16 | High |
| Confirmed |Translate then dispatch use identical DS:app+2C pointer |3A18–3A26 | High |
| Confirmed |FinalAX1 replaces downstream API results |3A2B | High |

## Behavior model
`if(!GetMessage(&app.message,0,0,0)) return0; if(!app.virtual44(&app.message)) { TranslateMessage(&app.message); DispatchMessage(&app.message); } return1;`

There is no signed-negative branch on the GetMessage WORD. FFFF follows the nonzero path in this original code. That synthetic result is not a claim that Win16 GETMESSAGE reports an error this way; no modern API contract is imposed on this older binary. Virtual+44 is called a pretranslation hook by role (Inferred / Medium); its actual body and message-consumption conditions remain unexecuted.

## Verification
131,072 cases passed: all65,536 GetMessage return words crossed with virtual results0/FFFF. Each verifies exact call sequence, every call's stack argument words, finalAX, finalSPD006, restoredBP/SI. Translate/dispatch stubs returnDEAD to prove39EE overwrites their results with1.

Original39EE executes without instruction patches. GETMESSAGE,virtual+44,TRANSLATEMESSAGE,DISPATCHMESSAGE call sites are intercepted beforeCALLF, consume their declared argument bytes, and return syntheticAX. No message contents, real queue, virtual method or Windows API executes. Synthetic application7000/table5000:6000 supplies LES operands. DS1048 differs from SS4000; CS2000 maps NE1. Native non-direct-CALLF bytes are checked against raw executable and preserved listing.

Run `python3 pass87/verify_message_pump.py` with Unicorn2.1.4. EXE SHA256:12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Evidence uses preserved Ghidra12.2 export, without a fresh database update.

## Implementation-ready findings
Keep GetMessage zero handling separate from pretranslation suppression. Do not dispatch a message already consumed by the hook. Ignore downstream Translate/Dispatch return values when reproducing this pump's boolean result. Preserve message storage at application+2C and caller ABI.

## Unknowns and next test
Resolve the application's virtual+44 target and its accelerator/dialog filtering chain. Actual queue/quit semantics and live Windows dispatch remain Unknown. Confidence High for isolated pump branching under declared call results.
