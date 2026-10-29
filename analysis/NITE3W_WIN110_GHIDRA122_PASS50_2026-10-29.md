# Win110 pass50 — three database boundary differences resolved by native evidence

## Finding
Confirmed, High: uploaded database differences at3C3D,4E24,59DC are analysis-boundary/flow issues, not newly discovered binary variants. This audit uses Ghidra12.2 read-only extraction, original EXE bytes, native baseline48 instructions, references, and the CS jump table. No whole-game runtime claim or automatic merge.

## Evidence
|Status|Observation|Location|Confidence|
|---|---|---|---|
|Confirmed|Uploaded3C3D body spans3C3D..3CB6, swallowing separate3C80 lookup|Uploaded body export|High|
|Confirmed|Uploaded3C7F instruction008CD890 consumes valid3C80 entry bytes|Encoding comparison, original EXE|High|
|Confirmed|Baseline3C80 starts8CD8 MOV AX,DS and has direct calls from3C48 and3CCD|Native listing and refs|High|
|Confirmed|Uploaded4E24 body has only4E24..4E81 plus5300..530A|Uploaded body export|High|
|Confirmed|Original4E7D dispatches through8 CS word targets at4E14|EXE table and native JMP|High|
|Confirmed|Original59B8 opcodeE9 displacement0085 targets5A40: JMP, not CALL|EXE file baseE8A0+59B8|High|
|Confirmed|Uploaded reference marks59B8 asUNCONDITIONAL_CALL; baseline marksJUMP|Independent reference exports|High|

## Behavior model
3C3D calls fatal Windows services through3C7A. The uploaded fallthrough disassembly begins at3C7F padding and crosses the called lookup entry3C80, producing a false ADD instruction. Baseline bounds3C3D through3C7E and separately decodes3C80. This validates the existing correction rather than introducing a new game mechanic. Even baseline decompiledC may still show an assumed external return flowing into following bytes; a bounded function body alone is not proof the external nonreturn property or decompiler output is correct. Do not use that C as executable specification without control-flow review.

4E24 has eight original table targets4E82,4E8D,4EA1,4ED5,4F01,4F09,4F32,4F64. Uploaded body excludes all eight starts because its indirect dispatch has not recovered them. Baseline includes the recovered state machine; its1057 body-byte count versus105 in uploaded DB is not proof of more executable bytes in the binary. State semantics and full formatted-output ABI remain separately scoped.

59DC uploaded body ends5A3F and splits5A40..5A4D into a function. Original5A1F branches there conditionally;5902 also reaches it with the originalE9 JMP at59B8. Shared tail loadsAX fromBP-4 minusBP-6, restoresSP fromBP-A,popsSI/DI,then jumps3D41. The uploaded CALL reference at59B8 is inconsistent with native opcode and could distort caller/callee analysis. Shared-tail ownership by59DC in baseline is a database organization choice, not evidence that it has only one logical predecessor.

## Verification and limits
169 uploaded instruction rows compared with native baseline listing:168 have identical bytes at the same instruction start; one start3C7F is absent because baseline preserves padding and the correct3C80 entry. This count is not whole-function byte equivalence: changed instruction boundaries and unowned regions require separate interpretation. Native code input SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Uploaded archive SHA256c65b3da070a6b4de11e3cc29357bfedfbbd13b0a5a9dcc318ef4a4015175d199. Ghidra script exports bodies, instructions, and incoming references without program changes. No new emulator cases, Windows execution, or parity percentages.

## Implementation-ready findings
Use original JMP semantics at59B8. Keep3C80 as separately called lookup code, and never execute a reconstructedADD spanning its entry based on uploaded fallthrough. Recover all eight formatter dispatch edges before deriving the state-machine specification. Retain baseline48 rather than replacing it with the uploaded DB. Next: verify fatal API nonreturn metadata and a fresh decompilation, then audit the formatter helpers and shared-tail stack contracts with original execution. Overall confidence High for opcode/table/boundary findings; Unknown for full CRT ABI and actual fatal-service runtime behavior.
