
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

uint __cdecl16far FUN_1ba8_0078(int param_1)

{
  byte bVar1;
  undefined2 uVar2;
  uint uVar3;
  undefined2 in_DX;
  
  if (param_1 == 0) {
    uVar3 = 0;
    if (DAT_374a_16bc == '\0') {
      bVar1 = FUN_1ba8_003a();
      FUN_1ba8_005c(10,bVar1 & 0xf0 | 6);
      uVar2 = FUN_21c7_39e6();
      _DAT_374a_35dc = CONCAT22(in_DX,uVar2);
      FUN_21c7_39f8(0x70,6,(char *)s_Omnifarious__all_things__374a_1b92 + 0x16);
      uVar3 = FUN_1ba8_003a();
      FUN_1ba8_005c(0xb,uVar3 | 0x40);
      FUN_1ba8_003a();
      bVar1 = in(0xa1);
      uVar3 = bVar1 & 0xfe;
      out(0xa1,(char)uVar3);
      DAT_374a_16bc = '\x01';
    }
  }
  else {
    if (param_1 - 1U != 0) {
      return param_1 - 1U;
    }
    uVar3 = 0;
    if (DAT_374a_16bc != '\0') {
      bVar1 = in(0xa1);
      out(0xa1,bVar1 | 1);
      uVar3 = FUN_1ba8_003a();
      FUN_1ba8_005c(0xb,uVar3 & 0xffbf);
      uVar3 = FUN_21c7_39f8(0x70,_DAT_374a_35dc);
      DAT_374a_16bc = '\0';
    }
  }
  return uVar3;
}

