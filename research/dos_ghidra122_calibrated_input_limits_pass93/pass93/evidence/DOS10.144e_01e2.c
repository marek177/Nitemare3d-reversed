
void __cdecl16far FUN_144e_01e2(char param_1)

{
  char cVar1;
  int iVar2;
  undefined2 uVar3;
  int in_DX;
  
  FUN_1155_0256();
  if (param_1 == '\0') {
    iVar2 = FUN_17f5_2966();
    if (in_DX == 0 && iVar2 == 0) {
      cVar1 = FUN_1273_15a0();
      if (cVar1 != '\0') {
        FUN_1155_0090();
        FUN_1155_0256();
        FUN_1cdc_04fa();
      }
    }
  }
  FUN_144e_01a4();
  if (param_1 == '\0') {
    FUN_1cdc_161c();
  }
  else {
    FUN_219b_08dc();
    FUN_219b_08dc();
    FUN_219b_08dc();
    FUN_219b_08dc(0x8c5,DAT_3360_3b50 - DAT_3360_3b52,DAT_3360_3b50,DAT_3360_3b52);
    FUN_219b_08dc(0x8f5,DAT_3360_3b54 - DAT_3360_3b56,DAT_3360_3b54,DAT_3360_3b56);
    if (DAT_3360_3b68 != '\0') {
      FUN_219b_08dc(0x928,DAT_3360_3b58 - DAT_3360_3b5a,DAT_3360_3b58,DAT_3360_3b5a);
    }
    uVar3 = FUN_1681_0b8c(DAT_3360_de4c,DAT_3360_de50,DAT_3360_de56,DAT_3360_de54);
    FUN_219b_08dc(0x956,uVar3);
    uVar3 = FUN_1739_0010(DAT_3360_de58,DAT_3360_de5c,DAT_3360_de62,DAT_3360_de60);
    FUN_219b_08dc(0x9a8,uVar3);
  }
  FUN_219b_01e3();
  return;
}

