# DOS multiversion pass 8 — checksum EOF contract

## Finding
Confirmed: the original file-validator code folds the destination byte after every fread call, without testing its return count. The full-stream path (length=0) checks stream byte +6 bit 0x10 before entry and after folding. The fixed positive-length path does not consult EOF. This is a targeted emulation of original EXE instructions exported by Ghidra 12.2, not a new decompiler coverage pass or full DOS runtime test.

## Evidence
216 passing cases across DOS 1.0, 1.1, 1.2, 1.5, 1.7, and the shared supplied 1.8/1.9 image. Inputs: empty, 00, 01, ff, 1234, and bytes 00..34; lengths: zero/full stream, input length+2, and ffffffff; initial destination locals: 00 and a5. Every case runs the original complete validator while mocking fopen/fread/fclose. The fread model sets EOF on the first read beyond available data, returns zero and leaves the destination unchanged. Fatal branches are observed and fail the successful-case assertion; process-exit implementation is not executed.

Exact entries, EXE SHA256, original instruction bytes and addresses are in evidence/checksum_locations.json. Detailed outcomes are in evidence/checksum_eof_emulation.json. V1.9 entry is 183c:28c2; fread sites 183c:2938 and 183c:2966, fold sites 183c:2943 and 183c:2971, EOF checks 183c:2952 and 183c:2974. Tests check read count, final local checksum, successful close, far return and stack restoration.

| Status | Claim | Confidence |
|---|---|---|
| Confirmed | Accumulator starts at 0x7b; failed-read return value is ignored | High, original instructions and emulation |
| Confirmed, conditional | With the stated fread model and initially clear EOF, full-stream checksum for nonempty data is 0x7b XOR all bytes XOR last byte | High within mocked dependency contract |
| Confirmed, conditional | Empty full stream folds the preexisting local byte once | High within mocked dependency contract |
| Confirmed | Negative signed 32-bit requested length reads no bytes, retaining checksum 0x7b | High; ffffffff exercised in all images |
| Confirmed, conditional | Requested positive length beyond EOF keeps folding the last available byte, or initial local for empty data | High within mocked dependency contract |
| Unknown | Whether original CRT preserves destination and exactly when it sets EOF on all error/empty paths | Actual CRT not executed in this pass |

## Behavior model
Let A=0x7b and B be an uninitialized stack byte. Open the file. For length=0, while EOF is clear: fread(&B,1,1,stream); A ^= B. For a positive signed length N, repeat that read/fold N times. For a negative length, skip reading. Compare A to expected low byte; mismatch calls fatal handler, success closes stream. This pseudocode abstracts compiler-generated split-word counting; very large positive lengths were not exhaustively emulated.

Examples under the mocked CRT contract: one-byte 01 full-stream yields 7b, not 7a; 1234 yields 69, not 5d. Empty input yields 7b for initial B=00 and de for B=a5. This resolves why the pass7 actual-file checks (all final bytes zero) could not distinguish the extra EOF fold.

## Unknowns and next test
Execute original fread/stream refill logic with mocked DOS INT21 only, including nonzero final byte, empty input, read error and initially set EOF. Audit allocator and seek/read ABI separately. No claim of full CRT, DOSBox, gameplay or 1:1 parity follows from these 216 tests. Existing 3445 stock / 3460 explicit-view decompiler counts are unchanged and were not rerun here. Remaining eight candidate seeds stay unresolved.

## Reproduce
From the archive/repository workspace with pass7 dependencies: `/usr/bin/python3 scripts/verify_checksum_eof.py` (Unicorn required). The delta archive includes exact reconstructed EXEs and Ghidra instruction exports to make this test standalone; prior Ghidra projects remain in pass7.
