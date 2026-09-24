# Win16 MFC reverse-engineering summary

Status: static architecture substantially closed; runtime trace validation remains.

## Recovered core

- 16-byte `CRuntimeClass16` records with class name, object size, schema, create callback, base and next-class links.
- 31 recovered MFC runtime-class facts spanning CObject, CCmdTarget, CWnd/document-view, DC/GDI and menu branches.
- CWnd object size `0x1A`, vtable `4:49A4`, primary HWND at `+0x14`.
- Four CWnd z-order sentinel objects at `10:41D6/41F0/420A/4224`.
- Four HandleMaps for HWND, HDC, HGDIOBJ and HMENU.
- permanent-first / temporary-second wrapper lookup, allocate-on-miss and nesting-zero temporary cleanup.
- relocation-aware CWnd constructor/create/destructor/vtable anchors.
- Win16 far-heap and resource-cache behavior documented separately.

## Canonical repository artifacts

- `src/re/Win16MfcMemory.hpp` — recovered structures, class hierarchy, HandleMaps, lifecycle and evidence levels.
- `src/re/Win16MfcAddresses.hpp` — consolidated code/data address catalog.
- `src/re/Win16MfcRuntimeProbes.hpp` — debugger probe list.
- `tests/win16_mfc_memory_test.cpp` — structural, hierarchy and lifecycle assertions.
- `tests/win16_mfc_addresses_test.cpp` — address-catalog assertions.
- `analysis/nite3w_win16_mfc_memory_2026-09-25.md` — binary-analysis narrative.
- `analysis/win16_mfc_runtime_capture_template.md` — trace recording form.
- `docs/WIN16_MFC_RUNTIME_VALIDATION.md` — Win3.1 validation procedure.
- `docs/WIN16_MFC_TO_X64_PORT.md` — mapping from historical ABI to modern implementation.

## Evidence boundary

Do not describe the whole MFC area as literally 100% verified. The major static architecture is recovered, but the repository deliberately keeps full runtime lifecycle validation as pending until a Windows 3.1 debugger trace confirms temporary wrapper identity, cleanup ordering, owned/borrowed handle behavior, CDC dual-handle behavior and sentinel use.

## Next action

Run the probes from `Win16MfcRuntimeProbes.hpp` under the exact audited executable and fill `analysis/win16_mfc_runtime_capture_template.md`. Promote individual evidence items only when the captured runtime values support them.
