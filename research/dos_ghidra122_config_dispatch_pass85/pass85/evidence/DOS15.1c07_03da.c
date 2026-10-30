
void __cdecl16far FUN_1c07_03da(word param_1,int param_2,byte param_3)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  dword dVar4;
  
  if ((DAT_374a_407c != '\0') && (((undefined2 *)&DAT_374a_3e92)[param_1 * 3] != 0)) {
    if (DAT_374a_3c37 == '\0') {
      iVar1 = FUN_2099_0fa7();
      if (iVar1 != 0) {
        if (param_3 < DAT_374a_17b2) {
          return;
        }
        FUN_2099_0f14();
      }
    }
    else {
      iVar1 = FUN_2099_0f75();
      if (iVar1 != 0) {
        if (param_3 < DAT_374a_17b2) {
          return;
        }
        FUN_2099_0ee5();
      }
    }
    DAT_374a_17b2 = param_3;
    dVar4 = FUN_1747_068a(param_1);
    uVar2 = (uint)dVar4;
    if (dVar4 == 0) {
      dVar4 = FUN_1c07_03a2(param_1);
      uVar2 = (uint)dVar4;
    }
    if (DAT_374a_3c37 == '\0') {
      FUN_2099_094f(uVar2,(int)(dVar4 >> 0x10));
    }
    else {
      if (param_2 == 1) {
        uVar2 = uVar2 & 0xff00;
      }
      else {
        uVar2 = ((uint)DAT_374a_4076._3_1_ * 0xf) / 100;
      }
      if (param_2 == 2) {
        uVar3 = uVar2 & 0xff00;
      }
      else {
        uVar3 = ((uint)DAT_374a_4076._3_1_ * 0xf) / 100;
      }
      FUN_2099_0540(CONCAT11((char)(uVar3 >> 8),(char)uVar2),uVar3);
      FUN_2099_0a05(dVar4);
    }
  }
  return;
}

