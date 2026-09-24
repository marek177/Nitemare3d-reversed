# Nitemare 3D reverse-engineering consolidated audit — 2026-09-22

This document consolidates the highest-confidence findings recovered from the Win16 NITE3W executable analysis, MAP/IMG/WALLS/OBJECTS data files, cross-version comparisons and gameplay observations.

## Confidence policy

- **CONFIRMED**: directly supported by executable control flow, fixed record stride, explicit class checks, data-file class tables, or repeated runtime evidence.
- **HIGH**: strongly supported but one small mapping/detail is still unresolved.
- **PARTIAL**: known structure/dispatch exists, but exact semantics are not yet complete.

## Wall class runtime properties

The executable builds a derived property byte for all 256 wall IDs from the wall-class table. Confirmed bits:

| Bit | Meaning | Status |
|---:|---|---|
| `0x01` | world/vector geometry participation | PARTIAL name, confirmed use |
| `0x02` | collision-relevant wall/cell | CONFIRMED |
| `0x04` | solid/static-interactive wall | CONFIRMED |
| `0x08` | door family | CONFIRMED |
| `0x10` | explodable wall family | CONFIRMED |
| `0x40` | trigger family | CONFIRMED |

Class ranges observed in the executable:

- `0x31..0x40` -> door family
- `0x2E..0x2F` -> explodable wall family
- `0x47..0x48` -> trigger family
- `0x3F` -> `DOORVC` (vertical curtain door)
- `0x40` -> `DOORHC` (horizontal curtain door)

## Main USE dispatcher

`FUN_1010_19d6` is the central interaction routine for the cell in front of the player.

Recovered dispatch order:

1. If derived wall properties contain `0x08`, dispatch to the door path.
2. Wall class `0x09` -> `LEVEL_UP`.
3. Wall class `0x0A` -> `LEVEL_UP2`.
4. Wall classes `0x0D..0x2C` -> WARP/portal family.
5. Object class `0x03` -> panel/control interaction, runtime event `0x27`.
6. Additional special wall classes `0x03`, `0x04`, `0x05`, `0x06`, `0x08` and object classes `0x26..0x29` remain partially named.

`LEVEL_UP` increments the zero-based level index by one. `LEVEL_UP2` increments it by two.

## Door subsystem

Confirmed runtime facts:

- base: `0x9DD6`
- capacity: 64 records
- record stride: 22 bytes
- four runtime states (`0..3`)
- movement step observed as 2
- countdown values 32 / 4 appear in the state logic
- auto-close logic exists
- obstruction is tested before closing
- collision flags change with door state
- colored-key doors test player key state
- ID-card doors test a separate player inventory byte
- remote-controlled door classes reject ordinary manual USE
- curtain doors (`0x3F`, `0x40`) are ordinary members of the same door-record subsystem

Open details: exact tick unit and a few class-specific event mappings.

## Panel/control subsystem

Confirmed runtime facts:

- base: `0xA356`
- capacity: 32 records
- record stride: 22 bytes
- states `0/1/2`
- object class `0x03` enters this path
- event code `0x27` is set by USE
- step value 2 is used in state progression
- records can contain up to four far pointers
- completion/link cleanup and map/collision changes are present

Open details: exact visual naming of all panel variants and final command mapping to remote doors/cannons.

## Push subsystem

Confirmed runtime facts:

- capacity: 12 records
- record stride: 6 bytes
- record `+0x00` stores object index/reference
- record `+0x04` is a runtime state byte
- object lookup uses the 28-byte object stride (`index * 0x1C`) in the observed Win16 build
- movement countdown 8 is observed

## WARP subsystem

The WARP classes are not independent scripts; several families share helpers.

### `WARP_L1..L4`

These use a common colored-key gate. The class value is converted to a key bit, then the shared teleport helper is called after a successful inventory check.

Status: HIGH / ~95%.

### `WARP_S1/S2`

The player state byte/mask at `DAT_1048_4C45` uses bits `1,2,4,8` for four pentagrams (red, green, blue, yellow).

- `WARP_S1` requires mask `0x0F`.
- On success it resolves the matching `WARP_S2` destination and calls the shared teleport helper.
- `WARP_S2` displays the broken-mirror result and does not provide a symmetric return.

Therefore the retail behavior is a one-way `S1 -> S2` portal.

Status: CONFIRMED / ~98%.

### Remaining WARP families

