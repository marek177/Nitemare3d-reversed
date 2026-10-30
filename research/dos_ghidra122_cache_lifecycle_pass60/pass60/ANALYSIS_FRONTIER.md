# Nitemare3D DOS analysis frontier — pass60,2026-10-30

Scope: supplied DOS1.0,1.1,1.2,1.5,1.7,1.8,1.9. The last two are byte-identical supplied images, represented by DOS18. This registry does not claim that every function is unknown or that other parallel DOS2.0/Win16 projects have the same status.

The restored runtime-correct Ghidra12.2 database contains3469 function entries and773 computed call/jump sites across six images. Of these sites686 have no destination in the instruction's static getFlows() array. Indirect API calls and table dispatch are expected; these numbers are a triage inventory, not missing-function counts, game bugs, or completeness percentages. Each .functions.tsv and .computed_flows.tsv is a reproducible per-build list. priority_candidates.tsv ranks functions needing target review in this pass, not functions proved never analyzed elsewhere.

| Priority | Open question | Evidence already available | Next discriminating action |
|---|---|---|---|
|P0|Segment context after dynamic DS/ES changes|Runtime DS verified, DS/SI-preserving XMS wrapper verified; some xrefs remain incomplete|Compare operand bytes and context at POP DS/PUSH SS paths; correct local DS/SS context only with evidence|
|P0|Real sound IDs, sizes and alias constraints|SND transfer, cache, negative-offset preparer and original store tested|Recover actual SND.DAT/resource-table producer, test real same-offset aliases and lengths|
|P0|Full sound-request chain|Individual dispatcher/backend request/cache/SND/XMS contracts preserved in prior passes|Run one enabled request through original chain with actual asset bytes; keep manager/audio boundaries explicit|
|P0|Renderer and viewport remaining branches|Earlier isolated render/projection/palette contracts retained in pass history|Use computed-flow inventory to locate unresolved game-code dispatch; trace unknown producer/consumer before more parity tests|
|P0|Gameplay state, projectiles and scheduler|Not expanded by this pass|Select unreviewed game functions from call/field evidence, distinguish CRT helpers and data from game code|
|P0|SAVE/LOAD first-state/frame and DEMO parity|Not measured by this pass|Original full-game controlled replay with matched assets, inputs and state snapshots|
|P1|Higher-level XMS lifecycle coordination|Mode1/2/3 original code tested in pass60: repeated unlock/free, reset and DOS1.0 backreference difference|Trace callers for re-entry guards and resource-source-offset restoration after reset|
|P1|Capacity reporting above32767 KiB|Original AH08-wrapper result interpreted signed by caller; conditional disable verified|Compare with actual installed manager policy and free-block reports; do not infer all high-RAM setups fail|
|P1|Remaining computed calls/jumps|773 sites catalogued,686 without getFlows targets|Classify API entry, vtable/table dispatch, switch and bad decoding; resolve targets from data and callers|

Completed local questions in this pass: successful initialization bounds64..2048 KiB; failure state transitions; original multiplex/manager wrappers at controlled boundaries; DOS1.0 fixed8192 vs later byte-product record store; negative-offset update and low-byte boolean return.

Do not repeat already confirmed cases as new semantic progress. Re-run only after changes or when removing a mock/boundary. Never equate successful C generation with a correct signature, complete CFG, or full-game1:1 parity.

Pass60 local completion:768 scenarios, each with two original routine invocations. Mode2 preserves payloads and resource offsets while resetting cache metadata/used count. Global re-entry and asset lifetime remain open.
