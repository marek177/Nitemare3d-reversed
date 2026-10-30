
void __cdecl16far FUN_16af_0192(int param_1)

{
  int iVar1;
  
  if (param_1 == 0) {
    if (DAT_376d_0b3f == '\0') {
      iVar1 = FUN_1831_0004();
      DAT_376d_414c = '\x01' - (iVar1 == 0);
    }
    DAT_376d_0b3f = 1;
    return;
  }
  if (param_1 != 1) {
    return;
  }
  if (DAT_376d_0b3f != '\0') {
    FUN_1831_001e();
  }
  DAT_376d_414c = 0;
  DAT_376d_0b3f = 0;
  return;
}

