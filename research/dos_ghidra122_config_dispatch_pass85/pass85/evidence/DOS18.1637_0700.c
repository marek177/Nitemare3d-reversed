
void __cdecl16far
FUN_1637_0700(int param_1,undefined2 param_2,undefined2 param_3,undefined2 param_4)

{
  byte bVar1;
  
  if ((DAT_376d_4151 == '\0') && (DAT_376d_3cd4 != 2)) {
    bVar1 = FUN_183c_040e(param_1,param_2,param_3,param_4);
    if (bVar1 < DAT_376d_4187) {
      DAT_376d_4187 = DAT_376d_4187 - bVar1;
    }
    else {
      DAT_376d_4187 = 0;
      DAT_376d_3cd4 = 2;
      DAT_376d_3cd1 = 1;
      DAT_376d_4184 = *(undefined2 *)(param_1 + 8);
      FUN_14c7_12f6(param_1,param_2,param_3,param_4);
      FUN_1c27_03da(10,0x20000);
    }
    FUN_183c_05d8();
  }
  return;
}

