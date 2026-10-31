
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

uint __cdecl16far FUN_1b7f_0078(int param_1)

{
  byte bVar1;
  undefined2 uVar2;
  uint uVar3;
  undefined2 in_DX;
  
  if (param_1 == 0) {
    uVar3 = 0;
    if (DAT_3360_1636 == '\0') {
      bVar1 = FUN_1b7f_003a();
      FUN_1b7f_005c(10,bVar1 & 0xf0 | 6);
      uVar2 = FUN_219b_3aa6();
      _DAT_3360_3512 = CONCAT22(in_DX,uVar2);
      FUN_219b_3ab8(0x70,6,(char *)s_Go_down_3360_1b7d + 2);
      uVar3 = FUN_1b7f_003a();
      FUN_1b7f_005c(0xb,uVar3 | 0x40);
      FUN_1b7f_003a();
      bVar1 = in(0xa1);
      uVar3 = bVar1 & 0xfe;
      out(0xa1,(char)uVar3);
      DAT_3360_1636 = '\x01';
    }
  }
  else {
    if (param_1 - 1U != 0) {
      return param_1 - 1U;
    }
    uVar3 = 0;
    if (DAT_3360_1636 != '\0') {
      bVar1 = in(0xa1);
      out(0xa1,bVar1 | 1);
      uVar3 = FUN_1b7f_003a();
      FUN_1b7f_005c(0xb,uVar3 & 0xffbf);
      uVar3 = FUN_219b_3ab8(0x70,_DAT_3360_3512);
      DAT_3360_1636 = '\0';
    }
  }
  return uVar3;
}

