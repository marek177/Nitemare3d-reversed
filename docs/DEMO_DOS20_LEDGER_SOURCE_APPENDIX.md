# Source appendix — DOS2 DEMO first consumer and shared-wrapper ledger

Source reports are preserved in [evidence/2026-10-19](evidence/2026-10-19/).
This integration rechecks the exported ledger, not the unavailable raw captures.

- The v12 breakpoint-first original-runtime report identifies the first observed
  post-reset RNG consumer at runtime `0CEB:0A36`. File offset `0x58A6`
  corresponds to MZ-image offset `0x56A6` (512-byte header); these are one
  callsite, not two consumers. The return is `0CEB:0A3B`.
- Seed `1` becomes `0x0029E2C0`, result 41. Observed actor mode 0 selects
  mask 3, writes Y vector `00→F8`, timer `0→24`, state `3→6`.
- Two independent selective captures export 8 and 18 shared-wrapper calls.
  Their first eight normalized `(callsite,state,result)` tuples match exactly.
  Entries 9–18 have one-run evidence only. The final state is `0xAEA69ED3`.
- `A047` repeats at calls 3–8 and `9FE3` at 16–18. Retry count is not
  an object count. Do not transfer DOS1.2 GUARD41 identity to this DOS2 ledger.

Run `python3 tools/verify_d02_ledger.py` to validate JSON sequence order,
recognized sites, recurrence, results and the eight-entry common prefix.
This portable tool requires no private `/mnt/data` module. The archived
`n3d_d02_verify_chain.py` is the historical raw-trace verifier and still needs
its external `n3d_d01_runtime_verify` parser and source captures.

**Open:** exhaustive indirect/CRT RNG census, per-entry scheduler depth,
actor identity, second capture through entry 18, later records, EOF, final DEMO
state and original-versus-port comparison. The first RNG consumer occurs after
already-recorded DEMO reader checkpoints; do not describe this prefix as
necessarily occurring before the first applied input.

Confidence: high for the rechecked exported arithmetic/prefix; original CPU
execution remains attributed to the source reports, not rerun by this update.
