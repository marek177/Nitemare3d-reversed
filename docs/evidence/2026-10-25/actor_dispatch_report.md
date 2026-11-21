# Original actor-loop dispatch and object-write checkpoint

## Identity and trace scope

The unpacked DOS2 image is SHA2565ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3. Owned original clean_run_c/ses-1 was revalidated stopped at logical0D29:16EA, then continued naturally to04C7:12B6. No guest state was written. A4,571-event contiguous trace starts at12B6 and reaches12F4 before the10,000-event capacity. The final trace event names RETF at the breakpoint; its execution is proved separately by stepping it, not inferred from that event alone.

The loop processed33 actor records and returned to0BDE:0382. Entry/exit SP and the saved FAR return agree; the step reaches the saved caller and increases SP by4. Final state is stopped at1401:0382, revision197, with no active breakpoints. This is one natural invocation, not an adversarial mutation/ABA or all-state acceptance suite.

## Live-count iteration and pointer formation

At04C7:12B6 the local contract initializes SI=264E, DI=0 and data segment21FD (relocated to2A20 in this run). Initial signed comparison skips the loop if DS6276<=0. Each iteration reloads the actor's word at+8, multiplies by28 with16-bit wrap and adds6 to form the referenced object offset. It passes that object FAR pointer and the current actor FAR pointer to04C7:0D80. After return it advances SI by26 and DI by1, then reloads DS6276 and uses signed DI<count for the next iteration.

The loop therefore uses a live count, not a count cached at entry. The callee restores DS from SS at its shared12B0 epilogue, then restores SI/DI/BP and FAR returns. This restoration is part of this particular callee contract; it is not a general DOS calling-convention assumption. There is no local capacity or generation check in this loop span. Large counts, pointer wrap, slot mutation and reentrancy still need caller and runtime evidence.

The trace visits slots0..32 in order, executes the count-reload compare33 times, and every observed passed object offset matches its actor index using the formula above. Counts are33 in both snapshots and reference indices match before/after. These endpoint observations do not exclude transient changes or slot ABA.

## Bounded indirect target domain04C7:0D9A

The selector is actor byte+0B. The prefix clears AH, loads AL, compares unsigned AX<=21, doubles AX and uses CS:[BX+0DA0]. Out-of-range values go directly to12B0. The22 table words encode20 distinct local targets, including shared target12B0. Runtime table bytes exactly match the hash-pinned source.

This switch already has an inherited proof in switch_proofs.json; the current work independently revalidates the prefix/table and adds original runtime target evidence. The regenerated CFG had retained an unresolved edge for this site. It now has20 bounded encoded-target edges with a proof reference. This does not add a newly discovered site to the inherited2,425 unresolved-site count: that list excluded this already classified switch. The count is not a census of all indirect instructions. Table immutability over every execution and alternate entry paths are not globally proved.

All33 observed switch transfers match the indexed table target.31 use state7→04C7:0F4A and2 use state8→04C7:0F9A. The other states and default branch are not claimed as runtime-tested. The full dispatcher-body and nested state semantics remain incomplete.

## A concrete nested object mutation

Actor slot24 references object index169. Actor records have no endpoint byte differences in this invocation. One referenced object changes bytes at offsets03,0C and10. Effective addresses reconstructed from trace pre-instruction register deltas and the source decoder identify six explicit writes to that object's28-byte record:

| Sequence | Writer | Field | Operation |
|---|---|---|---|
|2994|04C7:05C1|10 word|ADD AX|
|2996|04C7:05C8|12 word|ADD CX|
|3043|04C7:062A|03 byte|INC|
|3057|04C7:0652|03 byte|MOV AL|
|3097|04C7:068A|0C word|MOV AX|
|3098|04C7:068E|0E word|MOV CX|

Field offsets in this table are hexadecimal. Local replay of these six ADD/INC/MOV effects using initial bytes and captured register operands exactly matches all28 final bytes. It preserves writes whose endpoint value is unchanged and the intermediate INC before the later MOV. The ledger records values and addresses; it is not a global writer closure, a full CPU emulator, or proof that transient alias/ABA cases cannot occur. No field gameplay name or visual effect is assigned without additional evidence.

## Remaining P0 work

Observe natural spawn/remove/reentrant and same-slot reuse paths, including changes to live count and actor/object indices; identify generation and alias invariants; extend all22 state branches and caller modes; pair the original mutation order with the remake under controlled input/tick state. GUARD damage/boss RNG, full OBJECT closure, timing and renderer acceptance remain OPEN. Win16 runtime and global function/indirect-flow closure remain required.

The local package contains raw traces, before/after arrays and RPC proofs. Public metadata includes the bounded domain, numeric observations and writer ledger only; no game binaries, assets, whole memory dumps or full original instruction trace are published.

