# Nitemare 3D — Ghidra static target/cache alias audit (22.10.2026)

**Scope and provenance:** Consolidation of earlier GHIDRA01–GHIDRA03 passes over Ghidra-derived 16-bit code/listings. Those passes reported **20/20**, **21/21**, **25/25** local verification tests respectively. Their complete original projects and byte-level ledgers are **not part of this GitHub update**. These are archived **static findings**, not a new original-game execution in this commit.

## 1. Target record alias — GHIDRA01

The renderer's indexed render-target record and the projectile damage/hit target refer to the same record family in the inspected listing:

- Segment notation in that project: **21FD**.
- Indexed record starts at **21FD:(0x0006 + i × 0x001C)**; stride **0x1C = 28 bytes**.
- The projection-related cache lies at record displacement **+0x18**. It is written only on the identified conditional projection path.
- Projectile collision/damage logic reads data associated with this same record family; the address identity is the reason we must model the cached field and not invent a separate isolated target array.

**Crucial limit:** identical record addressing does **not** prove the value at +0x18 is fresh for every hit, every slot, or after SAVE/LOAD. The reader can observe an earlier value if the writer did not run in the intervening path; establishing that requires a real writer→reader ordered trace.

## 2. Runtime-order candidate — GHIDRA02

Recovered static control-flow order in the inspected route:

1. render/projection path may compute and write the target cache;
2. projectile scheduler visits a projectile slot;
3. hit/collision/damage may read the target cache;
4. a later render/projection pass can update it again.

The +0x18 arithmetic in the archived walkthrough involves **signed division, 16-bit addition/wrap and arithmetic shift by four**, not an unconstrained floating-point depth value. This is a scoped instruction-semantics statement; the complete operand ledger needs replay before assigning a universal formula.

**Do not promote the static order to a universal frame/tick ordering**: IRQ boundaries, multiple slots, conditional writers, list reordering, first render after LOAD and all other +0x18 aliases remain to be observed.

## 3. Different record family — GHIDRA03

The separate metadata/proximity writers associated with listing offsets **IMG:549D** and **IMG:54A7** address a **0x1A (26-byte) stride** family based at **21FD:264E**. This is *not* the 0x1C renderer damage-target layout above. The earlier audit checked the expected non-alias cases for its bounded indices; do not infer all indexes in the address space are universally disjoint.

| Attribute | Render/damage target | Metadata/proximity |
|---|---|---|
| Segment in archived listing | 21FD | 21FD |
| Indexed start | 0006 + i×001C | 264E + i×001A |
| Record stride | 28 B | 26 B |
| Focus | cached +0x18 field / damage reader | metadata writers IMG:549D / IMG:54A7 |
| Status | bounded static alias | bounded static separation |

## 4. Required original-runtime closure

Capture at the **same load-image/segment mapping**, with the active original EXE SHA and documented offset conversion:

- all writes and reads of target +0x18 (old/new, actor and target index, CS:IP, call depth and game tick);
- projection branch predicates, signed arithmetic operands/results and subsequent hit collision;
- projectile slot lifecycle and its writer/reader order, including E2M10 nested scheduler;
- all direct/indirect writers and bulk copies; first frame after LOAD;
- one natural collision in which a +0x18 read precedes a refresh, or an exhaustive proof that such an ordering is impossible for the relevant scenario.

**Outcome:** address aliases and specific control-flow edges are archived. Natural stale-cache damage, exhaustive writer census and 1:1 gameplay parity remain **OPEN**.

Related references: [v0.77 bulk-copy provenance](V077_REMAX_BULK_COPY_PROVENANCE.md), [controlled projectile limits](V083_RUNTIME_PROJECTILE_SAVE_WIN16_FRONTIER.md), [v0.78 geometry integration](BULK_UPDATE_20261020.md).
