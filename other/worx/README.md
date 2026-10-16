# WORX Toolkit 2.1 RE reference (16 October 2026)

All reconstructed **source code** is in [`../../worx`](../../worx/) ONLY:
5 `.cpp` files under `worx/src/` and 5 `.hpp` interfaces under
`worx/include/worx21/`. This folder is for **documentation, tests and static
evidence** only.

This is **original-byte-audited, partial clean-room C++17 RE code** for
Nitemare DOS 2.0's embedded Mystic Software WORX 2.1, **not original vendor
source**, and **not complete audio/IRQ/ISA/DMA parity**. Source bundle:
`WORX21_RE_MAX_v013.zip` archived in the project's research library.

Static reference: 82 original `AH=00h..51h` dispatch slots;
3 are zero **in the initial image only**; v0.13 audit counts 41/79
nonzero API branches with contracts, 38 not fully transitive reconstructed.
The older v0.11 audit counted 37 strictly verified standalone leaf bodies;
these are different accounting dimensions, not contradictory numbers.

Crucial 1:1 edge cases in `WORX21_FINDINGS_v013_SK.md`:
- `49BC` double DMA count read, signed JLE/JGE branches after unsigned gates;
- `4476` MIDI scheduler extra fall-through track call, even when count zero;
- `45F9` 32-bit VLQ has no 4-byte limit; 16-bit `DI` wraps;
- `455D` FF51 tempo skips a single length byte; x86 `DIV` can trap;
- PCM sample arithmetic uses wraparound, not saturation.

Standalone C++ test (from repository root):

```sh
cmake -S other/worx -B build-worx
cmake --build build-worx
ctest --test-dir build-worx --output-on-failure
```

With your own **unpacked** DOS v2.0 EXE, run the SHA-bound auditor
(`tools/audit_audio_inner_v013.py`) from `other/worx/` using the format
specified by the tool. Original proprietary files are intentionally not shipped.

`n3d_v20_int63_dispatch.json` pins the 82 dispatch entries; JSON and audit
scripts belong to `other/worx`, not `worx`. `WORX.H` and `TCWORXL.LIB`
obtained from Xargon/Kiloblaster are from WORX **2.01**, *not proven original*
WORX 2.1 SDK sources; do not put them into `worx/`.
