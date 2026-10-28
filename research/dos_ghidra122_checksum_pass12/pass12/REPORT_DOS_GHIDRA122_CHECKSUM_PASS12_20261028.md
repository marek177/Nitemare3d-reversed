# Checksum pass12 — original fclose and read-buffer ownership

## Finding
Confirmed across six distinct DOS images: original fclose releases an owned read buffer before calling low-level DOS close. If DOS close fails, fclose returnsffff and still clears FILE flags and owned buffer pointers/count; low-level handle flags remain unchanged. Successful close clears low-level handle flags. An allocation-fallback one-byte buffer is not passed to free.

## Evidence
768 targeted executions passed:576 checksum integration cases plus192 fclose matrix cases. Original EXE instructions are executed with Unicorn, guided by Ghidra12.2 exports; no new Ghidra analysis/coverage increase is claimed.

Integration now executes original fopen, low-level open, FILE initialization, fread/refill/copy/read, fclose, read-stream flush bookkeeping, owned-buffer cleanup and low-level close/common error handling. Only allocation/free and DOS INT21 interface are simulated. The previous fclose bypass is removed. Tests assert cleared FILE and handle flags after completed close, and exactly one free of9400 for successful buffer allocation when reads occurred, no free for allocation fallback or negative-length no-read path. Existing576 inputs include EOF, short reads, control bytes, allocation success/failure and persistent read errors. Twenty-four cases are intentional100000-instruction budget observations of the persistent read-error loop, so no close is reached in those cases.

Standalone fclose matrix: initial FILE flags00,01,05,09,19,29,41,49 x DOS close success/error5 x handle5/25 (maximum20), across6 images =192. FILE pointer9403,count3,base9400; temporary-file companion field0. Original fclose, read flush bookkeeping, cleanup and low-level close execute. Only actual free and DOS INT21 close are hooked. Each test checks AX, final pointers/count/flags, handle byte, free arguments/count, DOS close call count, low-level handle flags, far return and stack restoration.

V1.9 entries: fclose21ea:05fe, read flush bookkeeping21ea:0c50, buffer cleanup21ea:09b2, free call21ea:09c7 ->21ea:3cb2, low-level close21ea:1bba. Exact per-build entries and hashes are in fclose_matrix.json. Integration evidence records freed buffers and DOS call traces.

## Behavior model
For active tested read streams (FILE flags&83 nonzero and FILE bit40 clear): first flush bookkeeping resets current pointer to base and unread count0. If FILE bit08 is set, cleanup calls free(base), clears bit08 and sets current/base/count0. It then calls low-level close(handle). Return is0 on success,ffff on close failure or out-of-range handle. FILE flags are cleared regardless of those close results.

| Condition | Free | DOS close | FILE flags | Low-level handle flags | Return |
|---|---|---|---|---|---|
| Active owned buffer, valid handle, success | Yes, before close | Yes | 0 | 0 | 0 |
| Active owned buffer, DOS error5 | Yes, before close | Yes | 0 | Preserved | ffff |
| Active owned buffer, handle25/max20 | Yes | No | 0 | Preserved | ffff |
| Active fallback bit04, valid success | No | Yes | 0 | 0 | 0 |
| Inactive00 or FILE bit40 set | No | No | 0 | Preserved | ffff |

Inactive and bit40 paths leave pointer/count/base unchanged; active non-owned read paths retain base, set current=base/count0. This table concerns FILE flags; the same numeric bit in a low-level handle flag byte is a separate field and is not assigned a shared semantic meaning.

The validator does not inspect fclose's return before returning. Combined with earlier EOF evidence, the tested checksum success path can finish after a close error without invoking its fatal handler; standalone fclose error behavior is established here, while full validator error-on-close injection is not included in the576 integration cases (DOS close succeeds there).

## Classification and limitations
Confirmed/High for tested read-stream states, temporary-field0 and simulated DOS/free contract. Actual heap allocator/free internals are not executed; observing a free call proves ownership transfer request, not successful heap reclamation. DOS/device behavior is simulated. Write-buffer flushing, temporary-file deletion branch, startup/exit cleanup and whole-game runtime parity remain unknown. The two supplied1.8/1.9 labels still refer to the same image. Ghidra databases/counts unchanged.

## Reproduce and next step
Run `/usr/bin/python3 scripts/verify_checksum_close.py` and `/usr/bin/python3 scripts/verify_fclose_matrix.py` with Unicorn. Archive includes reconstructed EXEs, Ghidra instruction exports, pass7 specs and pass10 call-site metadata. Next: resource loader allocator/seek contracts and caller ownership of returned BSF text blocks; write/temporary-file fclose branches require separate tests.
