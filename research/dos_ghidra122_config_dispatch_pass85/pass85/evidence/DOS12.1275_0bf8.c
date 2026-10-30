
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl16far FUN_1275_0bf8(void)

{
  int iVar1;
  int iVar2;
  int in_DX;
  char *pcVar3;
  
  _DAT_339b_40a2 = 0x130;
  DAT_339b_40a8 = 0x3c;
  DAT_339b_40a9 = 0x46;
  DAT_339b_40aa = 1;
  DAT_339b_40ab = 1;
  DAT_339b_40ac = 1;
  DAT_339b_40a6 = 0x32;
  DAT_339b_40a7 = 0x32;
  DAT_339b_40ad = 0;
  DAT_339b_40ae = 0;
  DAT_339b_40af = 0;
  DAT_339b_40b0 = 0;
  DAT_339b_40b1 = 0;
  iVar1 = FUN_21c2_1c72(0x594,0x8000);
  if (0 < iVar1) {
    pcVar3 = (char *)0x21c2;
    iVar2 = FUN_21c2_290a(iVar1);
    if ((iVar2 != 0x10) || (in_DX != 0)) {
      pcVar3 = (char *)s_user_sav_339b_1f8e + 1;
      FUN_1f8f_0002(0x59f);
    }
    FUN_21c2_1e14(pcVar3,iVar1,(undefined2 *)&DAT_339b_40a2,0x10);
    FUN_21c2_1bb6(0x21c2,iVar1);
  }
  FUN_1275_0b9a(DAT_339b_40a2);
  return;
}

