# Nitemare 3D DOS V2.0 — GUARD41 post-death original runtime V066

**2026-10-20.** ORIGINAL DOS V2.0 execution, not clean-room parity. Original packed EXE / GAME files and RAM were not patched. New DOSBox-X v0.65 automatic CPU capture, including opt-in AL-value filter.

## New original executed state transitions

| Step | Observed DOS2 address | Original CPU result |
|---|---|---|
| state0 to state9 | 0CEB:0E03, MOV [BX+0B],AL | GUARD41 at DS:BX=2A21:2A78; AL=09; state 00->09, CPU #1 |
| state9 to state0A | 1061:0322 | GUARD41 state 09->0A, CPU #17; two independent DOS2 original traces |
| state9 RNG #19 | shared RNG wrapper | AEA69ED3->12DBCE4A, AX=4827; low/high state writes at CPU #81/#82 |
| linked map property gate | 0CEB:1045->104A | linked WALL BB property 00; ZF=1, skips special-action branch |
| state9 exit | 0CEB:12B0 | epilogue at CPU #4237 / #4240, separate DOS2 original sessions |

World flags byte +05 was written 0B->0B, because its low bit was already set. The map condition skipped one special action, but GLOBAL drop/pool cleanup is not proven absent.

## Why the new AL predicate is essential

Before adding the AL gate, exactly the same original writer CS:IP 0CEB:0E03 and GUARD41 identity captured a **pre-death** state00->05 transition (AL=05). A source gate on CS:IP and actor alone would therefore mislabel gameplay. The new opt-in source patch supports N3D_TRACE_START_AL=09, enforced BEFORE starting N3DTRC01. Successfully compiled original-compatible Linux ELF SHA256 69a3aaee12e5bec5b9c06c05425e3a6e0a5356eeb231d6bbff451d10d0700b17, GitHub Actions run 39479126124.

Tested trigger for this specific DOS2 relocation: START_CSIP=0CEB:0E03, START_OPCODE4=88470be9, START_ES_SI=2A21:1C5A, START_AL=09 and INSTRUCTION_LIMIT=15000. NOTE ES:SI here points at linked WORLD, whereas DS:BX points at GUARD41. At the separate fatal HP writer ES:SI instead points at GUARD41. All addresses require live confirmation after relocation.

## Original, private proof traces

| Route | CPU | Reads | Writes | SHA256 .n3dt |
|---|---:|---:|---:|---|
| DOS2 state00->09 | 15000 | 42387 | 3318 | fc18b45497dcf52961e3840c7d62c6f0ffd438471763d4a2a10db3928997dc5f |
| DOS2 state09->0A A | 12000 | 39615 | 14453 | 89a7ef6bb783cabaaa23a7e00ac7218aac167259b58d35765df251470d7b80b7 |
| DOS2 state09->0A B | 4600 | 18692 | 12771 | 52ac2aec7500e350b5c4368a38197e1025a42788641f454d81aa146d87fe9e05 |
| DOS2 predeath state00->05 NEGATIVE CONTROL | 15000 | 42704 | 3451 | 0a8d41aedc7ea1ba1ed1815ba87c9de5f0186c3e63929b64f0820835a884c643 |
| DOS1.2 state09 original reference | 4235 | 17665 | 12675 | 84cd4bf0c69b9a18f0d304499dc9e430bb90555df0e377728ca3a1e61c72bb6e |

All new DOS2 sessions end INSTRUCTION_BUDGET, NOT SIZE_LIMIT. The DOS1.2 reference stops on 0CC6:104C BEFORE executing its epilogue; the DOS2 captures actually reach 0CEB:12B0.

## Cross-DOS bounded execution comparison

DOS1.2 and DOS2 original state09 have identical values and CPU ordinals: WORLD+05 0B->0B (CPU #15), GUARD+0B 09->0A (#17), RNG low 9ED3->CE4A (#81), RNG high AEA6->12DB (#82), WALL BB property00 causing same conditional branch. This is original-vs-original scoped behavior, not original-vs-port pixel/timing parity.

## Reproducibility and strict boundaries

Private proof bundle N3D_GUARD41_POSTDEATH_DOS20_RUNTIME_V066_20261020.zip SHA256 067bcaf775132978f6b65787fa08871f3f3b051ca6fda08c172c2b22070dd5db includes the five original CPU traces, standalone read-only Python verifier, screenshots, source checksums and reproducer. Fresh extraction: all 12 manifest entries PASS. Independent 10/10 semantic byte mutations rejected with SHA gate disabled, and pre-death state00->05 correctly rejected.

OPEN P0: (1) gapless full simulated-tick history between death, state00->09, state09->0A, including IRQ/reentry; the state phases are recorded in INDEPENDENT runs, (2) eventual object drop/slot release and global aliases outside this bounded handler, (3) paired original vs clean-room state, framebuffer, DAC and timing zero-diff. Global parity percentages unchanged.