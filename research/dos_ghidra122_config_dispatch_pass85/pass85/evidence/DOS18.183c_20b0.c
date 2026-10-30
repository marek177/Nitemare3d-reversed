
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl16far FUN_183c_20b0(void)

{
  byte bVar1;
  
  if ((DAT_376d_4151 == '\0') &&
     (((undefined1 *)&DAT_376d_d40c)[*(byte *)((int)_DAT_376d_417a + 1)] == '\a')) {
    if (DAT_376d_1518 != DAT_376d_6268) {
      DAT_376d_1518 = DAT_376d_6268;
      DAT_376d_3635 = FUN_10f7_004e(7);
    }
    FUN_1156_0254();
    bVar1 = *(byte *)(((uint)*(byte *)((int)_DAT_376d_417a + 1) - (uint)DAT_376d_3635) + 0x1514);
    if (bVar1 < DAT_376d_4187) {
      DAT_376d_4187 = DAT_376d_4187 - bVar1;
    }
    else {
      DAT_376d_4187 = 0;
      DAT_376d_3cd4 = 3;
      DAT_376d_3cd1 = 1;
      FUN_1c27_03da(10,0x20000);
    }
    FUN_183c_05d8();
  }
  return;
}

