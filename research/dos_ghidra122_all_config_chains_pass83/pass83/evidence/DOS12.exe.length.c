
undefined2 __cdecl16far FUN_21c2_290a(int param_1)

{
  undefined2 uVar1;
  long lVar2;
  long lVar3;
  undefined2 local_6;
  
  if ((param_1 < 0) || (DAT_339b_2116 <= param_1)) {
    DAT_339b_2106 = 9;
    uVar1 = 0xffff;
  }
  else {
    lVar2 = FUN_21c2_1bd6(0x21c2,param_1,0,0,1);
    if (lVar2 == -1) {
      uVar1 = 0xffff;
    }
    else {
      lVar3 = FUN_21c2_1bd6(0x21c2,param_1,0,0,2);
      uVar1 = (undefined2)lVar3;
      if (lVar3 != lVar2) {
        FUN_21c2_1bd6(0x21c2,param_1,lVar2,0);
      }
    }
  }
  return uVar1;
}

