
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl16far FUN_1817_2080(void)

{
  byte bVar1;
  
  if ((DAT_3395_40af == '\0') &&
     (((undefined1 *)&DAT_3395_d35a)[*(byte *)((int)_DAT_3395_40d8 + 1)] == '\a')) {
    if (DAT_3395_14f1 == 0) {
      DAT_3395_14f1 = FUN_10f6_0054(7);
    }
    FUN_1155_0256();
    bVar1 = *(byte *)(((uint)*(byte *)((int)_DAT_3395_40d8 + 1) - (uint)DAT_3395_14f1) + 0x14ee);
    if (bVar1 < DAT_3395_40e5) {
      DAT_3395_40e5 = DAT_3395_40e5 - bVar1;
    }
    else {
      DAT_3395_40e5 = 0;
      DAT_3395_3c74 = 3;
      DAT_3395_3c71 = 1;
      FUN_1bff_040a(10,0x20000);
    }
    FUN_1817_05ca();
  }
  return;
}

