# Pass 53 — original packed EXE recovery, exact unpacking proof and startup DS

## Finding
Confirmed, High: the supplied DOS databases retain the exact original packed executable bytes. Executing their own unpacking/relocation code yields byte-identical images to every relocated reconstruction used in our isolated tests. The apparent DATA/layout mismatch is explained by the difference between pre-unpack file layout and post-unpack runtime layout. The next CRT initialization reaches the expected DS=SS in all seven entries.

## Evidence
Ghidra12.2 read-only ExportDosSources.java exports original FileBytes, not patched memory. Seven exported SHA256 values exactly match each program's original executable metadata in pass51. Six unique files: supplied1.8/1.9 share SHA2561cbb55c193b75424ee6b287f3a902a0a3c243a392d034086d040b07c99994be8.

| DOS entry | Packed bytes | Compared unpacked bytes | Unpacked CRT entry | CRT DS=SS | Stop after DS setup |
|---|---:|---:|---|---|---|
|1.0|115152|154448|219b:0010|3360|219b:00ab|
|1.1|115768|155552|21bc:0018|3395|21bc:00b3|
|1.2|115856|155632|21c2:0018|339b|21c2:00b3|
|1.5|115904|170672|21c7:001c|374a|21c7:00b7|
|1.7|116068|170848|21d1:0018|3754|21d1:00b3|
|1.8|116556|171296|21ea:001c|376d|21ea:00b7|
|1.9|116556|171296|21ea:001c|376d|21ea:00b7|

All 1,149,744 compared bytes match, including duplicate1.8/1.9 coverage. This is whole compared payload equality, not just selected instructions. Independent paths: (A) execute original packed EXE and its stub; (B) apply reconstruction MZ relocation words mathematically to its payload. No unpacking callees or instructions mocked, no interrupts occurred during unpacking. Initial loading base1000, PSP segment0ff0, initial DS/ES=PSP, original MZ CS/IP/SS/SP. Unicorn2.1.4, 2MiB RAM. Stop at reconstructed CRT entry, before first instruction there. Primary files, raw unpacked outputs, scripts and unpack.json are included.

## Packing and correction of prior interpretation
Confirmed: original MZ relocation count is zero in every source file. V1.9 original entry2b6f:0010 runs a backwards decoder and compact relocation routine, then transfers to21ea:001c. At original file offset1b8fe its stub data contains bytes52 42 (RB); the stub also contains `Packed file is corrupt`. Inferred/Medium: this is an EXEPACK-family format. Naming the exact packer version is unnecessary for the confirmed behavior and remains Unknown.

Pass51's description of unrelocated far-call words was a valid observation of the supplied database state, but the root cause is now established more precisely: that database models the packed, pre-execution image. Zero original MZ relocations are intentional, not evidence that the DOS loader omitted a nonzero original relocation table. The unpacking stub applies the runtime relocations itself. Pass52's narrowly checked call-word patches match this runtime model; pass53 validates the reconstruction payload they were based on. That partial patched database still does not contain the entire unpacked runtime image or correct DATA layout.

## CRT setup experiment
After unpacking, continue original CRT code with PSP:0002=9000h as a synthetic memory-top value. Only INT21/AH30 (DOS version: return AX1606) and INT21/AH4a (resize: clear carry) are mocked. Stop at first instruction boundary where DS equals expected runtime DS. DS=SS holds for every image; all seven bootstrap traces contain exactly those two DOS calls. This is a controlled startup experiment, not full DOS emulation.

V1.9: CRT21ea:001c starts INT21 version query;21ea:0029 loads DI376d;21ea:003c loads SS from DI; by21ea:00b7 DS=SS=376d. At the unpack-to-CRT boundary DS/ES still equal PSP0ff0; do not confuse that transitional state with gameplay DS.

## Confidence and implementation outcome
High for original-source provenance, exact unpacked-payload equivalence, and startup DS under the stated DOS boundary responses. Unknown for full gameplay, hardware, timing or end-to-end 1:1 parity. No new project modification is made here. Next discriminating work: build a full unpacked Ghidra image with runtime-correct memory and DS, compare its initialized bytes to these original-stub outputs, then transfer only compatible existing annotations. Do not blanket-relocate or initialize the packed project's DATA region based solely on its current block names.
