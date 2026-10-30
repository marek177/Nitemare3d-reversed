
void __cdecl16far FUN_1689_0198(int param_1)

{
  int iVar1;
  
  if (param_1 == 0) {
    if (DAT_3395_0aff == '\0') {
      iVar1 = FUN_180b_000a();
      DAT_3395_40aa = '\x01' - (iVar1 == 0);
    }
    DAT_3395_0aff = 1;
    return;
  }
  if (param_1 != 1) {
    return;
  }
  if (DAT_3395_0aff != '\0') {
    FUN_180b_0024();
  }
  DAT_3395_40aa = 0;
  DAT_3395_0aff = 0;
  return;
}

