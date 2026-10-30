
void __cdecl16far FUN_1d25_08ae(int param_1,int param_2,int param_3)

{
  undefined2 uVar1;
  
  if (param_1 == 0) {
    uVar1 = FUN_1277_0188(0x10006);
    FUN_1156_08d4(0xa0006e,DAT_376d_1c95 + 2,0x14,uVar1);
    return;
  }
  DAT_376d_3c8e = *(byte *)(param_1 + 0x1c91) + 0x6f;
  if (param_3 < 2) {
    param_3 = 2;
  }
  DAT_376d_1c96 =
       (int)(((long)(int)((uint)*(byte *)(param_1 + 0x1c92) - (uint)*(byte *)(param_1 + 0x1c91)) *
             (long)param_2) / (long)(param_3 + -1));
  if (DAT_376d_1c96 != DAT_376d_1c98) {
    uVar1 = FUN_1277_0188(0x1000e);
    FUN_1156_08d4(DAT_376d_3c8e,0xa1,DAT_376d_1c96,0x12,uVar1);
  }
  DAT_376d_1c98 = DAT_376d_1c96;
  return;
}

