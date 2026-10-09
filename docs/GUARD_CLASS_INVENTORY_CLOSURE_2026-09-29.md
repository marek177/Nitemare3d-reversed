# GUARD class inventory closure — shipped retail reachability — 2026-09-29

## Result

The shipped GUARD class inventory is now closed at the **class/reachability** level.

The executable accepts/scorers classes through GUARD25 (`OBJECT+06 = 0x20`), while editor/MAP data contains GUARD26/Dancers at class `0x21`. The two apparently awkward slots now have distinct explanations:

- **class 0x14 / GUARD13** — internal Dracula-Bat transform only; no retail MAP class-table assignment;
- **class 0x20 / GUARD25** — executable-only fallback slot; no shipped MAP class-table assignment and no recovered dynamic class writer;
- **class 0x21 / GUARD26** — real retail Dancers class, Episode-1 object ID `0x8C`, one supplied E1 map placement, scripted by the Radio/ACTIONSPOT path.

This supports **100% shipped-retail GUARD class reachability inventory**. It does not identify a hypothetical pre-release graphic/name for the unused GUARD25 slot.

## MAP/class-table audit

Across the supplied class-table inventory for DOS/Win episode data and the available versioned E1 packages:

- retail guard classes represented by object class-table assignments cover `0x08..0x13`, `0x15..0x1F`, and `0x21`;
- **no row exists for object class `0x14`**;
- **no row exists for object class `0x20`**;
- class `0x21` is consistently mapped to editor family **GUARD26**, object ID `0x8C`, name **Dancers**.

The absence of `0x14` is expected because the executable creates it dynamically from Dracula class `0x11`.

The absence of `0x20` is different: no equivalent dynamic writer has been recovered.

## Dynamic OBJECT-class writer audit

Known relevant class-changing writes in the audited Win16 core include:

- Dracula lethal special: `OBJECT+06 = 0x14`;
- exploding-wall runtime conversion: `OBJECT+06 = 0x2D`;
- normal spawn/class initialization copies the class derived from the current map/object definition.

A targeted literal-writer scan found no `OBJECT+06 = 0x20` producer in the audited Win16 1.3/1.6/1.8 state/gameplay exports.

A superficially similar `+06 = 0x20` write in the GUARD movement code is **not OBJECT class**: it writes the 16-bit GUARD countdown at `GUARD+06` during the strategy-1 door maneuver.

Therefore the executable contains support for class `0x20`, but the shipped retail graph does not create it through either class tables or the known runtime transform paths.

## GUARD25 / class 0x20 fallback profile

If class `0x20` is injected manually, the existing generic code still gives it a coherent fallback actor profile:

- fresh strength / HP: 255;
- default spawn profile: state 7, next state 2, strategy 0;
- no class-specific resistance entry in the `0x0C..0x1F` damage transform switch, so it uses the generic path;
- score switch value: 50;
- no dedicated entry in the three recovered class-specific GUARD sound selectors, therefore selector 0/default behavior;
- no shipped MAP placement;
- no recovered dynamic class writer.

The correct shipped-game classification is therefore **executable-only / cut-or-fallback guard slot**, not a hidden retail enemy and not a boss.

A future discovery of orphan IMG/SEQDEF material might reveal a pre-release visual identity, but that would be historical asset archaeology rather than a change to shipped reachability.

## GUARD26 / class 0x21 Dancers

Class `0x21` is explicitly present in the Episode-1 object class table:

```text
OBJECT ID 0x8C -> class 0x21 -> GUARD26 -> Dancers
```

The supplied class inventory records one E1 map cell using this ID. Available DOS and Win E1 distributions preserve the same mapping.

Runtime initialization gives class `0x21` the special state/next-state profile `0/0`. The Episode-1 Radio/ACTIONSPOT script is the active behavior path associated with the dancers sequence:

- the Radio path is gated to E1M9;
- eligible actors are moved into scripted state `0x14` with timer `0x70`;
- presentation/sequence state is swapped for the dance sequence;
- the restore branch returns affected actors from state `0x14` to state `0x06`.

GUARD26 is outside the GUARD1..25 score switch, so it uses the default zero-score result.

## Final shipped inventory classification

| Class | Inventory status |
|---:|---|
| `0x08..0x13` | retail guard classes |
| `0x14` | internal Dracula-Bat transform only |
| `0x15..0x1F` | retail guard classes |
| `0x20` | executable-only fallback/cut GUARD25 slot |
| `0x21` | retail scripted GUARD26 / Dancers |

## Coverage boundary

### Closed at 100%

- which GUARD-number/class slots are represented in shipped retail class tables;
- which special class is generated internally (`0x14`);
- which executable slot has no shipped producer (`0x20`);
- GUARD26/Dancers class and object ID (`0x21`, `0x8C`);
- GUARD25 fallback runtime profile if manually injected;
- score inclusion/exclusion boundary: GUARD1..25 switch through `0x20`, GUARD26 default zero.

### Still outside this inventory claim

- hypothetical pre-release name/art for class `0x20`;
- complete IMG/SEQDEF/SND archaeology for unused/orphan assets;
- full behavior/state timing of each retail enemy class.

Therefore **GUARD class/object inventory = 100% for shipped retail reachability**, while historical cut-content identity remains intentionally unknown.
