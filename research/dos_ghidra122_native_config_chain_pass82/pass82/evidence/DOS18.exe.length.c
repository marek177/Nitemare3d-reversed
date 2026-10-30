
undefined2 __cdecl16far FUN_21ea_290e(int param_1)

{
  undefined2 uVar1;
  long lVar2;
  long lVar3;
  undefined2 local_6;
  
  if ((param_1 < 0) || (DAT_376d_2126 <= param_1)) {
    DAT_376d_2116 = 9;
    uVar1 = 0xffff;
  }
  else {
    lVar2 = FUN_21ea_1bda(0x21ea,param_1,0,0,1);
    if (lVar2 == -1) {
      uVar1 = 0xffff;
    }
    else {
      lVar3 = FUN_21ea_1bda(0x21ea,param_1,0,0,2);
      uVar1 = (undefined2)lVar3;
      if (lVar3 != lVar2) {
        FUN_21ea_1bda(0x21ea,param_1,lVar2,0);
      }
    }
  }
  return uVar1;
}

