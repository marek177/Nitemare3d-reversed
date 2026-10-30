
void __cdecl16far FUN_1bda_02fc(void)

{
  uint uVar1;
  bool bVar2;
  
  if (DAT_376d_3cd4 == 2) {
    uVar1 = FUN_14c7_0006(*(int *)(DAT_376d_4184 * 0x1c + 0x16) - DAT_376d_4162,
                          *(int *)(DAT_376d_4184 * 0x1c + 0x18) - DAT_376d_4164);
    if (uVar1 == 0) {
      DAT_376d_3cd4 = 3;
      return;
    }
    if (((int)DAT_376d_455c <= (int)((uVar1 ^ (int)uVar1 >> 0xf) - ((int)uVar1 >> 0xf))) &&
       (bVar2 = (int)uVar1 < 0, uVar1 = DAT_376d_455c, bVar2)) {
      uVar1 = -DAT_376d_455c;
    }
    FUN_1c79_006c(DAT_376d_4156 + uVar1);
  }
  return;
}

