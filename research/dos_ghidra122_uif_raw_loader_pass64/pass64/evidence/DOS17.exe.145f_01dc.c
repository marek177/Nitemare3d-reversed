
void __cdecl16far FUN_145f_01dc(char param_1)

{
  char cVar1;
  int iVar2;
  undefined2 uVar3;
  int in_DX;
  
  FUN_1156_0254();
  if (param_1 == '\0') {
    iVar2 = FUN_1826_299a();
    if (in_DX == 0 && iVar2 == 0) {
      cVar1 = FUN_1277_1678();
      if (cVar1 != '\0') {
        FUN_1156_008e();
        FUN_1156_0254();
        FUN_1d0f_04fa();
      }
    }
  }
  FUN_145f_019e();
  if (param_1 == '\0') {
    FUN_1d0f_15fc();
  }
  else {
    FUN_21d1_07e0(0x8a5,DAT_3754_61dc,1000,DAT_3754_61de,0x15e,DAT_3754_61e4,100);
    FUN_21d1_07e0();
    FUN_21d1_07e0(0x8f9,DAT_3754_3c20 - DAT_3754_3c22,DAT_3754_3c20,DAT_3754_3c22);
    FUN_21d1_07e0(0x929,DAT_3754_3c24 - DAT_3754_3c26,DAT_3754_3c24,DAT_3754_3c26);
    if (DAT_3754_3c3e != '\0') {
      FUN_21d1_07e0(0x95c,DAT_3754_3c28 - DAT_3754_3c2a,DAT_3754_3c28,DAT_3754_3c2a);
    }
    uVar3 = FUN_1699_0b86(DAT_3754_df74,DAT_3754_df78,DAT_3754_df7e,DAT_3754_df7c);
    FUN_21d1_07e0(0x98a,uVar3);
    uVar3 = FUN_1699_0b8a(DAT_3754_df80,DAT_3754_df84,DAT_3754_df8a,DAT_3754_df88);
    FUN_21d1_07e0(0x9d0,uVar3);
    uVar3 = FUN_1751_000e(DAT_3754_df8c,DAT_3754_df90,DAT_3754_df96,DAT_3754_df94);
    FUN_21d1_07e0(0xa16,uVar3);
  }
  FUN_21d1_01eb();
  return;
}

