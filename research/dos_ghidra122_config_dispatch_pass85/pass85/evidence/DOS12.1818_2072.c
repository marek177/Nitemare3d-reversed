
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl16far FUN_1818_2072(void)

{
  byte bVar1;
  
  if ((DAT_339b_40af == '\0') &&
     (((undefined1 *)&DAT_339b_d36a)[*(byte *)((int)_DAT_339b_40d8 + 1)] == '\a')) {
    if (DAT_339b_14e3 == 0) {
      DAT_339b_14e3 = FUN_10f6_0054(7);
    }
    FUN_1155_0256();
    bVar1 = *(byte *)(((uint)*(byte *)((int)_DAT_339b_40d8 + 1) - (uint)DAT_339b_14e3) + 0x14e0);
    if (bVar1 < DAT_339b_40e5) {
      DAT_339b_40e5 = DAT_339b_40e5 - bVar1;
    }
    else {
      DAT_339b_40e5 = 0;
      DAT_339b_3c74 = 3;
      DAT_339b_3c71 = 1;
      FUN_1bff_040c(10,0x20000);
    }
    FUN_1818_05c6();
  }
  return;
}

