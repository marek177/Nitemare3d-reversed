# Win110 pass85 — idle-loop argument identity

## Finding
Confirmed / High static chain:3A34 zeroes a32-bit local count, checks PEEKMESSAGE, and when no message is reported invokes application virtual slot+48 with that count. Constructor-installed table1018:554C has3D72 in slot+48. Therefore3D72's two words are low/high halves of an idle-iteration count, rather than a message ID and separate argument.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed |3A34 resets local low/high count to0 and increments with carry after slot+48 call | Native3A34 export | High |
| Confirmed | Call occurs after zero result from PEEKMESSAGE |3A34 native/decompiler evidence | High |
| Confirmed | Table554C+48 contains offset3D72 |NE4 file2A7F4; constructor3936 table installation | High |
| Confirmed |3D72 classifies the combined argument as signed32 <=0 versus >0 |3D8B–3D9C and196608 cases | High |
| Confirmed | Count1 can trigger guarded maintenance, count0 selects the initial-work branch |3E5B–3E7A and prior pass84 | High |

The table selector requires normal NE relocation; the raw on-disk adjacent word is a relocation-chain link. The offset identity is checked directly; the full Windows virtual dispatch is not executed here.

## Behavior model
For each outer message-loop iteration, idleCount starts0. While PEEKMESSAGE reports no queued message, slot+48 executes with the current count, then the caller increments the count and repeats only if the virtual method returns nonzero. Afterwards3A34 calls39EE for message processing and handles its termination result.

3D72 uses signed32 <=0 for its initial-work branch. That branch sends0363-related calls to eligible visible windows and traverses an object list through virtual slot+60, as statically shown. At count1, its other branch may run the0→1→0 maintenance gate recovered in pass84. Positive counts other than1 do not trigger that gate. Negative counts would again select initial work; practical count overflow/reachability is not established.

This resolves pass84's deliberately numeric guards:BP+8=1 andBP+0A=0 represent idleCount1. The claim concerns idle iteration, not elapsed time or a gameplay tick.

## Verification
196,608 cases pass: every high WORD crossed with low0,1,FFFF through original3D72 classifier3D8B..3D9C. Branch boundary is checked against an independent signed32 interpretation. No stubs, imports or code patches are used. DS1048, SS4000, CS2000; frame words synthetic. Execution stops before the selected branch body. The complete idle message loop and Windows PEEKMESSAGE are statically inspected only.

Run `python3 pass85/verify_idle_argument.py` with Unicorn2.1.4. EXE SHA256:12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Source is original EXE and preserved Ghidra12.2 native export; no fresh database update.

## Implementation-ready findings
Represent this parameter as a32-bit idle-iteration count, preserve low/high word ABI, reset it at each outer loop, and increment after calling the virtual method. Keep initial work at count0 distinct from maintenance at count1. Do not map these words to WM_CREATE or another Windows message based on numeric coincidence.

## Unknowns and next test
Execute the bounded message loop with declared PEEKMESSAGE/virtual-method boundaries to verify count increment, return-controlled termination and reset. Trace39EE to the actual message-dispatch path. Confidence High for argument identity and classifier; live Windows scheduling remains Unknown.
