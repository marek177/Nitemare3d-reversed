# Nitemare 3-D Win16 1.10 — filename alias and `-p` prefix static closure

**Date:** 20 October 2026. **Scope:** archived original Ghidra
`nite3w(1).docx` and original Win16 v1.10 Ghidra decompiled C.
Static-only proof; no Win16 v1.10 original EXE was freshly rehashed
and no Windows 3.11 runtime trace ran in this pass.

## Original filename-builder semantics: prefix vs suffix

`FUN_1010_5260` (3:5260) constructs full filenames in
`DS:36BE` using a shared prefix from `DS:46BE` plus a caller-supplied
NUL-terminated filename.

- `3:5265`: DI=46BE (prefix), `3:5268`: SI=36BE (output).
- `3:526F–5282`: `REPNE SCASB` on prefix, then `REP MOVSW/MOVSB` into
  output.
- `3:5287`: DI receives caller's near filename argument.
- `3:528A–52A5`: scan filename and existing output, then append suffix
  with `REP MOVSW/MOVSB`, replacing the existing terminal NUL.
- No explicit capacity comparison for the buffer at DS:36BE occurs in
  the inspected function body. Any hidden runtime/global upper bound must
  come from **input provenance**, not an asserted in-function check.

Original DGROUP literals:
- `DS:101E = "config.sav\0"` — 10 characters plus terminal NUL.
- `DS:1E50 = "user.sav\0"` — 8 characters plus terminal NUL.

## 12 named direct caller paths — suffix is always a literal

There are exactly **five named direct code references to 3:5260**
in archived Ghidra: two literal `config.sav` callsites and one call
inside each of three save/load helper wrappers.

| Function invoking 5260 | 5260 callsite | Source of filename |
|---|---|---|
| `3:52AE` | `3:52F5` | immediate `DS:101E`, `config.sav` |
| `3:534E` | `3:5358` | immediate `DS:101E`, `config.sav` |
| `3:5388` | `3:5397` | wrapper's parameter 2 |
| `3:5466` | `3:548C` | wrapper's parameter 2 |
| `3:574C` | `3:5759` | wrapper's parameter 2 |

The apparently dynamic parameter 2 has now been resolved **across all
10 named direct callers of those three wrappers**:

| Wrapper | Direct callers in original NE4 | Near argument |
|---|---|---|
| 5388 | `4:2245`, `4:22BB`, `4:2321`, `4:2409`, `4:2C96` | `DS:1E50` |
| 5466 | `4:2CAA`, `4:2D8F` | `DS:1E50` |
| 574C | `4:243B`, `4:2945`, `4:2CC9` | `DS:1E50` |

Each original assembly callsite has a `PUSH 1E50` in the argument
position used by the wrapper's `[BP+8]` near filename parameter.
All 10 thus pass *the same literal*, `user.sav`, not a computed
per-save filename string. This closes the currently documented
**12 DIRECT caller filename-suffix arguments**; it does not exclude
missing machine-code functions, dynamic function pointers or indirect
callers of any wrapper/5260.

Evidence register:
`other/n3d/builds_12/static_byte_evidence/N3D_Win110_filename_alias_callers_20261020.csv`.

## The genuine variable component: `-p` command-line prefix

At Windows application startup, archived `FUN_1010_1118` implements a
switch with `switchD_1010:116D::caseD_70` (ASCII `'p'`, thus
`-p` in the parsed switch syntax).

    3:120C PUSH 46BE           ; output location DS:46BE
    3:120F PUSH 0D8C           ; literal format "%s"
    3:1212 LEA AX,[BP-4]
    3:1215 PUSH AX
    3:1216 PUSH 0
    3:1218 CALL FAR 2:6B06     ; tokenizer: returns next parsed argv token
    3:121D ADD SP,4
    3:1220 PUSH AX            ; token pointer, as vararg
    3:1221 CALL FAR 2:6442    ; output + "%s"
    3:1226 ADD SP,6
    3:1229 CALL FAR 3:52AE    ; immediately revisit config.sav path

Original `FUN_1008_6B06` scans the token string with an on-stack
32-byte character-acceptance bitset; it obtains its input near pointer
from the command-line parser or the global next-token pointer DS:0A8E.
It is a **tokenizer**, not the output writer.

Original `FUN_1008_6442` stores the output pointer in its formatting
state at `DS:45DC`, records the current strlen, then calls the
format implementation `FUN_1008_4504`. Thus `DS:46BE` may be
populated through an *indirect pointer write*, explaining why direct
Ghidra XREFs to `DS:46BE` only show the first-entry zero at `3:0ED9`.

The `-p` caller supplies no output-capacity parameter to
`FUN_1008_6442`. The complete recursive formatter's effective
length cap and the historical Windows 3.11 entry-point command-line
provider limit were **not proven** by current static evidence;
do not silently import a DOS PSP 127-character assumption into Win16.

When the original one-shot init `3:0E9E` is triggered,
`3:0ED9` resets the first byte at DS:46BE to zero, so the ordinary
startup *without `-p` and without another alias writer* uses an empty
directory prefix. This is a conditional path proof, not a global
assertion about all possible callers/state.

## Exact conditional write overlap

`DS:46B2 - DS:36BE = 0xFF4 = 4084` bytes.

For an ordinary, nonwrapping prefix of `p` characters and suffix of
`s` characters (not counting each input's NUL), the output final
terminator is at offset `p+s`. Consequently the copy can write the
clock flag when `p+s >= 4084`.

| Literal suffix | `s` | Smallest `p` that could reach timer flag |
|---|---:|---:|
| config.sav | 10 | **4074** |
| user.sav | 8 | **4076** |

The first copy of the prefix alone can reach the flag when `p>=4084`.
The second append can reach it with shorter prefixes under the
combined threshold.

**Critical distinction:** the threshold is an *address calculation*,
not a demonstrated gameplay buffer overflow or an observed way to
change `DS:46B2`. The existing original command-line buffer's maximum
length, formatted-output capacity and any other unknown pointer aliases
must be proved before declaring the overlap reachable/impossible in
normal Win16 runs.

## Automated regression

- `tools/n3d_win16_filename_alias_calls.py` verifies exactly the 12
  original direct edge/suffix records, and retains `-p` prefix
  provenance and command-line max as explicitly OPEN.
- `tests/test_n3d_win16_filename_alias_calls.py` verifies literal
  identity, all 10 save-wrapper fanout edges, command-line dataflow,
  exact 4074/4076 thresholds, and intentional corrupted-edge cases.
- `.github/workflows/win16-timer-ne-proof.yml` runs synthetic tests.
- Earlier `tools/n3d_win16_rep_destination_audit.py` still counts the
  **four REP filename-staging operations as unresolved input-bound
  sites**, correctly: suffix bounded does NOT imply prefix bounded.

## Next proof obligations

1. Finish `FUN_1008_4504` formatter's effective string-length guard
   (or prove absence of one) and the original Win16 input command-line
   upper bound across app launch, WinExec/Program Manager and MFC entry.
2. Trace other address-taken writers to `DS:46BE`, including byte/word
   aliasing, implicit offset pointers and source string mutations.
3. Rule out alternative indirect calls to `FUN_1010_5260` with
   unknown suffixes using complete NE call/address-taken provenance.
4. Continue outstanding non-filename REP destinations and computed
   ES:DI writes in the original 1.10 binary.
5. Only if static evidence cannot settle reachability: controlled
   Windows 3.11 runtime test of prefix length and `DS:46B2` write log,
   not general uninstrumented gameplay.

**No increase in global 1:1 behavior/timing/pixel parity percentage.**
