# Playback request ABI and uninitialized register inputs — pass49

648 tests execute six original backend wrappers,generic request and CRT interrupt marshalling. INT63 driver boundary injects response registers; no actual driver/audio executes. Six distinct images tested; supplied1.8/1.9 identical.

Confirmed (High), request mapping:

| Wrapper | INT63 input AX | BX | DX | DI |
|---|---:|---:|---:|---:|
| busyA |0800|0|0|0|
| stopA |0700|0|0|0|
| busyB |1c00|0|0|0|
| stopB |1500|0|0|0|
| playA |0600|0|pointer segment|pointer offset|
| playB |1b00|0|pointer segment|pointer offset|

Values hexadecimal. Full per-build entries and original bytes in requests.json. For V1.9 busyA20bc:0f75,stopA0ee5,busyB0fa7,stopB0f14,playA0a05,playB094f. Play wrappers check both pointer words:0000:0000 returns AXffff without interrupt; offset0 with nonzero segment is accepted. Non-null request paths return driver AX unchanged for injected0,1,ffff. This is raw return forwarding,not proof every status value has boolean semantics in hardware.

Confirmed (High): generic request allocates a register structure but does not initialize its input CX/SI words. Stack fill00 produces CX=SI=0000; filla5 produces CX=SI=a5a5 at driver boundary in every non-null test. Thus pass48's observed CX0 was a property of its zero-filled setup,not a general interface guarantee. Its established AX/BX/DX packing remains valid. A faithful abstraction should distinguish assigned registers from unspecified stack-derived inputs.

Run `/usr/bin/python3 scripts/verify_playback_requests.py` with Unicorn2.x. Six images ×six wrappers ×three pointers ×two stack fills ×three driver AX responses=648. Entire caller/callee chains execute; INT63 hook records all six general input registers and supplies AX plus distinctive BX/DX/DI responses. Check request register mapping,undefined-input dependence,null-pointer early return,return AX,far return,SP and DS. No callee-skipping mocks. No response-flag semantics claimed.

Ghidra12.2 preserved exports provide locations; no project database edits. Confidence High for wrapper/marshalling behavior; real driver handling of unspecified registers and actual audio remains Unknown.

Implementation-ready: preserve null-pointer guard,far pointer placement,command selection and raw AX forwarding. Do not assume CX/SI zero when replaying low-level requests. Next: locate/identify resident INT63 driver,inspect command handlers and trace cache/loader before actual sample playback. Full driver/audio/timing and gameplay parity remain open.
