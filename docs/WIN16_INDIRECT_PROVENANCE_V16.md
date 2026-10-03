# Win16 1.10 indirect-call provenance closure v16

- Total indirect sites: **212**
- Sites with resolved concrete target field: **46**
- Remaining VIRTUAL_DYNAMIC_RECEIVER: **113**
- Newly converted from dynamic in v16: **2**

## New v16 closures

- `FUN_1000_18e0` @ `0x192d`, slot `0x18` -> `1000:092C` / `FUN_1000_08ea`. Evidence: FUN_1000_337a -> map root 0x4548; mapped menu wrapper ctor FUN_1000_0868/0890 sets vptr 0x4934; FUN_1000_187a recursively returns this wrapper; vtable 0x4934 slot 0x18 = 1000:092C
- `FUN_1000_1f2e` @ `0x1f5e`, slot `0x68` -> `1000:2796;1000:279C` / `FUN_1000_26e8`. Evidence: puVar2 comes from FUN_1000_12fc window map root 0x4250; CWnd-family slot 0x68 is unanimous at source-function level FUN_1000_26e8 (entry variants 2796/279C)

## Closure-class census

- VIRTUAL_DYNAMIC_RECEIVER: 113
- STRUCT_FIELD_CALLBACK: 20
- RESOLVED_VIRTUAL_SELF: 18
- REGISTER_OR_SLOT0_DYNAMIC: 18
- RESOLVED_VIRTUAL_GLOBAL_081C: 14
- RESOLVED_VIRTUAL_SELF_EXACT_ENTRY: 9
- STACK_OR_FRAME_CALLBACK: 6
- RUNTIME_GLOBAL_CALLBACK: 5
- RUNTIME_GETPROCADDRESS_POINTER: 2
- RESOLVED_VIRTUAL_GLOBAL_081C_ALIAS: 1
- RESOLVED_VIRTUAL_MENU_MAP_4934: 1
- RESOLVED_VIRTUAL_SELF_FUNCTION_LEVEL: 1
- RESOLVED_VIRTUAL_WINDOWMAP_FUNCTION_LEVEL: 1
- RESOLVED_STATIC_GLOBAL_FARPTR: 1
- RUNTIME_SETTABLE_CALLBACK: 1
- OTHER_INDIRECT: 1