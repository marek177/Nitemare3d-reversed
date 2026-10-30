# Win110 pass88 — pretranslation hierarchy traversal

## Finding
Confirmed / High: application table554C slot+44 contains3AE8. It obtains a designated main object via application virtual+6C, walks the message's HWND through GETPARENT, resolves each HWND through130E and offers the message to object virtual+54. Any nonzero filter result returns1. A declining mapped object equal to the designated main object stops traversal and returns0.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed |Table554C+44 points3AE8 |NE4 raw offset2A7F0 | High |
| Confirmed |Main-object pointer supplied by application+6C |3AF1–3AF8 | High |
| Confirmed |Initial HWND is first message WORD |3AFB–3AFE | High |
| Confirmed |Each nonzero HWND resolves via130E; unmapped HWND still gets parent lookup |3B04–3B29 | High |
| Confirmed |First nonzero virtual+54 consumes message |3B16–3B1C→3B2D | High |
| Confirmed |Mapped main object declining stops immediately |3B1E–3B21→3B47 | High |
| Confirmed |At end of parent chain, main object gets fallback filter call if nonzero |3B32–3B45 | High |

## Behavior model
`main=app.virtual6C(); h=message.word0; while(h) { obj=lookup130E(h); if(obj) { if(obj.virtual54(message)) return1; if(obj==main) return0; } h=GetParent(h); } return main && main.virtual54(message) ? 1 : 0;`

This identifies hierarchy traversal and consumption policy, not accelerator/dialog semantics inside virtual+54. Object-slot meaning is per object type; application+54 used by A344 is a different receiver context. Shared slot offsets must not be conflated.

The main object can receive the fallback even if a synthetic HWND lookup omitted it from the traversed chain. Conversely, once it is encountered as a mapped object and declines, it is not called again as fallback. Thread-style messages with initialHWND0 go directly to that fallback. No cycle guard appears in the captured traversal; cyclic model hierarchies are not tested.

## Verification
768 cases passed: initialHWND0/1 × main0/7410/7500 × all8 mapping-presence masks for a three-level chain1→2→3→0 × all16 consumption masks for three mapped objects and external main. An independent traversal model checks exact ordered events, finalbooleanAX, caller-cleanedSPD008 and restoredBP/SI/DI. Detailed representative traces for consumption masks0/15 are retained; every combination executes and is asserted.

Original3AE8 executes without instruction patches. Application+6C,130E,GETPARENT and both virtual+54 call sites are intercepted, with argument validation and declared WORD results. Synthetic objects supply far table operands, but no getter/filter body, map implementation, parent API, accelerator or Windows queue executes. DS1048, SS4000, CS2000. Raw table target3AE8 checked directly; raw adjacent selector is a NE relocation-chain word, not a loaded selector.

Run `python3 pass88/verify_pretranslate_chain.py` with Unicorn2.1.4. EXE SHA256:12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Uses original EXE and preserved Ghidra12.2 export; no fresh database update.

## Implementation-ready findings
Preserve child-to-parent order, skip filtering for unmapped HWNDs while still climbing, stop after main-object rejection, and normalize any nonzero filter return to1. Keep main fallback distinct from traversed-object filtering.

## Unknowns and next test
Resolve virtual+6C's returned object and130E's HWND map semantics. Then inspect concrete virtual+54 targets to identify accelerator/dialog filters. Actual Windows hierarchy and message consumption remain Unknown. Confidence High for isolated traversal under declared callback/API models.