- `WARP_1..8`: mechanics mostly recovered; exact UI-option naming/orientation after transfer remains open.
- `WARP_E1..E8`: floor/elevator family mostly recovered; per-floor availability bits still need final naming.
- classes `0x25..0x2C`: executable paths exist but appear unused/reserved in retail data; keep marked PARTIAL.

## Trigger/remote control chain

- wall classes `0x47` and `0x48` carry derived property bit `0x40`.
- crossing/activating them enters a trigger handler.
- remote door classes and control-panel handling exist as distinct runtime systems.

The next target required for full closure is the exact mapping:

`TRIGGER1/2 -> CONTROL command/group -> remote door (vertical/horizontal) / remote cannon state`.

## Lookup helpers

Recovered meanings:

- `FUN_1010_22e8(class,start_id)`: find wall ID by wall class, wrapping search to zero.
- `FUN_1010_234c(class,start_id)`: analogous object-class lookup.
- `FUN_1010_2390(class)`: find runtime object variant/ID for requested class; emits `No objects of class ...` on failure.
- `FUN_1010_23da(class)`: scans current 64x64 map and returns the highest wall ID of the requested class actually present in the level.

## Runtime record sizes recovered

| System | Size / capacity | Status |
|---|---|---|
| Door | 22 B, 64 | CONFIRMED |
| Panel/control | 22 B, 32 | CONFIRMED |
| Push | 6 B, 12 | CONFIRMED |
| Guard | 26 B, 100 | CONFIRMED stride/capacity, field naming PARTIAL |
| Object (observed Win16 build) | 28 B stride | CONFIRMED for analysed build |

Known guard fields include timer at `+0x06`, object link at `+0x08`, state/next-state around `+0x0B/+0x0C`, sequence-definition index at `+0x0E`, and a damage-decremented strength/health candidate at `+0x10`.

## Diagnostic strings confirming separate subsystems

The executable contains distinct failure paths including:

- `Door not in map`
- `Push not in map`
- `Wall class %d undefined`
- `Obj class %d undefined`
- `No objects of class %d in level`
- `No seqdef defined for guard`
- `Guard not in map`
- `Object not in map`
- `Vector not in map`

This is strong evidence that doors, pushes, guards, objects and vectors are independent runtime arrays/records rather than aliases of one generic structure.

## Current closure estimate

These percentages describe reverse-engineering completeness, not implementation completeness:

- wall-property generation: 97-98%
- curtain doors: 100%
- level exits: 100%
- door subsystem: 97-98%
- main USE dispatcher: 94-96%
- `WARP_L1..L4`: ~95%
- `WARP_S1/S2`: ~98%
- control/panel subsystem: ~92-95%
- trigger/remote-command mapping: ~80-90%
- guard AI state machine: substantially lower; still a major open area
- renderer internals: substantially lower; vector/span semantics remain open

## Priority queue

1. Close `TRIGGER1/2 -> CONTROL -> remote doors/cannons`.
2. Recover animated-wall timer units, loop/one-shot semantics and final-frame collision/map updates.
3. Resolve remaining special USE classes (`0x03..0x06`, `0x08`, object `0x26..0x29`).
4. Finish guard state/strategy/strength naming and difficulty-dependent damage/HP tables.
5. Finish OBJECT field naming and reader/writer map.
6. Continue vector renderer reconstruction.

Do not promote a hypothesis to a named enum/field without executable/data evidence. Keep uncertain values explicitly marked as `Unknown`, `Reserved`, or `Candidate`.


## 2026-09-25 Win16 MFC / memory synchronization

The current repository now contains the relocation-aware Win16 MFC reconstruction and its modern compatibility layer. Canonical entry point: `docs/WIN16_MFC_RE_SUMMARY.md`. Static artifacts cover `CRuntimeClass16`, 31 runtime classes, CWnd layout/vtable/lifecycle anchors, HWND/HDC/HGDIOBJ/HMENU HandleMaps, evidence levels and explicit coverage states. Runtime validation remains separately tracked and requires the Win3.1 debugger checklist/capture template. The modern C++20 layer now includes `HandleRegistry`, `NativeHandleWrapper`, `WindowWrapper`, `WindowRegistry`, nested/RAII temporary scopes and the recovered z-order mapping. Historical 16:16 pointers, NE fixups and raw MFC object layouts are evidence only and are not reproduced as the x64 ABI.
