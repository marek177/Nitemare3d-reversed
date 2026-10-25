# DOS 2.0 RNG state and direct caller census

This supplement follows the verified 229-call / 275-input first-EOF runtime checkpoint. It audits the hash-pinned unpacked DOS 2.0 image 5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3 and inherited instruction membership 9c3049681c852a3cf0c1ed66fc984f6c00d626459cc09be0029283156a927f30. Candidate function ownership remains inherited.

The read-only audit decodes 37531 unique segment:offset members, with zero failures. Independent iced-x86 instruction lengths agree with Capstone. Operand access classification is Capstone's, not a second independent memory-effect proof. There are six explicit absolute memory operands overlapping byte offsets24B8..24BB: two reads and four writes. The four write sites are11EE:31EC,11EE:31EF (seed setter),11EE:3213,11EE:3216 (RNG core). All use default DS. Offset equality alone does not prove runtime segment identity. The scan includes accesses beginning before the state if their byte width overlaps it.

There are 25 direct FAR edges to the two wrappers, setter and core:22 calls to RNG wrapper0FBA:01A0, one to seed1 wrapper0FBA:01A6, and the two wrapper-to-core/setter calls. The complete load image contains25 literal offset:segment byte sequences for these four targets; all overlap these inherited direct calls. No additional literal FAR pointer is observed for these exact four encodings. This does not cover aliased FAR addresses, relocated runtime data, dynamically constructed targets or near calls.

The measured run_f ledger observes11 of the22 direct RNG wrapper callsites. The other11 sites are 0201:0468, 04C7:09F6, 04C7:0C37, 083D:0490, 083D:049C, 083D:04AC, 083D:1698, 083D:16A7, 083D:18F2, 083D:1B3C, 0AEA:03D6. This identifies concrete next runtime coverage targets without asserting that any is unreachable or measuring whole-program coverage.

No immediate operand equal to24B8..24BB or indexed operand using exactly those displacements is observed in this membership. That is a narrow syntactic result. There are2654 indexed explicit-write operands; any whose effective address can alias the RNG bytes needs value-domain analysis. String/implicit stores, external/interrupt/DOS/BIOS writes, unenumerated code and other versions remain open. Thus global writer/indirect closure and every-IRQ trace are NOT achieved.

Reproduce with Python plus Capstone and iced-x86:

`python audit_rng_state_references.py <hash-pinned-unpacked.exe> <nite3d20/functions.json> <output-directory>`

The output records source hashes, exact scope, explicit xrefs, direct edges, encoded pointer occurrences and open domains. No game binary or original asset is included in this supplement.
