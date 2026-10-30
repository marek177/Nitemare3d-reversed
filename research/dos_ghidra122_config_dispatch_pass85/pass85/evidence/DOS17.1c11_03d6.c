
void __cdecl16far FUN_1c11_03d6(word param_1,int param_2,byte param_3)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  dword dVar4;
  
  if ((DAT_3754_40be != '\0') && (((undefined2 *)&DAT_3754_3ed4)[param_1 * 3] != 0)) {
    if (DAT_3754_3c37 == '\0') {
      iVar1 = FUN_20a2_0fb3();
      if (iVar1 != 0) {
        if (param_3 < DAT_3754_17b6) {
          return;
        }
        FUN_20a2_0f20();
      }
    }
    else {
      iVar1 = FUN_20a2_0f81();
      if (iVar1 != 0) {
        if (param_3 < DAT_3754_17b6) {
          return;
        }
        FUN_20a2_0ef1();
      }
    }
    DAT_3754_17b6 = param_3;
    dVar4 = FUN_1751_0686(param_1);
    uVar2 = (uint)dVar4;
    if (dVar4 == 0) {
      dVar4 = FUN_1c11_039e(param_1);
      uVar2 = (uint)dVar4;
    }
    if (DAT_3754_3c37 == '\0') {
      FUN_20a2_095b(uVar2,(int)(dVar4 >> 0x10));
    }
    else {
      if (param_2 == 1) {
        uVar2 = uVar2 & 0xff00;
      }
      else {
        uVar2 = ((uint)DAT_3754_40bb * 0xf) / 100;
      }
      if (param_2 == 2) {
        uVar3 = uVar2 & 0xff00;
      }
      else {
        uVar3 = ((uint)DAT_3754_40bb * 0xf) / 100;
      }
      FUN_20a2_054c(CONCAT11((char)(uVar3 >> 8),(char)uVar2),uVar3);
      FUN_20a2_0a11(dVar4);
    }
  }
  return;
}

