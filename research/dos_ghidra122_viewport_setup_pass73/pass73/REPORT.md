# Pass 73 — viewport geometry, projection constants and table rebuild

## Finding
Confirmed for six distinct supplied DOS binaries: one viewport-setup routine writes geometry, calls projection-constant preparation, then calls the clipping-table builder. Both original callees execute together in this pass. Synthetic widths0/1 divide by zero in projection preparation before clipping tables rebuild. Supplied1.8/1.9 are identical; reachability of invalid widths is Unknown.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Geometry writes precede projection and clip rebuild calls | Fresh Ghidra exports and original execution | High |
| Confirmed | Width controls visible height by signed arithmetic shift1 | Original arithmetic, odd-width fixtures | High |
| Confirmed | Projection factor uses signed truncating division | Original IMUL/IDIV and independent comparison | High |
| Confirmed | Width0/1 triggers CPU divide error before clip rebuild | Unicorn exception0, call trace and unchanged tables | High under fixture |
| Unknown | Invalid widths reachable through game settings | Caller/input validation audit pending | No game-visible crash claim |

## Behavior model
Let W be the signed16 configured width. The original setup derives (wrap16 where stored): H=W>>1; L=floor((320−W)/2) using signed32 subtraction/shift; R=L+W−1; T=signed16(L)>>1; B=T+H−1; auxiliary=L+H; C=T+(H>>1); C16=C<<4. The nine stored values, in write order, are H,L,W,R,T,B,auxiliary,C,C16. These names describe arithmetic/layout roles; exact use of auxiliary remains to be traced. Odd widths retain arithmetic-shift rounding.

The first callee computes four32-bit projection values:

`F = trunc_toward_zero(W*12000/20480)`

`A = wrap32(H*0x8340)`

`B32 = wrap32(A<<4)`

`Q = trunc_toward_zero(signed32(B32)/F)`

Then the original clipping builder from pass72 runs using H. Geometry is already written when projection begins. For W0/1, F=0: the division for Q faults after F,A,B32 are stored; Q and clipping tables remain unchanged in these fixtures. No transactional rollback or local validation exists in the observed routine. Negative/out-of-range widths are synthetic arithmetic boundary tests, not accepted menu settings.

## Locations
DOS1.9 viewport setup1277:0bc2, projection preparation1c79:0008, clip builder1156:0030. Configured width DS4144; geometry DS4544,4546,4542,4548,454a,454c,454e,4550,4552; projection dwords DS367c,3680,3684,3688. Per-build exact locations and observed values are in viewport_tests.json. Full direct xrefs and function instructions/decompilation are included.

## Verification
72 cases pass: six distinct binaries × W=-2,0,1,2,3,64,159,160,161,319,320,321. All nine geometry values, projection values, call order and every511 clipping offset/fraction pair are checked on successful paths. Faulting paths verify exception0, no clip-builder entry, unchanged clip bytes and unchanged Q. Original setup and both original callees execute unchanged; no function, BIOS or I/O boundaries are mocked. Synthetic input width and table storage are used. These are local CPU tests, not a complete game render.

## Unknowns and next test
Trace all width writes and setup callers to establish legal sizes, persistence and update timing. Recover projection-value consumers to name their exact geometric meanings. Connect setup to original scaler call paths, especially the stack-byte precondition from pass71. Actual depth, assets, framebuffer/DAC and timing parity remain open. Confidence High for local setup sequence and exact arithmetic; incomplete for game-wide input reachability and rendering equivalence.
