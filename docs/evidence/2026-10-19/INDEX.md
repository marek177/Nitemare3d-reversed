# Recent source evidence — 19 October 2026

These are historical source reports preserved as received. Their statements
about “this run”, “GitHub unchanged”, tests and unavailable files refer to their
original sessions. Integration reports V060–V061 and the source appendices describe this checkout.
SOURCE_MANIFEST.json pins the text/JSON files; it does not hash missing captures.

| Topic | Current source | Integration |
|---|---|---|
| DOS2 RNG | D02_RUNTIME_CHAIN MD/JSON and first_RNG_report_v12 | DEMO_DOS20_LEDGER_SOURCE_APPENDIX |
| DOS1.9 indirect/depth | RE_MAX_NEXT2_STATIC_CLOSURE | V060 |
| DOS1.2 GUARD41 state09 | README_SK_20261019-192416_ | GUARD41_STATE09_SOURCE_APPENDIX |
| DDA/IMG corrections | REPORT_SK_20261019-194111_ and -191038_ | V061 |
| Original renderer observations | REPORT_SK_20261019-192305_ | V061 |
| DOS2 world-update/MAP dataset audit | REPORT_SK_20261019-191226_ | V061 |
| Palette compatibility/data smoke | REPORT_SK_20261019-184729_ | V061 |
| WinG startup and timer RNG | -183243_ and RNG_Runtime_report_v7 | Already summarized in V051/V052 |

Earlier GUARD41 README reports are superseded locally by -192416_; their OPEN
claims describe earlier evidence boundaries. The D01 static next-goal report
predates the v12/D02 captures. The two WinG source reports -183229_ and -183243_
are duplicate editions. Their presence does not count as two independent tests.

The archived n3d_d02_verify_chain.py depends on a separate raw-trace parser and
private sessions. Use tools/verify_d02_ledger.py from the repository root for
the portable exported-ledger consistency check. Neither tool's absence/presence
alone establishes all-engine RNG coverage or full port parity.
