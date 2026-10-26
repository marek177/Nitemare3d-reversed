# Operand-size semantic correction across DOS and Win16 evidence

While classifying an unobserved RNG caller,04C7:0C3F byte99 was printed as `cdq` by Capstone5.0.9 in16-bit mode. iced-x861.21.0 formats it as `cwd`. A four-case reproduction distinguishes98,99,6698,6699. Intel's [instruction reference](https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-software-developer-vol-2a-manual.pdf) specifies operand-size-dependent sign extension:16-bit98 reads AL and writes AX;16-bit99 reads AX and writes DX. With66 the corresponding destinations are EAX and EDX. These instructions do not change flags. Register effects are architectural dependencies, not whole-function liveness.

The audit rechecks all13 binary source hashes and matches every affected encoded instruction against its original file bytes, including NE source offsets. It corrects3922 inherited instruction references at3787 unique binary:PCs across1786 CFG files. Classes:861 `cwde` labels become `cbw`;2673 `cdq` labels become `cwd`;388 prefixed `cdq` entries retain their label but remove the erroneous EAX write dependency. All original Capstone observations remain in `raw_capstone_observation` beside the corrected fields. No binary, boundary, edge or instruction length changes. NE loader limitations remain in force; this byte-local correction does not validate all relocation semantics.

The previous zero-disagreement count checked lengths against iced and text against inherited Capstone output. It never proved agreement of independent semantic effects. This finding is an explicit limitation of those checks. Global semantic decoder agreement remains UNPROVEN; other implicit-register instructions require audit.

Validation checks all3922 corrected entries, retained raw observations and1786 file hashes, four operand-width cases and an unrelated instruction rejection. The evidence generator now applies the same rule when rebuilding. The public read-only audit defaults to no writes; use `--apply` only to update derived CFG metadata. Raw original assets and binaries are not published.

The initial eleven RNG caller gate classifications remain unfinished: this correction took priority because their arithmetic interpretation depends on the width of sign extension.

## Static follow-up, 2026-10-26

The eleven run_f-unobserved sites now have bounded byte-supported functional records in [RNG_unobserved_function_records.md](RNG_unobserved_function_records.md), with five decoded selector tables, synthetic CPU regressions and explicit remaining runtime activation gaps. The earlier unfinished-classification statement describes the preceding checkpoint. Original-game runtime coverage remains 11/22 direct sites in run_f; no global coverage or parity closure is claimed.
