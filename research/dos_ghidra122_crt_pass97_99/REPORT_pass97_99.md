# Nitemare3D DOS — passes97–99, 2026-10-31

30,072 native execution cases pass:144 calendar/date-change,29,568 DST and360 signed-timezone cases. All six distinct supplied EXEs are covered; supplied1.8/1.9 are identical. Ghidra12.2 freshly decompiled18 calendar/DST/init-gate functions. Reports distinguish explicit DOS/global fixtures from unverified runtime environment behavior.

Confirmed findings: date is re-read only during minute00:00; year2100 is treated as leap; DST uses original April/October rules with signed16/remainder anomalies in1967/2060; negative timezone minutes truncate toward zero. These results close specific clock-runtime unknowns, not all remaining game code.

Read pass97/REPORT.md, pass98/REPORT.md and pass99/REPORT.md for exact behavior and limits. Full case evidence, original input EXEs/specs, scripts and original Ghidra project dependency are included. From this archive root, install unicorn==2.1.4 capstone==5.0.7 and run the three scripts under scripts/. No project extraction is needed for native tests. For Ghidra reproduction, restore the included pass76 dependency/project and nested pass58 dependency, then use pass97 export script/seeds and logs as the mapping reference. Ghidra/JDK runtime binaries are not bundled.

Next unresolved runtime work: original TZ environment parser/defaults; cached-counter writes and scheduling callers; broader unknown gameplay functions. Every fixture and scope remains explicit; no full recovery percentage is claimed.
