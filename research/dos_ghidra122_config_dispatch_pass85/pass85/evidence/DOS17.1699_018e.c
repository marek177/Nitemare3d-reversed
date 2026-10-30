
void __cdecl16far FUN_1699_018e(int param_1)

{
  int iVar1;
  
  if (param_1 == 0) {
    if (DAT_3754_0b11 == '\0') {
      iVar1 = FUN_181b_0000();
      DAT_3754_40bc = '\x01' - (iVar1 == 0);
    }
    DAT_3754_0b11 = 1;
    return;
  }
  if (param_1 != 1) {
    return;
  }
  if (DAT_3754_0b11 != '\0') {
    FUN_181b_001a();
  }
  DAT_3754_40bc = 0;
  DAT_3754_0b11 = 0;
  return;
}

