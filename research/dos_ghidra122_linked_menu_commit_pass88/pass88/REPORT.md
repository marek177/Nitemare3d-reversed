# Pass88 — original menu indirect callback linked to native config commit

Confirmed, High confidence in isolated instruction fixtures: native menu → original indirect far callback → original staged config commit executes across all six distinct supplied DOS EXEs. After any tested non-Escape edit, the actual config block reflects callback conversion, and subsequent Escape does not roll it back. Supplied1.8/1.9 are identical. Hardware side effects, UI rendering/input and actual disk persistence remain mocked or outside scope.

## What is now linked
Pass87 mocked the indirect callback; pass86 tested it in isolation. Here the original CALLF [ES:SI+6] executes, reads the original relocated record callback pointer, enters the correct original commit routine, walks all native records and copies the16-byte result into config. The harness counts entry at that native target and asserts exactly one invocation for a non-Escape tested key and zero for immediate Escape. It does not replace or manually invoke the commit routine.

All four labels Mouse,Joystick,Music,Sound FX are exercised. Record data are original relocated MZ bytes, except the selected signed word and explicit selection flags: previous records' byte+4 is cleared and selected byte+4 set1 to select the target without mocking navigation behavior as if it were tested. No real menu initialization or device availability is implied by these flag fixtures.

## Results
1008 cases =6 binaries ×4 selected records ×7 initial signed values(-32768,-100,-1,0,1,100,32767) ×6 keys(left4b,right4d,space20,Enter0d,unknown7f,Escape1b). Non-Escape keys are followed by Escape to end the loop. Left/right original editing, sign toggle and unknown-key callback reach native commit; all four record values are converted into their magnitude/enable bytes. Full16-byte config is asserted, including preserved width/other bytes and converted nonselected record values from native data. On immediate Escape, initial config stays unchanged. After an edit followed by Escape, changed config stays committed.

This disproves an assumption that Escape in this routine always discards previous edits. It does not prove persistence to CONFIG.SAV or behavior of an outer menu controller, since this test returns only from the native inner menu. The original save dispatcher and DOS I/O are separate earlier experiments; they are not composed into this harness.

## Boundaries and recovery detail
Mocks: native menu font/render/key/navigation helper callsites; commit's five side-effect callsites. Original record lookup, edit branches, indirect pointer call, commit conversion/copy and native returns run unchanged. Side effects can alter real hardware/global behavior absent here; no hardware parity is claimed. Initial config sentinel fixture is explicitly set, not loaded by full startup. DS=SS,DF0,SPe000. Test asserts returned AL6 and restored SP, exact edited word, callback observation/entry count and full config result.

Some Ghidra commit function bodies omit tail callsites (notably1.1). Therefore side-effect hook coverage uses the complete original-byte instruction list recovered by Capstone in pass86, ending at native RETF; it does not trust the shorter Ghidra body. This matters even when Ghidra reports successful decompilation. The included copied Ghidra12.2 menu and commit C exports retain provenance from passes87/86; no new Ghidra run is claimed for88. Input metadata includes original EXE SHA256 and exact commit bytes/calls.

## Reproduce
Extract included pass76 dependency and nested baseline58 dependency to baseline58/. Run python scripts/verify_linked_menu_commit.py using Unicorn2.1.4 and included pass88/evidence/input_locations.json +menu TSVs. Expected168 passed per binary. Script regenerates linked_menu_tests.json. No actual host filesystem file is changed by the test.

Unknown: real input/render/navigation, actual initializer and disabled-item availability, commit hardware effects, outer acceptance/cancel/save flow, real DOS persistence and full parity. Next: link paired native initializer and outer dispatcher to this chain, and identify side-effect helpers by original behavior.
