# Pass97 — native CRT calendar boundaries

Confirmed, high confidence for explicit register/global fixtures. All six distinct DOS EXEs pass 144 native execution cases. Labels 1.8 and 1.9 refer to identical supplied bytes. No application or CRT function is mocked; only DOS INT21 date/time replies are modeled. Timezone initialization-complete is set1, timezone0 and DST0.

The original CRT queries date, then time. It queries date again exactly when hour==0 and minute==0, including 00:00:59. At 00:01:00 it retains the first date. Different first/second date replies prove which date is used. Date changes tested: 1999-12-31→2000-01-01, 2000-02-28→2000-02-29, 2026-10-31→2026-11-01 and 2038-01-19→2038-01-20, at four times each, per EXE.

Additional same-date samples cover 1969-12-31,1970-01-01,2038-01-19,2038-01-20,2099-12-31,2100-02-28,2100-03-01,2101-01-01. Every sample checks normal return, restored stack, exact interrupt sequence, all10 structure bytes, epoch seconds and final wrapped millisecond result. No special discontinuity is observed at the selected 2038 dates when interpreting seconds as unsigned32. This is not a signed-time API or real DOS year-support claim.

The original leap test is year&3. On 2100-03-01 and 2101-01-01 native epoch seconds are exactly86400 above the independent Gregorian Python datetime value, in every EXE; the remaining samples match Gregorian arithmetic. This is confirmed code behavior under supplied dates, not an assertion of practical game execution in2100.

Ghidra12.2 read-only exports freshly decompile calendar conversion, DST predicate and timezone-init gate in all six EXEs:18/18 completed. Native bytes and independently executed arithmetic are the behavioral evidence; decompilation success is not proof of complete recovery.

Evidence: calendar_tests.json retains every input, chosen date, native structure/result, request trace, EXE SHA256 and locations. ghidra_status.json, seeds.tsv, C exports, instruction TSVs, Java export script and ghidra.log retain static mapping.

Reproduce from the combined archive root: extract the pass76 dependency and nested baseline58 dependency into baseline58/, then run python scripts/verify_crt_calendar_boundaries.py with Unicorn2.1.4 and Capstone5.0.7. Original timezone environment parsing, invalid OS returns, asynchronous real midnight behavior and complete game parity remain unknown.
