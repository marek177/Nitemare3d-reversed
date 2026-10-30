
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl16far FUN_1277_0c70(void)

{
  undefined2 uVar1;
  int iVar2;
  int iVar3;
  int in_DX;
  char *pcVar4;
  
  _DAT_3754_40b4 = 0x130;
  DAT_3754_40ba = 0x3c;
  DAT_3754_40bb = 0x46;
  DAT_3754_40bc = 1;
  DAT_3754_40bd = 1;
  DAT_3754_40be = 1;
  DAT_3754_40b8 = 0x32;
  DAT_3754_40b9 = 0x32;
  DAT_3754_40bf = 0;
  DAT_3754_40c0 = 0;
  DAT_3754_40c1 = 0;
  DAT_3754_40c2 = 0;
  DAT_3754_40c3 = 0;
  uVar1 = FUN_1277_0c20(0x598,0x8000);
  iVar2 = FUN_21d1_1c72(uVar1);
  if (0 < iVar2) {
    pcVar4 = (char *)0x21d1;
    iVar3 = FUN_21d1_290a(iVar2);
    if ((iVar3 != 0x10) || (in_DX != 0)) {
      pcVar4 = (char *)s_About_to__s_game____s__Press_ESC_3754_1f72 + 0x2b;
      FUN_1f9d_000c(0x5a3);
    }
    FUN_21d1_1e14(pcVar4,iVar2,(undefined2 *)&DAT_3754_40b4,0x10);
    FUN_21d1_1bb6(0x21d1,iVar2);
  }
  FUN_1277_0bc2(DAT_3754_40b4);
  return;
}

