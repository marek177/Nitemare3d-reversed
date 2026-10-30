# Pass90 — native outer dispatcher through menu commit to CONFIG.SAV DOS write

Confirmed, High confidence for explicit modeled input/OS fixtures: all six distinct supplied DOS binaries execute outer dispatcher → native settings initializer → native inner menu → original indirect callback → native config commit → native config save → native CRT → DOS write request. Supplied1.8/1.9 are identical. This composes previously separate evidence from84/85/89. Real rendering/input/hardware and filesystem durability are not established.

## Integrated result
The outer selection provider returns23h to invoke the original settings subdialog. When the inner sequence is Mouse edit then Escape, subdialog returns low-byte0 and original outer loop continues. Provider then returns06h: native outer dispatcher exits through save. The original16-byte config payload at AH40 matches the committed edit, including any normalization of other enable fields. Escape from the inner menu therefore does not discard the edit before later outer exit/save in this tested path.

Done selected with Enter invokes native commit, returns15h from inner menu and acceptance1 from initializer. Outer dispatcher immediately calls save with no second selection. Immediate Escape without a preceding callback retains the initial config, which is still sent unchanged when the outer selection06h exits. Thus returning0 from the subdialog neither implies rollback nor prevents all later persistence.

No original save/CRT call is replaced here. The harness observes the exact DOS pointer/payload and supplies successful OS responses. It does not write a host file and does not claim a real DOS installation persisted bytes.

## Case matrix and assertions
144 cases =6 distinct binaries ×3 magnitudes(0,50,255) ×2 enables(0,1) ×4 scenarios: Mouse immediate Escape; Mouse right then Escape; Mouse Space then Escape; Done Enter. All four config pairs initially use the same selected profile; original initializer creates native record values. Selection flags explicitly choose Mouse or Done. Record data and callback pointers otherwise remain original relocated MZ bytes.

Assertions cover full initializer values, native indirect commit count, exact entire resulting config, restored SP, outer selection sequence([23h,06h] for inner Escape or[23h] for Done), exactly one original save call and one exact16-byte payload. DOS operation sequence is [AH3d open,AH44 IOCTL,AH40/CX0 truncate,AH43 attrs,AH40/CX16 write,AH3e close]; path must be lowercase config.sav, handle5. Payload equals independently calculated config expectation after all original conversions. 255 magnitude remains a legal byte fixture; right adjustment clamps it100, while sign toggle retains magnitude255.

## Boundaries
Mocks: outer menu render/selection helpers and unused alternate-subdialog site; initializer render helper; inner font/render/key/navigation helpers; five config-commit side-effect callees. Native initializer/menu call, indirect callback, original conversions/copies/returns, outer decision logic, save path helper and CRT open/truncate/write/close execute. DOS INT21 responses model existing regular writable file and successful full write/close. No create/error fixture is composed in90; those were isolated in84. Real device availability/input and menu navigation are not inferred from explicit selection flags. DS=SS,DF0,SPe000; initial config profile explicit, no full game startup/load.

## Evidence and reproduction
Input metadata retains original runtime EXE SHA256 and native callbacks; exact native outer/initializer/commit/menu instruction listings included. Fresh Ghidra12.2 read-only exports decompile outer+save for all6 binaries (12 functions). Menu listings come from87, initializer full-byte recovery and commit metadata from89/86. These original instructions are executed by Unicorn2.1.4. Successful Ghidra decompilation does not imply complete listing or semantic recovery.

Extract included pass76 dependency and nested baseline58 dependency into baseline58/. Run python scripts/verify_outer_menu_save_chain.py with included pass90 evidence files. Expected24 passed per binary. Script regenerates outer_save_tests.json. Ghidra script/seeds reproduce fresh exports using pass76/project N3D_Runtime54/inputs, readOnly/noanalysis.

Unknown: real DOS persistence/error timing, hardware effects and real input/render behavior, full startup/device flags, other outer-menu paths and full parity. Config menu value/acceptance/payload chain is now verified at instruction level for these cases; next investigate actual Mouse/Joystick sensitivity consumers and hardware boundaries rather than repeat this same conversion path.
