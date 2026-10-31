# Pass99 — signed timezone arithmetic

Confirmed, high confidence under explicit globals and modeled DOS replies:360 native clock→CRT cases pass across six distinct EXEs. The original clock, CRT ftime, calendar converter and signed division helper execute unchanged. The initializer gate is set1 and DST0; no TZ environment parser is exercised.

The matrix is6 EXEs ×6 calendar samples ×5 timezone-second values(-86399,-3600,-1,1,86399) ×2 hundredths(0,99). Seconds equal wrap32(Gregorian epoch+timezone_seconds). The timezone-minute field equals the low16 bits of signed division timezone_seconds/60 truncated toward zero. Thus -1 second yields minute-field0; -86399 yields signed-1439, encoded as u16. This adds negative/non-minute-aligned coverage to pass96 and verifies that Python floor division would be the wrong implementation for negatives.

Assertions check all10 structure bytes, normal return, stack restoration, DOS request sequence and wrap32(seconds*1000+hundredths*10). EXE SHA256 and native locations/instructions are in signed_timezone_tests.json; source_clocks.json preserves mapping provenance. This is numeric-offset behavior, not a claim about a location or modern timezone policy. Labels1.8/1.9 are byte-identical supplied files.

Run python scripts/verify_signed_timezone.py from combined archive root after restoring baseline58 from the included pass76 dependency. Requires Unicorn2.1.4 and Capstone5.0.7. Actual timezone initialization/defaults and real OS clock behavior remain unverified.
