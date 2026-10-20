# v0.76 — DOS2 DEMO RNG equality versus timing context

Date: 20 October 2026. Source integration and derived-data validation; no new
original gameplay execution or original-versus-port acceptance in this update.

The archived D02-E and D02-F reports extend the earlier 35-draw checkpoint.
D02-D source runs 13 (fixed 3000) and 12 (fixed 7000) report 229 and 220
completed shared-wrapper outcomes. All 220 common caller/state/result tuples
match, while their scheduler and input contexts diverge.

| Anchor | Fixed 3000 | Fixed 7000 | Evidence boundary |
|---|---|---|---|
| RNG 210 | A047, state F65F3A93, scheduler visits 1049, record 263 | Same | Local synchronization anchor, not whole-RAM equality |
| RNG 211–216 visits | 1051 | 1059 | Outer-scheduler calls; not eight extra simulation ticks |
| RNG 217–218 visits | 1055 | 1059 | Due-gate decisions not fully captured |
| RNG 219–220 record | 267, key/mask 0000/0000 | 273, key/mask 0000/0088 | Same RNG under different input context |
| Stop checkpoint | 1074 entries, 1073 returns, 275 unique records | Same | Maximum recorded depth 1; 276 stores include a post-EOF store |

The last common RNG state is `3807D88D`. The extra reference groups are draws
221–225 (`85AD + 9FE3×4`) and 226–229 (`85AD + 9FE3×3`), both at visits 1071,
record 273. Static source evidence ties `5F74→8590→85AD` to damage and
`5FA3→5FAD→9FB4→9FE3` to its lethal/variant-selection path. Known literal
handler callers are hitscan `6A2F` and projectile `8125`.

These groups are consistent with two lethal-path invocations. They do not
identify two different actors, an executed hitscan/projectile caller, or a
permanent missing effect. Events could occur after the sampled checkpoint.
The first differing clock/due/input decision remains OPEN.

## Tool and validation

`tools/n3d_d02e_audit.py` imports the source original-EXE audit, preserving its
SHA gate, 20 opcode windows and literal-call-pattern census. Integration adds
per-run ordinal/LCG/result/completeness checks, so identical corruption in both
exports cannot pass merely because the two streams agree. Empty context-diff
lists now fail cleanly. The unchanged imported script is archived separately.

11 synthetic robustness tests pass, including shared corruption, incorrect
results/ordinals, missing instruction outcomes, wrong assets, context crossing
and changed literal-call links. These test the verifier, not original execution.

```sh
python3 -m unittest discover -s tests -p test_n3d_d02e_audit.py -v
python3 tools/n3d_d02e_audit.py --exe /private/N3D-UNFU.exe \
  --evidence /private/N3D_REMAX_D02D_ORIGINAL_RUNTIME_EVIDENCE.json --output audit.json
```

The original EXE and D02-D JSON were unavailable in this integration. The
source's original-static and 229/220 runtime-derived claims are attributed to
its reports; they have not been independently rerun here. Archive-package
materialization was unavailable, so no uninspected renderer component installer
or raw capture was imported.

## Next discriminating proof

Capture both original runs from before visits 1049 through a defined post-EOF
window, recording actual BEB4/BEF4/C1A8 due-gate operands, old render generation,
applied input, scheduler invocation IDs, hit caller, actor pointer and HP.
Identify the first executed differing decision before comparing the port.
Full RNG indirect-call coverage, timing and framebuffer/audio parity stay OPEN.
