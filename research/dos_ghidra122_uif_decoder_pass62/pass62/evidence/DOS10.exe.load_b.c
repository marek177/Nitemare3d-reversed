
void __cdecl16far FUN_1cdc_08aa(int param_1,int param_2,int param_3)

{
  undefined2 uVar1;
  
  if (param_1 == 0) {
    uVar1 = FUN_1273_016c(0x10006);
    FUN_1155_08d6(0xa0006e,DAT_3360_1bb1 + 2,0x14,uVar1);
    return;
  }
  DAT_3360_3b34 = *(byte *)(param_1 + 0x1bad) + 0x6f;
  if (param_3 < 2) {
    param_3 = 2;
  }
  DAT_3360_1bb2 =
       (int)(((long)(int)((uint)*(byte *)(param_1 + 0x1bae) - (uint)*(byte *)(param_1 + 0x1bad)) *
             (long)param_2) / (long)(param_3 + -1));
  if (DAT_3360_1bb2 != DAT_3360_1bb4) {
    uVar1 = FUN_1273_016c(0x1000e);
    FUN_1155_08d6(DAT_3360_3b34,0xa1,DAT_3360_1bb2,0x12,uVar1);
  }
  DAT_3360_1bb4 = DAT_3360_1bb2;
  return;
}

