
void __cdecl16far FUN_1d00_087e(int param_1,int param_2,int param_3)

{
  undefined2 uVar1;
  
  if (param_1 == 0) {
    uVar1 = FUN_1275_0160(0x10006);
    FUN_1155_08d6(0xa0006e,DAT_3395_1c93 + 2,0x14,uVar1);
    return;
  }
  DAT_3395_3c2e = (byte)((char *)s_Press_a_key_3395_1c83 + 0xc)[param_1] + 0x6f;
  if (param_3 < 2) {
    param_3 = 2;
  }
  DAT_3395_1c94 =
       (int)(((long)(int)((uint)*(byte *)(param_1 + 0x1c90) -
                         (uint)(byte)((char *)s_Press_a_key_3395_1c83 + 0xc)[param_1]) *
             (long)param_2) / (long)(param_3 + -1));
  if (DAT_3395_1c94 != DAT_3395_1c96) {
    uVar1 = FUN_1275_0160(0x1000e);
    FUN_1155_08d6(DAT_3395_3c2e,0xa1,DAT_3395_1c94,0x12,uVar1);
  }
  DAT_3395_1c96 = DAT_3395_1c94;
  return;
}

