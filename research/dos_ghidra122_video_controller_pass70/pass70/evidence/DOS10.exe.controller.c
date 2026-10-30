
void __cdecl16far FUN_1155_00da(int param_1)

{
  code *pcVar1;
  char cVar2;
  
  if (param_1 == 0) {
    pcVar1 = (code *)swi(0x10);
    DAT_3360_334c = (*pcVar1)();
    FUN_1155_0a68();
    pcVar1 = (code *)swi(0x10);
    cVar2 = (*pcVar1)();
    if (cVar2 != '\x13') {
      FUN_1f67_000a();
    }
    FUN_1155_0002();
    return;
  }
  if (param_1 != 1) {
    return;
  }
  if (DAT_3360_334c != '\0') {
    pcVar1 = (code *)swi(0x10);
    (*pcVar1)();
  }
  return;
}

