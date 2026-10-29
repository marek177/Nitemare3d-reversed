# Win16 1.10 — Ghidra 12.2 pass46: GDI mode2 RGB conversion

Confirmed, High: original instructions1010:3304..3325 convert source palette indices10..245 inclusive into236 four-byte entries on the stack. Each entry contains unchanged R,G,B bytes followed by flag1. Unlike direct DAC3ACC, this conversion does not shift RGB values right2.

1024 controlled executions (4 cache-flag values0/1/80/FF ×256 deterministic random768-byte palettes, seed46) verify all944 output bytes, both adjacent sentinel bytes, unchanged input, finalSI/DI, cache flag00C4 and16 cache bytes327E..328D. All14 executed instruction encodings match the original EXE. No helper stubs or imported calls execute. TestCS2000,DS=SS1048, BP D000, source7000, DF0. EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.

The test starts at3304 after mode selection and stops at3327 before testing the palette handle. Stack output beginsBP-994 and ends beforeBP-50. Exactly30 source bytes are skipped at the front and30 at the end. FinalSI is source+738, finalDI isBP-50. This is execution of the conversion fragment, not the complete31AA function.

Static native instructions show that handle00BE nonzero permits ANIMATEPALETTE(handle,start10,count236,far stack entries). Independently, flag46AF zero calls3100 before RELEASEDC. These downstream effects were not executed in this pass. GDI return values, actual displayed colors, full-function cache preservation and Win16 runtime ordering remain Unknown. Local cache preservation must not be generalized across unexecuted callees.

Implementation: model the GDI conversion with full source byte values and flag1, restricted to indices10..245. Keep the DAC byte>>2 behavior specific to3ACC. Preserve explicit backend differences instead of assuming identical channel ranges.

Ghidra comments record this scoped evidence. Native internal decompile baseline remains1551 entries;310 EXTERNAL entries remain separate.1401 undefined executable bytes remain unresolved. Next: controlled execution of the full mode2 routine with documented Windows import boundaries, followed by actual Win16 palette/cache tracing.
