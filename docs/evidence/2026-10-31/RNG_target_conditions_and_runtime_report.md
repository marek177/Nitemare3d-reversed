# Eleven RNG caller conditions and original runtime gate tests — 2026-10-31

## Corrected checkpoint and source identity

The prior corrected checkpoint is revalidated from its archived content, SHA2568ba973087c274e56c3c84c48696a9553214fff28e0cabfec8c19ae08eece0216:42,232 manifest files, exact set, CRC, every archived SHA, CFG links and all3,922 semantic corrections. The archive is retained unchanged. The new checkpoint adds this continuation.

GitHub PR69 had advanced independently to f6cbb5d54ba15a65fb0430adabe6ecc9734b8d4c. Its eleven-site analysis is retained in upstream_function_records.md and upstream_static_audit.json. That analysis uses original EXE SHA552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301; this local analysis uses unpacked SHA5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3. They are different artifacts. This pass independently matches all11 CALL encodings,97 listed post-call instructions and iced text, five table hashes and five local bounded dispatch prefixes against the local image. Selected guard witnesses are byte matched at inherited instruction starts. No whole-binary equivalence is inferred.

## Bounded conditions for all eleven sites

All addresses are logical load-image-relative PCs. Candidate function ownership remains inherited. The classification describes local executable conditions, not a proof of every incoming path, callback registration or a natural map trigger. RNG outputs below use the established0..32767 wrapper range. CWD is16-bit sign extension; IDIV flags do not define later branch predicates.

| Site | Local activation conditions | Result consumers |
|---|---|---|
| 0201:0468 | Near DS record: due unsigned dword+08<=clock; class+06 not07/2D/2F; descriptor+04 nonzero; incremented byte+03 reaches sum of selected low/high bytes. Retry while selected high byte is zero. | AL&7 -> index+02; accepted low byte ->+03; next time clock+descriptor+02. |
| 04C7:09F6 | Record byte+0A==2 in inherited local dispatch. | CWD/IDIV8 then remainder+8 -> timer+06 (8..15). |
| 04C7:0C37 | No conditional between candidate entry and RNG. | CWD/IDIV80 remainder+8 ->timer+06 (8..87); state+0B=13h; direction+11 indexes DS tables0AD4/0ADC. |
| 083D:0490 | Descriptor+06 selector8 via bounded CS045E table. | AX&7 ->SI; scale via DS4180; returned AX=SI. |
| 083D:049C | Descriptor+06 selector9 or10 via CS045E. | AX&15 ->SI; same scale; returned AX=SI. |
| 083D:04AC | Descriptor+06 selector17..20 via CS045E. | AX&31 ->SI; same scale; returned AX=SI. |
| 083D:1698 | Entry argument7. N=DS41AF; divisor signed16(low16(N^3)); Q=trunc(500/divisor)>0. OR supplies JLE condition; divide fault possible for zero divisor. | RNG modulo62 ->DS3632; paired second draw at16A7; loop gate recomputes N after external calls. |
| 083D:16A7 | Unconditional second local draw following1698 and coordinate store; same outer gate. | RNG modulo36 ->DS3630; coordinates passed to helpers. |
| 083D:18F2 | Descriptor+06 selectors27..31 via CS1888 table (base9). | RNG modulo4+75 ->SI75..78; passes selected value to0C2B:03D6, not final returnAX. |
| 083D:1B3C | Descriptor+06 selectors9/10 via CS1B06 table (base8). | RNG modulo3+56 ->SI56..58; passed as consumer argument. |
| 0AEA:03D6 | FAR ES record: due unsigned dword+08<=clock; increment+03; near descriptor+04 table nonzero; incremented counter>=byte-sum threshold; retry high byte0. | AL&7 ->ES index+02; accepted low byte ->+03; next time clock+descriptor+02. |

