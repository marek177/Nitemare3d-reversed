# Natural mode0 actor RNG consumer and FAR exit — 2026-11-06

The independently owned original M process7772/loadbase0823 reaches a next natural RNG wrapper at render counter1267. Its actual saved caller is04C7:0A36. State0029E2C0→C823F683 and AX18467 match the LCG and15-bit output; the wrapper reaches04C7:0A3B with SP+4. This newly records the call itself; it does not reconstruct the earlier unobserved seed1→0029E2C0 transition or prove a global call count.

The caller's actual actor is2A20:2704, object type8, mode0, state3. Flags+17/+18 are1/0. Selector18467&7=3 chooses signed direction bytesF8/08 (-8,+8). The second original wrapper call04C7:0ACF changesC823F683→18BE873A and returns AX6334. Timer6334%8+8=14 is stored. Every byte of the26-byte actor record at0B0A matches the predicted direction/timer update, with other bytes unchanged over that consumer phase. This is a mode0 case; remaining mode2 RNG site09F6 and mode3 initializer0C37 are not covered by it.

The native state writer04C7:0B0D (MOV byte ES:[SI+0B],6) is separately stepped, changing only that actor byte3→6. A bounded nested trace then witnesses000B0,0012A and00422 and stops before0B47. POP SI, POP DI, LEAVE and RETF are stepped separately; actual saved return04C7:0EA4 and SP+4 for RETF match. Parent0938 entry and all nested side effects are not closed. The source call frame at0EA0/0EA1 is PUSH CS/NEAR CALL, not ordinary NEAR return ABI.

Three independently delimited original trace windows contain36/72/665 contiguous sequence-numbered events, below capacities1000/2000/10000. They are not described as one uninterrupted trace: debugger pauses separate phases, and the last recorded stop instruction is not assumed executed. Explicit steps prove the state store and FAR exit. The consumer trace gives nine observed conditional edges; this is one path, not complete branch coverage.

The read-only verifier correlates raw RPC IDs, serverPID, read addresses, lengths/hashes, register snapshots, original caller encoding, LCG/AX, all26 consumer bytes, state writer, frames and trace sequences. Three tamper fixtures (wrong AX, actor address and timer) are rejected. No gameplay-memory API writes were made; earlier menu inputs remain BIOS queue fixtures. Physical keyboard/IRQ and live remake timing parity are not claimed.

The canonical181-instruction candidate record for04C7:0938 is byte matched and updated with mode dispatch, explicit16-bit arithmetic, stack/parameters, memory dependencies and the bounded runtime evidence. Its whole-boundary status remains UNKNOWN. A36/ACF were already known RNG callsites; this is a new natural actor/consumer/exit proof, not a claim of additional hits among the eleven remaining target sites. All eleven targets remain enabled and the session is stopped for continuation.

Original binaries/assets and full traces stay local. This evidence does not close P0 or the full DOS/Win16 GOAL.
