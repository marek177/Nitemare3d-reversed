# Pass 9 — original CRT checksum chain

## Finding
Confirmed within the configured binary buffered stream: original CRT fread preserves the destination byte when DOS read returns zero and marks EOF. This independently validates the dependency assumed in pass8. Original validator therefore folds the final byte twice for a nonempty full-stream input. An empty input folds the preexisting stack byte once.

New error finding: injected DOS read failure (carry set, AX=5) sets the stream error bit 0x20 without EOF bit 0x10. The validator full-stream loop checks only EOF. Twelve runs exhausted a 100000-instruction budget while repeatedly retrying read, with no close or fatal branch reached. The repeated state/control-flow supports a retry loop under persistent error; finite-budget observation does not establish real hardware nontermination.

## Evidence
252 passing targeted cases: 216 normal/EOF cases plus 36 persistent DOS read-error cases across DOS 1.0, 1.1, 1.2, 1.5, 1.7 and supplied shared 1.8/1.9 image. Each image is hash-identified in evidence/checksum_crt_locations.json. Ghidra 12.2 exports supply exact instruction locations. Original instructions execute in Unicorn; no executable patching.

Executed original validator, fread, refill, memory-copy helper, low-level CRT read and its return/error handling. Only fopen/fclose calls are bypassed and DOS INT21 AH=3f is simulated. Unlike pass8, fread and its internal callees are not mocked. Code hooks count callee entries; evidence records DOS read calls and source position.

V1.9 chain: validator 183c:28c2 -> fread 21ea:0700 -> refill 21ea:0838 / copy 21ea:2f88 / low-level read 21ea:1e18 -> INT21 at 21ea:1e4f. Native stream table DS:2178, companion table DS:2218, maximum handle DS:2126. Exact corresponding addresses for other builds are extracted from their instructions, not assumed identical.

Stream setup: first native FILE record, empty buffer at DS:9400, flags 0x09, handle5, companion flag1 and buffer capacity8, maximum handles20, binary handle flags0, DS=SS=the build startup data segment. This deliberately bypasses fopen and dynamic buffer allocation. It does not prove all default stream setup or text-mode paths.

Inputs: empty, 00, 01, ff, 1234, sequence00..34. Requested lengths: zero (full stream), input length+2, and ffffffff (negative). Initial local byte00 or a5. Error cases use source01 but DOS fails every read. Tests check requested fread call count, final folded byte, close, far return and stack on terminating paths. Retry-loop cases check error set, EOF clear, over100 DOS reads and no close/fatal branch at the budget limit.

| Status | Behavior | Confidence |
|---|---|---|
| Confirmed | Zero-byte DOS read -> EOF flag, fread returns0, caller destination unchanged | High within binary buffered setup |
| Confirmed | Full-stream checksum = 7b XOR data XOR final byte for nonempty input | High; original CRT chain executed |
| Confirmed | Empty input checksum depends on uninitialized local byte | High; two seeded local values |
| Confirmed | Persistent read error sets error flag but full-stream validator retries | High for bounded traces under injected persistent failure |
| Confirmed | Fixed positive length ignores failed fread and keeps folding preserved local byte | High for tested short lengths |
| Unknown | Real-world reachability of persistent errors, default fopen setup, text conversion, allocation failure | Outside configured entry conditions |

## Implementation-ready findings
For parity with this binary buffered path, do not replace the original full-stream checksum with a plain XOR of all bytes. Keep EOF and error flags separate. A safer new implementation may stop on error, but that is an intentional behavior change requiring an explicit parity exception. Empty input checksum is not a universal constant because the destination local is uninitialized. The full-stream wrapper does not propagate read failure as a clean failure result.

## Reproduce and limits
`/usr/bin/python3 scripts/verify_checksum_crt.py` with Unicorn installed. Delta archive contains exact reconstructed EXEs, Ghidra instruction exports and pass7 specs needed to rerun. Existing Ghidra databases are unchanged; no decompiler coverage increase is claimed. No DOSBox, real DOS filesystem, gameplay, renderer or complete 1:1 parity test was performed. Next discriminating test: original fopen initialization and text-mode translation, then actual loader allocation/seek/error contracts.
