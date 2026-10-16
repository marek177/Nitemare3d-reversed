# Nitemare 3-D — WORX Toolkit 2.1 RE source and evidence

**Current statically verified research snapshot: v0.15 (16 October 2026).**
This is partial, instruction-backed clean-room C++17, **not** the Mystic
Software original source tree and **not** full IRQ/ISA/PCM/MIDI parity.

All reconstructed WORX `.cpp`/`.hpp` files are exclusively in
[`../../worx`](../../worx/). The present `other/worx` directory contains
ONLY CMake build, tests, static verifiers, reports and evidence metadata.
Neither proprietary Nitemare EXEs nor commercial WORX 2.01/2.1 SDK libraries
are distributed. In particular, `WORX.H` / `TCWORXL.LIB` from Xargon and
KiloBlaster are **WORX 2.01**, not verified 2.1 vendor source code.

## Verified steps

- [v0.13 inner audio](WORX21_FINDINGS_v013_SK.md): DMA count, MIDI tick,
  32-bit VLQ, FF51 tempo, PCM primitives and PIT rules.
- [v0.14 deep audio](WORX21_FINDINGS_v014_SK.md): MIDI gate/EOT, XMS call
  packet, two streaming modes, cross-version DOS 1.9 versus 2.0.
- [v0.15 MIDI event pipeline](WORX21_FINDINGS_v015_SK.md): 44EE..4552,
  running status, 3A4D prologue, MIDI data register survival, CALL 3A4D→45F9,
  FF meta integration and build-specific original-byte verification.
- [Remaining exact gaps](WORX21_UNKNOWN_TO_100_SK.md): hardware/driver
  callbacks, full device handlers, nested call graph, IRQ, timing, reentry.

**Accounting remains 41/79 nonzero INT63 handler contracts and 38 open,
with three additional initial-image zero slots; local subcontracts are not
full 79-handler behavioral parity.**

## Build, test and byte-audit

```sh
cmake -S other/worx -B build-worx
cmake --build build-worx --config Release
ctest --test-dir build-worx -C Release --output-on-failure
```

This runs nine CTest groups (C++ contracts and bundled Python synthetic,
evidence-only tests). Without original EXEs the optional byte-verification
tests skip direct source-image checks, **not** an assertion that the live binary
was verified on the CI runner.

For original-byte audit on your own legal copies of fully unpacked DOS 1.9
and 2.0, run from repository root:

```sh
python other/worx/tools/audit_midi_events_v015.py \
  /private/N3D_DOS_v1.9_IDA.EXE /private/N3D_DOS_v2.0_IDA.EXE
```

For the complete tests with both originals, set `WORX_N3D_V19_EXE` and
`WORX_N3D_V20_EXE` before invoking CTest; no proprietary input is copied
into the repo or generated evidence directory.
