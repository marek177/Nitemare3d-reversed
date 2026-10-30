
void __cdecl16far FUN_168f_0192(int param_1)

{
  int iVar1;
  
  if (param_1 == 0) {
    if (DAT_374a_0b0d == '\0') {
      iVar1 = FUN_1811_0004();
      DAT_374a_407a = '\x01' - (iVar1 == 0);
    }
    DAT_374a_0b0d = 1;
    return;
  }
  if (param_1 != 1) {
    return;
  }
  if (DAT_374a_0b0d != '\0') {
    FUN_1811_001e();
  }
  DAT_374a_407a = 0;
  DAT_374a_0b0d = 0;
  return;
}

