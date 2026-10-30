
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl16far FUN_1277_0c6e(void)

{
  undefined2 uVar1;
  int iVar2;
  int iVar3;
  int in_DX;
  char *pcVar4;
  
  _DAT_376d_4144 = 0x130;
  DAT_376d_414a = 0x3c;
  DAT_376d_414b = 0x46;
  DAT_376d_414c = 1;
  DAT_376d_414d = 1;
  DAT_376d_414e = 1;
  DAT_376d_4148 = 0x32;
  DAT_376d_4149 = 0x32;
  DAT_376d_414f = 0;
  DAT_376d_4150 = 0;
  DAT_376d_4151 = 0;
  DAT_376d_4152 = 0;
  DAT_376d_4153 = 0;
  uVar1 = FUN_1277_0c20(0x598,0x8000);
  iVar2 = FUN_21ea_1c76(uVar1);
  if (0 < iVar2) {
    pcVar4 = (char *)0x21ea;
    iVar3 = FUN_21ea_290e(iVar2);
    if ((iVar3 != 0x10) || (in_DX != 0)) {
      pcVar4 = (char *)s_About_to__s_game____s__Press_ESC_376d_1fac + 0xb;
      FUN_1fb7_0000(0x5a3);
    }
    FUN_21ea_1e18(pcVar4,iVar2,(undefined2 *)&DAT_376d_4144,0x10);
    FUN_21ea_1bba(0x21ea,iVar2);
  }
  FUN_1277_0bc2(DAT_376d_4144);
  return;
}

