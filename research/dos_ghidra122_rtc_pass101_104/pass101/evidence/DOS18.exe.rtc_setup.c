
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

uint __cdecl16far FUN_1bc8_0078(int param_1)

{
  byte bVar1;
  undefined2 uVar2;
  uint uVar3;
  undefined2 in_DX;
  
  if (param_1 == 0) {
    uVar3 = 0;
    if (DAT_376d_16ee == '\0') {
      bVar1 = FUN_1bc8_003a();
      FUN_1bc8_005c(10,bVar1 & 0xf0 | 6);
      uVar2 = FUN_21ea_39e6();
      _DAT_376d_366c = CONCAT22(in_DX,uVar2);
      FUN_21ea_39f8(0x70,6,(char *)s_Omnifarious__all_things__376d_1bc4 + 4);
      uVar3 = FUN_1bc8_003a();
      FUN_1bc8_005c(0xb,uVar3 | 0x40);
      FUN_1bc8_003a();
      bVar1 = in(0xa1);
      uVar3 = bVar1 & 0xfe;
      out(0xa1,(char)uVar3);
      DAT_376d_16ee = '\x01';
    }
  }
  else {
    if (param_1 - 1U != 0) {
      return param_1 - 1U;
    }
    uVar3 = 0;
    if (DAT_376d_16ee != '\0') {
      bVar1 = in(0xa1);
      out(0xa1,bVar1 | 1);
      uVar3 = FUN_1bc8_003a();
      FUN_1bc8_005c(0xb,uVar3 & 0xffbf);
      uVar3 = FUN_21ea_39f8(0x70,_DAT_376d_366c);
      DAT_376d_16ee = '\0';
    }
  }
  return uVar3;
}

