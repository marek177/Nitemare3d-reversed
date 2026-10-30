
void __cdecl16far FUN_1d00_0880(int param_1,int param_2,int param_3)

{
  undefined2 uVar1;
  
  if (param_1 == 0) {
    uVar1 = FUN_1275_0160(0x10006);
    FUN_1155_08d6(0xa0006e,DAT_339b_1c85 + 2,0x14,uVar1);
    return;
  }
  DAT_339b_3c2a = *(byte *)(param_1 + 0x1c81) + 0x6f;
  if (param_3 < 2) {
    param_3 = 2;
  }
  DAT_339b_1c86 =
       (int)(((long)(int)((uint)*(byte *)(param_1 + 0x1c82) - (uint)*(byte *)(param_1 + 0x1c81)) *
             (long)param_2) / (long)(param_3 + -1));
  if (DAT_339b_1c86 != DAT_339b_1c88) {
    uVar1 = FUN_1275_0160(0x1000e);
    FUN_1155_08d6(DAT_339b_3c2a,0xa1,DAT_339b_1c86,0x12,uVar1);
  }
  DAT_339b_1c88 = DAT_339b_1c86;
  return;
}

