
void __cdecl16far FUN_1458_01d2(char param_1)

{
  char cVar1;
  int iVar2;
  undefined2 uVar3;
  int in_DX;
  
  FUN_1156_0254();
  if (param_1 == '\0') {
    iVar2 = FUN_181c_299e();
    if (in_DX == 0 && iVar2 == 0) {
      cVar1 = FUN_1277_1600();
      if (cVar1 != '\0') {
        FUN_1156_008e();
        FUN_1156_0254();
        FUN_1d05_04fe();
      }
    }
  }
  FUN_1458_0194();
  if (param_1 == '\0') {
    FUN_1d05_1600();
  }
  else {
    FUN_21c7_07e4(0x8a5,DAT_374a_619a,1000,DAT_374a_619c,0x15e,DAT_374a_61a2,100);
    FUN_21c7_07e4();
    FUN_21c7_07e4(0x8f9,DAT_374a_3c20 - DAT_374a_3c22,DAT_374a_3c20,DAT_374a_3c22);
    FUN_21c7_07e4(0x929,DAT_374a_3c24 - DAT_374a_3c26,DAT_374a_3c24,DAT_374a_3c26);
    if (DAT_374a_3c3e != '\0') {
      FUN_21c7_07e4(0x95c,DAT_374a_3c28 - DAT_374a_3c2a,DAT_374a_3c28,DAT_374a_3c2a);
    }
    uVar3 = FUN_168f_0b8a(DAT_374a_df32,DAT_374a_df36,DAT_374a_df3c,DAT_374a_df3a);
    FUN_21c7_07e4(0x98a,uVar3);
    uVar3 = FUN_1747_000e(DAT_374a_df3e,DAT_374a_df42,DAT_374a_df48,DAT_374a_df46);
    FUN_21c7_07e4(0x9d0,uVar3);
    uVar3 = FUN_1747_0012(DAT_374a_df4a,DAT_374a_df4e,DAT_374a_df54,DAT_374a_df52);
    FUN_21c7_07e4(0xa16,uVar3);
  }
  FUN_21c7_01ef();
  return;
}

