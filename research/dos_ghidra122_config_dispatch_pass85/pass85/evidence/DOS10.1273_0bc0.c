
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl16far FUN_1273_0bc0(void)

{
  int iVar1;
  int iVar2;
  int in_DX;
  char *pcVar3;
  
  _DAT_3360_3f9c = 0x130;
  DAT_3360_3fa2 = 0x3c;
  DAT_3360_3fa3 = 0x46;
  DAT_3360_3fa4 = 1;
  DAT_3360_3fa5 = 1;
  DAT_3360_3fa6 = 1;
  DAT_3360_3fa0 = 0x32;
  DAT_3360_3fa1 = 0x32;
  DAT_3360_3fa7 = 0;
  DAT_3360_3fa8 = 0;
  DAT_3360_3fa9 = 0;
  DAT_3360_3faa = 0;
  DAT_3360_3fab = 0;
  iVar1 = FUN_219b_1d6e(0x54a,0x8000);
  if (0 < iVar1) {
    pcVar3 = (char *)0x219b;
    iVar2 = FUN_219b_29ce(iVar1);
    if ((iVar2 != 0x10) || (in_DX != 0)) {
      pcVar3 = (char *)s_Copyright_1992__David_P_Gray__Gr_3360_1f3f + 0x28;
      FUN_1f67_000a(0x555);
    }
    FUN_219b_1f10(pcVar3,iVar1,(undefined2 *)&DAT_3360_3f9c,0x10);
    FUN_219b_1cb2(0x219b,iVar1);
  }
  FUN_1273_0b62(DAT_3360_3f9c);
  return;
}

