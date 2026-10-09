# v0.28 — Independent source cross-check and reproducible BSF/DEMO probes

Date: 2026-10-09  
Repository: `marek177/Nitemare3d-reversed`

This is an **additive, evidence-scoped update** to v0.27, not a claim that the
original source code has been discovered or that behavioral/pixel parity is
complete. No original game executables, sound, artwork, maps, BSF manuals, or
external source files are embedded in this change.

## Source snapshots and attribution

1. **Independent DOS shareware v2.0 documentation**, published 2026-08-27:
   [vs-sr-dev/pc-nitemare3d-doc](https://github.com/vs-sr-dev/pc-nitemare3d-doc),
   especially [01-executable](https://github.com/vs-sr-dev/pc-nitemare3d-doc/blob/main/docs/01-executable.md),
   [07-demo](https://github.com/vs-sr-dev/pc-nitemare3d-doc/blob/main/docs/07-demo-config-and-saves.md),
   [08-BSF](https://github.com/vs-sr-dev/pc-nitemare3d-doc/blob/main/docs/08-branding-and-the-bsf.md),
   [10-unused content](https://github.com/vs-sr-dev/pc-nitemare3d-doc/blob/main/docs/10-easter-eggs-and-leftovers.md);
   commits [d3a1975](https://github.com/vs-sr-dev/pc-nitemare3d-doc/commit/d3a1975ea190ecc621f63c63c4bed6e720f627e2) and
   [049236e](https://github.com/vs-sr-dev/pc-nitemare3d-doc/commit/049236e3ff8ea4eb481c90636f0228eefd120c9f).
2. **Independent Windows 11 x64 C++20 rewrite**, first public commit
   2026-10-08: [mfoldes/nitemare3d-win64](https://github.com/mfoldes/nitemare3d-win64),
   commit [63c6100](https://github.com/mfoldes/nitemare3d-win64/commit/63c6100a5a93a7b77a2cce0e04ed3cd7969801c6).
   Specific comparison sources:
   [src/core/recordings.cpp](https://github.com/mfoldes/nitemare3d-win64/blob/master/src/core/recordings.cpp),
   [src/game/demo.cpp](https://github.com/mfoldes/nitemare3d-win64/blob/master/src/game/demo.cpp),
   [README.md](https://github.com/mfoldes/nitemare3d-win64/blob/master/README.md).
3. **Our pre-existing primary evidence**, notably
   [BSF_PROTECTION_RE_v5.md](BSF_PROTECTION_RE_v5.md),
   [DEMO_FORMAT_RE.md](DEMO_FORMAT_RE.md) and
   [V027_REMAX_PROJECTILE_LIFECYCLE.md](V027_REMAX_PROJECTILE_LIFECYCLE.md).

External findings are **reported external evidence**, not promoted to
`VERIFIED_EXE`/`VERIFIED_DATA` for our local binaries until reproduced. The
Windows 11 rewrite is a third-party *implementation*, not David P. Gray's
original source code or a runtime oracle with established 1:1 parity.

## Comparison ledger

| Topic | Evidence / scope | Status for our reconstruction |
|---|---|---|
| `NITE3D.BSF`: 52-byte key, 54-byte ciphertext-XOR-zero header, three independent key-phase resets | Independent DOS v2.0 report; already recovered across DOS/Win16 in our BSF v5 | **Already known**; add executable verification tool |
| BSF file-integrity seed `0x7B`; DOS checks EXE and shareware `MAP.1`; Win16 does not enforce EXE binding | Own executable-backed BSF v5 | **Existing confirmed, build-scoped**; now testable |
| DOS v2.0 packed by DIET; toolkit/CRT strings suggest Microsoft C 7.0 and WORX Toolkit 2.1 | External unpacked DOS v2.0 report | **External only** until cross-checked on our exact binary |
| DOS startup `N3D.EXE -o` creates `DEBUG.TXT`; `-t`, `-x`, `-p`, `-q`, `-s` documented | External DOS v2.0 `TECHNOTE.TXT`/EXE analysis | **Useful independent lead**; `-o` logs startup, *not* full per-tick function calls |
| Embedded manual credits: David P. Gray, Denise M. Tyler, David B. Schultz, Christine S. Rose | External decrypted DOS v2.0 BSF/manual | **Externally reported**; do not paste the copyrighted manual |
| Manual `%C<n>%`: direct palette index; `%o<n>%`: image id `n+256` | External DOS manual/parser | **External interpretation**; image-reference scanner implemented below |
| DOS v2.0 image 39: unreachable artist-note placeholder; tail IDs 505–511: late HUD/hit-detector assets | External IMG.1 mapping | **External finding**; independently reproduce on owned IMG/MAP data before elevating |
| DOS `MAP.1` blocks 2 and 10 have same wall-plane layout | External scan; aligns with our E1M3/E1M11 shared-geometry fingerprint | **Independent cross-check**, not a newly closed runtime algorithm |
| Independent native Win11 rewrite offers C++20 core, saves/audio/map browser and tests | External repo first commit 2026-10-08 | **Comparison target only**: trilogy parity and clean-machine deployment explicitly not verified |

### Caution on BSF executable addresses

The external DOS v2.0 decoder location `10CA:01B2` and our DOS v1.9
`0FB7:01A6` refer to different executable builds and address
representations. They are **not interchangeable**. Resolve original binary
identity, load segment and unpacked image before recording any cross-build
equivalence. Our older Win16 BSF notes further establish that DOS/Win16
integrity policies differ.

### DEMO.n framing: important build-scoped distinction

The common file framing is **six header bytes followed by eight-byte
records**, with a 32-bit tick/timestamp at record offset `+4`.

- Our executable-backed **Win16 v1.10** recording path and
  [src/formats/DemoFile.cpp](../src/formats/DemoFile.cpp) read each record as
  `u8 event, u16 input_mask, u8 pad, u32 render_generation`. Supplied
  Windows files have header `(10, 5, 20)`; our analysis associates the first
  two header fields with calibrated move/turn increments, not with a start pose.
- The independent DOS v2.0 shareware report observes header **`(15, 7, 30)`**
  and `DEMO.1` size **2,206** = `6 + 275 * 8`. It presents record bytes
  `+0..+3` as **two u16 input words**, while leaving their gameplay semantics
  unresolved.
- The new [mfoldes Windows x64 rewrite](https://github.com/mfoldes/nitemare3d-win64/blob/master/src/core/recordings.cpp)
  also parses `u8 event + u16 mask + u8 pad + u32 tick` and accepts the
  `(10,5,20)` header for its **specific registered Windows data set**.
  This agrees with our Win16 interpretation; it does not prove the DOS v2.0
  semantic layout.

**Do not silently combine these DEMO data sets** or assume that `(15,7,30)`
encodes a player spawn. The two byte interpretations overlap mechanically:
a word at `+0` consists of `event` and the low mask byte under the Win16 view.
Trace the actual DOS v2.0 writer and reader to decide whether the
interpretation is genuinely different. Keep our Win16 parser unchanged until
that evidence exists.

## New original tools (read only)

### 1. [tools/n3d_bsf_audit.py](../tools/n3d_bsf_audit.py)

An independently authored Python 3 verifier; no code is copied from external
repositories. It decodes the 54-byte header, respects the XOR-key restart
per chunk, checks spans/overlaps, prints local CP437 text or IMG reference IDs,
and validates selected DOS/Win16 checksum policy without modifying the input.

~~~sh
python tools/n3d_bsf_audit.py info "PATH_TO_YOUR_DOS_INSTALL" --json
python tools/n3d_bsf_audit.py verify "PATH_TO_YOUR_DOS_INSTALL" --platform dos
python tools/n3d_bsf_audit.py verify "PATH_TO_YOUR_WIN16_INSTALL" --platform win16
python tools/n3d_bsf_audit.py text "PATH_TO_YOUR_DOS_INSTALL" 1 --image-ids
~~~

**Win16 detail:** the original Win16 BSF loader checks the header XOR and
shareware `MAP.1`, not a `NITE3W.EXE` checksum. The tool explicitly avoids
imposing the DOS executable policy on Windows. Registered mode skips MAP.1.

### 2. [tools/n3d_demo_layout_probe.py](../tools/n3d_demo_layout_probe.py)

Prints both raw interpretations of the first four record bytes with the same
timestamp, and reports header words, record counts and nonzero Win16 padding.
It **does not** auto-detect a gameplay semantic layout from length alone.

~~~sh
python tools/n3d_demo_layout_probe.py "PATH_TO_YOUR_DOS_INSTALL/DEMO.1" --json --head 12
python tools/n3d_demo_layout_probe.py "PATH_TO_YOUR_WIN16_INSTALL/DEMO.1" --json --head 12
~~~

## Tests, reproducibility and current limitations

~~~sh
python -m unittest discover -s tests -p "test_bsf_audit.py" -v
python -m unittest discover -s tests -p "test_demo_layout_probe.py" -v
~~~

The tests construct small synthetic binary fixtures, including successful
checks, key-phase resets, bad-header XOR, overlapping/out-of-bounds chunks,
a DOS executable mismatch, conditional shareware MAP validation, and two
DEMO byte views. They require **no original copyrighted game data**.

**Evidence boundary:** Synthetic test results verify tool internal consistency
but **not** original-runtime compatibility. Full runtime tests on each
fingerprinted DOS/Win16 build and exhaustive cross-build replay remain open.
Do not change the project-level 1:1 completion percentage on this evidence.

## Next high-value closure steps

1. Compare the same real `NITE3D.BSF` and checksums against the original DOS
   and Win16 startup behavior; record exact executable SHA-256.
2. Record the first 8–12 raw DEMO records from independently fingerprinted
   DOS v2.0 and Win16 v1.10; trace DOS reader/writer byte offsets.
3. Reproduce IMG id 39 visibility/mapping and high-ID tail with owned
   IMG/MAP files; check edition differences.
4. Verify DOS `-o` `DEBUG.TXT` startup events in DOSBox-X; do not mistake them
   for frame-by-frame traces.
5. Continue **unclosed core** work: GUARD `+0B/+0C` writer XREFs, projectile
   `+0x0D` and pool reuse, OBJECT update ordering, RNG draw chronology,
   renderer edge rounding, and save/load side effects.

External information is evidence to investigate, not a substitute for original
EXE/asset/runtime capture or an excuse to promote OPEN hypotheses.
