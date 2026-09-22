# Nitemare 3D consolidated reverse-engineering update — 2026-09-22

This document records the current consolidated state from the Nitemare3D reverse-engineering threads and repository audit. It is intentionally evidence-oriented: values promoted here are backed by original NITE3W.EXE flow, original MAP/IMG/WALLS/OBJECTS/SND/UIF data, save-layout evidence, or direct original-game behaviour. Older guesses that conflict with newer evidence are superseded.

## Closed or near-closed systems

### Runtime record sizes and capacities

Direct indexing/boundary evidence supports:

- OBJECT: 28 bytes, capacity 350, base 0x6D66, count 0x7E58.
- GUARD: 26 bytes, capacity 100, base 0x93AE, count 0x7E5E.
- Door: 22 bytes, capacity 64, base 0x9DD6.
- Panel/control: 22 bytes, capacity 32, base 0xA356.
- Push: 6 bytes, capacity 12, base 0xA616.
- VEC: 28 bytes, capacity 1000.
- VECLIST: four orientation arrays, 333 far pointers each.
- Visible wall spans: 20 bytes, capacity 50.
- Projected sprite commands: 18 bytes, capacity 100.

Old OBJECT=80 B / GUARD=98 B / wall-span=52 B estimates are obsolete.

### Wall property preprocessing

The executable derives a byte property table for all 256 wall IDs. Confirmed bits:

- 0x01: world/geometry-related property; exact high-level label still partial.
- 0x02: collision-relevant wall/cell.
- 0x04: static/interactable hard block.
- 0x08: door family, classes 0x31..0x40.
- 0x10: projectile/explodable-wall special branch, classes 0x2E..0x2F.
- 0x40: trigger-on-passage branch, classes 0x47..0x48.

This resolves the old ambiguity around 0x3F and 0x40: they are the final two door classes, DOORVC and DOORHC (curtain vertical/horizontal), not renderer limits or dimensions.

### USE/ACTION dispatcher

Input bit 0x0200 is USE/ACTION and is edge-triggered. The central interaction path resolves the adjacent cardinal cell and dispatches roughly as follows:

1. If the derived wall property has 0x08, process a door record.
2. Otherwise process level exits (class 0x09 LEVEL_UP, 0x0A LEVEL_UP2).
3. Classes 0x0D..0x2C enter the WARP/special-passage dispatcher.
4. Object class 0x03 enters the panel/control path and emits event 0x27.
5. Remaining special wall/object classes are handled by dedicated branches.

Known door checks include colored-key state, ID-card state and remote-door rejection of ordinary manual USE.

### Level exits

- class 0x09 = LEVEL_UP: advance the zero-based level index by one.
- class 0x0A = LEVEL_UP2: advance by two.

These are considered functionally closed.

### WARP families

Important correction: WARP_L1..L4 are not four unrelated teleporter scripts. They participate in a generic key-gated passage/warp path; the color/key selection is derived from the class and the common transfer helper is called only after the gate succeeds.

WARP_S1/S2 are substantially closed:

- a four-bit mask stores Red/Green/Blue/Yellow Pentagram acquisition;
- all required bits = 0x0F;
- WARP_S1 refuses activation until the four required pentagrams are present;
- after success it routes through the common transfer helper to the WARP_S2 endpoint;
- WARP_S2 is the broken-mirror side and does not provide the symmetric return path;
- therefore the supported model is a one-way S1 -> S2 special portal.

WARP_1..8 and elevator groups are structurally known but still need final per-destination/orientation/UI naming proof.

### Door system

Supported runtime model:

- 64 records, 22 bytes each;
- states 0..3 are observed;
- movement step 2;
- countdown/auto-close logic exists;
- obstruction checks exist;
- collision-property transitions are tied to door state;
- normal, colored-key, ID-card, remote-controlled and curtain variants share the common runtime family.

Remaining door work is mostly semantic: class-specific event naming and exact tick-unit interpretation.

### Pushables

Push class 0x28 uses 8 movement updates of 8 world units, exactly one 64-unit tile. The push runtime family is separate from doors/panels and has capacity 12 with 6-byte records.

### Panels / controls

The panel/control runtime family has:

- capacity 32;
- stride 22 bytes;
- separate storage from doors;
- up to four far pointers in the record;
- observed states 0/1/2;
- object class 0x03 USE path;
- event 0x27;
- completion/link cleanup and map/collision changes.

Still open: exact visual-variant names and complete command/group mapping to remote doors/cannons.

### Trigger classes

- class 0x47 = TRIGGER1.
- class 0x48 = TRIGGER2.
- derived wall property includes bit 0x40 and passage invokes a trigger handler.

Next closure target is the complete TRIGGER1/2 -> CONTROL -> DOORVR/DOORHR / cannon command chain.

### Explodable walls

Classes 0x2E/0x2F are the explodable-wall family (WALL_EX1/WALL_EX2) and receive wall-property bit 0x10. Projectile-wall handling has a dedicated branch. Earlier audit also identified the destruction path using SFX/event request 0x29 and transition into the destruction runtime state/class family; exact per-frame timing/completion cleanup is the main remaining item.

