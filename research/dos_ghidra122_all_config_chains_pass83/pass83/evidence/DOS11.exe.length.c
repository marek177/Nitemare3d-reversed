
undefined2 __cdecl16far FUN_21bc_290a(int param_1)

{
  undefined2 uVar1;
  long lVar2;
  long lVar3;
  undefined2 local_6;
  
  if ((param_1 < 0) || (DAT_3395_211a <= param_1)) {
    DAT_3395_210a = 9;
    uVar1 = 0xffff;
  }
  else {
    lVar2 = FUN_21bc_1bd6((undefined1 *)&DAT_3395_21bc,param_1,0,0,1);
    if (lVar2 == -1) {
      uVar1 = 0xffff;
    }
    else {
      lVar3 = FUN_21bc_1bd6((undefined1 *)&DAT_3395_21bc,param_1,0,0,2);
      uVar1 = (undefined2)lVar3;
      if (lVar3 != lVar2) {
        FUN_21bc_1bd6((undefined1 *)&DAT_3395_21bc,param_1,lVar2,0);
      }
    }
  }
  return uVar1;
}

