
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl16far FUN_181c_20b0(void)

{
  byte bVar1;
  
  if ((DAT_374a_407f == '\0') &&
     (((undefined1 *)&DAT_374a_d33a)[*(byte *)((int)_DAT_374a_40a8 + 1)] == '\a')) {
    if (DAT_374a_14e6 != DAT_374a_6196) {
      DAT_374a_14e6 = DAT_374a_6196;
      DAT_374a_35a5 = FUN_10f7_004e(7);
    }
    FUN_1156_0254();
    bVar1 = *(byte *)(((uint)*(byte *)((int)_DAT_374a_40a8 + 1) - (uint)DAT_374a_35a5) + 0x14e2);
    if (bVar1 < DAT_374a_40b5) {
      DAT_374a_40b5 = DAT_374a_40b5 - bVar1;
    }
    else {
      DAT_374a_40b5 = 0;
      DAT_374a_3c44 = 3;
      DAT_374a_3c41 = 1;
      FUN_1c07_03da(10,0x20000);
    }
    FUN_181c_05d8();
  }
  return;
}

