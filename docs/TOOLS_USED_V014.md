# Nitemare3D-Reversed v0.14 — tools and analysis workflow

Date: 2026-09-27

## Evidence rule

Listing a tool here does not mean it was used for every individual finding. Important conclusions remain tied to direct executable/data evidence, runtime behavior, or clearly marked inference.

## Static analysis and decompilation

### IDA Free 9.2
Used for disassembly, function discovery, XREFs, code/data separation, control-flow inspection, offsets/structures, call-site tracing and cross-version comparison.

### Ghidra / Ghidra exports
Used as an independent static-analysis/decompiler representation where Ghidra material is available. Agreement between tools is corroboration, not proof by itself.

## v0.14 deep-analysis passes

- Control Flow Graph (CFG)
- SSA-style value tracking
- Data Flow Graph (DFG)
- Use-Def / Def-Use chains
- liveness analysis
- pointer / alias analysis
- cyclomatic complexity
- dominator analysis
- natural-loop detection
- interprocedural call graph
- side-effect/global-state analysis
- cross-version matching
- assembler-to-C/C++ semantic reconstruction

## Dynamic and behavioral verification

### DOSBox-X
DOS runtime execution and behavior comparison.

### OTVDM
Win16 execution/verification on modern Windows where applicable.

### Cheat Engine
Targeted runtime observation of mutable values and hypotheses.

### Original gameplay and walkthrough material
Behavioral comparison, timing, map/script behavior and visible state transitions.

## Project-local tools

- `tools/ne_inspect.py`
- `tools/ne_renderer_audit.py`
- `tools/n3d_save_inspect.py`
- `n3d_inspect`
- project parsers, audit scripts and regression tests

## Reconstruction and build

- C / C++ — reconstructed/reference logic and tests
- CMake — project/test configuration
- SDL3 — modern display/runtime path
- vcpkg — Windows dependency management
- Python — binary/data inspection and reproducible analysis scripts
- Git / GitHub — versioned preservation of findings and code

## AI assistance

### ChatGPT by OpenAI
Used for analysis planning, interpretation of supplied disassembly/decompiler material, cross-session consolidation, pseudocode/C++ reconstruction, documentation, test generation and consistency checking.

AI-assisted conclusions are not automatically considered verified. Important findings should be checked against original executable instructions, original data, runtime behavior or independent tooling.

## Evidence labels

- `VERIFIED_EXE`
- `VERIFIED_DATA`
- `VERIFIED_SAVE_LAYOUT`
- `BEHAVIORAL`
- `INFERRED`
- `PARTIAL`
- `TODO`

## Per-function v0.14 target

For each important function/subsystem record function identity, platform/version, callers/callees, CFG, inputs/outputs, global side effects, data-flow chains, aliases, loops/dominators, complexity, structures/constants, cross-version matches, semantic reconstruction, verification method and remaining uncertainty.