### Player movement / collision

Supported anchors:

- player X 0x4BF6, Y 0x4BF8;
- tile coordinates 0x4BF2/0x4BF4;
- world scale 64 units/tile;
- player AABB half extent 27;
- movement is subdivided and X/Y collisions are resolved separately, producing wall sliding.

### Health, ammo and difficulty

- player health 0x4C1D, normal 0..100;
- lethal normal damage clamps/writes zero before death flow;
- silver ammo 0x4C1F;
- laser ammo 0x4C20;
- wand ammo 0x4C44;
- active weapon 0x4C23;
- difficulty global 0x4C14 with values 0/1/2.

Difficulty evidence from independent paths supports easier/baseline/harder ordering: player->enemy damage is doubled/baseline/halved, enemy->player damage halved/baseline/doubled, with guard timing correspondingly slower/baseline/faster.

### GUARD / OBJECT model

OBJECT key offsets:

- +0x05 flags;
- +0x06 class;
- +0x07 associated GUARD index for guard objects;
- +0x0C/+0x0E map binding far pointer;
- +0x10/+0x12 world X/Y;
- +0x18 projected/view-space baseline used by damage math; not world Y.

GUARD key offsets:

- +0x06 timer;
- +0x08 OBJECT slot/index;
- +0x0A strategy;
- +0x0B state;
- +0x0C next state;
- +0x0D object/definition id;
- +0x10 strength/HP;
- +0x11 current octant;
- +0x12 result octant.

The state dispatcher accepts 0x00..0x15. State 0x15 is the confirmed pain/hit reaction. Remaining state names should stay conservative until their movement/attack/animation/sound XREFs are closed.

### Enemy strength, score and special cases

Normal GUARD creation initializes strength to 0xFF. No reliable class-specific spawn-HP table has yet been found; practical toughness is heavily affected by damage transforms and special phases.

The recovered score switch covers classes 0x08..0x20. Key special cases include:

- Dracula phase 1 scores 0 and transforms in place to class 0x14, strength 0xFF, state 0x08, next state 0x02, timer 1, sequence value 0x23, event/sound request 0x22.
- Penelope gives -1000.
- Dr. Hamerstein gives 1000.
- Cannon gives 0.
- class 0x20 / GUARD25 remains visually/unambiguously unresolved.
- GUARD26/Dancers follows a separate scripted route and is outside the normal score switch.

### Combat / weapons

Recovered active weapon selectors:

- 0 Single Shot Laser;
- 1 Magic Wand;
- 2 Silver Pistol;
- 3 Continuous Laser;
- 0xFF none/unset.

The audited player->GUARD damage producer uses a projected/view-dependent base plus RNG, then class/weapon transforms and difficulty. Therefore a universal fixed shots-to-kill table is not supported without fixing geometry, RNG, weapon and difficulty.

Special audited branches include Ghost/wand interaction, Alien rejection of wand in the producer, Penelope/Cannon normal-damage rejection, Baddie arithmetic reduction and Hamerstein's gated literal-damage branch.

### DEMO format

Supplied demos use a 6-byte WORD header and packed 8-byte events:

- byte eventByte;
- word inputMask;
- byte pad;
- dword timestamp.

DEMO.1 is behaviourally associated with the E1M11 attract setup. DEMO.2/3 source levels remain unproven and should not be guessed from suffixes.

### Renderer

The strongest current model is a projected vector/span renderer, not Wolf3D one-grid-ray-per-column DDA:

MAP -> exposed boundary extraction/merge -> VEC[1000] -> 4x VECLIST[333] -> camera transform / clipping -> projection -> per-column owner/occlusion -> <=50 visible wall spans -> wall raster -> <=100 projected sprite commands -> 320x200 indexed framebuffer.

The table at 0x58FE should not be called a conventional metric Z-buffer unless later evidence proves that interpretation.

## Highest-value open targets

1. TRIGGER1/2 -> CONTROL -> remote door/cannon exact command/group mapping.
2. ONE_SHOT activation and completion semantics.
3. SPECIAL1 dispatch variants.
4. Animated-wall exact frame delay, loop/one-shot completion and timer units.
5. Full GUARD state transition semantics and GUARD26+ scripted/cut uses.
6. Projectile ownership/lifetime and complete damage/death chain.
7. Remaining OBJECT/GUARD tail-field semantics.
8. RNG seed/order and deterministic main tick.
9. Complete SND.DAT event-to-resource map and original playback verification.
10. NITE3D.BSF consumer/validation algorithm across versions.
11. Remaining MAP header metadata and hidden/unused content audit.
12. Full renderer texture-U, flags and occlusion edge cases.

## Source-code update policy

Recovered facts should live in `src/re` or focused reconstruction headers until behaviour is sufficiently closed. Do not silently turn partial semantics into production gameplay names. Each constant/field should retain evidence comments where ambiguity remains.

The new `src/re/WallUseRecovered.hpp` is the canonical compact machine-readable summary for the newly closed wall/USE subset.
