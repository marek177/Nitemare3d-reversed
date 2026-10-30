# Nitemare3D Windows 1.10 — pass 68

## Confirmed, high confidence

The static exception object DS:41BC belongs to the startup initializer chain. This finding uses the preserved Ghidra 12.2 native export and original NE executable; no fresh database changes were made.

The startup path contains CALLF 1008:37EE at 1008:378F. Within 37EE, instructions 38BB–38C1 load SI=204A, DI=20CE and call 3994. The 132-byte interval contains 33 far callbacks. Original 3994 decrements DI by four before each callback, skips a completely zero far pointer, and processes the interval in reverse address order.

The callback at DS:205E is 1000:45CE. Its offset word exists at file offset 2E09E. The raw selector word is a relocation-chain link, not a valid loaded selector: NE segment 10, type 2 flags 0 relocation at 2060 targets NE segment 1. Normalizing that relocation yields Ghidra selector 1000.

45CE calls, in order:

| Entry | Native action |
|---|---|
| 4410 | Push 0500 and 41B6; call 0752 |
| 4530 | Push 0514 and 41BA; call 0752 |
| 4542 | Construct object 41BC through 036A, then install tables 48D0 and 48E4 |
| 4570 | Push 0524 and 41C0; call 0752 |
| 4582 | Construct object 41C2 through 036A, then install tables 48D0 and 48F8 |
| 45BE | Register callback 1000:45A4 through 1008:73CC; discard four argument bytes |

45A4 resets both 41C2 and 41BC to base table 1018:48BC. The registration result is not tested by 45BE; a full callback table therefore cannot be described as guaranteed registration success. The 0752 node links and class identities remain only partially understood.

After return from 37EE, startup proceeds through other initialization, then calls 37C2 at 37AD. That wrapper calls game entry 1000:2A8E at 37E0. Thus the constructor chain precedes this game-entry call on the normal returning startup path. This is a static ordering claim, not proof that every initializer succeeds in Windows.

## Verification

67 original-instruction Unicorn loop cases passed: all 34 aligned suffix ranges, including the empty range, and 33 separate cases nulling each callback slot. Each case checks exact reverse callback order and unchanged SP before the final RET. Callback invocation is intercepted before CALLF and skipped synthetically without effects; callback bodies, the full startup, and Windows imports are not executed in this pass. Original bytes of the complete 3994 loop are checked against the native listing. The supplied script reproduces these checks.

Executable SHA256: 12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.

## Remaining work

Resolve semantics of the 0752-linked metadata at 0500/0514/0524 and compare the second object 41C2 with 41BC. No claim of complete semantic recovery, real Win16 execution, or gameplay parity is made.
