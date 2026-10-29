# Pass57 — integrated cache/XMS state transitions and corrected Ghidra status ABI

## Finding
Confirmed, High: original cache code stamps the selected cache block only after the rounded XMS helper returns without entering its fatal path. A repeat request hits that block without a second driver call or timestamp refresh. On driver AX0/BL80, execution reaches the fatal call before the cache header is updated. Six XMS wrapper return interfaces are corrected in a separate Ghidra12.2 project copy, restoring the decompiled signed-status condition.

## Scope and evidence
576 passing integrated scenarios: 6 distinct images x4 lengths x4 nonpositive offsets x3 driver outcomes x2 initial cache states. Original cache, rounded-transfer helper and driver wrapper all execute. Only the indirect XMS driver boundary is simulated; it copies a deterministic synthetic byte pattern on nonzero AX and does not copy on AX0. Fatal handling stops at handler entry. No real XMS manager, asset bounds or audio is modeled. Supplied1.8/1.9 are identical EXE images, represented once by DOS18.exe.

Primary locations and instruction hashes: pass50/evidence/cache.json and pass56/evidence/xms.json. V1.9 cache1767:068a–0788, transfer1767:0356–03d3, XMS wrapper1767:0804–082b. Exact tested driver descriptors, returns and outcomes are in chain.json. The prior artifacts are included as reproduction dependencies.

## Confirmed state sequence
| Driver boundary outcome on cache miss | Payload action in synthetic driver | Original cache result | Second request |
|---|---|---|---|
|AX1,BL0|Copy rounded byte count|Header becomes timestamp100, ID66; returns payload pointer|Cache hit, no new driver call|
|AX0,BL80|No copy|Fatal call reached; all cache blocks and headers unchanged|Not executed|
|AX0,BL7f|No copy|Header still becomes timestamp100, ID66; old payload retained|Cache hit returns retained payload|

The BL7f row is a synthetic status probe, not evidence of a real XMS error code or reachable corrupt audio. It verifies the exact sign-test behavior established in pass56. No real-driver failure classification is inferred beyond the tested machine-code branch.

For an initial hit in slot3, no driver call occurs for any injected status settings; all four blocks stay byte-identical. In every returning scenario, a second request advances the global clock from100 to101, yet the cache block timestamp remains its original value (100 on a miss filled by the first call, or13 for the initial slot3 hit). Return pointer, restored DS, CS and SP are asserted. Unselected slots and untouched payload tails remain byte-identical.

## Transfer checks
Lengths1,1024,1025,8192 yield rounded lengths1024,1024,2048,8192. Source offsets0,-123,-65536,INT_MIN yield unsigned magnitudes0,123,65536,80000000h in the driver descriptor. The INT_MIN case preserves two's-complement wrap and is a synthetic range probe, not proof of a valid allocation that large.

Four cache buffers are nonoverlapping, each with6-byte header and8192-byte payload. The descriptor names the selected payload pointer in conventional memory, source handle1234 and destination handle0. The deterministic copy byte at positioni is `((source_magnitude+i)*17+3)&255`; this is a test fixture, not a recovered sound encoding. Full rounded copied regions and unchanged tails are compared. There are96 successful miss/copy scenarios,96 fatal misses,96 synthetic low-error misses and288 initial-hit scenarios.

## Ghidra interface repair
Working project: copy of pass54/project/N3D_Runtime54, stored separately under this artifact's project/ directory. CorrectXmsAbi.java changes only the six XMS move-wrapper interfaces:
- explicit32-bit unsigned result in DX:2,AX:2;
- one packed far descriptor argument,4 bytes at entry stack+4;
- custom variable storage, avoiding the compiler model's implicit return-buffer inference.

Instruction execution from pass56 independently established this register contract. A fresh read-only reopen verifies each interface and every runtime payload byte against pass53's original-unpacker outputs:978448 bytes total, no differences. Twelve diagnostic C outputs are regenerated (wrapper and rounded caller for each image). Before in V1.9 the caller incorrectly tested a stale arithmetic variable. After the repair it contains:
```
dVar3 = FUN_1767_0804(CONCAT22(uVar2,0x200));
if ((long)dVar3 < 0) {
    FUN_1fb7_0000();
}
```
This signed32 comparison is equivalent to the original signed-DX comparison because DX is the high word of the packed result. The repaired program bytes are unchanged. Dynamic ES scratch-memory writes are still misleadingly aliased to static DS strings in generated C; this pass does not repair that separate decompiler issue or certify all generated C semantics. No new function-count completeness claim is made.

## Outcome and next test
High confidence in the integrated local cache/header ordering, repeat-hit behavior, descriptor arguments and corrected XMS status ABI. Unknown: actual XMS allocation contents/bounds, source-offset producer, resident driver behavior, fatal-handler internals and full audio/game1:1 parity. Next: trace the producer that writes negative source offsets and DS:3504, then verify allocation and rounded resource packing against actual SND.DAT records. Keep the synthetic low-error case separate from reachable gameplay claims.
