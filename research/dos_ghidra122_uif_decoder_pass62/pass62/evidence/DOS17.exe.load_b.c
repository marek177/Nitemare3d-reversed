
void __cdecl16far FUN_1d0f_087a(int param_1,int param_2,int param_3)

{
  undefined2 uVar1;
  
  if (param_1 == 0) {
    uVar1 = FUN_1277_0188(0x10006);
    FUN_1156_08d4(0xa0006e,DAT_3754_1c5b + 2,0x14,uVar1);
    return;
  }
  DAT_3754_3c02 = (byte)((char *)s_Press_a_key_3754_1c4b + 0xc)[param_1] + 0x6f;
  if (param_3 < 2) {
    param_3 = 2;
  }
  DAT_3754_1c5c =
       (int)(((long)(int)((uint)*(byte *)(param_1 + 0x1c58) -
                         (uint)(byte)((char *)s_Press_a_key_3754_1c4b + 0xc)[param_1]) *
             (long)param_2) / (long)(param_3 + -1));
  if (DAT_3754_1c5c != DAT_3754_1c5e) {
    uVar1 = FUN_1277_0188(0x1000e);
    FUN_1156_08d4(DAT_3754_3c02,0xa1,DAT_3754_1c5c,0x12,uVar1);
  }
  DAT_3754_1c5e = DAT_3754_1c5c;
  return;
}

