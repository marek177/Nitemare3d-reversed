
void __cdecl16far FUN_168a_0194(int param_1)

{
  int iVar1;
  
  if (param_1 == 0) {
    if (DAT_339b_0b09 == '\0') {
      iVar1 = FUN_180c_0006();
      DAT_339b_40aa = '\x01' - (iVar1 == 0);
    }
    DAT_339b_0b09 = 1;
    return;
  }
  if (param_1 != 1) {
    return;
  }
  if (DAT_339b_0b09 != '\0') {
    FUN_180c_0020();
  }
  DAT_339b_40aa = 0;
  DAT_339b_0b09 = 0;
  return;
}

