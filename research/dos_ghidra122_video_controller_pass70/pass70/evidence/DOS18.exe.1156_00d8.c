
void __cdecl16far FUN_1156_00d8(int param_1)

{
  code *pcVar1;
  char cVar2;
  
  if (param_1 == 0) {
    pcVar1 = (code *)swi(0x10);
    DAT_376d_3450 = (*pcVar1)();
    FUN_1156_0a66();
    pcVar1 = (code *)swi(0x10);
    cVar2 = (*pcVar1)();
    if (cVar2 != '\x13') {
      FUN_1fb7_0000();
    }
    FUN_1156_0000();
    return;
  }
  if (param_1 != 1) {
    return;
  }
  if (DAT_376d_3450 != '\0') {
    pcVar1 = (code *)swi(0x10);
    (*pcVar1)();
  }
  return;
}

