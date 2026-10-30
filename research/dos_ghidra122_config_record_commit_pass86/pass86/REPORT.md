# Pass86 — staged configuration record conversion and commit ordering

Confirmed, High confidence within isolated record fixtures: all six distinct supplied DOS binaries use the same four magnitude/enable field mappings and signed conversion. Supplied1.8/1.9 are identical. This upgrades pass85's static mapping to original-instruction execution across all builds. All side-effect callees are mocked; their hardware/audio meaning and actual effects remain Unknown.

| Build | Commit entry |
|---|---|
|1.0|1cdc:1f52|
|1.1|1d00:1f36|
|1.2|1d00:1f38|
|1.5|1d05:1f36|
|1.7|1d0f:1f32|
|supplied1.8/1.9|1d25:1f66|

## Conversion
The routine copies the16-byte config block to a stack-local working copy, obtains an externally configured record segment, and walks records at offset1212h with stride12h until byte0==0. Signed word+2 is the value. Unknown nonzero record IDs leave fields unchanged. For recognized records:

| ID | Magnitude config offset | Enabled config offset |
|---|---|---|
|0a|+04|+08|
|0b|+05|+0b|
|0c|+07|+0a|
|0d|+06|+09|

Magnitude=low8(abs(signed16(value))) using original CWD/XOR/SUB and AL store; enabled=(signed value>0). No byte-range saturation. Tested values -32768,-32767,-257,-256,-255,-1,0,1,255,256,257,32767. In particular -32768 yields magnitude0,enable0; +256 yields magnitude0,enable1. Entire remaining config bytes retain initial values, including width and untouched pairs.

## Side-effect call ordering
Using five callsites ordered by address within each original routine:
0. Before commit, called if new+09 is0 and old+09 is nonzero.
1. Before commit, called if magnitude+07 changes.
2. Always after16-byte copyback.
3. Always after16-byte copyback.
4. After commit, called if new+09 is nonzero and old+09 is0.

The test records full config at every mocked callsite and asserts old bytes for0/1, committed bytes for2/3/4, and exact conditional call order. Caller stack argument bytes are preserved in evidence but their semantic interpretation is not validated. Names such as audio stop/start are intentionally not assigned without callee evidence. The commit does not itself invoke config-save; the connection from actual UI acceptance to this routine and later dispatcher save remains to be proven as an integrated path.

## Verification
600 cases =6 binaries ×(4 IDs ×12 signed values +empty list +unknown ID) ×2 initial+09 enable states. DS=SS,DF0,SPe000. Input record segment explicitly set5000h; no real menu resource initialization is asserted. Only one synthetic record plus terminator per case; duplicates, multiple interacting records and unterminated lists remain untested. All original copies, loop branches and conversions execute unchanged. All called side-effect functions return AX0 via boundary mocks. Assertions cover full16-byte result, call sequence, commit timing, normal return, restored DS and SP. EXE SHA256, exact routine bytes, per-case call snapshots and args are included.

Fresh Ghidra12.2 exports decompile all six commit routines. Test callsite discovery uses Capstone5.0.7 over original relocated MZ bytes, bounded by original RETF; it does not rely on completeness of earlier Ghidra listing. Emulator Unicorn2.1.4 executes native bytes. Decompilation success is not proof of full semantic recovery.

## Reproduction and remaining work
Extract included pass76 dependency and nested baseline58 into baseline58/. Run python scripts/verify_config_record_commit.py with Unicorn2.1.4/Capstone5.0.7 and included pass86 input_locations.json. Expected100 passed per binary. Included script/seeds reproduce Ghidra read-only exports against pass76/project N3D_Runtime54/inputs.

Unknown: UI labels/actual record segment setup, zero-record path with DS!=SS, multiple/duplicate records, side-effect callees, integrated menu acceptance/save and hardware/runtime parity. Next: decode actual record labels and trace callers of this commit routine to prove acceptance timing.
