# Runtime-correct DOS analysis project

Open project/N3D_Runtime54.gpr next to project/N3D_Runtime54.rep. Programs are under /inputs. DOS18.exe also represents supplied DOS1.9: the original imported EXE hashes and original-stub outputs are identical. There are six distinct program images, not seven independent versions.

Source chain: original packed EXE stored in uploaded Ghidra database -> execute original unpacking/relocation stub (pass53) -> byte-verified reconstruction MZ -> Ghidra MZ loader -> bytewise comparison against original-stub output -> runtime DS context -> analysis. The runtime project is separate from the user's packed project and the partial pass52 repair.

The DS value is a static analysis assumption for normal runtime code. It is not a claim that DS holds this value on every instruction path: at unpack-to-CRT transfer DS is the PSP, and startup or specialized routines may change it. Do not interpret a globally configured DS as a proved per-function preservation contract. Autoanalysis may propagate more specific contexts, which the focused verification checks at dispatcher/cache/fallback entries.

No labels, comments or signatures were copied from the packed user project. The cache/fallback return and argument interfaces were explicitly set from original-instruction evidence: DX:AX packed32 return and resource_id u16 at stack+4. Preserve it for comparison. This avoids treating annotations created against different bytes as verified facts. Existing pass47/pass50/pass51 addresses are used only as audit/decompilation targets, not as evidence that every automatically created function is correct.

Decompiler output is diagnostic. Successful generation is not semantic verification. The logs retain p-code/disassembly warnings, analysis timeouts if any, and the initial pre-script error that was corrected before the final verification. Entire runtime memory equality is checked again after saving/reopening.
