
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

uint __cdecl16far FUN_1bb2_0074(int param_1)

{
  byte bVar1;
  undefined2 uVar2;
  uint uVar3;
  undefined2 in_DX;
  
  if (param_1 == 0) {
    uVar3 = 0;
    if (DAT_3754_16c0 == '\0') {
      bVar1 = FUN_1bb2_0036();
      FUN_1bb2_0058(10,bVar1 & 0xf0 | 6);
      uVar2 = FUN_21d1_39e2();
      _DAT_3754_35e0 = CONCAT22(in_DX,uVar2);
      FUN_21d1_39f4(0x70,2,0x1bb2);
      uVar3 = FUN_1bb2_0036();
      FUN_1bb2_0058(0xb,uVar3 | 0x40);
      FUN_1bb2_0036();
      bVar1 = in(0xa1);
      uVar3 = bVar1 & 0xfe;
      out(0xa1,(char)uVar3);
      DAT_3754_16c0 = '\x01';
    }
  }
  else {
    if (param_1 - 1U != 0) {
      return param_1 - 1U;
    }
    uVar3 = 0;
    if (DAT_3754_16c0 != '\0') {
      bVar1 = in(0xa1);
      out(0xa1,bVar1 | 1);
      uVar3 = FUN_1bb2_0036();
      FUN_1bb2_0058(0xb,uVar3 & 0xffbf);
      uVar3 = FUN_21d1_39f4(0x70,_DAT_3754_35e0);
      DAT_3754_16c0 = '\0';
    }
  }
  return uVar3;
}

