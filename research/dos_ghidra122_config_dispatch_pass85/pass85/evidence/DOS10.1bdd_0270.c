
void __cdecl16far FUN_1bdd_0270(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  bool bVar5;
  int local_c6 [96];
  int local_6;
  int iStack_4;
  
  if ((DAT_3360_3fa5 != '\0') || (param_1 == 0)) {
    if (DAT_3360_16c4 != 0) {
      FUN_219b_214e((int)DAT_3360_16c4,(int)((ulong)DAT_3360_16c4 >> 0x10));
    }
    FUN_1bdd_025a();
    FUN_1273_006e(local_c6);
    piVar4 = local_c6 + param_1 * 3;
    iVar1 = *piVar4;
    local_6 = local_c6[param_1 * 3 + 1];
    iVar3 = local_c6[param_1 * 3 + 2];
    if (iVar3 < 0) {
      bVar5 = local_6 != 0;
      local_6 = -local_6;
      iVar3 = -(iVar3 + (uint)bVar5);
    }
    iStack_4 = iVar3;
    if (*piVar4 == 0) {
      FUN_1f67_000a((char *)s_Tune__d_not_found_3360_16c8,param_1);
    }
    iVar2 = FUN_219b_2161(*piVar4);
    DAT_3360_16c4 = CONCAT22(iVar3,iVar2);
    if (iVar3 != 0 || iVar2 != 0) {
      FUN_1273_006e(iVar2,iVar3,local_6,iStack_4,iVar1);
      if (param_1 == 0) {
        FUN_206c_0004(0x39,0,0,DAT_3360_16c4._2_2_,(undefined2)DAT_3360_16c4);
      }
      else if (local_c6[param_1 * 3 + 2] < 0) {
        FUN_206c_0b1d((undefined2)DAT_3360_16c4,DAT_3360_16c4._2_2_);
      }
      else {
        FUN_206c_0b72((undefined2)DAT_3360_16c4,DAT_3360_16c4._2_2_);
      }
      FUN_1bdd_0082();
    }
  }
  return;
}

