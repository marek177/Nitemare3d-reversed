
void __cdecl16far FUN_17f5_2080(void)

{
  byte bVar1;
  
  if ((DAT_3360_3fa9 == '\0') &&
     (((undefined1 *)&DAT_3360_d254)[*(byte *)((int)DAT_3360_3fd2 + 1)] == '\a')) {
    if (DAT_3360_1423 == 0) {
      DAT_3360_1423 = FUN_10f6_0054(7);
    }
    FUN_1155_0256();
    bVar1 = *(byte *)(((uint)*(byte *)((int)DAT_3360_3fd2 + 1) - (uint)DAT_3360_1423) + 0x1420);
    if (bVar1 < DAT_3360_3fdf) {
      DAT_3360_3fdf = DAT_3360_3fdf - bVar1;
    }
    else {
      DAT_3360_3fdf = 0;
      DAT_3360_3b6e = 3;
      DAT_3360_3b6b = 1;
      FUN_1bdd_03e6(10,0x20000);
    }
    FUN_17f5_05ca();
  }
  return;
}

