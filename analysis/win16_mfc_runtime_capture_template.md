# Win16 MFC debugger capture template

Use this file when running NITE3W under Windows 3.1. Record observations; do not replace static evidence with assumptions.

## Environment

- NITE3W executable SHA-256:
- Windows version:
- emulator/VM:
- debugger:
- executable load segment / selector mapping:

## Capture rows

| Probe | CS:IP / data | object | handle | runtime class | observation |
|---|---|---:|---:|---:|---|
| IsKindOf traversal | 1:068A | | | | |
| generic CreateObject | 1:06C0 | | | | |
| CWnd ctor | 1:114A | | | 0594 | |
| CWnd ctor(handle) | 1:1172 | | | 0594 | |
| CWnd create thunk | 1:1AEC | | | 0594 | |
| CWnd teardown | 1:1666 | | | | |
| DestroyWindow/detach | 1:171C | | | | |
| deleting destructor | 1:281E | | | | |
| CWnd HandleMap | 10:4250 | | | | |
| CDC HandleMap | 10:44F2 | | | | |
| CGdiObject HandleMap | 10:451C | | | | |
| CMenu HandleMap | 10:4548 | | | | |

## Temporary wrapper identity

First FromHandle:
- raw handle:
- permanent lookup:
- temporary lookup:
- allocated object:
- object +14/+04:
- runtime class:

Second FromHandle in same scope:
- returned object:
- same identity as first: yes/no

Cleanup:
- nesting count before:
- handle field before clear:
- handle field after clear:
- deleting destructor reached:
- native handle still valid after wrapper deletion:

## CWnd sentinels

| static object | expected pseudo HWND | observed |
|---|---:|---:|
| 10:41D6 | 0 | |
| 10:41F0 | 1 | |
| 10:420A | FFFF | |
| 10:4224 | FFFE | |

Record the SetWindowPos/insert-after call using each observed sentinel if reachable.

## Evidence promotion

Attach this completed trace to the repository before changing the MFC evidence register from RuntimePending. Include exact register/memory values for any discrepancy.
