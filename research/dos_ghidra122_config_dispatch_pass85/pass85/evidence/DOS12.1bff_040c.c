
void __cdecl16far FUN_1bff_040c(word param_1,int param_2,byte param_3)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  dword dVar4;
  
  if ((DAT_339b_40ac != '\0') && (((undefined2 *)&DAT_339b_3ec2)[param_1 * 3] != 0)) {
    if (DAT_339b_3c67 == '\0') {
      iVar1 = FUN_2093_0fb3();
      if (iVar1 != 0) {
        if (param_3 < DAT_339b_17e0) {
          return;
        }
        FUN_2093_0f20();
      }
    }
    else {
      iVar1 = FUN_2093_0f81();
      if (iVar1 != 0) {
        if (param_3 < DAT_339b_17e0) {
          return;
        }
        FUN_2093_0ef1();
      }
    }
    DAT_339b_17e0 = param_3;
    dVar4 = FUN_1742_068c(param_1);
    uVar2 = (uint)dVar4;
    if (dVar4 == 0) {
      dVar4 = FUN_1bff_039c(param_1);
      uVar2 = (uint)dVar4;
    }
    if (DAT_339b_3c67 == '\0') {
      FUN_2093_095b(uVar2,(int)(dVar4 >> 0x10));
    }
    else {
      if (param_2 == 1) {
        uVar2 = uVar2 & 0xff00;
      }
      else {
        uVar2 = ((uint)DAT_339b_40a9 * 0xf) / 100;
      }
      if (param_2 == 2) {
        uVar3 = uVar2 & 0xff00;
      }
      else {
        uVar3 = ((uint)DAT_339b_40a9 * 0xf) / 100;
      }
      FUN_2093_054c(CONCAT11((char)(uVar3 >> 8),(char)uVar2),uVar3);
      FUN_2093_0a11(dVar4);
    }
  }
  return;
}

