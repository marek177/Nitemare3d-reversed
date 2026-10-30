# Win110 pass 71 — exception fallback policy

## Finding
Confirmed / High: 1000:3CEA suppresses its A344 call for CUserException ancestry, selects F10A/1030 for CMemoryException ancestry, and otherwise selects F108 or F109 with flag0010. This is a verified call-selection policy, not proof of rendered Windows dialogs.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Descriptor0686 names CUserException and has base0500 | NE10:0686, relocation at0688 to NE2, name NE2:003E | High |
| Confirmed | Virtual getter1008:023E returns0686 and RETF2 | Original executable and native listing | High |
| Confirmed | 3CEA tests0514 first,0686 second | 1000:3D36–3D5A | High |
| Confirmed | Successful user-exception test bypasses A344 | JNZ3D66 at3D5A | High |
| Confirmed | Memory branch calls A344 with stack words FFFF,1030,F10A | 3D45–3D61 and integrated checks | High |
| Confirmed | Other branch uses FFFF,0010,F109 only when message0111 and source word+6 is0; otherwiseF108 | 3D14–3D33,3D5C–3D61 | High |

The second test is a type/ancestry predicate, not an examination of an arbitrary exception-code field. CNotSupportedException falls through the generic branch; it is not CUserException merely because both descend from CException.

## Behavior model
For the message-like record supplied as the second near argument:

| word at record+2 | Action | DX:AX return |
|---|---|---|
| 0001 | No type test or UI call | FFFF:FFFF |
| 000F | VALIDATERECT(record.word0,0,0), then return | 0000:0000 |
| 0111 | Type policy above; generic code depends on record.word+6 | 0000:0001 |
| Other | Type policy above | 0000:0000 |

The numeric values resemble WM_CREATE, WM_PAINT and WM_COMMAND; those API-name interpretations are not necessary to the tested numeric policy. The ignored first argument is consumed by RETF6 along with the other two words. SI/DI/BP restore. Entry SPD000 returns D00A. A344's selected return value does not become 3CEA's result.

## Verification
131,132 cases passed: full65,536-message sweeps for memory and user exception objects with source0, plus60 cases crossing four types (memory, unsupported, base exception, user), five message words (0,1,15,0111,FFFF), and three source words (0,1,FFFF). Full sweeps and samples overlap intentionally and are counted as executed cases.

Original3CEA calls original068A and original virtual getters. VALIDATERECT at3D0B and A344 at3D61 are intercepted before CALLF; each stub records three stack words, consumes six bytes and returns AX7777. No A344 body, string loading, Windows import, dialog, or actual painting is executed. The user object is a synthetic fixture using the real023E getter through a synthetic table slot. Memory/unsupported/base tables are original offsets48E4/48F8/48D0. This verifies selection and arguments only.

CS2000 maps NE1, CS3000 maps NE2, DS1048, SS4000. Vtable bytes map at5000. Original internal CALLF selectors in3CEA normalize to2000; three original table slot-zero selectors normalize to2000; synthetic user slot points3000:023E. All object table selectors are5000. No getter or predicate instructions are patched. Script checks raw bytes of predicate/getters, raw class-name bytes, and base link. NE selector relocation for descriptor0688 targets NE2, independently recorded in metadata evidence.

Run `python3 pass71/verify_exception_policy.py` after unpacking, with Unicorn2.1.4. EXE SHA256:12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Sources are preserved Ghidra12.2 exports and original EXE; no fresh Ghidra database mutation occurred.

## Implementation-ready findings
Preserve message-specific bypasses before type classification. Prefer the memory-exception branch before user-exception suppression. Keep handler return independent of UI-call return. Do not suppress generic unsupported exceptions.

## Unknowns and next test
Trace A344→3250 resource loading and virtual method+54 to recover actual text/flags and owner selection. A controlled real Win16 exception remains required to prove the observable dialog and paint behavior. Confidence is High for isolated handler dispatch; real Windows UI is Unknown.
