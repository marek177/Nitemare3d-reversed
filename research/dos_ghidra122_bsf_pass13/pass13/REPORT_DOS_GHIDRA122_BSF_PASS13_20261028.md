# BSF pass13 — original seek ABI and ignored seek failure

## Finding
Confirmed across six distinct DOS EXEs: CRT seek returns a 32-bit position in DX:AX or ffffffff on failure, with handle word, offset dword and origin word on the far-call stack. The resource loader ignores that result. When injected DOS seek fails, it reads from the unchanged old file position, appends NUL, closes and decodes the requested length, returning the buffer as on success.

## Evidence
1074 passing targeted executions:1008 original CRT seek matrix cases and66 resource loader integration cases. These execute original code from reconstructed EXEs with Ghidra12.2 instruction exports. No new Ghidra reanalysis, signature edit or decompiler coverage increase is claimed.

Matrix: origin0/1/2 x offset00000000,00000001,0000ffff,00010000,7fffffff,80000000,ffffffff x negative-offset guard0/1 x handle5/25 (max20) x injected DOS error0/5, across6 images. DOS INT21 AH42 is the only hooked dependency. Simulated initial position100,file length1000; signed offsets are applied by the DOS model, negative targets fail, nonnegative32-bit positions are accepted. These are controlled OS semantics, not evidence that a real DOS/filesystem supports every large position. Checks: DX:AX, final position, flag bit change, far return and stack. All DOS requests are recorded, including guard query/restore paths.

Loader suite retains the prior60 resource tests and adds one seek-error test/build. Original full loader and original decoder execute; original seek now executes rather than being bypassed. Open/malloc/read/close are simulated; fatal dependency branches stop before executing the fatal callee. Original seek calls mocked DOS INT21 AH42. Open returns handle3, initial position0, allocated buffer5000:0200 prefilleda5. Seek error asks for offset54,length54 but DOS returns carry/error5 and preserves position0. Mocked read therefore supplies bytes0..53; original decoder produces decoded header bytes, not the requested bytes54..107. All6 return normal buffer5000:0200 with NUL at+54, correct far return/stack and intact guards. Tests assert source-dependent decoded bytes and call order.

V1.9 seek21ea:1bda, actual DOS seek21ea:1c4f, global negative-offset guardDS:232e, handle flagsDS:2128+handle, maximum handlesDS:2126. Exact per-build entries/hashes and each trace are in seek_matrix.json; loader traces are in loader_seek_emulation.json.

## Behavior model
CRT seek arguments at entry SP+4 handle,SP+6 offset low/high,SP+10 origin. Successful DOS seek returns DX:AX and clears handle flag bit02 (the logical/text EOF marker observed in earlier text-read tests). Failed seek returns DX:AX=ffffffff and preserves that flag. Out-of-range handle fails before DOS seek. The FILE EOF bit10 is a separate field and is not changed by this routine.

When the guard global is nonzero and offset has signed bit31 set: origin0 is rejected before DOS; origin1 queries current position and rejects a negative resulting target; origin2 queries current position and end, and restores the saved position before rejecting a negative resulting target. These observations apply to tested origins0..2 and deterministic successful query requests. IO errors specifically on second query or restore were not injected separately. With guard0, signed offsets are passed directly to DOS. Positive offsets are not rejected solely because the resulting position exceeds signed31-bit range in the simulated interface.

Loader sequence remains open -> allocate(L+1 mod65536) -> seek(handle,offset,0) -> read(buffer,L) -> buffer[L]=0 -> close -> decode -> return saved buffer. Neither seek nor read return is checked. The allocation overflow atL=ffff and actual allocation internals are still untested. Real BSF resource blocks used in66 integration cases come from the prior hash-identified inputs.

## Classification and limits
Confirmed/High for original seek ABI, tested guard branches and flag updates under stated simulated DOS behavior. Confirmed/High for loader continuation after seek error with original decoder and mocked I/O. Unknown: real DOS seek quirks/filesystem limits, invalid origins, independently failing query/restore, loader heap allocator, actual short-read/error cleanup and caller ownership. No DOSBox or whole-game1:1 parity test. Supplied1.8/1.9 still share one image.

## Reproduce and next step
Run `/usr/bin/python3 scripts/verify_seek_matrix.py` and `/usr/bin/python3 scripts/verify_bsf_loader_seek.py` with Unicorn. Archive contains EXEs, Ghidra instruction exports, pass7 specs, BSF metadata and BSF files required by the scripts. Next: loader allocation ABI/ffff length overflow and BSF return-buffer ownership at callers.
