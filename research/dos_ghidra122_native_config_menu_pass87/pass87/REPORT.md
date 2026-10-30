# Pass87 — native configuration menu labels, callbacks and editing loop

Confirmed, High confidence: relocated runtime MZ data across six distinct supplied DOS EXEs identifies actual configuration record labels and callback pointers. Labels1.8/1.9 share one identical binary. Native menu-loop instruction tests add252 cases. These tests mock indirect callbacks and UI/key helpers; pass86 independently executes the callbacks' conversion/commit logic. An unstubbed whole menu→commit→save integration remains Unknown.

## Actual record data
The data-segment global used by the commit routine already contains a relocated segment in each supplied MZ. This resolves pass86's synthetic-segment limitation for static layout, without claiming full startup initialization. Record offset1212h, stride12h, terminator byte0=0. Native records are in this order:

| ID | Native label | Magnitude config offset | Enabled config offset |
|---|---|---|---|
|0a|Mouse|+04|+08|
|0b|Joystick|+05|+0b|
|0d|Music|+06|+09|
|0c|Sound FX|+07|+0a|
|15|Done|—|—|

Thus magnitude and enable semantics are now tied to original labels. Exact sensitivity/volume scale and hardware effects still require consumer analysis. Labels are read through original far pointers at record+0e, not inferred from Ghidra auto-names. Every record, including Done, has the build's pass86 commit far pointer at+06. Record+02 is signed value; byte+04 marks selectable entries; byte+05 supplies item type. Mouse/Joystick/Music/Sound FX use type3, Done type1. Full raw18-byte records, far label pointers, callback addresses, segment-global offset and EXE SHA256 are in native_records.json.

| Build | Record segment | Menu loop |
|---|---|---|
|1.0|2ca8|1cdc:1936|
|1.1|2cdd|1d00:191a|
|1.2|2ce3|1d00:191c|
|1.5|3092|1d05:191a|
|1.7|309c|1d0f:1916|
|supplied1.8/1.9|30b5|1d25:194a|

## Original menu loop
For current type3 item: key4b/4d takes signed absolute value, subtracts/adds5 with16-bit wrap, then signed-clamps result to0..100. Space20h and Enter0dh negate the signed word, preserving16-bit wrap; they do not exit a type3 item. Unknown key7fh changes no value but still reaches callback. Escape1bh returns low-byte06h immediately and bypasses callback for that key. Earlier record edits are not rolled back by Escape in this tested routine.

After any tested non-Escape key the loop checks current record's far callback and invokes it if nonzero, before deciding whether to return for an exit item. Native records supply the original commit pointer. Therefore commit dispatch is not restricted to the Done item: edited type3 records dispatch it as well. Actual callback effects are not executed by this harness. Static original type1 branch sets exit flag on Enter/Space, then invokes callback before returning record ID. That Done behavior is statically supported, not part of the Mouse-only key execution fixtures.

Corner: -32768 absolute value wraps8000h. Left subtract5 wraps to32763 and clamps100; right adds5 remains negative and clamps0. Negating -32768 leaves-32768. These are instruction-level boundary results, not valid user-facing slider values asserted in actual gameplay.

## Verification
252 cases =6 binaries ×7 initial Mouse values(-32768,-100,-1,0,1,100,32767) ×6 keys(4b,4d,20,0d,7f,1b). Original menu and actual relocated record data execute; only selected word is changed as fixture input. Font/render/key/navigation helpers and indirect callback are mocked. Key provider supplies the tested key then Escape. Assertions cover final signed record word, exact callback count/value and return AL6. No navigation or actual input device is exercised. DS=SS,DF0,SPe000. The label audit verifies exact ID order and all native callback targets against pass86 locations; it reads relocated bytes directly.

Fresh Ghidra12.2 menu-loop exports included with full instruction listings. Decompiler success is not proof of full game semantics. audit_native_config_menu.py and verify_native_menu_record_keys.py reproduce native data extraction and252 cases with Unicorn2.1.4; extract included pass76 and nested baseline58 dependencies, retain pass87 source_locations.json supplied in bundle.

Next: run original indirect commit from menu loop, resolve paired UI initializer and accept/cancel flow, then trace callback side-effect callees. Rendering, hardware effects, true input behavior, whole menu persistence and full parity remain unverified.
