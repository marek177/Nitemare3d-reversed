# NEXT16: DOS GUARD resolver contract

The bounded semantic model in `N3DDosGuardResolver.hpp` follows the supplied **NEXT16_STATIC_REPORT_SK.md**, dated 2026-10-20 (Library ID `libfile_3b039bf4fe5481918a55373eca8d63c7`). That report describes a read-only audit of seven SHA-checked EXEPACK load images, 91 opcode anchors and 21 relocation-backed FAR callers. Those original images and the verifier were not rerun or inspected for this implementation. Confidence is medium for the source-to-model transfer; original runtime reachability remains unknown.

| DOS | Resolver IMG | Projectile caller | Message caller | UI/event caller |
|---|---|---|---|---|
| 1.0 | 05EA2 | 07C58 | 08C4D | 08C9B |
| 1.1 | 05F26 | 07E78 | 08E6D | 08EBB |
| 1.2 | 05F32 | 07E84 | 08E6F | 08EBD |
| 1.5 | 05F80 | 07ED2 | 08EC1 | 08F0F |
| 1.7 | 0601C | 07F6E | 08F5D | 08FAB |
| 1.9 | 06180 | 080D2 | 090C1 | 0910F |
| 2.0 | 06180 | 080DC | 090CB | 09119 |

Addresses are offsets in unrelocated load images, not runtime breakpoints.

First pass: signed count <=0 skips the pool; otherwise scan GUARD records in order, rejecting +0B==0A or +0C==09. Compare both words of the input map FAR pointer against WORLD:[28*GUARD.word08+12/+14]. These correspond to OBJECT+0C/+0E because the object begins at WORLD+6. Return the first eligible match. The native pool stride is 26 bytes; the host API instead accepts explicit semantic records and returns their index, not a native FAR address.

Second pass: if no accepted match, scan again without the rejection predicates, reading the separately supplied AREA bank. A match identifies diagnostic fields +0D/+0C/+0B then the reported CRT exit(1) path. No match reaches the generic error helper and the same exit(1). The model returns distinct outcomes rather than terminating the host. Missing snapshot bytes produce a separate `IncompleteSnapshot`, never an original-game null-return claim.

The original report found initial WORLD/AREA segment equality across the seven builds. Runtime alias stability is not established: both banks are explicit inputs. The low-word 28-byte object displacement wraps at 16 bits; no host object-array bounds repair is silently substituted. This does not establish malformed-save behavior or raw pool address traversal for pathological counts.

Synthetic scenarios verify rejected duplicates followed by an eligible match, both skip predicates, second-pass diagnostics, missing matches, signed counts, incomplete captures, distinct banks, both FAR words and wrapped object displacement. They do not establish natural E1M9 reachability, stale OBJECT+18 damage, all field writers, Win16 equivalence or exotic exit callbacks. The projectile caller's property/distance gates remain outside this local resolver model.
