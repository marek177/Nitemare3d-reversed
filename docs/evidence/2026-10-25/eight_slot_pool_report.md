# Eight-slot pool activation, state transitions and reuse scope

## Source and scope

Exact DOS2 source SHA2565ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3 is unchanged. Three local spans07ED:000E..00C5,0272..035E and0360..044C contain237 instructions whose lengths independently agree in Capstone5.0.9 and iced-x86 1.21.0. This is bounded instruction analysis, not complete interprocedural or parity acceptance. The pool is reached from literal call0637:06DA; this is the one such literal FAR call in inherited instruction membership.

The pool starts at DS41B6, with8 records of42 bytes. State is byte0C; each slot embeds a28-byte record at0E. The first state byte is41C2, then stride2A through42E8. An original stopped-state snapshot at revision197 shows all8 state bytes zero. No active allocation, collision, release or same-slot reuse runtime invocation is claimed.

## Local allocator07ED:000E

The scan tests state bytes in increasing slot order for zero. If all8 are nonzero it returns AL0 before calling083D:0B42. Otherwise it calls that external gate; AL0 also returns failure. DI carries the scan index across that call, so the complete first-free selection contract depends on its interprocedural preservation, which is not closed here.

After a successful gate the routine computes41B6+42*DI and writes state1 at003E BEFORE subsequent initialization. It sets word0A to+1 only for signed90<DS4156<270, otherwise-1. Word08 is+1 for signed DS4156<180, otherwise-1. It copies words DS4172/4174/4176/4178 to slot00/02/04/06.

For the embedded record it ORs flag byte05 with01 and ANDs withEF, calls083D:0AF6, stores returned AL as byte04, sets frame byte03=0 and dword08=0, copies dword DS417C to0C and player-position words DS4162/4164 to10/12, then sets byte1A=5. Success returns AL1, not a promised zero-extended AX boolean. SI/DI are locally restored and FAR return performs no argument cleanup.

This is partial initialization. The local body does not clear all42 bytes, other flag bits remain, and external helpers may have further effects. The early state1 store and preserved bytes are original ordering facts; they are not proof of a reachable reentrancy bug and do not justify changing game behavior.

## Movement/collision helper07ED:0272

The helper uses the slot pointer and embedded record, and performs a signed-loop count governed by DS4560 with incremental coordinates and a call to07ED:00C6 for candidate collision handling. A nonzero return takes0318: state becomes2 at0320, embedded frame03 is reset,083D:0B1C supplies the new embedded type04, and embedded flag05 gains10. The local transition does NOT clear embedded deadline dword08.

The shared tail increments byte1A, compares it with14 using signed JLE and otherwise stores14; it writes embedded position words10/12. This is a signed byte condition, not a universal unsigned saturation claim. Nested collision/damage and alias effects are still open.

## Update/render dispatcher07ED:0360

The routine visits exactly8 slot positions in increasing address order. It derives the animation-table pointer from embedded type byte04, stride8 at DS3D1E, before dispatching on state. States other than1/2 skip the active branches.

State1 compares unsigned32 embedded deadline with RTC DS081E. If due, it increments the frame once, compares the zero-extended frame byte with a signed animation-table frame count and resets frame to0 if not less. It sets deadline=RTC+the table's16-bit period modulo2^32. There is no local catch-up loop. It then calls0272 regardless of whether animation was due. Subsequent code remains in the state1 branch even if that helper just changed state to2; the new state is not redispatched locally in the same call. Position-distance tests can skip the rendering call; their full coordinate and overflow invariants are not closed.

State2 uses the same unsigned deadline test and at most one frame increment. After the deadline block it compares frame against the table count. If frame is not signed-less-than count,042C writes state0. This release clears only the state byte locally; it leaves the other slot/embedded bytes. Otherwise it calls0AEA:0434. Renderer and type/table side effects require further evidence.

## Separate six-byte motion population

The earlier candidate0000:0E50 iterates6-byte records at21FD:36B6 using count at21FD:0004. Its population builder0000:052A scans object type byte06 for28, assigns an object index and sets record byte04=0. This is structurally separate from the8x42-byte pool. It must not be substituted for projectile-slot allocation/reuse merely because both contain counters and object references. Save/load paths also reference that motion population; their restoration semantics remain open.

## Runtime/input evidence and remaining work

The original ses-1 is still stopped at1401:0382, revision197, and snapshot reads leave the same revision. No guest fixture writes were made. Agent capabilities advertise memory/trace/breakpoints but no input method. Computer-use inventories find no targetable window for this owned hidden run, so no UI keys were sent. This is input-route availability evidence only; neither physical keyboard nor IRQ9 parity is claimed. No replacement game-state mutation is presented as a native input test.

Next: establish a targetable original input route, stop allocator entry before a real fire input, capture gate/activation order and ammo changes, follow first movement/collision and state2 release, then fire again to test same-slot reuse and retained bytes. Observe nested reentrancy only on demonstrated paths. Pair the exact original slot/state/write order with the remake; global OBJECT, generation/ABA, all weapon/guard branches, Win16 runtime and renderer acceptance remain OPEN.

Public output contains findings, hashes and numeric empty-pool metadata. Original pool bytes, binaries/assets and raw traces stay local.

