# Linux build and SDL3 smoke validation — 19 October 2026

This document records clean-room build validation only. It must not be cited as proof of original Nitemare 3-D behavior.

## Source-level build validation

The v0.48 source snapshot with the portability fixes applied was reported to build with GCC 14.2 and Clang 17 in C++20 mode.

Reported regression results:
- GCC CTest: 64/64 pass;
- Clang CTest: 64/64 pass;
- Clang AddressSanitizer + UndefinedBehaviorSanitizer CTest: 64/64 pass;
- main Python unittest discovery: 139/139 pass;
- WORX compatibility test set: 11/11 pass;
- v0.57 Python: 41/41 pass;
- v0.58 Python: 22/22 pass;
- v0.57/v0.58 and 12-build static primitive standalone C++ checks: pass.

The data-dependent pushable test was not registered without original episode data.

## SDL3 3.4.18 smoke

SDL3 3.4.18 was built from the supplied source archive in headless/console mode. The patched clean-room project produced an ELF64 `nitemare3d` executable.

With synthetic test data:
- 12 frames rendered;
- SDL virtual window size was 960x600;
- SDL readback succeeded;
- automatic exit returned code 0;
- sanitizer smoke produced the same first-frame fingerprint without a reported sanitizer error.

This smoke does not test original assets, AI, gameplay parity, audible audio or pixel equality with the DOS/Win16 originals.
