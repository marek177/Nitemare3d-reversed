
void __cdecl16far
FUN_1617_0700(int param_1,undefined2 param_2,undefined2 param_3,undefined2 param_4)

{
  byte bVar1;
  
  if ((DAT_374a_407f == '\0') && (DAT_374a_3c44 != 2)) {
    bVar1 = FUN_181c_040e(param_1,param_2,param_3,param_4);
    if (bVar1 < DAT_374a_40b5) {
      DAT_374a_40b5 = DAT_374a_40b5 - bVar1;
    }
    else {
      DAT_374a_40b5 = 0;
      DAT_374a_3c44 = 2;
      DAT_374a_3c41 = 1;
      DAT_374a_40b2 = *(undefined2 *)(param_1 + 8);
      FUN_14a7_12f6(param_1,param_2,param_3,param_4);
      FUN_1c07_03da(10,0x20000);
    }
    FUN_181c_05d8();
  }
  return;
}

