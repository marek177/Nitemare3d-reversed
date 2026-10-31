
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

uint __cdecl16far FUN_1b9f_0080(int param_1)

{
  byte bVar1;
  undefined2 uVar2;
  uint uVar3;
  undefined2 in_DX;
  
  if (param_1 == 0) {
    uVar3 = 0;
    if (DAT_3395_16c6 == '\0') {
      bVar1 = FUN_1b9f_0042();
      FUN_1b9f_0064(10,bVar1 & 0xf0 | 6);
      uVar2 = FUN_21bc_39e2();
      _DAT_3395_360c = CONCAT22(in_DX,uVar2);
      FUN_21bc_39f4(0x70,0xe,(char *)s_Omnipotent__all_powerful__3395_1b9b + 4);
      uVar3 = FUN_1b9f_0042();
      FUN_1b9f_0064(0xb,uVar3 | 0x40);
      FUN_1b9f_0042();
      bVar1 = in(0xa1);
      uVar3 = bVar1 & 0xfe;
      out(0xa1,(char)uVar3);
      DAT_3395_16c6 = '\x01';
    }
  }
  else {
    if (param_1 - 1U != 0) {
      return param_1 - 1U;
    }
    uVar3 = 0;
    if (DAT_3395_16c6 != '\0') {
      bVar1 = in(0xa1);
      out(0xa1,bVar1 | 1);
      uVar3 = FUN_1b9f_0042();
      FUN_1b9f_0064(0xb,uVar3 & 0xffbf);
      uVar3 = FUN_21bc_39f4(0x70,_DAT_3395_360c);
      DAT_3395_16c6 = '\0';
    }
  }
  return uVar3;
}

