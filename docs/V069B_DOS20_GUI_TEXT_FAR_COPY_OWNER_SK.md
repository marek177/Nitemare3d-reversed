# Nitemare 3D V069B — GUI type-4 FAR destination at DOS2 IMG:E2A4

**20 October 2026 · original DOS V2.0 static reverse engineering only.** No new original gameplay execution and **no original-versus-remake parity proof**.

## 1. Original verified binary

DOS V2.0 unpacked `N3D-UNFU.exe` SHA256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`. All `IMG:` addresses refer to the 512-byte-MZ-headerless **load image**, not live runtime CS:IP.

The earlier V069/NEXT7 29-opcode typed REP MOVS census left **one** 41-byte copy at `IMG:E2A4` with a dynamically supplied FAR destination. Direct disassembly now identifies the bounded owner/caller:

| Original IMG | Executed-instruction semantics from static bytes |
|---|---|
| `EC2F`, `EC57` | GUI record iteration uses `ADD SI,0x12` (18-byte stride). |
| `EC50` | Control byte at GUI record `+0x04` is tested. |
| `ECD3` | Load GUI record type from `ES:[SI+0x05]`. |
| `ECD9–ECE3` | Repeated decrement/conditional branches route **type 4** to `ECFC`. |
| `ECFC–ECFF` | `PUSH ES; PUSH SI; PUSH CS; CALL E1DE` — **one found literal near callsite**. |
| `E1DE` | `ENTER 0x2C,0`: 44-byte local stack frame for text editing. |
| `E1E4–E1F5` | Ten doublewords initialized by `REP STOSD` to local text scratch space. |
| `E1F8–E1FF` | Load FAR pointer to text from the supplied control record `+0x0E/+0x10`. |
| `E206` | Original comparison reference string at `DS:1CE9`. |
| `E27E`, `E288` | Editor/dialog callback and result-dependent branch; on unsuccessful result, skip the copy. |
| `E28C–E29E` | Reload control record FAR destination, set `DI` from record+0E, `ES` from record+10, `SI=BP-2C`, `ECX=10`. |
| `E2A4–E2A7` | `REP MOVSD` ten times, followed by one `MOVSB`: **exact 40+1=41 copied bytes**. |

An exhaustive **literal relative near-call** census over the original MZ load image found exactly `E8` at **IMG:ECFF** targeting `E1DE` and **no literal 9A FAR-call** targeting the same linear image address.

### Interpretation

The `E2A4` routine's **local purpose is GUI type-4 text editing**, not an ordinary scheduler copy into a GUARD record. This significantly narrows the former open *record FAR destination* class. But the record's FAR pointer is **supplied from outside the local routine**. The audit does not exhaust writers, indirect function pointers, corrupted-editor-record inputs, SAVE/LOAD rebase or heap aliases. Therefore it does **not** prove that this destination can never alias a GUARD region in all possible machine states.

## 2. Executed static verification

A new **original-SHA-gated** Python stdlib verifier independently checked **14 exact opcode windows**, decoded the unique near and zero literal FAR callsites, verified stride and type-4 route, and checked 10×4+1 output width. **15/15 deliberately mutated image bytes were rejected** with the SHA gate bypassed only during negative tests.

User-private proof file: `N3D_GUARD41_FAR_UI_COPY_V069B_20261020.zip`, SHA256 `4a3b4be2431b05a2cf19dd1294164a8b435cb0cc7959de08d5a0e4a3800d5df3`; **5,738 bytes, 4 files**, consisting of the standalone Python verifier, verification JSON, Slovak README and SHA256SUMS.txt. ZIP integrity and all checksums PASS. **No commercial game assets are included.**

Run with privately supplied original DOS2 unpacked EXE:

```bash
python3 tools/verify_e2a4_editor.py --exe /private/N3D-UNFU.exe --self-test
```

## 3. Next RE-first obligations

- Traverse all producer/writer paths for the type-4 editor record `+0x0E/+0x10` FAR pointer; prove its allocation and which memory segment it can target in legitimate UI calls.
- Separately close generic `MOVS/STOS` aliases and original SAVE→LOAD GUARD/WORLD memory reconstruction — these are **not** proved by the UI editor.
- Consider a controlled collision/interactor runtime test for the alternative `WORLD+01=0; WORLD+05 &= 0xFE` helper only if the static caller/flags/lookup graph cannot resolve natural reachability after GUARD41 death.
- Ultimate complete original-versus-clean-room state/pixel/DAC/audio zero-diff remains **OPEN**. No global parity percentage increase.
