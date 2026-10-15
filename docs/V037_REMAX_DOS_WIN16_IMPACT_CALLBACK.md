# RE MAX v0.37 — DOS/Win16 scripted projectile callback: AL ABI and MAP reachability

15 October 2026. Scope: **original static machine-code proof** over three SHA-pinned builds plus one identified original MAP.1–3 set. **No original game was executed. No full combat/timing/pixel parity claimed.**

## Direct original evidence

| Item | DOS v2.0 unpacked image | Win16 v1.10 NE3 | Win16 v1.8 NE3 |
|---|---:|---:|---:|
| Read object property into AL | 7FAF | 9B7D | 9ACF |
| Test property bit 0x40 | 7FB6 | 9B84 | 9AD6 |
| FAR script callback call | 7FBE → A982 | 9B8C → C356 | 9ADE → C2A8 |
| Test returned AL | 7FC6 | 9B94 | 9AE6 |
| E2M10 return MOV AL,1 | A97E | C351 | C2A3 |
| Non-E2M10 wrapper return | A99E (LEAVE; RETF) | C378 (XOR AL,AL; LEAVE; RETF) | C2CA (XOR AL,AL; LEAVE; RETF) |
| Class 4 → property 0x40 | 1239 | 25CF | 2583 |

Build identities:
- DOS v2.0 unpacked image, 171,360 B, SHA256 e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297.
- Win16 v1.10, 230,400 B, SHA256 12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.
- Win16 v1.8, 230,224 B, SHA256 144e96bb649c5463d440c343ad982ed8e5f143e788c9af08bbb890fcd1b3db22.

The Win16 far-call **segment operands are NE relocations**, not literal executable runtime CS values. Parsing original NE3 relocation chains confirms 9B8F (v1.10) and 9AE1 (v1.8) each target logical NE segment **3**. The DOS link-time far 083D:25B2 maps to load-image byte offset A982.

In the DOS no-match path, wrapper A982 only changes DX and CPU flags; it **preserves the AL property byte** loaded by 7FAF. With bit 0x40 present, AL remains nonzero, so the caller's special callback condition succeeds. Win16 explicitly clears AL on a no-match and continues to the ordinary wall/guard collision code; that later path may still report a collision. On E2M10 all three handlers return AL=1 **if the scripted handler returns normally**. Fault/abort and timing side effects are outside this local contract.

## Initial-map reachability, not dynamic impossibility

All three audited property builders set objectProperty bit 0x40 **iff objectClass=0x04**. In the **specific** SHA-pinned original MAP set below, exactly **12 starting cells** have class 4, all E2M10 object ID 0x61:

- MAP.1 SHA 3eddb0ad3a29e93d63fa16e9b8cfbb434d3699a84bd5372ed2d6f4a1e89c42fc: 0 class-04 initial cells.
- MAP.2 SHA 938b7e79c9881eab71fdef4b7afa9b0482c870c808785f599a4ba52093d44756: 12 class-04 cells, all E2M10.
- MAP.3 SHA 0008775106854b3e9302f36fbcd7001607bcf2fd26cc9d8db6bccc732ead4217: 0 class-04 initial cells.

E2M10 coordinates (zero-based): Y37 X49–52; Y38 X50,52; Y39 X50,52; Y40 X49–52. Initial retail-map triggering of the **non-E2M10** DOS-vs-Win callback difference is therefore absent in these 31 unmodified level blocks.

Remaining **static RE tasks**: complete XREF/data-flow census of dynamic object ID 0x61 writers, atypical SAVE restore behavior, indirect callers, and post-callback normal WALL/GUARD acceptance. Modified maps can expose the difference without new game code.

## Reproduction and proof boundaries

Companion separate research archive N3D_REMAX_V037_IMPACT_CALLBACK_STATIC_CLOSURE_20261015.zip contains:
- tools/n3d_v037_callback_audit.py: SHA-256-gated original verifier, **36 opcode windows**, two NE relocation-chain checks, and 31 MAP-block census;
- tests/test_n3d_v037_callback_audit.py: 12 synthetic checks + one opt-in original-input audit;
- evidence/v037_original_static.json: derived provenance and witnesses, **no commercial bytes**;
- the C++ reference and regression mirrored in this branch.

Executed locally: 13/13 Python checks PASS with original files; 12/12 synthetic without originals; isolated C++20 g++ test PASS. The public repository does not redistribute original EXE/MAP or the companion ZIP; its C++ test checks an inferred local contract, NOT original runtime. No overall estimated parity percentages are raised.
