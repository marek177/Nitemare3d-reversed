# Nitemare 3D — RE MAX NEXT: static indirect/OBJECT+18 closure pass

**Date:** 19 October 2026. **Scope:** SHA-bounded historical repository reports plus archived DOS 1.9 *linear ASM with opcode hex bytes* and Win16 v1.10 Ghidra C export. Read-only; no original gameplay runtime and no GitHub mutation.

## Provenance

- GitHub `marek177/Nitemare3d-reversed`, main tree `d507dcc17e606d27086cddde77f505c926d6d633` (accessed in this turn).
- DOS 1.9 disassembly export `N3D_DOS19_EXE_linear_all(1).asm` reconstructs contiguous 116044 bytes, offsets 00000–1C54B, SHA256 of *reconstructed slice* `1699be5dc6db8a18d1131c369eb0cbaffd7c748127d6170d6f8dc04a07fa81de`. This is **not the SHA256 of an original executable**. Original EXE not rematerialized or rerun in this pass.
- Win16 decompiler text `nite3w110.exe(20260927-130639).c`; not author source or original opcode verification.
- **Consistency check:** exact DOS1.9 RNG FAR-CALL opcode `9A 94 01 B7 0F` appears exactly 22 times at the 22 image offsets independently listed in the repository's hash-gated `N3D_DOS_rng_22_calls_each.csv`.
- Linear disassembly can turn inline tables/data into plausible instructions; counts below are **candidate decoded sites**, not exhaustive CFG-reachable instructions.

## 1. Indirect candidate census

- 40 FAR memory CALL; 10 NEAR memory CALL; 4 FAR memory JMP; 23 NEAR memory JMP. **77 total decoded candidates.**
- 6 XMS calls via `DS:350C`; 7 XMS calls via `CS:21CC`; 1 suspected INT09 interrupt chain; 23 indexed CS near jump tables; 1 CS dynamic FAR jump; **39 other** candidates.

### XMS family (pointer-origin local closure)

- `IMG:07DFD` calls `INT 2Fh` with AX=4300h to test XMS presence. `IMG:07E06` calls `INT 2Fh` with AX=4310h, then stores BX and ES to `DS:350C/350E` at `IMG:07E0B/07E0F`.
- This pointer is used at `07E26, 07E41, 07E62, 07E86, 07EA4, 07EC2`.
- Separate `IMG:15CB9–15CC3` uses AX=4310h/INT 2Fh, writing the returned BX/ES to `CS:21CC/21CE`; callsites `15CCA,15CD2,15D63,16761,18323,183C5,18494`.
- XMS documented contract `AX=4310h => ES:BX` driver entry; runtime address/provider and callback/hardware semantics remain environment-dependent. Reference: https://fd.lod.bz/rbil/interrup/memory/2f4310.html.

### Previous interrupt handler chain

At `IMG:06C07`, `PUSHF; CALL FAR [DS:3F52]` appears in an ISR ending in `IRET`. Beforehand the helper invoked with argument 9 at `IMG:06C43` returns AX:DX, which are saved at `IMG:06C4A/06C4D` to `DS:3F52/3F54`. Strong evidence of INT09 original-vector chaining, not a random gameplay dispatcher. Full helper and all aliases are still OPEN.

### Jump table sample: local 20-case damage dispatch

`IMG:085C6 JMP WORD PTR CS:[BX+020Ch]` indexes an inline 20-word table at `IMG:085CC–085F3`. The logical segment-to-image base is `083C0`. The decoded targets are in `dos19_damage_dispatch_table.csv`, class 0C–1F; class 15 dispatch reaches IMG:0861E (text callback / SI reset path). This cross-check corroborates the historical table evidence but not callback reachability.

## 2. OBJECT+0x18 local data flow

DOS1.9 `IMG:08592` is `MOV SI, WORD ES:[DI+18h]` in damage scalar; next `SUB SI,[DS:4550]`, `SHL SI,3`, RNG modulo 25, then class/difficulty selection. The source actor pointer is restored from argument stack BP+0A/0C.

DOS1.9 projector at `IMG:0B2D7` does SAR4 of `[BP-08]`, saves unbounded depth to `[BP-06]` at `0B2DE`. After cull checks and successful slot acquisition/fill `0B441..0B470`, the original FAR actor pointer reload `0B473/0B475` precedes `IMG:0B47A MOV WORD ES:[BX+18h],CX` where CX comes from `[BP-06]` at `0B477`. The selected slot rank may be capped independently; **the stored OBJECT depth is the pre-cap SAR4 value**.

Branches that exit the projector before slot allocation do not pass the observed local writer, so they preserve the prior depth *on that path*, barring other aliases. The following `IMG:0B47E...` class/flag check can update GUARD generation stamps only after the depth write.

Seven literal `ES:[reg+18h]` accesses were decoded. Four at `0549D/054A7/054C4/05728` are **one-byte proximity/status** accesses, not the WORD projection access. One at `1833E` is in a distinct XMS record path, which also accesses +28,+2C,+2E (beyond a 28-byte gameplay OBJECT). The two obvious WORD actor-path instructions are `08592` and `0B47A`; this is NOT an indirect/memcpy/bulk alias census.

Win16 v1.10 decomp independently shows `FUN_1010_cc7c` computing `local_8=local_a>>4` and writing `param_1+18h` only after allocation; the `FUN_1010_9fa2` damage producer uses `*(int*)(param_3+18h)-DAT_1048_53ee`. Renderer `FUN_1010_6348` calls the projector four times in separate traversal paths; wrapper `FUN_1010_80f8` calls the damage scalar.

## 3. Remaining proofs for static 100%

1. Normalize 77 decoded FF /2,/3,/4,/5 against *executable* CFG, eliminating any data false positives and resolving all remaining table/target ranges.
2. Build alias-aware pointer-provenance graphs for DS/ES/SS/CS, relocation entries and indirect callbacks, with version identity.
3. Complete all OBJECT+18 aliases (memcpy, struct reset, render cull, SAVE/LOAD, indirect writers) and DS:4550 producers; track the next hit after failed projection.
4. Prove legal actor eligibility/path for stale-depth projectile hit or a formal exclusion; do not infer gameplay occurrence from local geometry alone.
5. Reverify recovered opcode bytes using the full, SHA256-identified DOS 1.9/2.0 images, then compare Win16 1.10 actual NE bytes. No runtime claim is made.

**Status:** two XMS pointer origins locally classified; one INT09 chain strongly classified; exact 20-way class dispatch table and actor-projection-to-damage chain reproduced from an archived code dump. Whole-program graph closure, naturally reached stale-hit, exact timing, pixel zero-diff and a validated 100% core score remain OPEN.
