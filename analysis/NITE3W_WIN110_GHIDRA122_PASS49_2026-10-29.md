# Win110 pass49 — uploaded Ghidra database comparison

Confirmed, High: uploaded ghidra-n3d(1).zip SHA256 c65b3da070a6b4de11e3cc29357bfedfbbd13b0a5a9dcc318ef4a4015175d199 passes ZIP CRC and contains18 Program metadata records. Its Win110 executable SHA256 matches baseline48:12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Opened with Ghidra12.2 read-only after index rebuild and owner adjustment in extracted working copy; original ZIP unchanged.

Explicit function iteration gives969 internal Code entries and310 EXTERNAL-block entries in uploaded DB, versus1551 internal and310 EXTERNAL in baseline48. getFunctionCount returned1589 but iteration gives1279; those API totals must not be compared directly. The prior1589 headline was an API count, not internal function coverage. This pass uses explicit entry inventory and memory-block classification.

There are583 internal entry addresses only in baseline48 and one only in uploaded DB:1008:5A40. Baseline native listing assigns5A40 MOV AX,[BP-4],5A43 SUB AX,[BP-6], then common5A46 stack restoration to function59DC. Thus this uploaded-only entry is already covered code, not evidence of a new algorithm. This does not prove either function boundary ideal; original control-flow and calling convention need separate audit.

Three shared entries differ in body byte count:3C3D uploaded122/baseline66;4E24 uploaded105/baseline1057;59DC uploaded100/baseline114. These are boundary-analysis candidates, not proven executable changes. No automatic merging performed. Function counts do not measure semantic completeness or1:1 parity.

Evidence: uploaded_functions.tsv, baseline functions.tsv, comparison.json, original native listing excerpts and reproducible Java inventory script. Confidence High for inventory and explicit address comparison; Unknown for ideal CRT boundaries. Next discriminating test: compare instructions, branch targets, and callers around3C3D/4E24/59DC before changing any function bodies.
