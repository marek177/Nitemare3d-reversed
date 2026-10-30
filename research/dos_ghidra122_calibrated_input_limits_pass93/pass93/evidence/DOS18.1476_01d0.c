
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl16far FUN_1476_01d0(char param_1)

{
  char cVar1;
  int iVar2;
  undefined2 uVar3;
  int in_DX;
  
  FUN_1156_0254();
  if (param_1 == '\0') {
    iVar2 = FUN_183c_299e();
    if (in_DX == 0 && iVar2 == 0) {
      cVar1 = FUN_1277_17dc();
      if (cVar1 != '\0') {
        FUN_1156_008e();
        FUN_1156_0254();
        FUN_1d25_04fe();
      }
    }
  }
  FUN_1476_0192();
  if (param_1 == '\0') {
    FUN_1d25_1630();
  }
  else {
    FUN_21ea_07e4(0x8d3,DAT_376d_626c,1000,DAT_376d_626e,0x15e,_DAT_376d_6274,100);
    FUN_21ea_07e4();
    FUN_21ea_07e4(0x927,DAT_376d_3cb0 - DAT_376d_3cb2,DAT_376d_3cb0,DAT_376d_3cb2);
    FUN_21ea_07e4(0x957,DAT_376d_3cb4 - DAT_376d_3cb6,DAT_376d_3cb4,DAT_376d_3cb6);
    if (DAT_376d_3cce != '\0') {
      FUN_21ea_07e4(0x98a,DAT_376d_3cb8 - DAT_376d_3cba,DAT_376d_3cb8,DAT_376d_3cba);
    }
    uVar3 = FUN_16af_0b8a(DAT_376d_e004,DAT_376d_e008,DAT_376d_e00e,DAT_376d_e00c);
    FUN_21ea_07e4(0x9b8,uVar3);
    uVar3 = FUN_1767_000e(_DAT_376d_e010,DAT_376d_e014,DAT_376d_e01a,DAT_376d_e018);
    FUN_21ea_07e4(0x9fe,uVar3);
    uVar3 = FUN_1767_0012(DAT_376d_e01c,DAT_376d_e020,DAT_376d_e026,DAT_376d_e024);
    FUN_21ea_07e4(0xa44,uVar3);
  }
  FUN_21ea_01ef();
  return;
}

