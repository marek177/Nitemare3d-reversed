# Checksum pass 10 — original fopen, buffer allocation fallback, text-mode control

## Finding
Confirmed for all six distinct supplied DOS images: the validator passes literal `rb` to original fopen; original mode parsing passes low-level open flag 0x8000. Original FILE initialization and lazy buffering produce the same EOF/checksum behavior established in pass9. Allocation failure does not abort reading: CRT uses a one-byte buffer within its stream companion record.

## Evidence
720 executions passed: 576 through original fopen and buffering initialization, plus 144 text-mode control cases. This is a continuation using original EXE code and Ghidra 12.2 instruction exports, not a new Ghidra reanalysis or coverage increase. All images are hash-identified; supplied 1.8/1.9 remain one identical image.

The 576-case suite executes original validator -> fopen wrapper -> free FILE slot search -> mode parser -> fread/refill/copy/low-level read. Hooks bypass low-level open (return handle5), 512-byte allocation (success at DS:9400 or null), fclose and DOS INT21 AH3f only. The original fopen call is observed but not skipped. Native first FILE slot and companion record are cleared and stream-table upper bound is configured to that slot; startup initialization of the entire CRT is outside scope. The synthetic filename pointer is supplied by the harness; the mode pointer is the actual literal used by the validator.

V1.9 addresses: validator183c:28c2, fopen21ea:06ea, wrapper21ea:06be, free-slot21ea:1b24, mode parser21ea:0a22, buffer-init21ea:09de, allocation call21ea:09e9. Per-build entries/call sites and hashes are in checksum_open_locations.json. All mode arguments were `rb`, all low-level open flags were8000. Successful terminating read cases assert capacity512 for allocator success or1 for failure, exactly one allocation call, read count, checksum byte, close, far return and stack restoration. Negative-length cases assert no allocation and capacity0.

Inputs: empty,00,01,ff,1234,00..34 and `A CR LF B Ctrl-Z C`; requested lengths0/full-stream, input length+2 andffffffff; stack-local seeds00/a5; allocation success/failure. Persistent DOS read-error cases retain error/EOF separation: 24 runs exhausted100000 instructions with error set, EOF clear and repeated reads. These are bounded traces, not completed game runs or proof of hardware nontermination.

The 144-case text-mode control suite retains pass9's explicitly configured buffer8/FILE flags09 but sets low-level handle flag80. It executes original text conversion within CRT low-level read, with DOS reads injected. Inputs and expected logical bytes: empty->empty; `A CR LF B`->`A LF B`; `A Ctrl-Z B`->`A`; `A CR X B`->unchanged. Each uses full-stream, length+2 and negative length, two local seeds, six images. It checks validator checksum and call counts against transformed bytes. It does not exercise original fopen in text mode, CR at a DOS read boundary, device IOCTL or seek lookahead paths.

## Behavior model
Original `rb` opening initializes FILE flags to read mode1, pointers/count to0 and handle byte to5 from low-level open. First fread refill attempts malloc512. Success sets FILE buffering bit08, capacity512 and allocated buffer base. Failure sets bit04, capacity1 and buffer base at companion+1 (FILE+0xa1 for this layout). Both paths preserve the caller's destination byte on EOF and therefore preserve the validator's extra EOF fold.

Text conversion is an independently demonstrated control path: CRLF collapses, Ctrl-Z ends logical input, isolated CR followed by a non-LF stays. The actual validator binary-open flag excludes that conversion under the tested low-level handle contract; construction of low-level handle flags from a real DOS open remains unexecuted.

## Classification and confidence
Confirmed / High: rb literal and parsed8000 flag, original fopen FILE field initialization, 512/1 buffer branches, EOF destination preservation and checksum behavior under the stated simulated DOS interface. Confirmed / High within configured text handle: tested CRLF/Ctrl-Z transformations. Unknown: actual allocator internals, low-level open implementation and real DOS handle creation, original fclose cleanup, default process startup, all text-mode boundary/device cases. No complete DOS runtime or 1:1 gameplay parity claim.

## Reproduce and next test
Run `/usr/bin/python3 scripts/verify_checksum_open.py` and `/usr/bin/python3 scripts/verify_checksum_text.py` with Unicorn. Archive includes reconstructed EXEs, prior Ghidra instruction exports and pass7 specs. Next: execute low-level open through DOS INT21 interception and close/free cleanup; separate loader allocator/seek ABI remains open. Existing Ghidra projects and decompiler success counts are unchanged.
