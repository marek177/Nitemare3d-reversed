# Pass98 — native CRT DST predicate and signed16 boundary arithmetic

Confirmed, high confidence for controlled input registers/globals:29,568 cases pass across the six distinct supplied DOS EXEs. Labels1.8/1.9 share identical bytes. Each case executes original clock→ftime→calendar conversion→DST and arithmetic helpers. No function is mocked. Only INT21 date/time replies are modeled; timezone-init-complete is explicitly1, DST-enable1, timezone seconds0 or25200. This establishes the predicate and numeric adjustment, not real TZ environment initialization.

The test matrix per EXE is8 years(1966,1967,1986,1987,1994,2007,2026,2060) ×308 datetimes ×2 timezone offsets =4928. Per year: January1/March15/July1 at noon; every April and October day at00:59:59,01:00:00,01:59:59,02:00:00,03:00:00. Native returned structure is checked against an independently implemented arithmetic model derived from original instructions, not against a modern timezone-policy library. All10 bytes, final wrapped milliseconds, normal return, stack and DOS request sequence are asserted.

## Exact predicate
Let Y=calendar_year-1900 and M=month-1. Y<67 or M outside3..9 means no DST; M4..8 means DST. For April/October use cumulative month table T=[-1,30,58,89,119,150,180,211,242,272,303,333,364]. Let L=T[M+1] unless Y>=87 and M==3, in which case L=T[M]+7; add1 if Y&3==0. Then N=sign16(wrap16((Y-70)*365+((Y-1)>>2)+L)); R is signed remainder of (N-13)/7 truncated toward zero; boundary B=L-R. The supplied yday is zero-based. April is active for yday>B or equality and hour>=2; October is active for yday<B or equality and hour<1. This model covers the tested domain; it does not generalize all signed-overflow corner cases outside that domain.

For ordinary tested years this yields the first Sunday in April from1987, the last Sunday before1987, and the last Sunday in October at01:00. It retains the same April/October algorithm for2007 and2026. The input is a local DOS wall-clock fixture; interpretation of a repeated physical hour is outside this test.

|Year|April transition observed|October transition observed|
|---|---|---|
|1966|none, disabled|none, disabled|
|1967|30th 02:00|none within October, remains active|
|1986|27th 02:00|26th 01:00|
|1987|5th 02:00|25th 01:00|
|1994|3rd 02:00|30th 01:00|
|2007|1st 02:00|28th 01:00|
|2026|5th 02:00|25th 01:00|
|2060|13th 02:00|none within October, remains active|

1967 and2060 expose arithmetic behavior that a historical-rule oracle misses: the signed remainder can be negative, and the year-derived expression is narrowed to16 bits before division. For1967 October L303, N-13=-789, signed remainder-5, B308, which lies after October. In2060 the signed16 narrowing also moves the calculated transition. These are original native-code results, not emulation patches. Exact discrepancy discovery initially invalidated an assumed last-Sunday oracle; the final model explicitly preserves original arithmetic.

Native seconds equal wrap32(Gregorian epoch+timezone_seconds-3600*DST) for this sampled year range. Structure DST flag matches the applied adjustment in all tested cases, despite the helper being called twice by the conversion/ftime chain. Month/day/year valid-input domain only; no automatic leap-century correction is added. Pass97 separately proves the original year&3 divergence in2100.

## Evidence and limits
Fresh Ghidra12.2 DST/calendar exports, addresses, native instructions and successful18/18 status are in pass97. dst_tests.json preserves all29,568 input/results, hashes and locations; summary.json provides counts and observed transitions. Full case evidence is retained in the combined ZIP, with its SHA256 in summary.json; the repository retains compact review evidence and executable verifier.

Run python scripts/verify_native_crt_dst.py from combined archive root with Unicorn2.1.4/Capstone5.0.7 and included baseline58 input/specs. Runtime defaults, TZ strings/environment, real OS date support, game counter writers and complete gameplay parity remain unknown. Case volume does not imply all code has been analyzed.
