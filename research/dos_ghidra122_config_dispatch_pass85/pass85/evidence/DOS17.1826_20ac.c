
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl16far FUN_1826_20ac(void)

{
  byte bVar1;
  
  if ((DAT_3754_40c1 == '\0') &&
     (((undefined1 *)&DAT_3754_d37c)[*(byte *)((int)_DAT_3754_40ea + 1)] == '\a')) {
    if (DAT_3754_14ea != DAT_3754_61d8) {
      DAT_3754_14ea = DAT_3754_61d8;
      DAT_3754_35a9 = FUN_10f7_004e(7);
    }
    FUN_1156_0254();
    bVar1 = *(byte *)(((uint)*(byte *)((int)_DAT_3754_40ea + 1) - (uint)DAT_3754_35a9) + 0x14e6);
    if (bVar1 < DAT_3754_40f7) {
      DAT_3754_40f7 = DAT_3754_40f7 - bVar1;
    }
    else {
      DAT_3754_40f7 = 0;
      DAT_3754_3c44 = 3;
      DAT_3754_3c41 = 1;
      FUN_1c11_03d6(10,0x20000);
    }
    FUN_1826_05d4();
  }
  return;
}

