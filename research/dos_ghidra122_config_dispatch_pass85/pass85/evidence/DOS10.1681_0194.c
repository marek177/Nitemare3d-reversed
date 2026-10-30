
void __cdecl16far FUN_1681_0194(int param_1)

{
  int iVar1;
  
  if (param_1 == 0) {
    if (DAT_3360_0aa7 == '\0') {
      iVar1 = FUN_17e9_000a();
      DAT_3360_3fa4 = '\x01' - (iVar1 == 0);
    }
    DAT_3360_0aa7 = 1;
    return;
  }
  if (param_1 != 1) {
    return;
  }
  if (DAT_3360_0aa7 != '\0') {
    FUN_17e9_0024();
  }
  DAT_3360_3fa4 = 0;
  DAT_3360_0aa7 = 0;
  return;
}

