
void __cdecl16far
FUN_1609_0702(int param_1,undefined2 param_2,undefined2 param_3,undefined2 param_4)

{
  byte bVar1;
  
  if ((DAT_3360_3fa9 == '\0') && (DAT_3360_3b6e != 2)) {
    bVar1 = FUN_17f5_0400(param_1,param_2,param_3,param_4);
    if (bVar1 < DAT_3360_3fdf) {
      DAT_3360_3fdf = DAT_3360_3fdf - bVar1;
    }
    else {
      DAT_3360_3fdf = 0;
      DAT_3360_3b6e = 2;
      DAT_3360_3b6b = 1;
      DAT_3360_3fdc = *(undefined2 *)(param_1 + 8);
      FUN_1499_12f8(param_1,param_2,param_3,param_4);
      FUN_1bdd_03e6(10,0x20000);
    }
    FUN_17f5_05ca();
  }
  return;
}

