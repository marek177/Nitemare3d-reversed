
void __cdecl16far FUN_1d05_087e(int param_1,int param_2,int param_3)

{
  undefined2 uVar1;
  
  if (param_1 == 0) {
    uVar1 = FUN_1277_0188(0x10006);
    FUN_1156_08d4(0xa0006e,DAT_374a_1c57 + 2,0x14,uVar1);
    return;
  }
  DAT_374a_3bfe = (byte)((char *)s_Press_a_key_374a_1c47 + 0xc)[param_1] + 0x6f;
  if (param_3 < 2) {
    param_3 = 2;
  }
  DAT_374a_1c58 =
       (int)(((long)(int)((uint)*(byte *)(param_1 + 0x1c54) -
                         (uint)(byte)((char *)s_Press_a_key_374a_1c47 + 0xc)[param_1]) *
             (long)param_2) / (long)(param_3 + -1));
  if (DAT_374a_1c58 != DAT_374a_1c5a) {
    uVar1 = FUN_1277_0188(0x1000e);
    FUN_1156_08d4(DAT_374a_3bfe,0xa1,DAT_374a_1c58,0x12,uVar1);
  }
  DAT_374a_1c5a = DAT_374a_1c58;
  return;
}

