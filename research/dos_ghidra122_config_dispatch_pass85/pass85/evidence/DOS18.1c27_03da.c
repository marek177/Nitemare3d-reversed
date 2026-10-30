
void __cdecl16far FUN_1c27_03da(word param_1,int param_2,byte param_3)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  dword dVar4;
  
  if ((DAT_376d_414e != '\0') && (((undefined2 *)&DAT_376d_3f64)[param_1 * 3] != 0)) {
    if (DAT_376d_3cc7 == '\0') {
      iVar1 = FUN_20bc_0fa7();
      if (iVar1 != 0) {
        if (param_3 < DAT_376d_17e4) {
          return;
        }
        FUN_20bc_0f14();
      }
    }
    else {
      iVar1 = FUN_20bc_0f75();
      if (iVar1 != 0) {
        if (param_3 < DAT_376d_17e4) {
          return;
        }
        FUN_20bc_0ee5();
      }
    }
    DAT_376d_17e4 = param_3;
    dVar4 = FUN_1767_068a(param_1);
    uVar2 = (uint)dVar4;
    if (dVar4 == 0) {
      dVar4 = FUN_1c27_03a2(param_1);
      uVar2 = (uint)dVar4;
    }
    if (DAT_376d_3cc7 == '\0') {
      FUN_20bc_094f(uVar2,(int)(dVar4 >> 0x10));
    }
    else {
      if (param_2 == 1) {
        uVar2 = uVar2 & 0xff00;
      }
      else {
        uVar2 = ((uint)DAT_376d_414b * 0xf) / 100;
      }
      if (param_2 == 2) {
        uVar3 = uVar2 & 0xff00;
      }
      else {
        uVar3 = ((uint)DAT_376d_414b * 0xf) / 100;
      }
      FUN_20bc_0540(CONCAT11((char)(uVar3 >> 8),(char)uVar2),uVar3);
      FUN_20bc_0a05(dVar4);
    }
  }
  return;
}

