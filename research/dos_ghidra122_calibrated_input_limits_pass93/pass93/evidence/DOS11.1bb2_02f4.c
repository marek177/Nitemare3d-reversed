
void __cdecl16far FUN_1bb2_02f4(void)

{
  uint uVar1;
  bool bVar2;
  
  if (DAT_3395_3c74 == 2) {
    uVar1 = FUN_14a2_0002(*(int *)(DAT_3395_40e2 * 0x1c + 0x16) - DAT_3395_40c0,
                          *(int *)(DAT_3395_40e2 * 0x1c + 0x18) - DAT_3395_40c2);
    if (uVar1 == 0) {
      DAT_3395_3c74 = 3;
      return;
    }
    if (((int)DAT_3395_44b8._2_2_ <= (int)((uVar1 ^ (int)uVar1 >> 0xf) - ((int)uVar1 >> 0xf))) &&
       (bVar2 = (int)uVar1 < 0, uVar1 = DAT_3395_44b8._2_2_, bVar2)) {
      uVar1 = -DAT_3395_44b8._2_2_;
    }
    FUN_1c54_006c(DAT_3395_40b4 + uVar1);
  }
  return;
}

