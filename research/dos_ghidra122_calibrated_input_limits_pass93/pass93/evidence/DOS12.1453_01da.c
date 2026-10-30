
void __cdecl16far FUN_1453_01da(char param_1)

{
  char cVar1;
  int iVar2;
  undefined2 uVar3;
  int in_DX;
  
  FUN_1155_0256();
  if (param_1 == '\0') {
    iVar2 = FUN_1818_2958();
    if (in_DX == 0 && iVar2 == 0) {
      cVar1 = FUN_1275_15d8();
      if (cVar1 != '\0') {
        FUN_1155_0090();
        FUN_1155_0256();
        FUN_1d00_0500();
      }
    }
  }
  FUN_1453_019c();
  if (param_1 == '\0') {
    FUN_1d00_1602();
  }
  else {
    FUN_21c2_07e0(0x8a1,DAT_339b_61ca,1000,DAT_339b_61cc,0x15e,DAT_339b_61d2,100);
    FUN_21c2_07e0();
    FUN_21c2_07e0(0x8f5,DAT_339b_3c50 - DAT_339b_3c52,DAT_339b_3c50,DAT_339b_3c52);
    FUN_21c2_07e0(0x925,DAT_339b_3c54 - DAT_339b_3c56,DAT_339b_3c54,DAT_339b_3c56);
    if (DAT_339b_3c6e != '\0') {
      FUN_21c2_07e0(0x958,DAT_339b_3c58 - DAT_339b_3c5a,DAT_339b_3c58,DAT_339b_3c5a);
    }
    uVar3 = FUN_168a_0b8c(DAT_339b_df62,DAT_339b_df66,DAT_339b_df6c,DAT_339b_df6a);
    FUN_21c2_07e0(0x986,uVar3);
    uVar3 = FUN_1742_0010(DAT_339b_df6e,DAT_339b_df72,DAT_339b_df78,DAT_339b_df76);
    FUN_21c2_07e0(0x9cc,uVar3);
    uVar3 = FUN_1742_0014(DAT_339b_df7a,DAT_339b_df7e,DAT_339b_df84,DAT_339b_df82);
    FUN_21c2_07e0(0xa12,uVar3);
  }
  FUN_21c2_01eb();
  return;
}

