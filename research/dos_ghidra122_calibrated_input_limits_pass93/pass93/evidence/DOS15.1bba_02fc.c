
void __cdecl16far FUN_1bba_02fc(void)

{
  uint uVar1;
  bool bVar2;
  
  if (DAT_374a_3c44 == 2) {
    uVar1 = FUN_14a7_0006(*(int *)(DAT_374a_40b2 * 0x1c + 0x16) - DAT_374a_4090,
                          *(int *)(DAT_374a_40b2 * 0x1c + 0x18) - DAT_374a_4092);
    if (uVar1 == 0) {
      DAT_374a_3c44 = 3;
      return;
    }
    if (((int)DAT_374a_4488._2_2_ <= (int)((uVar1 ^ (int)uVar1 >> 0xf) - ((int)uVar1 >> 0xf))) &&
       (bVar2 = (int)uVar1 < 0, uVar1 = DAT_374a_4488._2_2_, bVar2)) {
      uVar1 = -DAT_374a_4488._2_2_;
    }
    FUN_1c59_006c(DAT_374a_4084 + uVar1);
  }
  return;
}

