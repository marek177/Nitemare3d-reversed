
void __cdecl16far FUN_1b91_02ea(void)

{
  uint uVar1;
  bool bVar2;
  
  if (DAT_3360_3b6e == 2) {
    uVar1 = FUN_1499_0002(*(int *)(DAT_3360_3fdc * 0x1c + 0x16) - DAT_3360_3fba,
                          *(int *)(DAT_3360_3fdc * 0x1c + 0x18) - DAT_3360_3fbc);
    if (uVar1 == 0) {
      DAT_3360_3b6e = 3;
      return;
    }
    if (((int)DAT_3360_43b2._2_2_ <= (int)((uVar1 ^ (int)uVar1 >> 0xf) - ((int)uVar1 >> 0xf))) &&
       (bVar2 = (int)uVar1 < 0, uVar1 = DAT_3360_43b2._2_2_, bVar2)) {
      uVar1 = -DAT_3360_43b2._2_2_;
    }
    FUN_1c30_0068(DAT_3360_3fae + uVar1);
  }
  return;
}

