# Pass 52 — verified direct far-call relocation repair in supplied DOS project

## Finding
Confirmed, High: repaired 7,682 original direct far CALL segment operands in seven supplied DOS program entries. A fresh Ghidra12.2 read-only reopen independently checked persistence and decoded direct flow targets for every patch. Six distinct images account for 6,542 sites; supplied1.8/1.9 are duplicate images and must not be counted as independent behavioral evidence.

## Evidence
Working project: copy of pass51/project/11, ultimately from user upload ghidra-n3d(1).zip. Runtime: Ghidra12.2 PUBLIC20261016 and JDK25.0.2. Input reconstructed MZs: analysis/inputs/DOS*.exe. These reconstruction files are not byte-identical whole-file copies of the original import files. The uploaded project records different original EXE hashes. Therefore repair requires an exact local instruction match and a supporting MZ relocation record, not filenames or a whole-file identity assumption.

| Program | Patched and reopened flows | Existing function count retained | Unmapped relocation entries | Different values | Other entries excluded |
|---|---:|---:|---:|---:|---:|
| DOS1.0 |1074|509|130|3|432|
| DOS1.1 |1065|518|130|3|453|
| DOS1.2 |1076|531|130|3|446|
| DOS1.5 |1096|521|130|3|426|
| DOS1.7 |1091|527|130|3|433|
| DOS1.8 |1140|539|130|3|396|
| DOS1.9 |1140|539|130|3|396|

Per-site TSVs contain address, old/new segment and before/after decoded call. Separate verified TSVs report fresh-open checks. The scripts and execution logs are included. Confirmed/High: 7,682 checks for stored segment values and 7,682 checks for decoded flow targets. No new function recovery count or gameplay coverage is claimed.

## Repair contract
1. Locate a relocation word from the reconstruction MZ relocation table.
2. Require mapped/readable project memory and exact old word equality.
3. Require a defined five-byte instruction, relocation at instruction+3, opcode9a and all five bytes equal to the corresponding unrelocated reconstruction payload bytes.
4. Clear only this instruction code unit, write segment `(old+0x1000)&0xffff`, redisassemble only its original five-byte range without flow following.
5. Preserve existing function count; verify stored values after writing.
6. Save project. Reopen read-only and verify every patched segment plus decoded destination physical address `segment*16+offset`.

Example DOS1.1 1000:00f1: segment0f89 becomes1f89; the displayed call target changes from0000:f892 to1000:f892 (Ghidra's alias formatting). The checked property is physical destination equality, not the printed segment alias.

## Limits and corrections
Initial attempts required full reconstructed-payload equality before mutation and stopped before patching when that precondition failed. The layout includes unmapped regions and mismatching data outside the verified code windows. A subsequent audit also found unmapped relocation entries. These attempts are preserved in headless.log/audit.log; their script errors are intentional stopping evidence, not successful repair runs. Final repair.log and verify.log complete without script errors.

The broad claim 'all project relocations are repaired' would be false. Data-pointer relocations, other instruction forms, the three differing words per entry, and 130 unmapped entries per image remain unresolved. Whole-project DS/context correctness and indirect references are not established. Only exact-match direct far calls were patched. No reanalysis, renaming, decompilation parity, actual DOSBox execution or audio output was performed. DOS2.0/aliases and Win16 were not targets of this patch; Ghidra may save ordinary language-version metadata for DOS files it processes.

The original upload and pass51 project remain available unchanged by this pass. The deliverable contains a separate repaired project with all its original entries. Open project/11.gpr beside project/11.rep. The existing project owner metadata is the execution user's value inherited from pass51; Ghidra ownership checks may require changing ownership when copied to another account.

## Implementation-ready outcome and next test
The corrected direct calls can now support more reliable caller/callee tracing in these supplied databases. Semantic conclusions still require instruction/data validation. Next: resolve the DATA layout and DS context against initialized source bytes before repairing far pointers or trusting data xrefs; then resume sound-loader integration. Overall confidence High for patched call destinations, Unknown for remaining relocation classes and whole-game 1:1 parity.
