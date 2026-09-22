# Nitemare 3D OBJECT + Combat audit (2026-09-22)

This note consolidates confirmed runtime findings already present in `src/game/ObjectSystem.hpp` and `src/game/GuardSystem.hpp`, and separates them from open questions.

## OBJECT runtime record

The Win16 NITE3W runtime OBJECT record is 0x1C (28) bytes in the currently recovered build. Confirmed/strong fields:

- `+0x00` object/map identifier
- `+0x01` class-relative variant index
- `+0x02/+0x03` signed animation/render offsets
- `+0x04` object definition index
- `+0x05` object property flags
- `+0x06` runtime object class/type
- `+0x07` guard index for guard-producing objects
- `+0x08..+0x0B` runtime value initialized to zero; semantic open
- `+0x0C/+0x0E` far pointer to associated map cell
- `+0x10` world X
- `+0x12` world Y
- `+0x14/+0x16` renderer/sort values (partial naming only)
- `+0x18` projected/view-space vertical baseline read by combat/damage producer
- `+0x1A` initialized runtime byte
- `+0x1B` unknown

Important correction: the verified runtime stride here is **28 bytes (0x1C)**. References elsewhere to an 80-byte OBJECT stride must not be merged into this structure unless tied to a different build/array and independently verified.

## OBJECT property bits

Confirmed from the recovered object-property table and runtime readers:

- `0x01`: instantiate runtime OBJECT
- `0x02`: blocks player movement
- `0x04`: special/touch handling family (subtype semantics still partial)
- `0x08`: creates GUARD record
- `0x20`: semantic open
- `0x40`: semantic open

## GUARD binding

A guard-producing OBJECT stores the assigned GUARD index at OBJECT `+0x07`. The GUARD record stores the corresponding object slot at GUARD `+0x08`, creating an explicit bidirectional runtime relationship.

The GUARD runtime record is 0x1A (26) bytes and already has verified fields for timer, strategy, state, next-state and strength/HP in `GuardSystem.hpp`.

## Combat path currently verified

The receiver side of enemy damage is structurally recovered:

1. a computed damage value reaches the GUARD damage routine;
2. damage is compared to GUARD `strength` (`+0x10`);
3. lethal damage clears strength to zero and enters the death path;
4. non-lethal positive damage subtracts from strength;
5. ordinary hit reaction sets the reaction direction/result value and enters state `0x15` (pain reaction) before returning to the queued next state.

OBJECT `+0x18` participates in the producer side as a projected/view-space vertical value. It is not the object's world-Y coordinate (`+0x12`).

## Score dispatch

The recovered score dispatcher maps object classes `0x08..0x20` to GUARD1..GUARD25. The table is encoded in `GuardSystem.hpp`. Classes outside that switch return zero by default; this includes later/special classes unless another script path awards score.

## Still open

The following should remain `PARTIAL`/`TODO` until direct executable evidence or controlled runtime traces close them:

- semantic meaning of OBJECT `+0x08..+0x0B`;
- exact original names/roles of OBJECT `+0x14` and `+0x16`;
- writer and exact renderer meaning of OBJECT `+0x18`;
- object property bits `0x20` and `0x40`;
- complete weapon-class -> base damage mapping;
- exact difficulty transformation of incoming/outgoing damage;
- enemy class-specific resistances/immunities, if any;
- exact death-state/SFX mapping for every guard class;
- whether any score awards bypass the main GUARD1..GUARD25 dispatcher.

## Next high-value runtime tests

1. Watch OBJECT `+0x08..+0x0B` while moving, animating, picking up and destroying several object classes.
2. Trace writes to OBJECT `+0x14/+0x16/+0x18` during renderer projection.
3. Break on writes to GUARD `+0x10` under difficulty 1, 2 and 3 with the same weapon and target.
4. Compare lethal/non-lethal paths and SND.DAT event IDs for several guard classes.
5. Test classes outside `0x08..0x20` for alternate score writers.
