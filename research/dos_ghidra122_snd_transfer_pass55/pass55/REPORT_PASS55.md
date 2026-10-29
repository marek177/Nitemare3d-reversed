# Pass55 — original SND.DAT transfer and DOS far-read error handling

## Finding
Confirmed, High: the original resource-transfer routine lazily opens `snd.dat`, ignores the seek return value, and requires the DOS read wrapper's AX result to equal the requested unsigned16 byte count. The original wrapper preserves DS and converts DOS carry-set read errors to AXffff. This creates an equality collision for the synthetic request length65535: a read error is accepted by this caller's count comparison.

## Evidence
2160 passing scenarios across six distinct DOS images, with up to two calls per scenario. No repeated counts represent independent versions: supplied1.8/1.9 are the same image. Original transfer and original far-read-wrapper instructions execute from relocated EXEs. CRT open, CRT seek, fatal-handler calls and the INT21/AH3f read service boundary are mocked; actual SND.DAT contents are not copied. Fatal tests stop at handler entry, making no claim about handler internals or return behavior.

Ghidra12.2 independently exports both functions' current instructions and diagnostic C from pass54's runtime-correct project. Twelve C outputs generated. Their automatic CRT prototypes are incomplete (for example, an apparent zero-argument open call); instruction arguments and execution traces, not inferred C prototypes, define this contract. No project changes made in this pass.

| DOS | Transfer entry | Original far-read wrapper | Handle global | Filename |
|---|---|---|---|---|
|1.0|1273:006e|1f67:009c|DS:01a8|snd.dat|
|1.1|1275:0062|1f89:0094|DS:01a8|snd.dat|
|1.2|1275:0062|1f8f:0094|DS:01a8|snd.dat|
|1.5|1277:008a|1f94:0092|DS:01ac|snd.dat|
|1.7|1277:008a|1f9d:009e|DS:01ac|snd.dat|
|1.8/1.9 supplied|1277:008a|1fb7:0092|DS:01ac|snd.dat|

## Confirmed behavior and exact locations (V1.9)
- 1277:008d–00b4: handle0 is the unopened sentinel; call CRT open with `(near_filename,0x8000)`. Store returned AX; only fresh open returnffff invokes the open-failure handler. An already storedffff bypasses opening and proceeds to seek/read. Opening as handle0 succeeds for this invocation but causes another open on the next invocation.
- 1277:00b6–00c5: seek `(handle,source_offset_i32,whence0)`. Neither AX nor DX is checked after the call. Injected seek failure AX=DX=ffff does not stop reading.
- 1277:00c7–00d7: read `(handle,dest_offset,dest_segment,length_u16)` through the original far wrapper.
- 1fb7:0092–00aa: push DS; load destination into DS:DX using LDS; set BX=handle,CX=length,AH3f; INT21; carry clear retains DOS AX, carry set replaces AX withffff; pop DS and far-return.
- 1277:00d9–00ea: compare AX against requested length bit-for-bit. Mismatch calls the read-failure handler. Equality returns with AX equal to requested length under the tested boundary responses. The routine does not close the cached handle in this body.

All listed branch/state claims are Confirmed/High from static instructions plus repeatable original-code execution. Claiming real leaked handles or a reachable65535-byte asset would be unsupported: those are Unknown.

## Test matrix
Six images x5 initial/open handle combinations x4 requested lengths x3 offsets x3 read outcomes x2 seek outcomes=2160 scenarios.

Handles `(cached,open_result)`: `(0,0),(0,5),(0,ffff),(7,5),(ffff,5)`. Lengths0,1,8192,65535. Source offsets0,123,-123. Read outcomes: exact count, max(length-1,0), or carry-set DOS errorAX5 (original wrapper turns it intoffff). Seek mock returns requested offset or AX=DXffff. Successful first calls are repeated to expose the handle0 sentinel behavior; fatal paths stop immediately. Every trace checks exact open/seek/read arguments and fatal-call arguments extracted independently from the instructions. Final cached handle, normal-return AX, SP, CS and restored DS are asserted. Read-service traces prove destination DS6000,DX0200 and unmodified requested CX. No real filesystem or DOS segment-crossing transfer semantics is modeled.

## Implementation-ready contract
```
if cached_handle == 0:
    cached_handle = open("snd.dat",0x8000)
    if cached_handle == 0xffff: fatal_open(...)
seek(cached_handle,source_offset,0)   # result ignored
n = far_read(cached_handle,destination,length)
# far_read maps carry-set DOS error to0xffff and restores DS
if n != length: fatal_read(...)
```
Do not silently add a seek-result guard, change the handle sentinel or replace this count comparison with signed-negative detection when reproducing original behavior. For a safer modern API, any intentional change should be kept separate from parity mode.

## Unknowns and next test
The open/seek CRT internals, fatal-handler termination, cached-handle lifecycle outside this function, real asset sizes/IDs and negative-offset backing-store interpretation remain unresolved. Next: run the cache/dispatcher chain with this original routine and original far-read wrapper, provide a synthetic DOS file service or real SND.DAT bytes, then replace remaining CRT boundary mocks. Confidence High for the tested local control flow and register ABI; full audio/game parity remains unverified.
