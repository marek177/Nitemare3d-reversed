# Win110 pass 70 — original virtual runtime-class ancestry

## Finding
Confirmed / High: original 1000:068A distinguishes the two static exception objects by virtual metadata getter and walks metadata +0C. This differs from the startup registry chain at +0E. 196,618 original-code microexecutions passed without function stubs.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Obtain object table with LES BX,[DI], invoke far slot zero with object argument | 1000:0692–0695 | High |
| Confirmed | Compare nonzero descriptor against requested near pointer; follow descriptor+0C on mismatch | 0698–06AF | High |
| Confirmed | 41BC table48E4 getter453C returns0514; chain0514→0500→04EE→0 | Raw tables, original getter, exhaustive target checks | High |
| Confirmed | 41C2 table48F8 getter457C returns0524; chain0524→0500→04EE→0 | Same | High |
| Confirmed | Exception base table48D0 getter441C returns0500; chain0500→04EE→0 | Same | High |
| Confirmed | Zero target never matches the terminating zero node | All three exhaustive sweeps | High |
| Confirmed | Changing +0E to FFFF does not change tested ancestry outcomes | Ten additional original-code cases | High |

Raw data locations are NE10 file base2C040 plus node offsets. Node0500+0C contains04EE; 0514+0C and0524+0C contain0500;04EE+0C is zero. Preserved getter annotations identify04EE=CObject,0500=CException,0514=CMemoryException,0524=CNotSupportedException. Class names are prior static evidence, while exhaustive behavior verification is new in this pass.

## Behavior model
`p = object.virtual_slot_0(object); while(p != 0) { if(p == requested) return 1; p = word[DS:p+0C]; } return 0;`

No null-object guard or cycle guard exists in the captured 068A instructions. Valid object/table and acyclic metadata are preconditions of the tested model; invalid-object faults and cyclic hangs were not tested. AX is exactly0 or1; RETF4 consumes both near arguments. SI/DI/BP restore; an entry stack D000 returns at D008.

The exception handler 1000:3CEA actually calls068A with target0514 at3D3C. A match selects constantsF10A and1030 before callingA344. A nonmatch tests0686 at3D53; that second class and the real UI/import behavior were not executed here. This establishes a static consumer of the memory-exception type without claiming that Windows message handling was reproduced.

## Verification
Run `python3 pass70/verify_class_ancestry.py` after unpacking; requires Unicorn2.1.4. Every one of65,536 requested descriptor words is tested for each of the three tables (196,608 cases), plus10 registry-link independence checks. Code bytes for068A and all three invoked getters are cross-checked against the preserved Ghidra12.2 listing and raw EXE. No instruction patches or function stubs are used.

Mapping: code CS2000; DS1048; SS4000; vtable segment mapped at5000 to avoid real-mode overlap with DS. Only three slot-zero selector words are normalized to2000, and supplied object table selectors to5000. Table offsets for41BC/41C2 are the final constructor values verified in pass69; constructors are not rerun here. The base exception object at7000 is a synthetic fixture. Original EXE SHA256:12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.

An initial fixture incorrectly paired base CObject table48BC with expected CException metadata0500. The original getter returned04EE and rejected that expectation; the corrected base CException fixture uses48D0/441C. All reported results come from the corrected full run.

No fresh Ghidra database export or actual Windows/game execution occurred.

## Implementation-ready findings
Keep metadata base-class link at+0C separate from registry-next at+0E. Test pointer identity through the base chain, including CObject. A null requested type returns false. Do not classify sibling exception types as each other.

## Unknowns and next test
Resolve target0686 in the3CEA fallback and trace the selected constants throughA344. Execute a controlled real Win16 exception path before claiming Windows UI or lifecycle parity.

Confidence: High for original getter/ancestry behavior under declared segment normalization; Windows reachability and UI behavior remain Unknown.
