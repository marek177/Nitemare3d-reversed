
void __cdecl16far FUN_1277_0c20(void)

{
  int iVar1;
  int iVar2;
  int in_DX;
  char *pcVar3;
  
  DAT_374a_4072 = 0x130;
  DAT_374a_4076._2_1_ = 0x3c;
  DAT_374a_4076._3_1_ = 0x46;
  DAT_374a_407a = 1;
  DAT_374a_407b = 1;
  DAT_374a_407c = 1;
  DAT_374a_4076._0_1_ = 0x32;
  DAT_374a_4076._1_1_ = 0x32;
  DAT_374a_407d = 0;
  DAT_374a_407e = 0;
  DAT_374a_407f = 0;
  DAT_374a_4080 = 0;
  DAT_374a_4081 = 0;
  iVar1 = FUN_21c7_1c76(0x598,0x8000);
  if (0 < iVar1) {
    pcVar3 = (char *)0x21c7;
    iVar2 = FUN_21c7_290e(iVar1);
    if ((iVar2 != 0x10) || (in_DX != 0)) {
      pcVar3 = (char *)s_About_to__s_game____s__Press_ESC_374a_1f6e + 0x26;
      FUN_1f94_0000(0x5a3);
    }
    FUN_21c7_1e18(pcVar3,iVar1,(undefined4 *)&DAT_374a_4072,0x10);
    FUN_21c7_1bba(0x21c7,iVar1);
  }
  FUN_1277_0bc2((undefined2)DAT_374a_4072);
  return;
}

