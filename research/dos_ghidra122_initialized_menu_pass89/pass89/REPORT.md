# Pass89 — native initializer → menu → indirect commit → accept/cancel status

Confirmed, High confidence within synthetic config/input fixtures: all six distinct supplied DOS EXEs execute original subdialog initializer, original menu, native indirect record callback and original staged config commit together. Supplied1.8/1.9 are identical. Rendering/input/hardware callees remain mocked. No disk save or outer dispatcher is executed here.

| Build | Initializer entry |
|---|---|
|1.0|1cdc:1eb0|
|1.1|1d00:1e94|
|1.2|1d00:1e96|
|1.5|1d05:1e94|
|1.7|1d0f:1e90|
|supplied1.8/1.9|1d25:1ec4|

## Native initialization and normalization
For each Mouse/Joystick/Music/Sound FX pair, initializer reads magnitude byte and enable byte from config. Any nonzero enable produces positive magnitude; zero enable negates it. Signed words are written into original record+2. No synthetic signed menu value replaces this conversion in89. Tests assert all four initialized words before entering native menu.

A zero magnitude cannot preserve enabled status through this representation: enabled1/2/255 plus magnitude0 produces signed0, and native commit uses signed>0 to write enable0. More generally nonzero enable bytes2/255 normalize to1 on callback when magnitude>0. On immediate Escape without callback, original config bytes retain their noncanonical enable values. No claim is made that every such config byte combination is normally produced by UI; they are explicit boundary fixtures.

## Acceptance versus committed state
Original Done type1 with Enter/Space sets menu exit state, invokes native commit through its original far pointer, returns record ID15h, and initializer returns low-byte1. Original Escape returns menu code06h, initializer returns low-byte0. This accepted status does not imply rollback: an earlier Mouse edit or even an unknown non-Escape key has already dispatched native commit, and subsequent Escape leaves resulting config in memory.

Thus low-byte acceptance and committed state must be modeled separately. Unknown key7fh dispatches callback without changing the current record. For Done selected, right4dh does not edit (type1), but still invokes callback; later Escape returns0 with normalized config. This test does not prove that an outer menu saves immediately on Escape; the outer dispatcher remains outside this run.

## Verification
960 cases =6 binaries ×4 uniform magnitudes(0,1,100,255) ×4 uniform enables(0,1,2,255) ×2 selected records(Mouse/Done) ×5 keys(Escape,unknown7f,Space,right4d,Enter). Nonexit actions are followed by Escape. Original native records are retained, but selectability flags are explicitly set to select Mouse or Done, avoiding any claim of tested navigation/device availability. Input16-byte config is explicit; full startup/load is not run.

Assertions cover all four initializer values, native commit entry count, exact full16-byte resulting config, accepted low byte and restored SP. Native initializer→menu call and menu→indirect commit are not mocked; commit's side-effect calls and font/render/key/navigation calls are mocked. Exact relocated EXE hashes and callback bytes are retained in input metadata from87/86. DS=SS,DF0,SPe000.

Fresh Ghidra12.2 exports decompile all six initializers. Complete initializer callsite discovery uses Capstone over original MZ bytes because prior1.7 Ghidra body omitted tail calls; native execution does not trust decompiler completeness. Menu TSVs copied from87 are separately named to retain provenance. Decompilation success does not prove full semantics.

## Reproduce / next
Extract included pass76 and nested baseline58 dependency to baseline58/. Run python scripts/verify_initialized_menu_commit.py with Unicorn2.1.4 and included pass89 evidence files. Expected160 passed per binary. Capstone-derived initializers.json already contains exact byte discovery used by harness. Ghidra script/seeds reproduce initializer exports read-only against pass76/project N3D_Runtime54/inputs.

Unknown: outer dispatcher persistence/loop interaction, real OS writes, actual input/render/hardware callees, availability flags and whole-game parity. Next link native outer dispatcher and native save to resolve whether an edit followed by Escape later reaches CONFIG.SAV.
