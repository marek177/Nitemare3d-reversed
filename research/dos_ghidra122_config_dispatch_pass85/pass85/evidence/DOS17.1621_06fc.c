
void __cdecl16far
FUN_1621_06fc(int param_1,undefined2 param_2,undefined2 param_3,undefined2 param_4)

{
  byte bVar1;
  
  if ((DAT_3754_40c1 == '\0') && (DAT_3754_3c44 != 2)) {
    bVar1 = FUN_1826_040a(param_1,param_2,param_3,param_4);
    if (bVar1 < DAT_3754_40f7) {
      DAT_3754_40f7 = DAT_3754_40f7 - bVar1;
    }
    else {
      DAT_3754_40f7 = 0;
      DAT_3754_3c44 = 2;
      DAT_3754_3c41 = 1;
      DAT_3754_40f4 = *(undefined2 *)(param_1 + 8);
      FUN_14b1_12f2(param_1,param_2,param_3,param_4);
      FUN_1c11_03d6(10,0x20000);
    }
    FUN_1826_05d4();
  }
  return;
}