CSV includes concrete next experiments; JSON includes byte witnesses and bounded selector prefixes. Pointer identities, descriptor producers and natural map/episode domains remain open. In particular the retry loops have no proved universal termination; the coordinate cube gate uses low16 arithmetic and can divide by zero for some synthetic N values, which were not injected into the original game.

## Original runtime observations

DOSBox-X executable SHA78fd1926272de172c2a87b9456aafce5eb54ea928ad1e5103a6d943bc26f0f57 was rechecked. The packed N3D.EXE remains SHAa3fa02335e1d8bc531918f3bfaa66217aef65c81e562a2fdf1c749be652ca485. Each run has a separate game directory, pipe and input manifest. These user-provided assets/configuration are not asserted pristine stock.

Historical process18800 had been reused by a different program; it was not controlled. New run_g returned OPERATION_TIMEOUT and then authoritative session.status=failed; its owned process was later missing. Run_h ended with an empty RPC response and its owned process missing. No gameplay coverage is assigned to either. Run_i started successfully after returning to the baseline disk configuration, removing console redirection and raising startup timeout; these changes are confounded, so a specific startup failure cause is UNKNOWN.

Run_i is owned process41260, session ses-1, loadbase0823. Preserved BIOS queue fixtures passed copyright/title, a hash-matched Main Menu, Episode1 and visually verified default difficulty Be gentle!. One early operation was still unpacking and was recovered using the same op-3 handle; there was no timeout-driven restart. An early short-settle image hash failed on the title screen, so the controller stopped before more input and recovered from that observed state. BIOS queue fixtures bypass physical keyboard IRQ9. Computer-use inventory exposed no targetable DOSBox window; no Windows key input was sent.

Eleven persistent breakpoint addresses were armed and remain verified in the final snapshot. Bounded original execution progressed to render counter13. No direct CALL among those eleven was observed; this neither proves unreachability nor closes their runtime acceptance tests.

The discriminating gate test targets the actor-state7 path before initializer04C7:0C30, which contains missing RNG site04C7:0C37:

* Natural baseline actor2A20:264E, counter13: record mode+0A=0 and state+0B=7; global2F94:4153=01. Original CMP at04C7:0F60 produces ZF0, and original JNE at0F65 is stepped to12B0. This actor invocation skips the initializer before its helper/mode tests.
* Controlled precondition case actor2A20:2668, counter13: only global data byte2F94:4153 was changed01→00. The original CMP/JNE falls through to0F69. Original helper06D2 returns AL0 at0F7B; stepped OR/JE produces ZF1 and reaches12B0. It skips the initializer at the next predicate. Record mode+0A is also0, but that later guard was not executed in this case.
* These are two different actor records, not a paired same-actor A/B experiment. The fixture was restored00→01 with readback. No executable or RNG state bytes were written. Endpoint RNG remains1; no claim excludes arbitrary unobserved core entries or all writers.

The independent read-only verifier correlates all proof RPC UUIDs/responses to server PID41260, validates read lengths/hashes/addresses, frame-derived actor pointers, original branch results and all11 live breakpoints. Three negative cases are rejected: changed branch PC, changed restoration bytes and actor-pointer splice. Public validation is derived metadata; raw RPC, record contents, images and binaries remain local.

A later VGA projection was rejected by the DAC/xlat consistency guard. No decoded image or frame-aligned parity claim is made for that capture; the guard was not relaxed.

## Resume and remaining work

Last observed stop: revision107 at runtime0CEA:12B0, logical04C7:12B0, with global4153 restored, no active operation and11 persistent target breakpoints. Revalidate actual server PID, session state and breakpoint list before any resume; a saved control file alone is not liveness evidence.

Next work is provenance of global4153 (configuration/data writers), actors satisfying helper and mode3 gates, appropriate descriptor selector groups in other maps/episodes, callbacks and coordinate argument7. All11 original RNG call/return acceptance cases remain open. Every-IRQ/global alias closure, remaining DOS/Win16 functions and paired remake parity remain open; no completion percentage is asserted.
