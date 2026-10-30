
void __cdecl16far
FUN_1611_0706(int param_1,undefined2 param_2,undefined2 param_3,undefined2 param_4)

{
  byte bVar1;
  
  if ((DAT_3395_40af == '\0') && (DAT_3395_3c74 != 2)) {
    bVar1 = FUN_1817_0400(param_1,param_2,param_3,param_4);
    if (bVar1 < DAT_3395_40e5) {
      DAT_3395_40e5 = DAT_3395_40e5 - bVar1;
    }
    else {
      DAT_3395_40e5 = 0;
      DAT_3395_3c74 = 2;
      DAT_3395_3c71 = 1;
      DAT_3395_40e2 = *(undefined2 *)(param_1 + 8);
      FUN_14a2_12ec(param_1,param_2,param_3,param_4);
      FUN_1bff_040a(10,0x20000);
    }
    FUN_1817_05ca();
  }
  return;
}

