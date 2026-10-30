
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl16far FUN_1275_0be6(void)

{
  int iVar1;
  int iVar2;
  int in_DX;
  char *pcVar3;
  
  _DAT_3395_40a2 = 0x130;
  DAT_3395_40a6._2_1_ = 0x3c;
  DAT_3395_40a6._3_1_ = 0x46;
  DAT_3395_40aa = 1;
  DAT_3395_40ab = 1;
  DAT_3395_40ac = 1;
  DAT_3395_40a6._0_1_ = 0x32;
  DAT_3395_40a6._1_1_ = 0x32;
  DAT_3395_40ad = 0;
  DAT_3395_40ae = 0;
  DAT_3395_40af = 0;
  DAT_3395_40b0 = 0;
  DAT_3395_40b1 = 0;
  iVar1 = FUN_21bc_1c72(0x589,0x8000);
  if (0 < iVar1) {
    pcVar3 = (char *)&DAT_3395_21bc;
    iVar2 = FUN_21bc_290a(iVar1);
    if ((iVar2 != 0x10) || (in_DX != 0)) {
      pcVar3 = (char *)s_About_to__s_game____s__Press_ESC_3395_1f66 + 0x23;
      FUN_1f89_0002(0x594);
    }
    FUN_21bc_1e14(pcVar3,iVar1,(undefined2 *)&DAT_3395_40a2,0x10);
    FUN_21bc_1bb6((undefined1 *)&DAT_3395_21bc,iVar1);
  }
  FUN_1275_0b88(DAT_3395_40a2);
  return;
}

