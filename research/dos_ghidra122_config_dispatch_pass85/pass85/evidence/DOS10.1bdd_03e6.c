
void __cdecl16far FUN_1bdd_03e6(word param_1,int param_2,byte param_3)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  dword dVar4;
  
  if ((DAT_3360_3fa6 != '\0') && (((undefined2 *)&DAT_3360_3dbc)[param_1 * 3] != 0)) {
    if (DAT_3360_3b67 == '\0') {
      iVar1 = FUN_206c_0fab();
      if (iVar1 != 0) {
        if (param_3 < DAT_3360_170c) {
          return;
        }
        FUN_206c_0f18();
      }
    }
    else {
      iVar1 = FUN_206c_0f79();
      if (iVar1 != 0) {
        if (param_3 < DAT_3360_170c) {
          return;
        }
        FUN_206c_0ee9();
      }
    }
    DAT_3360_170c = param_3;
    dVar4 = FUN_1739_04f0(param_1);
    uVar2 = (uint)dVar4;
    if (dVar4 == 0) {
      dVar4 = FUN_1bdd_0376(param_1);
      uVar2 = (uint)dVar4;
    }
    if (DAT_3360_3b67 == '\0') {
      FUN_206c_0953(uVar2,(int)(dVar4 >> 0x10));
    }
    else {
      if (param_2 == 1) {
        uVar2 = uVar2 & 0xff00;
      }
      else {
        uVar2 = ((uint)DAT_3360_3fa3 * 0xf) / 100;
      }
      if (param_2 == 2) {
        uVar3 = uVar2 & 0xff00;
      }
      else {
        uVar3 = ((uint)DAT_3360_3fa3 * 0xf) / 100;
      }
      FUN_206c_0544(CONCAT11((char)(uVar3 >> 8),(char)uVar2),uVar3);
      FUN_206c_0a09(dVar4);
    }
  }
  return;
}

