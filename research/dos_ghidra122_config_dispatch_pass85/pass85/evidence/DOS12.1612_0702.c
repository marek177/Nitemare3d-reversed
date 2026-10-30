
void __cdecl16far
FUN_1612_0702(int param_1,undefined2 param_2,undefined2 param_3,undefined2 param_4)

{
  byte bVar1;
  
  if ((DAT_339b_40af == '\0') && (DAT_339b_3c74 != 2)) {
    bVar1 = FUN_1818_03fc(param_1,param_2,param_3,param_4);
    if (bVar1 < DAT_339b_40e5) {
      DAT_339b_40e5 = DAT_339b_40e5 - bVar1;
    }
    else {
      DAT_339b_40e5 = 0;
      DAT_339b_3c74 = 2;
      DAT_339b_3c71 = 1;
      DAT_339b_40e2 = *(undefined2 *)(param_1 + 8);
      FUN_14a2_12f8(param_1,param_2,param_3,param_4);
      FUN_1bff_040c(10,0x20000);
    }
    FUN_1818_05c6();
  }
  return;
}

