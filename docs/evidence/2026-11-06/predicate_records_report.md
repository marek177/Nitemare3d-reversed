# Bounded lookup/predicate function records and M continuation — 2026-11-06

Two existing Function Analysis Records now contain byte-matched local algorithms, ABI, stack, memory dependencies, FLAGS, callers, evidence scope and next tests. Their whole-function boundary status remains UNKNOWN; neither is labelled completely analyzed. The matched inherited memberships contain38 and14 instructions respectively.

0000:0000 scans stride18 records at21FD:3076, bounded by a reread signed count at21FD:0000, for exact offset/segment words at+4/+6. The found path returns DX:AX and changes DS to SS. FAR representation aliases are not normalized. The missing-key path passes near string offset0042 (“Door not in map”) to0FBA:000C; cleanup, formatter, termination, mutation and all error-path effects are not closed.

0000:01E0 returns AL1 iff record.word+8 is0 or4. AH is preserved; it is not a16-bit AX boolean contract. BX/ES receive the pointer and CX receives the word. Local return FLAGS are CF0/PF1/ZF1/SF0/OF0; AF is excluded. An exhaustive original-byte CPU test covers all65536 words with AH=A5 fixture and alternatingDF, verifies FAR return, preserved registers, and exactly one saved-BP stack write. These are SYNTHETIC_CPU_ONLY cases with a valid pointer/stack and no IRQs, not original-game invocation evidence. The test does not resolve gameplay names for state0/4.

The inherited callgraph's explicit inbound edges are byte checked: frame categories are {'PUSH CS then NEAR CALL; FAR-compatible return frame': 3, 'FAR CALL': 11}. PUSH CS followed by a NEAR CALL supplies a FAR-compatible return frame; treating these solely as ordinary NEAR ABI would be wrong. Unknown pointer/alternate callers and global ownership remain open.

The live original M search separately advances counter67→384 over a requested300-second window. All eleven exact targets remain enabled; no target invocation is observed. Endpoint RNG1 does not prove zero global RNG calls. The process is stopped at revision75, no pending RNG return. Inputs and writes retain the prior file-availability/BIOS queue fixture scope.

The original requested goal attachment is now preserved verbatim in this local supplement, SHA256b86d099e25aeb7ad3fee9bda04ef14b4905262d824173f8b9177f32394cfbad3. Its full DOS/Win16/function/IRQ/render/parity requirements remain in force. No P0 gate or full-goal completion is claimed. Historical archives are unchanged.
