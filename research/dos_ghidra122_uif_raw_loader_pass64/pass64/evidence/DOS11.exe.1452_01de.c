
void __cdecl16far FUN_1452_01de(char param_1)

{
  char cVar1;
  int iVar2;
  undefined2 uVar3;
  int in_DX;
  
  FUN_1155_0256();
  if (param_1 == '\0') {
    iVar2 = FUN_1817_2966();
    if (in_DX == 0 && iVar2 == 0) {
      cVar1 = FUN_1275_15c6();
      if (cVar1 != '\0') {
        FUN_1155_0090();
        FUN_1155_0256();
        FUN_1d00_04fe();
      }
    }
  }
  FUN_1452_01a0();
  if (param_1 == '\0') {
    FUN_1d00_1600();
  }
  else {
    FUN_21bc_07e0(0x897,DAT_3395_61ca,1000,DAT_3395_61cc,0x15e,DAT_3395_61d2,100);
    FUN_21bc_07e0();
    FUN_21bc_07e0(0x8eb,DAT_3395_3c50 - DAT_3395_3c52,DAT_3395_3c50,DAT_3395_3c52);
    FUN_21bc_07e0(0x91b,DAT_3395_3c54 - DAT_3395_3c56,DAT_3395_3c54,DAT_3395_3c56);
    if (DAT_3395_3c6e != '\0') {
      FUN_21bc_07e0(0x94e,DAT_3395_3c58 - DAT_3395_3c5a,DAT_3395_3c58,DAT_3395_3c5a);
    }
    uVar3 = FUN_1689_0b90(DAT_3395_df52,DAT_3395_df56,DAT_3395_df5c,DAT_3395_df5a);
    FUN_21bc_07e0(0x97c,uVar3);
    uVar3 = FUN_1689_0b94(DAT_3395_df5e,DAT_3395_df62,DAT_3395_df68,DAT_3395_df66);
    FUN_21bc_07e0(0x9c2,uVar3);
    uVar3 = FUN_1689_0b98(DAT_3395_df6a,DAT_3395_df6e,DAT_3395_df74,DAT_3395_df72);
    FUN_21bc_07e0(0xa08,uVar3);
  }
  FUN_21bc_01eb();
  return;
}

