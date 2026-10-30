
void __cdecl16far FUN_1bff_040a(word param_1,int param_2,byte param_3)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  dword dVar4;
  
  if ((DAT_3395_40ac != '\0') && (((undefined2 *)&DAT_3395_3ec2)[param_1 * 3] != 0)) {
    if (DAT_3395_3c67 == '\0') {
      iVar1 = FUN_208d_0fb3();
      if (iVar1 != 0) {
        if (param_3 < DAT_3395_17ee) {
          return;
        }
        FUN_208d_0f20();
      }
    }
    else {
      iVar1 = FUN_208d_0f81();
      if (iVar1 != 0) {
        if (param_3 < DAT_3395_17ee) {
          return;
        }
        FUN_208d_0ef1();
      }
    }
    DAT_3395_17ee = param_3;
    dVar4 = FUN_1742_0680(param_1);
    uVar2 = (uint)dVar4;
    if (dVar4 == 0) {
      dVar4 = FUN_1bff_039a(param_1);
      uVar2 = (uint)dVar4;
    }
    if (DAT_3395_3c67 == '\0') {
      FUN_208d_095b(uVar2,(int)(dVar4 >> 0x10));
    }
    else {
      if (param_2 == 1) {
        uVar2 = uVar2 & 0xff00;
      }
      else {
        uVar2 = ((uint)DAT_3395_40a6._3_1_ * 0xf) / 100;
      }
      if (param_2 == 2) {
        uVar3 = uVar2 & 0xff00;
      }
      else {
        uVar3 = ((uint)DAT_3395_40a6._3_1_ * 0xf) / 100;
      }
      FUN_208d_054c(CONCAT11((char)(uVar3 >> 8),(char)uVar2),uVar3);
      FUN_208d_0a11(dVar4);
    }
  }
  return;
}

