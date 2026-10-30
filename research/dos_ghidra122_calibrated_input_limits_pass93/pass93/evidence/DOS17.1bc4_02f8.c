
void __cdecl16far FUN_1bc4_02f8(void)

{
  uint uVar1;
  bool bVar2;
  
  if (DAT_3754_3c44 == 2) {
    uVar1 = FUN_14b1_0002(*(int *)(DAT_3754_40f4 * 0x1c + 0x16) - (int)DAT_3754_40d2,
                          *(int *)(DAT_3754_40f4 * 0x1c + 0x18) - DAT_3754_40d2._2_2_);
    if (uVar1 == 0) {
      DAT_3754_3c44 = 3;
      return;
    }
    if (((int)DAT_3754_44ca._2_2_ <= (int)((uVar1 ^ (int)uVar1 >> 0xf) - ((int)uVar1 >> 0xf))) &&
       (bVar2 = (int)uVar1 < 0, uVar1 = DAT_3754_44ca._2_2_, bVar2)) {
      uVar1 = -DAT_3754_44ca._2_2_;
    }
    FUN_1c63_0068(DAT_3754_40c6 + uVar1);
  }
  return;
}

